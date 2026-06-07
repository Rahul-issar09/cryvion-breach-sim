-- Seed data. Weak/guessable passwords drive the Hydra brute-force stage.
INSERT INTO users (username, password, role) VALUES
    ('admin',   'admin123',   'admin'),
    ('jsmith',  'password',   'user'),
    ('mwilson', 'Summer2024', 'user'),
    ('svc-backup', 'Password1', 'user');

-- Fake PII (synthetic — not real people). Crown jewels for the exfiltration stage.
INSERT INTO customers (name, email, ssn, credit_card, balance) VALUES
    ('Alice Morgan',  'alice.morgan@example.com',  '111-22-3333', '4111-1111-1111-1111', 18450.00),
    ('Bilal Khan',    'bilal.khan@example.com',    '222-33-4444', '4222-2222-2222-2222',  9320.50),
    ('Carmen Diaz',   'carmen.diaz@example.com',   '333-44-5555', '4333-3333-3333-3333', 51200.75),
    ('David O''Neil', 'david.oneil@example.com',   '444-55-6666', '4444-4444-4444-4444',   210.00),
    ('Emi Tanaka',    'emi.tanaka@example.com',    '555-66-7777', '4555-5555-5555-5555', 76410.20);
