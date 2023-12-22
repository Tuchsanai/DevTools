### Clone

```
git clone https://github.com/Tuchsanai/devpot_week9.git
```


### go to Directory
```
cd devpot_week9/Lab4

```




### Next, create a new file called Dockerfile in the root of your project directory with the following contents:
```
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

```

### build Docker image with docker build 
```
docker build -t fastapi-docker .
```

### Run the Docker container by executing the following command:
```
docker run -p 8087:80 fastapi-docker
```


### Test Path Parameters

#### 1. With Python
```
book_id      = 3
url_base     = "http://localhost:8087"
url          = f"{url_base}/book/{book_id}"

response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("Error:", response.status_code, response.json())
```

#### 2. URL

```
http://localhost:8087/book/3
```

### Test Query Parameters

#### 1. URL

```
http://localhost:8087/search?title=the&author=tolkien
```

#### 1. With Python

```
import requests

url_base     = "http://localhost:8087"
url          = f"{url_base}/search"


params = {
    "title": "the",
    "author": "tolkien"
}

response = requests.get(url, params=params)
if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("Error:", response.status_code, response.json())
    
```
