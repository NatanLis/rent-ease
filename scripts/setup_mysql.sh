#!/bin/bash

# Check if MySQL is installed
if ! command -v mysql &> /dev/null
then
    echo "MySQL is not installed. Please install it first."
    exit 1
fi

# MySQL credentials
DB_NAME="rent_ease_db"
DB_USER="rent_ease_user"
DB_PASS="your_password"

echo "Setting up MySQL database..."

# Run MySQL commands
mysql -u root -p <<EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

echo "MySQL database setup completed."
