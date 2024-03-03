#!/bin/bash

# Function to start Docker containers
start_container() {
    docker start $1
}

# Function to stop Docker containers
stop_container() {
    docker stop $1
}

# Function to remove Docker containers
remove_container() {
    docker rm $1
}

# Function to build Docker images from Dockerfiles
build_image() {
    docker build -t $2 $1
}

# Function to create a new Docker container from an existing image
create_container() {
    docker run -d --name $1 $2
}

# Function to restart Docker containers
restart_container() {
    docker restart $1
}

# Function to kill Docker containers
kill_container() {
    docker kill $1
}

# Function to start Docker containers defined in docker-compose.yml
docker_compose_up() {
    docker-compose -f $1 up -d
}

# Function to stop Docker containers defined in docker-compose.yml
docker_compose_down() {
    docker-compose -f $1 down
}

# Function to list all Docker containers
list_containers() {
    docker ps -a
}

# Function to list all Docker images
list_images() {
    docker images
}

# Check for command-line arguments and call the appropriate function
case "$1" in
    start)
        start_container "$2"
        ;;
    stop)
        stop_container "$2"
        ;;
    remove)
        remove_container "$2"
        ;;
    build)
        build_image "$2" "$3"
        ;;
    create)
        create_container "$2" "$3"
        ;;
    restart)
        restart_container "$2"
        ;;
    kill)
        kill_container "$2"
        ;;
    compose-up)
        docker_compose_up "$2"
        ;;
    compose-down)
        docker_compose_down "$2"
        ;;
    list-containers)
        list_containers
        ;;
    list-images)
        list_images
        ;;
    *)
        echo "Invalid command: $1"
        echo "Usage: $0 <command> [<args>]"
        exit 1
        ;;
esac

exit 0
