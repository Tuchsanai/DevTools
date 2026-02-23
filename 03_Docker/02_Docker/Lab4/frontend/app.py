import streamlit as st
from PIL import Image
import os
import cv2
import requests
import base64
import numpy as np
import json


# encode image as base64 string
def encode_image(image):
    _, encoded_image = cv2.imencode(".jpg", image)
    return "data:image/jpeg;base64," + base64.b64encode(encoded_image).decode()

# decode base64 string to image
def decode_image(image_string):
    encoded_data = image_string.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


env_BACKEND_URL = os.environ.get('BACKEND_URL', '127.0.0.1') # Adjust the default port if necessary



st.title(f'Upload and Display Image with Username and ID with Backend Url = {env_BACKEND_URL}')

username = st.text_input("Enter your name")
surname = st.text_input("Enter your surname")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if st.button('Finish'):
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image.', use_column_width=True)
            st.write('username: ', username, 'surname: ', surname)

        with col2:
            image = Image.open(uploaded_file)
            encoded_image = encode_image(np.array(image))
            payload = {
                "image":  encoded_image,
                "name": username,
                "surname": surname,
                "numbers": [1, 2, 3]  # Replace with user input if necessary
            }

            response = requests.post(f"http://{env_BACKEND_URL}:8088/process-image", json=payload)
        

            if response.status_code == 200:
                data = json.loads(response.content)
                processed_image_string = data["processed_image"]
                st.image(processed_image_string, caption="Processed Image")
            else:
                st.error(f"Error in processing the image: {response.status_code}")
    else:
        st.write("Please upload an image.")
