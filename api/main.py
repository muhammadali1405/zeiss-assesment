from fastapi import FastAPI

app = FastAPI()

# GET /health/live
@app.get("/health/live")
def liveness():
    return {"status": "Live"}

# GET /health/ready
@app.get("/health/ready")
def readiness():
    return {"status": "Ready"}

# GET /api/work
@app.get("/api/work")
def get_work():
    return {"response": "Work endpoint"}