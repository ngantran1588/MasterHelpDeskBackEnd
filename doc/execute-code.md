## upload file
```server_manager.upload_file_to_remote("test.txt", "/home/user/test2")```

## download file
```server_manager.download_file_from_remote("/home/user/test/test.txt", "C:/Users/HP-PC/Downloads/test.txt")```

## upload folder
```server_manager.upload_folder("test2", "/home/user/")```

## download folder
```server_manager.download_folder("/home/user/test2", "C:/Users/HP-PC/Downloads")```

## Execute the custom script on the server
```server_manager.execute_script(script_path)```

## Execute the show_status.sh script
```server_manager.execute_script("src/scripts/firewall/show_status.sh")```

## Execute the allow_port.sh script with port 8080
```server_manager.execute_script("src/scripts/firewall/allow_port.sh", 8080)```

## Execute the deny_port.sh script with port 8080
```server_manager.execute_script("src/scripts/firewall/deny_port.sh", 8080)```

## Execute the allow_ip.sh script with IP address 192.168.1.1
```server_manager.execute_script("src/scripts/firewall/allow_ip.sh", "192.168.1.1")```

## Execute the deny_ip.sh script with IP address 192.168.1.1
```server_manager.execute_script("src/scripts/firewall/deny_ip.sh", "192.168.1.1")```

## Execute the https_proxy.sh script with host proxy.fpt.edu.vn
```
server_manager.execute_script("src/scripts/proxy/https_proxy.sh", "proxy.fpt.edu.vn", 3128)
server_manager.execute_script("src/scripts/proxy/https_proxy.sh", "ahihi.com", 3000)
server_manager.execute_script("src/scripts/lib/install_pip.sh")
server_manager.execute_script("src/scripts/lib/install_docker.sh")
```