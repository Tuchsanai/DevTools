
# Build and run the container as before:

## create directory

   
    mkdir LAB5_Week9_Frontend
    cd    LAB5_Week9_Frontend
    

## git clone branch dev
    
    
   ```
    git clone -b dev https://github.com/Tuchsanai/DevTools.git
   ```
   
   ```   
    cd DevTools/02_Docker/Week09/Lab5/frontend
   ```


1. **Build the Docker Image**:
   ```bash
   docker build -t streamlit-app_lab5  .
   ```

2. **Run the Docker Container**:
   ```bash
   docker run -d --rm -p 8089:8501 -v  ./:/app -e BACKEND_URL=host.docker.internal  streamlit-app_lab5 
   ```

After completing these steps, your Streamlit application will be running in a Docker container. The app will now display the uploaded image and the entered details only after the user clicks the "Finish" button. Access the app at `http://localhost:8089` in your web browser.