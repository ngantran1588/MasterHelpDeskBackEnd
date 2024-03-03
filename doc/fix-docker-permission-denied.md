## Enable Non-Root User Access
While the previous method stops the error from appearing, it requires sudo every time you issue a Docker command. The following section explains how to enable non-root access for a user and grant sufficient privileges to run Docker commands without sudo.

1. Enter the command below to create the docker group on the system.

```sudo groupadd -f docker```

2. Type the following usermod command to add the active user to the docker group.

```sudo usermod -aG docker $USER```

3. Apply the group changes to the current terminal session by typing:

```newgrp docker```

4. Check if the docker group is in the list of user groups.

```groups```

The group appears in the command output.

You should now be able to issue Docker commands as a non-root user without sudo.