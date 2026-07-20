-- 业务数据库Schema - 理解整个系统核心业务
CREATE TABLE projects (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    value DECIMAL(15,2),
    status VARCHAR(50),
    created_at TIMESTAMP
);

CREATE TABLE transactions (
    id INT PRIMARY KEY,
    project_id INT,
    amount DECIMAL(15,2),
    type ENUM('income', 'expense'),
    date DATE
);

-- 其他业务表...