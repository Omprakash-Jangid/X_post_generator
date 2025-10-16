from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from core.generator import run_tweet_generation  
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate", response_class=HTMLResponse)
def generate(request: Request, topic: str = Form(...)):
    result = run_tweet_generation  (topic)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "topic": topic,
        "result": result['tweet_history'][-1]
    })



