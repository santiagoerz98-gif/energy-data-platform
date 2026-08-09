from fastapi import FastAPI

app = FastAPI(title = "Energy Data Platform API", description = "API for serving energy data", version = "1.0.0")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/demand")
def get_demand():
    return {"message": "This endpoint will return demand data."}

@app.get("/generation")
def get_generation():
    return {"message": "This endpoint will return generation data."}