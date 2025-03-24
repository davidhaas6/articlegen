# generate news articles
from datetime import datetime
from multiprocessing import Pool
import re
from typing import Dict, List
import logging
import os
from openai import OpenAI
from pydantic import BaseModel
import yaml
import json
import sys
import random
import traceback
import uuid
from pathlib import Path
import dotenv

import text_processing
import util

VERBOSE = True

dotenv.load_dotenv()
prompts_dir = Path(__file__).resolve().parent / "prompts"
with open(prompts_dir / "system.yaml") as f:
    systems = yaml.safe_load(f)

client = OpenAI()
image_client = OpenAI()

json_llm = "gpt-4o-mini"
light_llm = "gpt-4o-mini"
heavy_llm = "gpt-4o"

PARODY_CATEGORY = "Featured"

logging.basicConfig(
    # filename='logs/generator.log',
    format="%(asctime)s:%(levelname)s:%(message)s",
    # encoding='utf-8',
    level=logging.INFO,
    # prevent logs from other files from showing
)
logger = logging.getLogger(__name__)


class ArticleIdea(BaseModel):
    description: str
    category: str
    title: str

class ParodyIdea(ArticleIdea):
    src_url: str
    category:str =PARODY_CATEGORY

class IdeaResponse(BaseModel):
    ideas: List[ArticleIdea]

def _cli_main():
    """Command line interface main function"""
    global VERBOSE
    VERBOSE = True
    if len(sys.argv) == 1:
        print("usage: gen.py idea image full parody")
        return
    action = str(sys.argv[1])
    if "idea" in action:
        if len(sys.argv) < 3:
            print("usage: gen.py idea <num_ideas>")
            return
        num_ideas = int(sys.argv[2])
        print("\n***INITIAL IDEAS:")
        ideas = article_ideas(num_ideas)
        print(ideas)
    elif "full" in action:
        if len(sys.argv) > 2:
            idea = " ".join(sys.argv[2:])
        elif len(sys.argv) < 3:
            print("usage: gen.py full <idea>")
            return
        logger.info(f"Generating article from idea: {idea}")
        article = article_from_idea(ArticleIdea(description=idea,title='',category=''))
        logger.info(f"Article created: {article}")
        util.download_and_compress_image(
            article["img_path"], f'out/articles/{article["article_id"]}.webp'
        )
        article["img_path"] = f'{article["article_id"]}.webp'
        # save to out/articles
        with open(f'out/articles/{article["article_id"]}.json', "w") as f:
            json.dump(article, f)
            logger.info(f'Article saved to out/articles/{article["article_id"]}.json')
    elif "image" in action:
        if len(sys.argv) < 4:
            print("usage: gen.py image <title> <outline>")
            return
        url = article_image(sys.argv[2], sys.argv[3])
        print(url)
        logger.info(url)
    elif "parody" in action:
        if len(sys.argv) < 3:
            print("usage: gen.py parody <num>")
            return
        # article = article_from_article(sys.argv[2], sys.argv[3])
        num = int(sys.argv[2])
        articles = new_parody_articles(num)
        for article in articles:
            if article is None:
                print("Error generating article")
            with open(f'out/articles/{article["article_id"]}.json', "w") as f:
                json.dump(article, f)
                logger.info(
                    f'Article saved to out/articles/{article["article_id"]}.json'
                )
            print(article)
    elif "articleid" in action:
        if len(sys.argv) < 4:
            print("usage: gen.py articleid <title> <body>")
            return
        article_id = make_article_id(sys.argv[2], sys.argv[3])
        # print(article_id)
        logger.info(article_id)
    elif "comments" in action:
        if len(sys.argv) < 3:
            print("usage: gen.py comments <article_path>")
            return
        with open(sys.argv[2], "r") as f:
            article = json.load(f)
        comments = get_comments(article, int(sys.argv[3]) if len(sys.argv) > 3 else 5)
        logger.info(comments)


def new_articles(num: int, ideas=None) -> List[dict]:
    """Generates a list of new articles

    Args:
        num (int): number of new articles to generate

    Returns:
        List[dict]: the article objects
    """
    if num <= 0:
        return []
    if ideas is None:
        ideas = article_ideas(num)

    num_cpus = min(8, os.cpu_count())
    n_threads = min(num, num_cpus)
    with Pool(n_threads) as pool:
        # string_ideas = map(json.dumps, ideas)
        print("Generating articles. Ideas:", ideas)
        articles = pool.map(article_from_idea, ideas)

    return articles


def new_parody_articles(num: int) -> List[dict]:
    from src.parody import generate_top_story_outlines

    if num <= 0:
        return []
    ideas = []
    for idea in generate_top_story_outlines(num):
        if isinstance(idea, dict):
            ideas.append(ParodyIdea(
                title='',
                description=idea.get('description'),   # type: ignore
                src_url=idea.get('src_url','')   # type: ignore
            ))
    return new_articles(len(ideas), ideas)


def article_from_idea(idea: ArticleIdea) -> dict | None:
    """Create an article from an idea

    Args:
        idea (dict): An article idea with three keys: "title", "description", "category"

    Returns:
        dict: an article object. returns empty dict on error.
              keys:
                img_path -> image url
                title -> article title
                overview -> article overview
                body -> article body
                timestamp -> article timestamp
    """
    try:
        logging.info(f"Creating article from idea: {idea}")
        idea_str = f'Title: {idea.title}\nDescription: {idea.description}'
        outline = article_outline(idea_str)
        logging.info("Generating body")
        # sample from normal distribution for word count within limits
        num_words = int(random.gauss(450, 150))
        num_words = max(100, min(10000, num_words))

        article = article_body(idea_str, outline, num_words)
        article["Outline"] = outline
        article["reading_time_minutes"] = text_processing.estimate_reading_time(
            article["body"]
        )
        article["category"] = idea.category
        if isinstance(idea,ParodyIdea):
            article['parody_src'] = idea.src_url

        # comments
        num_comments = random.gauss(4, 2.7)
        min_comments = 2 if article["category"] == PARODY_CATEGORY else 0
        num_comments = round(max(min_comments, num_comments))
        logging.info(f"Generating with {num_comments} comments")
        article["comments"] = get_comments(article, num_comments)

        logging.info("creating image")
        try:
            article["img_path"] = article_image(article["title"], outline)
        except Exception as e:
            logging.error(f"Error creating image: {e}")
            article["img_path"] = ""
        article["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(
            f'*Article created*\nTitle: {article["title"]}\nImage: {article["img_path"]}\nOverview:{article["overview"]}'
        )
        article["article_id"] = make_article_id(article["title"], article["overview"])
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return None
    return article


def article_image(title: str, outline: str) -> str | None:
    with open(prompts_dir / "images.yaml") as f:
        prompts = yaml.safe_load(f)

    convo_1_ideas = [
        {
            "role": "user",
            "content": prompts["brainstorming2"]
            .replace("{{title}}", title)
            .replace("{{overview}}", outline),
        }
    ]
    chat_completion = client.chat.completions.create(
        messages=convo_1_ideas, model=heavy_llm, temperature=0.7  # type: ignore
    )
    ideas = _get_text(chat_completion)

    convo_2_discretize = convo_1_ideas + [
        {"role": "assistant", "content": ideas},
        # {"role": "system", "content": systems["discretize"]},
        {"role": "user", "content": prompts["select"]},
    ]
    chat_completion = client.chat.completions.create(
        messages=convo_2_discretize, model=json_llm, temperature=0
    )
    img_idea_json = _extract_jsonstr(_get_text(chat_completion))

    response = image_client.images.generate(
        model="dall-e-3",
        prompt=prompts["create"]
        .replace("{{image_idea}}", img_idea_json)
        .replace("{{title}}", title),
        quality="standard",
        n=1,
    )
    for img in response.data:
        logger.info("\nRevised prompt: %s", img.revised_prompt)
        logger.info("%s", img.url)

    image_url = response.data[0].url
    return image_url


def article_ideas(n: int) -> List[ArticleIdea]:
    """Generate n 1-sentence article ideas

    Args:
        n (int): The number of ideas to create.

    Returns:
        str: a string containing a set of article ideas
    """
    with open(prompts_dir / "ideas.yaml", "rb") as f:
        prompts = yaml.safe_load(f)

    convo_1_ideas = [
        {
            "role": "system",
            "content": prompts["idea_generator"].replace("{{n}}", str(n)),
        },
    ]
    chat_completion = client.beta.chat.completions.parse(
        messages=convo_1_ideas,
        model=heavy_llm,
        temperature=1,
        response_format=IdeaResponse,
    )
    obj = chat_completion.choices[0].message.parsed
    if isinstance(obj, IdeaResponse):
        return obj.ideas
    return []


def article_outline(idea: str) -> str:
    """Create an outline for an article

    Args:
        idea (str): a textual description of an article idea

    Returns:
        str: A brief outline for the article
    """
    with open(prompts_dir / "article.yaml", "rb") as f:
        prompts = yaml.safe_load(f)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": prompts["outline2"].replace("{{idea}}", idea.strip()),
            }
        ],
        model=heavy_llm,
        temperature=0.2,
    )
    return _get_text(chat_completion)


def article_body(idea: str, outline: str, num_words: int) -> Dict:
    """Generate the actual text for an article

    Args:
        topic (str): The article's topic sentence
        title (str): The title of the article
        outline (str): An outline of the article
        n_paragraphs (int): The length of the article
        reading_level (int): The complexity of the article's structure and vocabulary

    Returns:
        Dict: an object containing the article data:
               title -> article title
               overview -> article overview
               body -> article body
               generator -> generator version
    """

    with open(prompts_dir / "article.yaml", "rb") as f:
        prompts = yaml.safe_load(f)

    article_generator = random.choice(
        [k for k in prompts.keys() if k.startswith("article_gen")]
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": systems["whisker"],
            },
            {
                "role": "user",
                "content": prompts[article_generator]
                .replace("{{idea}}", idea)
                .replace("{{outline}}", outline)
                .replace("{{num_words}}", str(num_words))
                .strip(),
            },
        ],
        model=heavy_llm,
    )
    raw_article = _get_text(chat_completion).strip()

    article_json = article_to_json(raw_article)
    article_json["generator"] = article_generator
    return article_json


def get_comments(article: dict, num_comments: int, model=light_llm) -> List[str]:
    with open(prompts_dir / "article.yaml", "rb") as f:
        prompts = yaml.safe_load(f)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": prompts["comments"]
                .replace("{{title}}", article["title"])
                .replace("{{body}}", article["body"])
                .replace("{{num_comments}}", str(num_comments)),
            },
        ],
        response_format={"type": "json_object"},
        model=model,
        temperature=1,
    )
    raw_comments = _get_text(chat_completion)
    try:
        json_comments = json.loads(_extract_jsonstr(raw_comments))
        # extract the list
        comments_list = []
        if type(json_comments) == dict:
            for key in json_comments.keys():
                if (
                    isinstance(json_comments[key], list)
                    and len(json_comments[key]) > 0
                    and isinstance(json_comments[key][0], dict)
                ):
                    comments_list = json_comments[key]
                    break
        return comments_list
    except json.JSONDecodeError as e:
        logger.error(f"Json decode error: {e}")
        logger.error(traceback.format_exc())
        logger.debug("Raw comments: %s", raw_comments)
        return []


def article_to_json(article_text: str, model=light_llm) -> dict:
    with open(prompts_dir / "article.yaml", "rb") as f:
        prompts = yaml.safe_load(f)

    article_json_str = _get_text(
        client.chat.completions.create(
            messages=[
                {"role": "system", "content": systems["article_to_json"]},
                {
                    "role": "user",
                    "content": prompts["articleToJson"]
                    .replace("{{article}}", article_text)
                    .strip(),
                },
            ],
            model=model,
            temperature=0,
            # **other_args
            response_format={"type": "json_object"},
        )
    )

    try:
        return json.loads(_extract_jsonstr(article_json_str))
    except json.JSONDecodeError as e:
        logger.error(f"Json decode error: {e}")
        logger.error(traceback.format_exc())
        return {}


def summarize_article(title: str, body: str, num_sentences=3, model=light_llm) -> str:
    with open(prompts_dir / "article.yaml") as f:
        prompts = yaml.safe_load(f)
    summary = _get_text(
        client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompts["summary"]
                    .replace("{{num_sentences}}", str(num_sentences))
                    .replace("{{title}}", title)
                    .replace("{{body}}", body),
                }
            ],
            model=model,
            temperature=0,
        )
    )
    return summary


def ultra_short_summary(title, body, num_words=3, model=light_llm):
    prompt = f"Come up with a witty {num_words}-word summary of this article for Rat News Network."
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"# {title}\n\n{body}"},
        ],
        model=model,
        temperature=1,
    )
    summary = _get_text(chat_completion)
    return summary


def make_article_id(title: str, body: str) -> str:
    semantic_id = ultra_short_summary(title, body, 3)
    # clean the string for a url
    # remove punctuation and replace spaces with dashes
    semantic_id = semantic_id.lower()
    semantic_id = re.sub(r"[^\w\s]", "", semantic_id)
    semantic_id = re.sub(r"\s+", "-", semantic_id)
    return semantic_id + "-" + str(uuid.uuid4())[:2]


def _get_text(chat_completion) -> str:
    text = chat_completion.choices[0].message.content
    print("TEXT:", text)
    if True:
        logger.debug("\n%s", text)
    return text


def _extract_jsonstr(text: str) -> str:
    if "{" not in text or "}" not in text:
        logger.warning(
            f"""JSON formatting of generation may be incorrect. brackets are 
                       missing.\n generation length: {len(text)}
                       generation:{text}"""
        )
        return text
    return text[text.find("{") : text.rfind("}") + 1]


if __name__ == "__main__":
    _cli_main()
