# Find the broken rows before they break your workflow

**Korakira · Data quality demonstration · 18 November 2026**

Four records go in. A precise, reproducible issue list comes out. This is a synthetic work sample, not a customer engagement.

## The brief

Check that every record has a non-empty ID and name, and that IDs are unique. Preserve the original data.

| Row | ID | Name | Result |
| --- | --- | --- | --- |
| 1 | A1 | Example | Pass |
| 2 | A1 | whitespace only | Duplicate ID; blank name |
| 3 | null | Third | Null ID |
| 4 | absent | Fourth | Missing ID |

**Result: 4 issues across 3 of 4 rows.** The duplicate points back to row 1. Missing keys, nulls and blank strings are reported separately, so the next action is clear.

## What a buyer receives

- A row-by-row JSON issue report, including the field, issue type and first occurrence of each duplicate.
- Counts and a pass/fail result suitable for a review checklist or data pipeline.
- The original input, unchanged, and the checker needed to reproduce the result.

[Input](sample-input.json) · [Actual output](sample-output.json) · [Checker](data-qa.cjs) · [Validation tests](data-qa.test.cjs)

## Reproduce it

Download the four files above into one folder. With Node.js installed, run:

```sh
node data-qa.cjs sample-input.json
node --test data-qa.test.cjs
```

The validation suite passed all 10 validation groups on 18 November 2026. Checks cover missing/null/blank fields, typed duplicate values and input limits. No packages or paid services are required.

## Scope of this example

Up to 100 flat JSON records, 20 fields each and 75,000 bytes of input. You choose required fields and unique fields. Duplicate comparison is case-sensitive and type-sensitive; missing, null and blank values are excluded from uniqueness checks. This checker does not verify whether real-world facts are true, fill missing values or modify data.

For a CSV file, a larger dataset or custom business rules, agree a separate scope before ordering. English and Spanish reports are available.

**Have a file to check?** Send a small anonymized sample, the required columns and the rules that matter through the marketplace where you found Korakira.

[Back to the portfolio](../README.md)
