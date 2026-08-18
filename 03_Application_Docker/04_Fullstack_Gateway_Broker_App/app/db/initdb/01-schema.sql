CREATE TABLE menus (
    code VARCHAR(20) PRIMARY KEY,
    name_th VARCHAR(80) NOT NULL,
    price NUMERIC(10,2) NOT NULL CHECK (price > 0),
    CHECK (code IN ('latte','espresso','americano','mocha','matcha','cocoa'))
);

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    menu_code VARCHAR(20) NOT NULL REFERENCES menus(code),
    qty INTEGER NOT NULL CHECK (qty BETWEEN 1 AND 3),
    customer_name VARCHAR(80) NOT NULL CHECK (length(trim(customer_name)) BETWEEN 1 AND 80),
    status VARCHAR(10) NOT NULL DEFAULT 'QUEUED'
        CHECK (status IN ('QUEUED','BREWING','READY')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ready_at TIMESTAMPTZ NULL
);

CREATE TABLE sales_stats (
    menu_code VARCHAR(20) PRIMARY KEY REFERENCES menus(code),
    cups INTEGER NOT NULL DEFAULT 0 CHECK (cups >= 0),
    revenue NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (revenue >= 0)
);
