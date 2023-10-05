# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app
COPY requirements.txt . 


# Install Python dependencies

RUN pip install --upgrade pip
RUN pip install  -r requirements.txt


# Set environment variables
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    JUPYTER_TOKEN=my_token \
    JUPYTER_PORT=8888


# Start Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=my_token"]
