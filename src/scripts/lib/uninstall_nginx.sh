# Stop Nginx service
sudo systemctl stop nginx

# Remove Nginx packages
sudo apt-get -y purge nginx

# Optionally remove Nginx configuration directory
sudo rm -rf /etc/nginx
