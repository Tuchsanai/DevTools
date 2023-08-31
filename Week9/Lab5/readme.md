### Clone

```
git clone https://github.com/Tuchsanai/devpot_week9.git
```


### go to Directory
```
cd devpot_week9/Lab5

```




### Next, create a new file called Dockerfile in the root of your project directory with the following contents:
```
FFROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```

### build Docker image with docker build 
```
docker build -t fastapi-docker_lab5 .
```

### Run the Docker container by executing the following command:
```
docker run -p 8088:80 fastapi-docker_lab5 
```
### run client test

```
import requests
import base64
import matplotlib.pyplot as plt
import numpy as np
import cv2
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



image_file = 'building.jpg'
url        = "http://localhost:8088"


# Load the image
image        = cv2.imread(image_file)
image        = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
image_string = encode_image(image)

payload = {
    "image": image_string,
    "name": "John",
    "surname": "Doe",
    "numbers": [1, 2, 3, 4, 5]
}

response = requests.post(f"{url}/process-image", json=payload)
data = json.loads(response.content)

processed_image_string = data["processed_image"]
processed_image        = decode_image(processed_image_string)




```