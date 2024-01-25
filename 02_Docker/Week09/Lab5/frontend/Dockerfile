# Use the official Python base image
FROM python:3.8

# Set the working directory in the Docker container
WORKDIR   /app

# Copy the dependencies file to the working directory

COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory


# Specify the command to run on container start
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
