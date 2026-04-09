# 11 — Fault Record

A running log of bugs, failures, anomalies, and the fixes that resolved them. Anything that surprised me, broke, or wasted time gets an entry here. Future-me will thank present-me.

The point is twofold:
- **Operational:** if I see the same symptom again, I can find the previous root cause fast.
- **Interview / CV:** real, dated, documented debugging is one of the most credible signals in an interview. "Walk me through a tough bug you fixed" is much easier to answer with this in hand.

## How to use this file

Append new entries at the **top**. One entry per fault. Use the template below.

```
## YYYY-MM-DD — <subsystem>: <one-line symptom>

**Symptom:**
What I saw (sensor reading wrong, board didn't power up, frame CRC mismatched, etc.).

**Context:**
What I was doing when it appeared. Rev / commit / branch / hardware revision.

**Investigation:**
What I tried, in order. Include dead-ends — they save time later.

**Root cause:**
The actual cause. Be honest.

**Fix:**
What I changed. Link to commit if applicable.

**Lesson:**
What I'll do differently next time. (Optional but encouraged.)
```

---

## Example entry (delete or replace once a real fault is logged)

## 2026-04-09 — repo: GitHub repo not accessible during initial planning

**Symptom:**
`git clone` and `WebFetch` against `github.com/wooseongjung/spyderrobot` returned 404.

**Context:**
Phase 0 setup. Trying to read the existing repo state before restructuring.

**Investigation:**
Tried HTTPS clone, tried fetching the README via `raw.githubusercontent.com`, tried browsing the user profile. User profile listed only 3 public repos and `spyderrobot` was not among them.

**Root cause:**
The repository was set to private.

**Fix:**
Owner toggled the repo to public; subsequent fetches succeeded.

**Lesson:**
Before assuming a remote resource is missing, verify visibility. `gh repo view` would have surfaced the private status quickly with auth.

---

> Real entries start below this line. Newest first.
