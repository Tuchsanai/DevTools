# Grade Submission Portal

## *** This project demonstrates a simple grade submission system using a Flask frontend and a Node.js backend. It's designed to be deployed using Docker Compose and later applied in Kubernetes sections.

## Architecture

The application consists of two main components:

1. **Flask Frontend** (`flask-app`): Provides the user interface for grade submission.
2. **Node.js Backend** (`node-server`): Handles the API for grade processing and storage.

## Prerequisites

- Docker
- Docker Compose

## Setup and Deployment

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Docker Compose Configuration

The `docker-compose.yml` file defines the services and their configurations:

```yaml
version: '3'
services:
  flask-app:
    image: rslim087/kubernetes-course-grade-submission-portal
    container_name: flask-app
    ports:
      - "5001:5001"
    environment:
      - GRADE_SERVICE_HOST=node-server
    depends_on:
      - node-server
    networks:
      - app-network

  node-server:
    image: rslim087/kubernetes-course-grade-submission-api:stateless
    container_name: node-server
    ports:
      - "3000:3000"
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### 3. Run the Application

To start the application, run:

```bash
docker compose up
```

This command will pull the necessary images and start both the Flask frontend and Node.js backend services.

### 4. Access the Application

Once the containers are running, you can access the grade submission portal at:

```
http://localhost:5001
```

## Usage

1. Open the grade submission portal in your web browser.
2. Enter the required information (student name, subject, grade).
3. Submit the grade.
4. View the submitted grades in the list below the form.

## Screenshots

![Grade Submission Form](./images/1.jpg)
*Figure 1: Grade Submission Form*

![Submitted Grades List](./images/2.jpg)
*Figure 2: List of Submitted Grades*

## Kubernetes Deployment

This demo is designed to be later applied in Kubernetes sections. The Docker Compose setup serves as a foundation for understanding the application structure before moving to a Kubernetes deployment.

## Troubleshooting

If you encounter any issues:

1. Ensure Docker and Docker Compose are correctly installed and up to date.
2. Check if the required ports (5001 and 3000) are not in use by other applications.
3. Review the Docker Compose logs for any error messages:
   ```bash
   docker compose logs
   ```

## Contributing

Instructions for contributing to this project...

## License

Specify the license under which this project is released...