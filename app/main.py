from fastapi import FastAPI

app = FastAPI(title="EasyFriend")

@app.get("/health")
def health():
    return {"status": "ok", "versao": "0.1.0"}
