# generate news articles
from datetime import datetime
from multiprocessing import Pool
from typing import List
import logging
import os
from openai import OpenAI
import yaml
import json
import sys
import random
import traceback
import uuid
import pathlib
from pathlib import Path
from groq import Groq

VERBOSE = True
journalist1_system = {
    "role": "system",
    "content": "Your name is Whisker Walters. You are a famous journalist and the chief news editor for Rat News Network. Your job is to come up with the next juicy story."   # noqa: E501
}

prompts_dir = Path(__file__).resolve().parent / 'prompts'
with open(prompts_dir / 'system.yaml') as f:
    systems = yaml.safe_load(f)

client = OpenAI()
image_client = OpenAI()

json_llm = 'gpt-4o'
light_llm = 'gpt-35-turbo'
heavy_llm = 'gpt-4o'

logging.basicConfig(
    # filename='logs/generator.log',
    format="%(asctime)s:%(levelname)s:%(message)s",
    # encoding='utf-8',
    level=logging.INFO,
    # prevent logs from other files from showing
)
logger = logging.getLogger(__name__)



def _cli_main():
    """Command line interface main function
    """
    global VERBOSE
    VERBOSE = True
    if len(sys.argv) == 1:
        print('usage: gen.py idea image full topic[topic_idea]')
        return
    action = str(sys.argv[1])
    if 'idea' in action:
        print("\n***INITIAL IDEAS:")
        ideas = article_ideas(1)
    elif 'full' in action:
        logger.info(new_articles(int(sys.argv[2]) if len(sys.argv) > 1 else 2))
    elif 'image' in action:
        if len(sys.argv) < 4:
            print('usage: gen.py image <title> <outline>')
            return
        url = article_image(sys.argv[2], sys.argv[3])
        print(url)
        logger.info(url)
    elif 'topic' in action:
        article_from_idea(sys.argv[2])
    




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
        ideas_str = article_ideas(num)
        ideas = json.loads(ideas_str)
        ideas = ideas[list(ideas.keys())[0]] # output json has a single key
    
    num_cpus = min(6, os.cpu_count())
    n_threads = min(num, num_cpus)
    with Pool(n_threads) as pool:
        string_ideas = map(json.dumps, ideas)
        print("Generating articles. Ideas:", string_ideas)
        articles = pool.map(article_from_idea, string_ideas)   

    return articles


def article_from_idea(idea: str) -> dict:
    """Create an article from an idea

    Args:
        idea (str): A description of the article

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
        outline = article_outline(idea.strip())
        article = article_body(idea, outline)
        article['img_path'] = article_image(article['title'], outline)
        article['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f'*Article created*\nTitle: {article["title"]}\nImage: {article["img_path"]}\nOverview:{article["overview"]}')
        article['article_id'] = str(uuid.uuid4())
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return None
    return article


def adhoc_article(topic: str, title=None, model=heavy_llm, temp=0) -> dict:
    """Create an article from an idea

    Args:
        topic (str): A description of the article
        model (str): the model to use for generation
        temp (float): the temperature to use for generation

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
        article_text = _get_text(client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are one of the world's best journalists, currently working at Rat News Network. You are known for writing articles that are well-structured, easy to read, and interesting."
                },
                {
                    "role": "user",
                    "content": f"Write a high-quality article for the following topic: {topic}"
                }
            ],
            model=model,
            temperature=temp
        ))
        article = article_to_json(article_text)

        # create the image
        with open(prompts_dir / 'article.yaml') as f:
            prompts = yaml.safe_load(f)
            
        summary = _get_text(client.chat.completions.create(messages=[
                {
                    "role": "user",
                    "content": prompts['summary'].replace('{{num_sentences}}', '3')
                                                 .replace('{{title}}', article["title"])
                                                 .replace('{{body}}', article["title"])
                }
            ],
            model=light_llm,
            temperature=temp
        ))
        article['summary'] = summary  # unused rn
        article['img_path'] = article_image(article['title'], summary)
        article['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f'*Article created*\nTitle: {article["title"]}\nImage: {article["img_path"]}\nOverview:{article["overview"]}')
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return None
    return article


def get_ad_prompt(article: str) -> str:
    pass


def article_image(title: str, outline: str) -> str:
    with open(prompts_dir / 'images.yaml') as f:
        prompts = yaml.safe_load(f)

    convo_1_ideas = [
        {
            "role": "user",
            "content": prompts['brainstorming'].replace('{{title}}', title).replace('{{overview}}', outline)
        }
    ]
    chat_completion = client.chat.completions.create(
        messages=convo_1_ideas,
        model=heavy_llm,
        temperature=0.7
    )
    ideas = _get_text(chat_completion)

    convo_2_discretize = convo_1_ideas + [
        {
            "role": "assistant",
            "content": ideas
        },
        {
            "role": "system",
            "content": systems['discretize']
        },
        {
            "role": "user",
            "content": prompts['select']
        }
    ]
    chat_completion = client.chat.completions.create(
        messages=convo_2_discretize,
        model=json_llm,
        temperature=0
    )
    img_idea_json = _extract_jsonstr(_get_text(chat_completion))

    response = image_client.images.generate(
        model="dall-e-3",
        prompt=prompts['create'].replace('{{image_idea}}', img_idea_json).replace('{{title}}', title),
        quality="standard",
        n=1,
    )
    for img in response.data:
        logger.info("\nRevised prompt: %s", img.revised_prompt)
        logger.info("%s", img.url)
        
    image_url = response.data[0].url
    return image_url


def article_ideas(n, system_prompt='whisker') -> str:
    """Generate n 1-sentence article ideas

    Args:
        n (int): The number of ideas to create. 

    Returns:
        str: a string containing a set of article ideas
    """
    with open(prompts_dir / 'ideas.yaml','rb') as f:
        prompts = yaml.safe_load(f)
    
    convo_1_ideas = [
        {
            "role": "system",
            "content": systems[system_prompt],
        },
        {
            "role": "user",
            "content": prompts['idea_generator'].replace('{{n}}', str(n))
        }
    ]
    chat_completion = client.chat.completions.create(
        messages=convo_1_ideas,
        model=heavy_llm,
        temperature=1
    )
    ideas = _get_text(chat_completion)

    convo_2_discretize = convo_1_ideas + [
        {
            "role": "assistant",
            "content": ideas
        },
        {
            "role": "user",
            "content": prompts['json_formatter']
        }
    ]
    chat_completion2 = client.chat.completions.create(
        messages=convo_2_discretize,
        model=json_llm,
        temperature=0
    )

    discrete_ideas = _get_text(chat_completion2)
    return _extract_jsonstr(discrete_ideas)


def select_idea(ideas: str) -> str:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "As an expert AI news editor for Rat News Network, please analyze each of these article ideas and select the idea that will make the best article."  # noqa: E501
            },
            {
                "role": "user",
                "content": f"# Article Ideas:\n\n{ideas}",
            }
        ],
        model=heavy_llm,
    )
    best_article = _get_text(chat_completion)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "As an expert AI news editor for Rat News Network, please analyze each of these article ideas and select the idea that will make the best article."  # noqa: E501
            },
            {
                "role": "user",
                "content": f"# Article Ideas:\n\n{ideas}",
            },
            {
                "role": "assistant",
                "content": best_article,
            },
            {
                "role": "user",
                "content": "Thank you! Now, please **copy** the article's title, description, and a summary of your editorial analysis into a *valid* JSON formatted string.",  # noqa: E501
            },
        ],
        model=light_llm
    )
    idea_json = _get_text(chat_completion)
    idea_json = idea_json[idea_json.find('{'):idea_json.rfind('}')+1]
    return idea_json


def article_outline(idea: str) -> str:
    """Create an outline for an article

    Args:
        idea (str): a textual description of an article idea

    Returns:
        str: A brief outline for the article
    """
    with open(prompts_dir / 'article.yaml','rb') as f:
        prompts = yaml.safe_load(f)
    
    chat_completion = client.chat.completions.create(
        messages=[
            # {
            #     "role": "system",
            #     "content": systems['whisker'],
            # },
            {
                "role": "user",
                "content": prompts['outline2'].replace('{{idea}}',idea.strip()),
            }
        ],
        model=heavy_llm,
        temperature=0.2
    )
    return _get_text(chat_completion)


def article_body(idea: str, outline: str, num_words=500) -> str:
    """Generate the actual text for an article

    Args:
        topic (str): The article's topic sentence
        title (str): The title of the article
        outline (str): An outline of the article
        n_paragraphs (int): The length of the article
        reading_level (int): The complexity of the article's structure and vocabulary

    Returns:
        str: an article json string:
               title -> article title
               overview -> article overview
               body -> article body
        str: generator version
    """
    
    with open(prompts_dir / 'article.yaml','rb') as f:
        prompts = yaml.safe_load(f)

    article_generator = random.choice([k for k in prompts.keys() if k.startswith('article_gen')])

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": systems['whisker'],
            },
            {
                "role": "user",
                "content": prompts[article_generator].replace('{{idea}}', idea) \
                                                    .replace('{{outline}}', outline) \
                                                    .replace('{{num_words}}', str(num_words)).strip()
            }
        ],
        model=heavy_llm,
    )
    raw_article = _get_text(chat_completion).strip()

    article_json = article_to_json(raw_article)
    article_json['generator'] = article_generator
    return article_json


def article_to_json(article_text: str, model=heavy_llm) -> dict:
    with open(prompts_dir / 'article.yaml','rb') as f:
        prompts = yaml.safe_load(f)

    other_args = {}
    if type(client) == Groq:
        print('groq')
        other_args["response_format"] = {"type": "json_object"}

    article_json_str = _get_text(client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": systems['article_to_json']
            },
            {
                "role": "user",
                "content":prompts['articleToJson'].replace('{{article}}', article_text).strip()
            }
        ],
        model=model,
        temperature=0,
        # **other_args
        response_format= {"type": "json_object"}
    ))

    try:
        return json.loads(_extract_jsonstr(article_json_str))
    except json.JSONDecodeError as e:
        logger.error(f'Json decode error: {e}')
        logger.error(traceback.format_exc())
        return {}


def _get_text(chat_completion) -> str:
    text = chat_completion.choices[0].message.content
    if VERBOSE:
        print(text)
        # logger.info()
        logger.debug('\n%s', text)
    # TODO: error handle
    return text

def query_llm(chat_completion) -> str:
    text = chat_completion.choices[0].message.content
    if VERBOSE:
        print(text)
        # logger.info()
        logger.debug('\n%s', text)
    # TODO: error handle
    return text


def _extract_jsonstr(text: str) -> str:
    if '{' not in text or '}' not in text:
        logger.warning(f'''JSON formatting of generation may be incorrect. brackets are 
                       missing.\n generation length: {len(text)}
                       generation:{text}''')
        return text
    return text[text.find('{'):text.rfind('}')+1]



if __name__ == '__main__':
    _cli_main()