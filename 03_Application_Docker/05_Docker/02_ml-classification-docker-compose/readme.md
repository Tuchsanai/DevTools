Here is the folder structure for the project:

```
ml-classification-docker-compose/
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── docker-compose.yml
└── README.md  # Optional: Add a README file for project documentation
```

### Folder and File Descriptions:

- **`backend/`**: Contains the FastAPI backend files.
  - **`Dockerfile`**: Dockerfile for the FastAPI backend.
  - **`main.py`**: The FastAPI application for training and inference.
  - **`requirements.txt`**: Python dependencies for the backend.

- **`frontend/`**: Contains the Gradio frontend files.
  - **`Dockerfile`**: Dockerfile for the Gradio frontend.
  - **`app.py`**: The Gradio application for interacting with the backend.
  - **`requirements.txt`**: Python dependencies for the frontend.

- **`docker-compose.yml`**: Docker Compose file to define and run the multi-container application.


# ML Classification with Gradio and FastAPI

This project demonstrates how to build a machine learning classification system using a Gradio frontend and a FastAPI backend, orchestrated by Docker Compose. Below is an overview of the system's architecture and workflow.

## System Architecture

The system is composed of three main components:

1. **Gradio Frontend**
   - User interface where users can:
     - **Select Model**: Choose between different machine learning models (e.g., Random Forest, Gradient Boosting).
     - **Select Dataset**: Choose between different datasets (e.g., Iris, Wine).
     - **Enter Test Data**: Input test data in a comma-separated format.
     - **Get Prediction**: Receive predictions based on the trained model.

2. **FastAPI Backend**
   - Handles the core logic of the application:
     - **Train Model**: Trains the selected machine learning model using the chosen dataset.
     - **Predict with Test Data**: Uses the trained model to predict outcomes based on the test data provided by the user.
     - **Return Predictions**: Sends the predictions back to the Gradio frontend for display.

3. **Model Training/Inference**
   - The component where the actual machine learning operations occur:
     - **Train Model**: The training process for the selected model.
     - **Predict**: Inference process where the model predicts outcomes from the test data.

## Flow Diagram

```plaintext

## Flow Diagram

```plaintext
+--------------------------+      +----------------------------+      +------------------------+
|                          |      |                            |      |                        |
|      Gradio Frontend      +----->|       FastAPI Backend      +----->|      Model              |
|                          |      |                            |      |    Training/            |
|      User Interface       |      |       Training and         |      |    Inference            |
|                          |      |       Inference Logic       |      |                        |
|                          |      |                            |      |                        |
|  - Select Model           |      |  - Train Model             |      |  - Train Model         |
|  - Select Dataset         |      |  - Predict with            |      |  - Predict             |
|  - Enter Test Data        |      |    Test Data               |      |                        |
|  - Get Prediction         |<-----+  - Return                  |<-----+  - Return              |
|                          |      |    Predictions              |      |    Predictions         |
+--------------------------+      +----------------------------+      +------------------------+
           

```


![Front end](img/1.jpg)