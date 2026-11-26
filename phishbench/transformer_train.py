"""Fine-tuning loop for the transformer detectors D4 (DistilBERT) and D5 (RoBERTa), with optional M2 consistency.

Pre-registration §4, frozen settings:
- max_len 256 using head 128 + tail 128 tokens;
- lr 2e-5, batch 16, weight decay 0.01, warmup 6%;
- at most 4 epochs (D4: at most 2, as in N12), keeping the best epoch by validation average precision.

M2 adds lam * symmetric KL between the predictions for parent and rewrite pairs, with lam = 0.2.
torch and transformers are imported lazily, so the pure helpers stay testable without them.
"""

from __future__ import annotations

import math
import time

import numpy as np


def head_tail(ids: list[int], max_tokens: int, head: int) -> list[int]:
    """Keep the first `head` and the last (max_tokens - head) ids when the sequence is too long."""
    if len(ids) <= max_tokens:
        return list(ids)
    tail = max_tokens - head
    return list(ids[:head]) + (list(ids[-tail:]) if tail > 0 else [])


def encode(tokenizer, texts: list[str], max_len: int = 256) -> list[list[int]]:
    """Tokenise without truncation, apply head+tail to the content tokens, then add special tokens."""
    n_special = tokenizer.num_special_tokens_to_add(pair=False)
    body = max_len - n_special
    out = []
    for t in texts:
        ids = tokenizer(t, add_special_tokens=False, truncation=False)["input_ids"]
        out.append(tokenizer.build_inputs_with_special_tokens(head_tail(ids, body, body // 2)))
    return out


def _pad(batch_ids, pad_id):
    import torch
    L = max(len(x) for x in batch_ids)
    ids = torch.full((len(batch_ids), L), pad_id, dtype=torch.long)
    att = torch.zeros((len(batch_ids), L), dtype=torch.long)
    for i, x in enumerate(batch_ids):
        ids[i, :len(x)] = torch.tensor(x)
        att[i, :len(x)] = 1
    return ids, att


def predict_proba(model, tokenizer, enc: list[list[int]], batch_size: int = 64, device: str = "cuda") -> np.ndarray:
    import torch
    model.eval()
    order = np.argsort([len(x) for x in enc], kind="stable")
    probs = np.zeros(len(enc))
    with torch.no_grad():
        for s in range(0, len(enc), batch_size):
            idx = order[s:s + batch_size]
            ids, att = _pad([enc[i] for i in idx], tokenizer.pad_token_id)
            with torch.autocast("cuda", dtype=torch.float16, enabled=device.startswith("cuda")):
                logits = model(input_ids=ids.to(device), attention_mask=att.to(device)).logits.float()
            probs[idx] = torch.softmax(logits, dim=-1)[:, 1].cpu().numpy()
    return probs


def train_classifier(model_dir: str, tokenizer, train_enc, y, w, val_enc, yv, seed: int, max_epochs: int,
                     pairs: list[tuple[int, int]] | None = None, lam: float = 0.0, lr: float = 2e-5,
                     batch_size: int = 16, weight_decay: float = 0.01, warmup: float = 0.06, device: str = "cuda",
                     log=print):
    """Train and return (best_model, history). Rows are weighted per sample (balanced class weights times base weights)."""
    import torch
    from sklearn.metrics import average_precision_score
    from transformers import AutoModelForSequenceClassification, get_linear_schedule_with_warmup

    from .models import balanced_weights

    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    model = AutoModelForSequenceClassification.from_pretrained(model_dir, num_labels=2).to(device)
    sw = balanced_weights(y, w)
    sw = torch.tensor(sw / sw.mean(), dtype=torch.float32)
    yt = torch.tensor(np.asarray(y), dtype=torch.long)
    n = len(train_enc)
    steps_per_epoch = math.ceil(n / batch_size)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    sched = get_linear_schedule_with_warmup(opt, int(warmup * steps_per_epoch * max_epochs), steps_per_epoch * max_epochs)
    scaler = torch.amp.GradScaler("cuda", enabled=device.startswith("cuda"))
    rng = np.random.default_rng(seed)
    pairs = list(pairs or [])
    best, best_ap, history = None, -1.0, []
    for epoch in range(max_epochs):
        model.train()
        t0 = time.time()
        perm = rng.permutation(n)
        pair_perm = rng.permutation(len(pairs)) if pairs else []
        tot = 0.0
        for s in range(steps_per_epoch):
            idx = perm[s * batch_size:(s + 1) * batch_size]
            ids, att = _pad([train_enc[i] for i in idx], tokenizer.pad_token_id)
            with torch.autocast("cuda", dtype=torch.float16, enabled=device.startswith("cuda")):
                logits = model(input_ids=ids.to(device), attention_mask=att.to(device)).logits.float()
                ce = torch.nn.functional.cross_entropy(logits, yt[idx].to(device), reduction="none")
                loss = (ce * sw[idx].to(device)).mean()
                if pairs and lam > 0:
                    k = 8
                    sel = [pairs[j] for j in pair_perm[(s * k) % len(pairs):(s * k) % len(pairs) + k]] or pairs[:k]
                    pid, patt = _pad([train_enc[a] for a, _ in sel], tokenizer.pad_token_id)
                    rid, ratt = _pad([train_enc[b] for _, b in sel], tokenizer.pad_token_id)
                    lp = torch.log_softmax(model(input_ids=pid.to(device), attention_mask=patt.to(device)).logits.float(), -1)
                    lr_ = torch.log_softmax(model(input_ids=rid.to(device), attention_mask=ratt.to(device)).logits.float(), -1)
                    skl = 0.5 * (torch.sum(lp.exp() * (lp - lr_), -1) + torch.sum(lr_.exp() * (lr_ - lp), -1)).mean()
                    loss = loss + lam * skl
            opt.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(opt)
            scaler.update()
            sched.step()
            tot += float(loss)
        pv = predict_proba(model, tokenizer, val_enc, device=device)
        ap = float(average_precision_score(yv, pv))
        history.append({"epoch": epoch + 1, "train_loss": tot / steps_per_epoch, "val_ap": ap,
                        "seconds": round(time.time() - t0, 1)})
        log(f"    epoch {epoch + 1}: loss {tot / steps_per_epoch:.4f} val AP {ap:.4f}")
        if ap > best_ap:
            best_ap = ap
            best = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    model.load_state_dict(best)
    return model, history
