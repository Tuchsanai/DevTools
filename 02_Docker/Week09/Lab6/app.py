import streamlit as st
from PIL import Image
import os

env_SERVER_URL = os.environ['SERVER_URL']
   

st.title('Upload and Display Image with Username and ID to {}'.format(env_SERVER_URL))

# User input
username = st.text_input("Enter your username")
id_number = st.text_input("Enter your ID number")

# Image upload
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Finish button
if st.button('Finish'):
    if uploaded_file is not None:
        # Display the image and details
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image.', use_column_width=True)
        st.write("Username:", username)
        st.write("ID Number:", id_number)
    else:
        st.write("Please upload an image.")
