import unittest
from datetime import date
from pathlib import Path
from audit import audit, csv_safe


class AuditTest(unittest.TestCase):
    def test_sample_and_closed_lead(self):
        result = audit(Path(__file__).with_name('sample.csv').read_text(), date(2026, 11, 20))
        self.assertEqual(result['records'], 8)
        self.assertEqual(result['records_flagged'], 5)
        self.assertEqual(result['counts'], {'DUPLICATE_ID': 2, 'OVERDUE': 1,
                                           'INCOMPLETE_FOLLOWUP': 2, 'INVALID_DATE': 1})
        self.assertFalse(any(x['lead_id'] in {'L004', 'L007'} for x in result['findings']))

    def test_reordered_columns_and_bom(self):
        a = 'lead_id,status,owner,next_action_date\nX,new,Ana,2026-11-19\n'
        b = '\ufeffowner,next_action_date,status,lead_id\nAna,2026-11-19,new,X\n'
        self.assertEqual(audit(a, date(2026, 11, 20)), audit(b, date(2026, 11, 20)))

    def test_missing_header_fails(self):
        with self.assertRaises(ValueError):
            audit('lead_id,status\nX,new\n', date(2026, 11, 20))

    def test_duplicate_headers_and_malformed_record_fail(self):
        with self.assertRaises(ValueError):
            audit('lead_id,status,owner,owner,next_action_date\n', date(2026, 11, 20))
        with self.assertRaises(ValueError):
            audit('lead_id,status,owner,next_action_date\nX,new\n', date(2026, 11, 20))

    def test_unknown_state_is_not_assumed_active(self):
        r = audit('lead_id,status,owner,next_action_date\nX,unknown,,2026-11-01\n', date(2026, 11, 20))
        self.assertEqual(r['counts'], {'UNKNOWN_STATUS': 1})

    def test_csv_formulas_are_neutralized(self):
        self.assertEqual(csv_safe('=1+1'), "'=1+1")
        self.assertEqual(csv_safe('  @SUM(A1)'), "'  @SUM(A1)")
        self.assertEqual(csv_safe('L001'), 'L001')


if __name__ == '__main__':
    unittest.main()
