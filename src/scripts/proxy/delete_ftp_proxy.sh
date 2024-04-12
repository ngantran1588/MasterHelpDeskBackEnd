domain=$1
port=$2
sudo sed -i "/ftp_proxy.*$domain.*$port/d" /etc/environment
echo "Proxy configuration for domain $domain and port $port deleted successfully."