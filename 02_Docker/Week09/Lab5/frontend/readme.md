
# Build and run the container as before:

1. **Build the Docker Image**:
   ```bash
   docker build -t streamlit-app_lab5  .
   ```

2. **Run the Docker Container**:
   ```bash
   docker run -d --rm -p 8089:8501 -e BACKEND_URL="127.0.0.1:8088" streamlit-app_lab5 
   ```

After completing these steps, your Streamlit application will be running in a Docker container. The app will now display the uploaded image and the entered details only after the user clicks the "Finish" button. Access the app at `http://localhost:8089` in your web browser.