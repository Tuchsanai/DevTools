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
    gr.Markdown(
        """
        # 🌟 ML Classification Interface 🌟
        
        This interface allows you to train a machine learning model on different datasets and make predictions on test data. 
        Please select your options and input your test data below.
        """
    )
    
    with gr.Row(equal_height=True):
        with gr.Column(scale=2):
            dataset_name = gr.Dropdown(
                choices=["iris", "wine"], 
                label="Select Dataset", 
                info="Choose a dataset for model training",
                value="iris",
                show_label=True
            )
            model_name = gr.Dropdown(
                choices=["random_forest", "gradient_boosting"], 
                label="Select Model", 
                info="Choose a model for training",
                value="random_forest",
                show_label=True
            )
            train_button = gr.Button("🚀 Train Model", variant="primary")

        with gr.Column(scale=3):
            sample_input = "5.1,3.5,1.4,0.2; 6.7,3.0,5.0,1.7"  # Example for iris dataset
            test_data = gr.Textbox(
                label="Enter Test Data",
                value=sample_input, 
                placeholder="Input comma-separated values; separate rows with semicolons.",
                lines=3
            )
            predict_button = gr.Button("🔍 Predict", variant="secondary")
            output = gr.Textbox(
                label="Model Predictions",
                placeholder="Model predictions will appear here.",
                lines=4
            )

    gr.Markdown(
        """
        ---
        ### Instructions:
        1. **Select Dataset:** Choose a dataset for training the model.
        2. **Select Model:** Pick the model you wish to train.
        3. **Train Model:** Click the 'Train Model' button to train the model.
        4. **Enter Test Data:** Provide your test data for prediction.
        5. **Predict:** Click 'Predict' to get the model's predictions.

        *Tip:* Example data is provided by default for easy testing.
        """
    )

    train_button.click(train_model, inputs=[dataset_name, model_name], outputs=None)
    predict_button.click(predict_model, inputs=[model_name, test_data], outputs=output)

interface.launch(server_name="0.0.0.0", server_port=7860)
