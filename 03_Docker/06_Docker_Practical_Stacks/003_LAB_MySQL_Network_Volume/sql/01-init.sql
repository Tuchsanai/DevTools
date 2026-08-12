CREATE DATABASE IF NOT EXISTS labdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE labdb;

CREATE TABLE IF NOT EXISTS notes (
  id INT PRIMARY KEY AUTO_INCREMENT,
  message VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO notes (message)
SELECT 'ข้อมูลนี้อยู่ใน named volume'
WHERE NOT EXISTS (
  SELECT 1 FROM notes WHERE message = 'ข้อมูลนี้อยู่ใน named volume'
);
