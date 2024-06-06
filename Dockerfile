# Use an official Python runtime as the base image
FROM python:3.11.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
RUN source /app/.env

# Run app.py when the container launches
CMD ["python", "api/main.py"]
