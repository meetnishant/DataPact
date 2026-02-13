USE commercial_finance;

INSERT INTO customers (customer_id, customer_name, segment, country_code, kyc_status, created_at) VALUES
  (1001, 'NatWest Corp', 'commercial', 'GB', 'verified', '2025-11-15 09:00:00'),
  (1002, 'Institutional Alpha', 'institutional', 'GB', 'verified', '2025-11-20 10:15:00'),
  (1003, 'Commercial Beta', 'commercial', 'US', 'pending', '2025-12-02 08:30:00'),
  (1004, 'Institutional Gamma', 'institutional', 'DE', 'verified', '2025-12-10 14:45:00'),
  (1005, 'Commercial Delta', 'commercial', 'GB', 'verified', '2026-01-05 11:20:00');

INSERT INTO deposit_accounts (account_id, customer_id, product_type, status, currency, balance, opened_at) VALUES
  (2001, 1001, 'checking', 'active', 'GBP', 2500000.00, '2025-11-16 09:00:00'),
  (2002, 1001, 'treasury', 'active', 'GBP', 12500000.00, '2025-11-18 10:00:00'),
  (2003, 1002, 'savings', 'active', 'GBP', 4800000.00, '2025-11-22 12:00:00'),
  (2004, 1003, 'checking', 'dormant', 'USD', 150000.00, '2025-12-05 09:30:00'),
  (2005, 1004, 'treasury', 'active', 'EUR', 7200000.00, '2025-12-12 13:15:00'),
  (2006, 1005, 'savings', 'closed', 'GBP', 0.00, '2026-01-08 10:10:00');

INSERT INTO deposit_transactions (txn_id, account_id, txn_type, txn_amount, txn_ts, channel) VALUES
  (3001, 2001, 'credit', 250000.00, '2025-11-20 09:15:00', 'online'),
  (3002, 2001, 'debit', 120000.00, '2025-11-21 10:45:00', 'api'),
  (3003, 2002, 'credit', 2000000.00, '2025-11-23 14:20:00', 'branch'),
  (3004, 2002, 'fee', 500.00, '2025-11-24 16:00:00', 'api'),
  (3005, 2003, 'credit', 600000.00, '2025-11-25 11:30:00', 'online'),
  (3006, 2003, 'debit', 250000.00, '2025-11-26 12:00:00', 'online'),
  (3007, 2004, 'credit', 50000.00, '2025-12-06 10:30:00', 'branch'),
  (3008, 2004, 'debit', 15000.00, '2025-12-07 15:00:00', 'api'),
  (3009, 2005, 'credit', 1250000.00, '2025-12-13 09:10:00', 'online'),
  (3010, 2005, 'fee', 900.00, '2025-12-14 17:30:00', 'api'),
  (3011, 2006, 'debit', 0.00, '2026-01-10 08:40:00', 'online'),
  (3012, 2006, 'credit', 0.00, '2026-01-11 09:50:00', 'online');

INSERT INTO lending_loans (loan_id, customer_id, product_type, status, currency, principal_balance, interest_rate, opened_at) VALUES
  (4001, 1001, 'term', 'active', 'GBP', 8000000.00, 0.0425, '2025-11-19 10:00:00'),
  (4002, 1002, 'revolver', 'active', 'GBP', 4500000.00, 0.0350, '2025-11-28 09:30:00'),
  (4003, 1003, 'term', 'delinquent', 'USD', 1200000.00, 0.0650, '2025-12-08 11:15:00'),
  (4004, 1004, 'revolver', 'closed', 'EUR', 0.00, 0.0300, '2025-12-18 14:00:00');

INSERT INTO loan_payments (payment_id, loan_id, payment_amount, payment_ts, payment_status) VALUES
  (5001, 4001, 250000.00, '2025-11-30 09:00:00', 'posted'),
  (5002, 4001, 250000.00, '2025-12-30 09:00:00', 'posted'),
  (5003, 4002, 150000.00, '2025-12-05 10:00:00', 'posted'),
  (5004, 4002, 150000.00, '2026-01-05 10:00:00', 'pending'),
  (5005, 4003, 80000.00, '2025-12-20 15:00:00', 'posted'),
  (5006, 4003, 80000.00, '2026-01-20 15:00:00', 'failed'),
  (5007, 4004, 0.00, '2025-12-25 12:00:00', 'posted'),
  (5008, 4004, 0.00, '2026-01-25 12:00:00', 'posted');
