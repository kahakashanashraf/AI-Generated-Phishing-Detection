# Data intake (no raw dataset committed)

Use legally redistributable sources and record URL, version, checksum, license, collection method, and label provenance.

Expected CSV columns: text,label,generator,source,group_id
- `label=1`: AI-produced phishing email; `label=0`: human-produced phishing email.
- No benign examples in this first baseline: this is **origin attribution**.
- Use one stable group_id per original campaign/template/ancestor across all derivatives, even across sources if provenance reveals overlap.
- Reject unknown generator provenance for leave-one-generator-out evaluation.
- PII and email bodies should stay outside GitHub. The provided sample is synthetic dummy data only.

## Initial audit
```bash
python -m src.audit --csv /kaggle/input/your-dataset/manifest.csv
```
Do not train if it reports exact duplicate text assigned to multiple groups or labels; audit near duplicates manually as well.
