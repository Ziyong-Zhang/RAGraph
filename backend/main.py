from fastapi import FastAPI


app = FastAPI(title="RAGraph")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ragraph"}