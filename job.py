
from datetime import datetime
from multiprocessing import Pool
from typing import List
import os
from pathlib import Path
import gen
import traceback
import sys
import uuid
import json
import requests
import logging
import time

ARTICLE_PATH = (Path(__file__).parent.parent / "static" / "articles" ).as_posix()


def main():
    if len(sys.argv) > 1:
        start=time.time()
        n = int(sys.argv[1])
        write_articles(n)
        logging.info(f'Generated {n} articles in {round(time.time()-start,2)} seconds')


def write_articles(n: int, article_dir=None) -> str:
    """Generates and writes n articles to disk

    Args:
        n (int): The number of articles to generate
        article_dir (str, optional): The directory to write the articles to. Defaults to None.
    
    Returns:
        str: The directory where the articles were written
    """
    if article_dir is None:
        article_dir = _daily_article_dir()
    
    if not os.path.isdir(article_dir):
        os.makedirs(article_dir)

    try:
        article_jsons = gen.new_articles(n)
        for article in article_jsons:
            if article is None:
                logging.error('Article is None')
                continue
            article_id = article['article_id']  # new articles have article_id
            article['id'] = article_id  # backwards compatibility
            if 'img_path' in article:
                local_imgpath = os.path.join(article_dir, f'{article_id}.png')
                try:
                    if  download_file(article['img_path'], local_imgpath):
                        article['url'] = article['img_path']
                        article['img_path'] = 'articles/' + f'{article_id}.png'  # static path the website will use
                        
                except Exception as e:
                    logging.error('Error downloading images' + str(e))
            
            fpath = os.path.join(article_dir, f'{article_id}.json')
            with open(fpath, 'w') as f:
                json.dump(article, f)

    except Exception as e:
        traceback.print_exc()
        print(e)
    
    return article_dir


def get_article_paths(article_dir=None):
    if article_dir is None:
        article_dir = _daily_article_dir()
    
    paths = []
    for path in os.listdir(article_dir):
        if path.endswith('json'):
            paths.append(os.path.join(article_dir,path))
    return paths


def download_file(url: str, file_path:str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path,'wb') as f:
            f.write(response.content)
        logging.info(f'Downloaded file to {file_path}')
        return True
    else:
        logging.error(f'Image couldn\'t be retrieved. {url=}')
    return False


def _daily_article_dir(time_format="%m%d%Y"):
    date = datetime.now().strftime(time_format)
    todays_articles_path = os.path.join(ARTICLE_PATH, date)
    return todays_articles_path

def recent_news_dir(time_format="%m%d%Y"):
    date = datetime.now().strftime(time_format)
    todays_articles_path = os.path.join(ARTICLE_PATH, date)

    # find the most recent day
    if not os.path.exists(todays_articles_path):
        article_dirs = []
        for filename in os.listdir(ARTICLE_PATH):
            full_path = os.path.join(ARTICLE_PATH, filename)
            if os.path.isdir(full_path):
                article_dirs.append(full_path)

        if len(article_dirs) == 0:
            logging.critical(f"ERROR: No articles exist in {ARTICLE_PATH}")
            raise Exception("No articles exist")

        closest_time = 1_000_000
        recent_dir = article_dirs[0]
        for dir_path in article_dirs:
            dir_name = os.path.basename(dir_path)
            try:
                dir_time = datetime.strptime(dir_name, time_format)
                dir_time_diff = (datetime.now() - dir_time).days
                if dir_time_diff < closest_time:
                    closest_time = dir_time_diff
                    recent_dir = dir_path
            except ValueError as e:
                logging.error(f"Could not parse dir {dir_path}: " + str(e))
        todays_articles_path = recent_dir

    return todays_articles_path


if __name__ == '__main__':
    main()

