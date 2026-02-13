#!/usr/bin/env bash
set -euo pipefail

export DB_HOST=${DB_HOST:-127.0.0.1}
export DB_PORT=${DB_PORT:-3306}
export DB_USER=${DB_USER:-root}
export DB_PASSWORD=${DB_PASSWORD:-secret}
export DB_NAME=${DB_NAME:-commercial_finance}
export DB_RESET_STATUS=${DB_RESET_STATUS:-active}

echo "==> Seeding MySQL demo database"
python3 demo/scripts/seed_mysql.py

echo "==> Scenario 1: Baseline validation (producer)"
datapact validate --contract demo/contracts/producer_customers.yaml \
  --db-type mysql --db-host "$DB_HOST" --db-port "$DB_PORT" \
  --db-user "$DB_USER" --db-password "$DB_PASSWORD" --db-name "$DB_NAME" \
  --db-table customers

datapact validate --contract demo/contracts/producer_deposit_accounts.yaml \
  --db-type mysql --db-host "$DB_HOST" --db-port "$DB_PORT" \
  --db-user "$DB_USER" --db-password "$DB_PASSWORD" --db-name "$DB_NAME" \
  --db-table deposit_accounts

datapact validate --contract demo/contracts/producer_deposit_transactions.yaml \
  --db-type mysql --db-host "$DB_HOST" --db-port "$DB_PORT" \
  --db-user "$DB_USER" --db-password "$DB_PASSWORD" --db-name "$DB_NAME" \
  --db-table deposit_transactions

datapact validate --contract demo/contracts/producer_lending_loans.yaml \
  --db-type mysql --db-host "$DB_HOST" --db-port "$DB_PORT" \
  --db-user "$DB_USER" --db-password "$DB_PASSWORD" --db-name "$DB_NAME" \
  --db-table lending_loans

datapact validate --contract demo/contracts/producer_loan_payments.yaml \
  --db-type mysql --db-host "$DB_HOST" --db-port "$DB_PORT" \
  --db-user "$DB_USER" --db-password "$DB_PASSWORD" --db-name "$DB_NAME" \
  --db-table loan_payments

echo "==> Scenario 1: Baseline validation (consumer A)"
datapact validate --contract demo/contracts/consumer_a_deposit_accounts.yaml \
  --db-type mysql --db-host "$DB_HOST" --db-port "$DB_PORT" \
  --db-user "$DB_USER" --db-password "$DB_PASSWORD" --db-name "$DB_NAME" \
  --db-table deposit_accounts

datapact validate --contract demo/contracts/consumer_a_deposit_transactions.yaml \
  --db-type mysql --db-host "$DB_HOST" --db-port "$DB_PORT" \
  --db-user "$DB_USER" --db-password "$DB_PASSWORD" --db-name "$DB_NAME" \
  --db-table deposit_transactions

echo "==> Scenario 1: Baseline validation (consumer B)"
datapact validate --contract demo/contracts/consumer_b_accounts_agg.yaml \
  --db-type mysql --db-host "$DB_HOST" --db-port "$DB_PORT" \
  --db-user "$DB_USER" --db-password "$DB_PASSWORD" --db-name "$DB_NAME" \
  --db-table deposit_accounts

datapact validate --contract demo/contracts/consumer_b_loans_agg.yaml \
  --db-type mysql --db-host "$DB_HOST" --db-port "$DB_PORT" \
  --db-user "$DB_USER" --db-password "$DB_PASSWORD" --db-name "$DB_NAME" \
  --db-table lending_loans

echo "==> Scenario 1: Baseline validation (consumer C)"
datapact validate --contract demo/contracts/consumer_c_exposure.yaml \
  --db-type mysql --db-host "$DB_HOST" --db-port "$DB_PORT" \
  --db-user "$DB_USER" --db-password "$DB_PASSWORD" --db-name "$DB_NAME" \
  --db-query "SELECT c.customer_id, c.segment,\
    COALESCE(SUM(da.balance), 0) AS total_deposits,\
    COALESCE(SUM(ll.principal_balance), 0) AS total_loans\
   FROM customers c\
   LEFT JOIN deposit_accounts da ON c.customer_id = da.customer_id\
   LEFT JOIN lending_loans ll ON c.customer_id = ll.customer_id\
   GROUP BY c.customer_id, c.segment"

echo "==> Scenario 2: Producer change (introduce suspended status)"
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" \
  -e "UPDATE deposit_accounts SET status='suspended' WHERE account_id=2002;"

echo "==> Scenario 2: Consumer A validation expected to fail"
datapact validate --contract demo/contracts/consumer_a_deposit_accounts.yaml \
  --db-type mysql --db-host "$DB_HOST" --db-port "$DB_PORT" \
  --db-user "$DB_USER" --db-password "$DB_PASSWORD" --db-name "$DB_NAME" \
  --db-table deposit_accounts || true

echo "==> Scenario 3: Consumer contract update (allow suspended)"
datapact validate --contract demo/contracts/consumer_a_deposit_accounts_updated.yaml \
  --db-type mysql --db-host "$DB_HOST" --db-port "$DB_PORT" \
  --db-user "$DB_USER" --db-password "$DB_PASSWORD" --db-name "$DB_NAME" \
  --db-table deposit_accounts

echo "==> Reset: Restore deposit_accounts status"
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" \
  -e "UPDATE deposit_accounts SET status='${DB_RESET_STATUS}' WHERE account_id=2002;"

echo "==> Demo complete"
