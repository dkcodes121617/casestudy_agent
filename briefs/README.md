# Briefs

One file per project: `briefs/<project-id>.md`. The agent will not write a study
for a project without a clean brief here.

## Why these exist

The PDF and `projects.ts` say **what** was built. Neither says what may be
**published**, and neither contains the reasoning behind any decision. A brief
supplies both, and it is the only place confidential material is ever recorded.

## Drafting one

```bash
python -m casestudy.brief cubbi        # or: make brief P=cubbi
```

The drafter fills in everything it can source, tags each line with where it came
from, and marks everything else `[NEEDS REVIEW]` rather than guessing.

## The three rules

1. **Every line carries a provenance tag or `[NEEDS REVIEW]`.** No untagged lines.
2. **`[NEEDS REVIEW]` is a hard gate.** The writer refuses to run against a brief
   containing one. Clear them at the rate you publish — about five per brief,
   five minutes each.
3. **`## Confidential` is never shown to the writer.** It is fed only to the
   confidentiality scanner, as a denylist. That asymmetry is what makes
   unattended generation safe.
