from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "service": "kube-ai-guardian"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/ready")
def ready():
    return {"status": "ready"}
memory_hog = []

@app.get("/memory")

def memory():

    memory_hog.append(bytearray(100 * 1024 * 1024))

    return {

        "status": "allocated",

        "allocated_mb": len(memory_hog) * 100

    }
