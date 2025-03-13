#!/bin/bash

# Exit immediately if any command exits with a non-zero status
set -e


# Check if .env.example exists
if [ ! -f "../.env.example" ]; then
    echo "Error: .env.example file not found!"
    exit 1
fi

# Duplicate .env.example as .env (only if it doesn't already exist)
cp -n "../.env.example" "../.env"

echo "Updating package list and installing PostgreSQL..."
sudo apt update && sudo apt install -y postgresql postgresql-contrib


# Prompt for username and password
echo "Configuring PostgreSQL for user access..."

read -p "Enter the PostgreSQL username you want to create (suggestion: first inital plus last name aka rkoenig): " PG_USER

while true; do
    # Prompt for password (hidden)
    read -s -p "Enter the password for $PG_USER: " PG_PASS
    echo ""  # New line for readability

    # Prompt for password confirmation (hidden)
    read -s -p "Confirm the password for $PG_USER: " PG_PASS_CONFIRM
    echo ""  # New line for readability

    # Check if passwords match
    if [ "$PG_PASS" == "$PG_PASS_CONFIRM" ]; then
        echo "Password confirmed!"
        break  # Exit loop when passwords match
    else
        echo "Passwords do not match. Please try again."
    fi
done

# Prompt for database name (visible)
read -p "Enter the database name (suggestion: roster_builder): " PG_DATABASE


# Get the server's public IP address
SERVER_IP=$(ip addr show | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}' | cut -d'/' -f1)

# # Modify the .env file with the collected values
sed -i "s|^RB_DB_HOST=.*|RB_DB_HOST='$SERVER_IP'|" ../.env
sed -i "s|^RB_DB_NAME=.*|RB_DB_NAME='$PG_DATABASE'|" ../.env
sed -i "s|^RB_DB_USER=.*|RB_DB_USER='$PG_USER'|" ../.env
sed -i "s|^RB_DB_PASSWORD=.*|RB_DB_PASSWORD='$PG_PASS'|" ../.env

echo ".env file updated successfully with server IP: $SERVER_IP"


# Create PostgreSQL user and database
sudo -u postgres psql <<EOF
CREATE ROLE $PG_USER WITH LOGIN PASSWORD '$PG_PASS' CREATEDB;
CREATE DATABASE $PG_DATABASE;
GRANT ALL PRIVILEGES ON DATABASE $PG_DATABASE TO $PG_USER;
EOF


echo "PostgreSQL installation!"

# =============================
# PGADMIN INSTALLATION SECTION
# =============================

echo "Installing pgAdmin4..."

# Add pgAdmin repo
curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg
sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list'
sudo apt update
sudo apt install -y pgadmin4-web


### Running Postgres and PgAdmin config
echo "Configuring PostgreSQL and PgAdmin for remote access..."
sudo sed -i "s/^DEFAULT_SERVER_PORT = 5050/DEFAULT_SERVER_PORT = 8080/" /usr/pgadmin4/web/config.py
sudo sed -i 's/^Listen 80$/Listen 8080/' /etc/apache2/ports.conf
sudo sed -i 's/^MAX_LOGIN_ATTEMPTS = 3/MAX_LOGIN_ATTEMPTS = 10/' /usr/pgadmin4/web/config.py
sudo sed -i "s/^#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/16/main/postgresql.conf

echo "Updating pg_hba.conf to allow remote connections..."
echo "host all $PG_USER 0.0.0.0/0 md5" | sudo tee -a /etc/postgresql/*/main/pg_hba.conf


echo "Starting PostgreSQL to apply changes..."
sudo systemctl enable postgresql
sudo systemctl start postgresql
# sudo systemctl restart postgresql


echo "Configuring pgAdmin..."
sudo /usr/pgadmin4/bin/setup-web.sh

# Start Apache (needed for pgAdmin web interface)
echo "Enabling and starting Apache for pgAdmin..."
sudo systemctl enable apache2
sudo systemctl restart apache2

# # Optional: Auto-start pgAdmin on boot
# sudo systemctl enable pgadmin4

echo "pgAdmin installation and configuration completed!"

# =============================
# SUMMARY
# =============================
echo -e "\nInstallation Complete!"
echo "PostgreSQL is installed and running."
echo -e "\npgAdmin is installed and available at: http://$SERVER_IP:8080/pgadmin4"
echo "Log in to pgAdmin and register your database using:"
echo "     - Hostname: $SERVER_IP"
echo "     - Username: $PG_USER"
echo "     - Password: (your chosen password)"
