# frontend/app.py
import gradio as gr
import requests

backend_url = "http://backend:8000"

def train_model(dataset_name, model_name):
    response = requests.post(f"{backend_url}/train/", json={"dataset_name": dataset_name, "model_name": model_name})
    return response.json()

def predict_model(model_name, test_data):
    # Convert the input string to a list of lists of floats
    test_data_list = [list(map(float, row.split(','))) for row in test_data.strip().split(';')]
    response = requests.post(f"{backend_url}/predict/", json={"model_name": model_name, "test_data": test_data_list})
    return response.json()["predictions"]

# Create Gradio interface
with gr.Blocks() as interface:
    with gr.Row():
        dataset_name = gr.Dropdown(choices=["iris", "wine"], label="Dataset")
        model_name = gr.Dropdown(choices=["random_forest", "gradient_boosting"], label="Model")
        train_button = gr.Button("Train Model")

    with gr.Row():
        # Pre-fill the textbox with a sample input
        sample_input = "5.1,3.5,1.4,0.2; 6.7,3.0,5.0,1.7"  # Example for iris dataset
        test_data = gr.Textbox(label="Test Data (Comma-separated values)", value=sample_input)
        predict_button = gr.Button("Predict")
        output = gr.Textbox(label="Predictions")

    train_button.click(train_model, inputs=[dataset_name, model_name], outputs=None)
    predict_button.click(predict_model, inputs=[model_name, test_data], outputs=output)

interface.launch(server_name="0.0.0.0", server_port=7860)
