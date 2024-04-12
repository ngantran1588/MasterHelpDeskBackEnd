domain=$1
old_port=$2
new_domain=$3
new_port=$4
sudo sed -i "s/ftp_proxy=http:\/\/$domain:$old_port/ftp_proxy=http:\/\/$new_domain:$new_port/g" /etc/environment
echo "Proxy configuration updated successfully"