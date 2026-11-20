"""Read-only lead follow-up audit. No network calls or message sending."""
import argparse
import csv
import io
import json
from collections import Counter
from datetime import date
from pathlib import Path

REQUIRED = {'lead_id', 'status', 'owner', 'next_action_date'}
ACTIVE = {'new', 'contacted', 'proposal', 'negotiation'}
CLOSED = {'won', 'lost', 'closed'}


def audit(text, as_of):
    reader = csv.DictReader(io.StringIO(text.lstrip('\ufeff')))
    headers = reader.fieldnames or []
    if len(headers) != len(set(headers)):
        raise ValueError('Duplicate column names; resolve them before auditing.')
    if not REQUIRED.issubset(headers):
        raise ValueError('Missing columns: ' + ', '.join(sorted(REQUIRED - set(headers))))
    rows = list(reader)
    if len(rows) > 100 or len(headers) > 20:
        raise ValueError('Starter scope: at most 100 records and 20 columns.')
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError('A record has a different number of cells from the header.')
    counts = Counter(row['lead_id'].strip() for row in rows if row['lead_id'].strip())
    findings = []

    def add(index, row, code, detail):
        findings.append({'record': index, 'lead_id': row['lead_id'], 'code': code, 'detail': detail})

    for index, row in enumerate(rows, 1):
        lead = row['lead_id'].strip()
        state = row['status'].strip().lower()
        if not lead:
            add(index, row, 'MISSING_ID', 'A stable lead ID is needed; no ID was invented.')
        elif counts[lead] > 1:
            add(index, row, 'DUPLICATE_ID', 'Review both records before merging or contacting anyone.')
        if state not in ACTIVE | CLOSED:
            add(index, row, 'UNKNOWN_STATUS', 'Confirm status before deciding whether follow-up is required.')
            continue
        if state in CLOSED:
            continue
        missing = []
        if not row['owner'].strip():
            missing.append('owner')
        if not row['next_action_date'].strip():
            missing.append('next_action_date')
        if missing:
            add(index, row, 'INCOMPLETE_FOLLOWUP', 'Missing: ' + ', '.join(missing))
        raw_date = row['next_action_date'].strip()
        if raw_date:
            try:
                due = date.fromisoformat(raw_date)
                if due.isoformat() != raw_date:
                    raise ValueError('Use YYYY-MM-DD.')
            except ValueError:
                add(index, row, 'INVALID_DATE', 'Expected a real calendar date in YYYY-MM-DD format.')
                continue
            if due < as_of:
                add(index, row, 'OVERDUE', f'Next action is {(as_of - due).days} days overdue; review before contacting.')
    return {'as_of': as_of.isoformat(), 'records': len(rows),
            'records_flagged': len({f['record'] for f in findings}),
            'counts': dict(Counter(f['code'] for f in findings)), 'findings': findings,
            'limitations': ['Uses the supplied export only; no live CRM or email access.',
                            'Does not infer payments, consent or whether the customer was already contacted.',
                            'Dates have day precision; the caller supplies the relevant local date.']}


def csv_safe(value):
    value = str(value)
    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@')) else value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--as-of', required=True, type=date.fromisoformat)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.input.resolve() in {(args.output / name).resolve() for name in ('report.json', 'findings.csv')}:
        parser.error('Output files must not overwrite the input file.')
    result = audit(args.input.read_text(encoding='utf-8-sig'), args.as_of)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'report.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    with (args.output / 'findings.csv').open('w', newline='', encoding='utf-8-sig') as target:
        writer = csv.DictWriter(target, fieldnames=['record', 'lead_id', 'code', 'detail'])
        writer.writeheader()
        writer.writerows({k: csv_safe(v) for k, v in f.items()} for f in result['findings'])
    print(json.dumps({k: result[k] for k in ['records', 'records_flagged', 'counts']}))


if __name__ == '__main__':
    main()
