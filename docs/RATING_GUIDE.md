# Rating guide for the human validation (raters A and B)

**Status:** frozen before rating (deviation 11). The kit run records this file's hash.
**Protocol:** `docs/PREREGISTRATION_V2.md` §3.5 and deviations 9–11. The workflow is in `docs/HUMAN_VALIDATION_PROTOCOL.md`.
**Supporting Information:** this guide is published with the paper.

## 1. Why we rate

The study asks whether phishing detectors raise false alarms on legitimate emails that an AI helped write. To trust that result, we must show that the AI versions are what we claim they are. Two things need to hold:
- a **rewrite** (RW) of a legitimate email is still legitimate, and a rewrite of a phishing email is still phishing, with the same intent;
- an email the AI **composed** (DN) from a subject line looks like a real legitimate email.

Your answers measure exactly this. You are **not** asked whether the text sounds like AI. Ignore style.

## 2. General rules

1. **Work alone.** Do not discuss items with the other rater until both workbooks are finished. Do not use ChatGPT or any other AI tool, a web search, or any other help.
2. **Stay blind.** Until the score run, do not open:
   - `key.csv`;
   - the outputs of the `04-human-validation-*` kernels on Kaggle;
   - the sampling code run on the real data.
   You will sign a one-line confirmation when you submit (DECISION_LOG D015).
3. **Safety.** Links are defanged (`hxxp`, `www[.]`). Never visit a link or call a number. Never copy text out of the workbook. The workbook stays private: do not upload or forward it.
4. **Pace.** An RW item takes about one minute and a DN item about 30 seconds. Work in sessions of at most 60 minutes, rate in the given order, and answer every cell.
   - You may correct a slip in the same session.
   - Do not go back to systematically change earlier answers.
5. **First do the practice workbook (section 6),** then the real one.

## 3. Sheet RW: an ORIGINAL email and an AI REWRITE of it

Read the original first, then the rewrite. Answer three questions.

### (a) `intent_preserved`: does the rewrite keep the intent of the original?

The intent is the sender's purpose and what the sender wants the reader to do.

**Answer `yes` when** the purpose and every request are the same. Changes to any of these do NOT matter:
- wording, tone, length, formality;
- order of sentences, greeting or sign-off;
- grammar or spelling fixes.

**Answer `no` when any of these is true:**
- a request is added, removed or changed (for example, "review the attached file" becomes "log in to confirm your details");
- the sender's role changes in a way that matters (for example, a colleague becomes "your bank");
- a key fact changes materially (an amount, a date, the person or account involved);
- the main point is missing, or the rewrite is cut off or a different email altogether.

### (b) `security_element_changed`: was a security-relevant element added or removed?

There are four kinds of security-relevant element:

| Element | Counts as present when the email… |
|---|---|
| **Request** | asks the reader to log in, give a password or code, give personal or financial details, pay or transfer money, buy gift cards, open a file, click a link, call a number, or reply with information |
| **Link** | contains a URL or web address (defanged here) |
| **Attachment** | says a file is attached or enclosed, or asks to open one |
| **Deadline / pressure** | sets an explicit time limit or threat ("within 24 hours", "today", "or your account will be closed", "immediately") |

Compare the original and the rewrite element by element:
- **`added`:** the rewrite has an element the original does not have. Example: a link appears, or "immediately" is added where there was no time pressure.
- **`removed`:** the original has an element the rewrite lacks. Example: one of two links disappears, or the 24-hour threat is dropped.
- **`added_and_removed`:** both of the above happen.
- **`no`:** every element is unchanged.

Not a change:
- the same link written differently (for example, "click here" pointing to the same address the original shows);
- the same deadline reworded ("by Friday" becomes "before the end of the week");
- the same request phrased more or less politely.

### (c) `rewrite_label`: is the REWRITE phishing or legitimate?

Judge the **rewrite on its own**, as if it had just arrived in your inbox. The original is shown only for (a) and (b).

**`phishing`:** the email tries to **deceive** the reader into one of these:
- revealing credentials or personal or financial information;
- paying money;
- opening or clicking something harmful;
- taking any other action that benefits the sender at the reader's expense.

Typical signs are impersonation (a bank, IT desk, courier or boss), a pretext, pressure, or a mismatch between the claimed sender and the request. Advance-fee ("419") fraud and fake invoices count as phishing.

**`legitimate`:** ordinary communication with no deceptive intent. This includes:
- work and personal emails;
- genuine notifications, newsletters and ordinary marketing that does not deceive.

**`unsure`:** use this **only** when, after a careful reading, the email could reasonably be either. Do not use it to save time. Note that "unsure" counts **against** label preservation.

**Do NOT use these as reasons by themselves:**
- polished or clumsy writing;
- signs that an AI wrote it;
- unusual names;
- bracketed placeholders such as `[Name]`;
- a link, if nothing deceptive is asked.

## 4. Sheet DN: ONE email that an AI composed from a subject line

### `plausible_legitimate`: would this pass as a plausible, ordinary legitimate email?

**`yes`:** a real person or organisation could plausibly send this email with this subject. It is coherent and on topic. Ignore bracketed placeholders such as `[Name]` and `[Date]`.

**`no`:** any one of these makes the answer `no`:
- incoherent, rambling or repetitive;
- contradicts its own subject;
- contains AI meta-text ("Sure, here is an email…", "As an AI…", notes to the user);
- is not an email (for example, a list of options or an essay);
- reads as phishing or a scam.

## 5. Short made-up examples (not from the data)

| Original | Rewrite | (a) | (b) | (c) |
|---|---|---|---|---|
| "Hi all, please send me your timesheets by Friday so I can run payroll. — Maria" | "Hello everyone, kindly submit your timesheets by Friday so that payroll can be processed. Best, Maria" | yes | no | legitimate |
| "Hi all, please send me your timesheets by Friday so I can run payroll." | "Please confirm your payroll details at hxxp://payroll-check[.]example by Friday." | no | added | phishing |
| "Your mailbox will be closed within 24 hours. Verify now at hxxp://mail-verify[.]example" | "We noticed unusual activity on your mailbox. Please verify it at hxxp://mail-verify[.]example" | yes | removed | phishing |
| "Your invoice is attached. Pay today at hxxp://pay[.]example to avoid penalties." | "Thanks for your business! Let me know if you have questions about our services." | no | removed | legitimate |

DN examples:
- Subject "Team lunch on Thursday", with a short, friendly note giving the place and time: **yes**.
- Subject "Q3 budget review", but the body begins "Sure! Here's a professional email you can use:": **no**.

## 6. Practice round (before the real workbook)

1. Each rater fills the practice workbook (`practice.xlsx`) alone. It holds about 20 items, none of which appear in the real sample.
2. The coordinator runs `python scripts/human_validation.py practice A.xlsx B.xlsx`. This lists agreement and the disagreements.
3. The three authors meet and walk through every disagreement using this guide.
4. Wording that caused confusion may be **clarified once**, before the real rating starts. The definitions and answer options themselves do not change. Each clarification is committed as a dated change to this file and logged in DECISION_LOG.
5. Then the real workbooks are rated, and the guide stays frozen.
