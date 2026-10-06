# Notes: invoice export fix (fictional "Ledgerly" service)

Problem: the nightly invoice export dropped any invoice with a null `due_date`, so
finance saw totals that were short with no error logged.

Change: `export_invoices()` in `export.py` now writes null-due-date invoices with an empty
due date column and logs a warning with the invoice id. Considered failing the whole
export instead; rejected because finance needs the file by 06:00 even when data is dirty.

Verification so far:
- Unit tests `test_export_null_due_date` and `test_export_warns_on_null` pass locally.
- Integration test against the sample SQLite database passes locally.
- Not yet run: the nightly job on staging. No PR is open, so no CI run exists.
