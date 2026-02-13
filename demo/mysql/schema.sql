DROP DATABASE IF EXISTS commercial_finance;
CREATE DATABASE commercial_finance;
USE commercial_finance;

CREATE TABLE customers (
  customer_id        BIGINT PRIMARY KEY,
  customer_name      VARCHAR(200) NOT NULL,
  segment            VARCHAR(50) NOT NULL,
  country_code       CHAR(2) NOT NULL,
  kyc_status         VARCHAR(20) NOT NULL,
  created_at         DATETIME NOT NULL
);

CREATE TABLE deposit_accounts (
  account_id         BIGINT PRIMARY KEY,
  customer_id        BIGINT NOT NULL,
  product_type       VARCHAR(30) NOT NULL,
  status             VARCHAR(20) NOT NULL,
  currency           CHAR(3) NOT NULL,
  balance            DECIMAL(18,2) NOT NULL,
  opened_at          DATETIME NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE deposit_transactions (
  txn_id             BIGINT PRIMARY KEY,
  account_id         BIGINT NOT NULL,
  txn_type           VARCHAR(30) NOT NULL,
  txn_amount         DECIMAL(18,2) NOT NULL,
  txn_ts             DATETIME NOT NULL,
  channel            VARCHAR(30) NOT NULL,
  FOREIGN KEY (account_id) REFERENCES deposit_accounts(account_id)
);

CREATE TABLE lending_loans (
  loan_id            BIGINT PRIMARY KEY,
  customer_id        BIGINT NOT NULL,
  product_type       VARCHAR(30) NOT NULL,
  status             VARCHAR(20) NOT NULL,
  currency           CHAR(3) NOT NULL,
  principal_balance  DECIMAL(18,2) NOT NULL,
  interest_rate      DECIMAL(5,4) NOT NULL,
  opened_at          DATETIME NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE loan_payments (
  payment_id         BIGINT PRIMARY KEY,
  loan_id            BIGINT NOT NULL,
  payment_amount     DECIMAL(18,2) NOT NULL,
  payment_ts         DATETIME NOT NULL,
  payment_status     VARCHAR(20) NOT NULL,
  FOREIGN KEY (loan_id) REFERENCES lending_loans(loan_id)
);
