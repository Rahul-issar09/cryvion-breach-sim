-- CryvionPortal schema. Loaded automatically by the mysql image on first boot.
CREATE TABLE IF NOT EXISTS users (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL,
    password VARCHAR(128) NOT NULL,   -- VULN: plaintext storage (T1552)
    role     VARCHAR(16)  NOT NULL DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS customers (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(128),
    email       VARCHAR(128),
    ssn         VARCHAR(16),          -- crown-jewel PII
    credit_card VARCHAR(24),
    balance     DECIMAL(12,2)
);
