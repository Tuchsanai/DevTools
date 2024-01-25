
# Build and run the container as before:

1. **Build the Docker Image**:
   ```bash
   docker build -t streamlit-app .
   ```

2. **Run the Docker Container**:
   ```bash
   docker run -d --rm -p 8501:8501 -e SERVER_URL="127.0.0.1:8080" streamlit-app
   ```

After completing these steps, your Streamlit application will be running in a Docker container. The app will now display the uploaded image and the entered details only after the user clicks the "Finish" button. Access the app at `http://localhost:8501` in your web browser.