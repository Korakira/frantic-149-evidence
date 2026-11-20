# Which leads need attention?

**A small, repeatable check for a customer spreadsheet.**

An overdue action, a missing owner or two records for the same lead can be easy to miss. This demonstration turns an exported CSV into a short list of records to review. It reads columns by name, so moving a column does not break the check.

All eight records below are **synthetic demonstration data**, not client records or paid work. The cutoff date is **20 November 2026**.

## What the example finds

| Record | Finding | Action to consider |
| --- | --- | --- |
| L002, records 2 and 6 | Duplicate lead ID | Check both records before merging or contacting |
| L002, record 2 | Next action is two days overdue | Confirm whether follow-up already happened |
| L003 | No next-action date | Agree a date |
| L005 | No owner | Assign responsibility |
| L006 | Impossible calendar date | Correct the date from the source |

**Result: five of eight records flagged, six findings.** A record can have more than one finding. A closed lead is not flagged for missing follow-up, and an action due today is not treated as overdue.

## Inspect and rerun

- [Original checker](audit.py), using Python's standard library only.
- [Synthetic input](sample.csv).
- [Expected report](report.json).
- [Six checks](test_audit.py), including reordered columns and closed leads.

Download these four files into one folder, then run:

```sh
python -m unittest discover -s . -v
python audit.py sample.csv --as-of 2026-11-20 --output result
```

The command produces `report.json` and `findings.csv` in the output folder. It does not edit the input or send messages. Unknown statuses are flagged for clarification; missing dates and owners are not guessed.

## Request a small audit

Starter work is **5 USDC** for one anonymized CSV or flat JSON file, up to 100 records and 20 fields, with up to three agreed validation rules. This example illustrates possible checks; we confirm which rules your order includes. Payment in EUR through PayPal is available by an agreed quote.

You receive row-level findings, a summary and a rerunnable checker. Scope, payment details and delivery date are confirmed before funding; the usual starter target is two business days after funding and receipt of inputs. CRM migration, integrations and ongoing maintenance need a separate quote.

[Request a quote](https://github.com/Korakira/frantic-149-evidence/issues/new?template=work-request.yml) · [All starter services](../fixed-price-services.md)

GitHub requests are public. Share only a public or anonymized example there. A private channel for confidential files is agreed separately.

## Limits

This checks the supplied export, not a live CRM. It cannot tell whether a colleague already followed up elsewhere, whether a customer consented to contact, or whether an invoice was paid. It makes no bank or email connections. Dates have day precision; use the relevant local cutoff date. Customer statuses and business rules must be agreed before applying it to real work.

**En español:** detectamos duplicados, seguimientos incompletos y fechas que necesitan revisión. La muestra es ficticia y permite comprobar la entrega antes de pedir un trabajo. Revisiones pequeñas desde **5 USDC**, o precio acordado en euros por PayPal.
