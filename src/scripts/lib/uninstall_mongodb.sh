# Stop MongoDB service
sudo systemctl stop mongodb

# Remove MongoDB packages
sudo apt-get -y purge mongodb-org*

# Optionally remove data directory
sudo rm -rf /etc/mongod /var/lib/mongodb
