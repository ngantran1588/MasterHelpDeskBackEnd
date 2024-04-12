# Stop PostgreSQL service
sudo systemctl stop postgresql

# Remove PostgreSQL packages
sudo apt-get --purge -y remove postgresql postgresql-*

# Optionally remove data directory
sudo rm -rf /etc/postgresql /var/lib/postgresql
