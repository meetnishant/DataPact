# DataPact 2.0 Demo Plan - Banking Data Product (MySQL)

## Goal
Demonstrate DataPact2.0 validating a realistic banking data product in MySQL against a producer contract and three consumer contracts, including change scenarios.

## Personas
- Producer: Commercial & Institutional Banking Data Platform team
- Consumer A: Deposits Operations (strict)
- Consumer B: Finance Analytics (aggregate, tolerant)
- Consumer C: Risk/Exposure (cross-product view)

## Data Product Model (MySQL)
Tables and relationships:
- customers (master)
- deposit_accounts (FK -> customers)
- deposit_transactions (FK -> deposit_accounts)
- lending_loans (FK -> customers)
- loan_payments (FK -> lending_loans)

## Schema Setup
Create database: commercial_finance
DDL location: demo/mysql/schema.sql

## Seed Data
Create seed data that passes strict producer rules.
Seed SQL: demo/mysql/seed.sql
Seeder script: demo/scripts/seed_mysql.py

Minimum seed set (provided in seed.sql):
- 5 customers
- 6 deposit_accounts
- 12 deposit_transactions
- 4 lending_loans
- 8 loan_payments

## Contracts
Contracts location: demo/contracts/

Producer contracts (per table):
- producer_customers.yaml
- producer_deposit_accounts.yaml
- producer_deposit_transactions.yaml
- producer_lending_loans.yaml
- producer_loan_payments.yaml

Consumer A (Deposits Ops, strict):
- consumer_a_deposit_accounts.yaml
- consumer_a_deposit_transactions.yaml

Consumer B (Finance Analytics, tolerant):
- consumer_b_accounts_agg.yaml
- consumer_b_loans_agg.yaml

Consumer C (Risk/Exposure, cross-product):
- consumer_c_exposure.yaml

## Demo Scenarios

### Scenario 1: Baseline Validation
Validate data product against all contracts, expect PASS.

### Scenario 2: Producer Change (Breaking)
Introduce a breaking change (new enum value or nulls) and show consumer failures.

### Scenario 3: Consumer Contract Change
Update a consumer contract to accept the new data shape and show PASS again.

## Setup Steps (CLI)

### 1) Environment variables
```bash
export DB_HOST=127.0.0.1
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=secret
export DB_NAME=commercial_finance
```

### 2) Create schema and seed data
```bash
python demo/scripts/seed_mysql.py
```

## Scenario 1 - Baseline Validation (PASS)

### Producer validations
```bash
datapact validate --contract demo/contracts/producer_customers.yaml \
	--db-type mysql --db-host $DB_HOST --db-port $DB_PORT \
	--db-user $DB_USER --db-password $DB_PASSWORD --db-name $DB_NAME \
	--db-table customers

datapact validate --contract demo/contracts/producer_deposit_accounts.yaml \
	--db-type mysql --db-host $DB_HOST --db-port $DB_PORT \
	--db-user $DB_USER --db-password $DB_PASSWORD --db-name $DB_NAME \
	--db-table deposit_accounts

datapact validate --contract demo/contracts/producer_deposit_transactions.yaml \
	--db-type mysql --db-host $DB_HOST --db-port $DB_PORT \
	--db-user $DB_USER --db-password $DB_PASSWORD --db-name $DB_NAME \
	--db-table deposit_transactions

datapact validate --contract demo/contracts/producer_lending_loans.yaml \
	--db-type mysql --db-host $DB_HOST --db-port $DB_PORT \
	--db-user $DB_USER --db-password $DB_PASSWORD --db-name $DB_NAME \
	--db-table lending_loans

datapact validate --contract demo/contracts/producer_loan_payments.yaml \
	--db-type mysql --db-host $DB_HOST --db-port $DB_PORT \
	--db-user $DB_USER --db-password $DB_PASSWORD --db-name $DB_NAME \
	--db-table loan_payments
```

### Consumer A validations (strict deposits)
```bash
datapact validate --contract demo/contracts/consumer_a_deposit_accounts.yaml \
	--db-type mysql --db-host $DB_HOST --db-port $DB_PORT \
	--db-user $DB_USER --db-password $DB_PASSWORD --db-name $DB_NAME \
	--db-table deposit_accounts

datapact validate --contract demo/contracts/consumer_a_deposit_transactions.yaml \
	--db-type mysql --db-host $DB_HOST --db-port $DB_PORT \
	--db-user $DB_USER --db-password $DB_PASSWORD --db-name $DB_NAME \
	--db-table deposit_transactions
```

### Consumer B validations (aggregate analytics)
```bash
datapact validate --contract demo/contracts/consumer_b_accounts_agg.yaml \
	--db-type mysql --db-host $DB_HOST --db-port $DB_PORT \
	--db-user $DB_USER --db-password $DB_PASSWORD --db-name $DB_NAME \
	--db-table deposit_accounts

datapact validate --contract demo/contracts/consumer_b_loans_agg.yaml \
	--db-type mysql --db-host $DB_HOST --db-port $DB_PORT \
	--db-user $DB_USER --db-password $DB_PASSWORD --db-name $DB_NAME \
	--db-table lending_loans
```

### Consumer C validation (cross-product exposure)
```bash
datapact validate --contract demo/contracts/consumer_c_exposure.yaml \
	--db-type mysql --db-host $DB_HOST --db-port $DB_PORT \
	--db-user $DB_USER --db-password $DB_PASSWORD --db-name $DB_NAME \
	--db-query "SELECT c.customer_id, c.segment,\
		COALESCE(SUM(da.balance), 0) AS total_deposits,\
		COALESCE(SUM(ll.principal_balance), 0) AS total_loans\
	 FROM customers c\
	 LEFT JOIN deposit_accounts da ON c.customer_id = da.customer_id\
	 LEFT JOIN lending_loans ll ON c.customer_id = ll.customer_id\
	 GROUP BY c.customer_id, c.segment"
```

## Scenario 2 - Producer Change (Breaks Consumers)

### Change example (introduce new status)
```bash
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD $DB_NAME \
	-e "UPDATE deposit_accounts SET status='suspended' WHERE account_id=2002;"
```

### Re-run a strict consumer contract to show failure
```bash
datapact validate --contract demo/contracts/consumer_a_deposit_accounts.yaml \
	--db-type mysql --db-host $DB_HOST --db-port $DB_PORT \
	--db-user $DB_USER --db-password $DB_PASSWORD --db-name $DB_NAME \
	--db-table deposit_accounts
```

## Scenario 3 - Consumer Contract Update

### Update consumer contract
Add `suspended` to enum in consumer_a_deposit_accounts.yaml.

### Re-run validation (PASS)
```bash
datapact validate --contract demo/contracts/consumer_a_deposit_accounts.yaml \
	--db-type mysql --db-host $DB_HOST --db-port $DB_PORT \
	--db-user $DB_USER --db-password $DB_PASSWORD --db-name $DB_NAME \
	--db-table deposit_accounts
```

## Notes
- Seed data is aligned with the contract enums and ranges.
- MySQL credentials are read from env vars in the seed script.
- Reports are saved under ./reports by default.
