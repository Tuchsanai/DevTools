import uvicorn

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=5000, reload=True)
