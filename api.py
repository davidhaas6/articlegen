# API endpoint for article generation


from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import logging
from pydantic import ValidationError

import gen
import job
import datamodels
import json


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/')
def index():
    return RedirectResponse('/docs')


@app.get("/create/", response_class=HTMLResponse)
def create_articles(n: int = 1, topic: str = 'rats'):
    if n < 1:
        return JSONResponse(
            status_code=404, 
            content={"message": f"must generate at least 1 article. you requested {n}"}
        )
    if n > 10:
        n = 10
    
    article_jsons = gen.new_articles(n)
    return JSONResponse({"articles": article_jsons})


@app.get("/create_one/", response_class=HTMLResponse)
def create_one(topic: str):
    article = gen.adhoc_article(topic)
    return JSONResponse(article)


@app.get("/todays_articles/", response_class=HTMLResponse)
def todays_articles():
    articles = []
    for path in job.get_article_paths(job.recent_news_dir()):
        with open(path) as f:
            json_obj = json.load(f)
        try:
            article = datamodels.Article.from_dict(json_obj)
            articles.append(article.dict())
        except ValidationError as e:
            logging.error(e)
        
    return JSONResponse(articles)