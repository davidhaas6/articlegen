import argparse
import os
import random
from typing import List, Optional, Dict, Any
from multiprocessing import Pool
from markitdown import MarkItDown
from openai import OpenAI
import sys
import requests
import yaml
import dotenv
import re

import config

if not dotenv.load_dotenv(".env"):
    print("WARNING: Could not load env file")
client = OpenAI()
PROMPT_PATH = config.PROMPTS_DIR / "parody.yaml"
with open(PROMPT_PATH) as f:
    PROMPTS = yaml.safe_load(f)


class ParodyError(Exception):
    """Base exception for parody-related errors"""

    pass


class DocumentConversionError(ParodyError):
    """Raised when document conversion fails"""

    pass


class ArticleExtractionError(ParodyError):
    """Raised when article extraction fails"""

    pass


def fetch_response(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def article_to_md(url: str) -> str | None:
    """Converts the text from a website into markdown

    Args:
        url (str): the website url

    Returns:
        str: the markdown text

    Raises:
        DocumentConversionError: If conversion fails
        ValueError: If URL is invalid
    """
    converter = MarkItDown(enable_plugins=False)
    html = fetch_response(url)
    if html:
        result = converter.convert(html)
        return result.text_content
    return None


def clean_article_md(website_md: str, title: str = "", description: str = "") -> str:
    """Uses a language model to extract structured data from markdown text

    Args:
        website_md (str): Markdown text of the article

    Returns:
        str: Article title and body

    Raises:
        ArticleExtractionError: If extraction fails
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": PROMPTS["clean_article_md"]
                    .replace("{{title}}", title)
                    .replace("{{description}}", description),
                },
                {"role": "user", "content": website_md},
            ],
            model="gpt-4o-mini",
            max_completion_tokens=3000,
        )
        article = chat_completion.choices[0].message.content
        if article is None:
            raise ArticleExtractionError("Failed to extract article data")
        return article
    except Exception as e:
        raise ArticleExtractionError(f"Failed to clean article: {str(e)}")


def generate_parody_outline(article: str) -> str:
    """Transform a normal article into an outline for a Rat News Network article

    Args:
        article (str): The article title and body

    Returns:
        str: outline and brainstorming
    """
    try:
        # get rat overview
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": PROMPTS["convert_article_system"],
                },
                {
                    "role": "user",
                    "content": PROMPTS["convert_article"].replace(
                        "{{article}}", article
                    ),
                },
            ],
            model="gpt-4o",
            temperature=0.3,
        )
        rat_article_overview = chat_completion.choices[0].message.content
        if rat_article_overview:
            return rat_article_overview
    except Exception as e:
        print(e)
    return ""


def process_single_article(article: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """Process a single article and return its outline.

    Args:
        article (Dict[str, Any]): Article data containing url, title, and description

    Returns:
        Optional[str]: The processed outline if successful, None otherwise
    """
    url = article.get("url")
    if not url:
        return None

    md_text = article_to_md(url)
    if not md_text:
        return None

    try:
        md_text_clean = clean_article_md(
            md_text, article.get("title", ""), article.get("description", "")
        )
        outline_full_text = generate_parody_outline(md_text_clean)
        outline = extract_step_5(outline_full_text)

        if not outline:
            print("Could not extract outline!!!\nText:\n", outline_full_text)
            return None

        return {"description": outline, "src_url": url}
    except Exception as e:
        print(f"Error processing article {url}: {e}")
        return None


def generate_top_story_outlines(
    num: int, num_processes: Optional[int] = None
) -> List[Dict[str, str]]:
    """Generate parody outlines for top news stories using parallel processing.

    Args:
        num (int): Number of articles to process
        num_processes (Optional[int]): Number of processes to use. Defaults to CPU count.

    Returns:
        List[str]: List of generated outlines
    """
    api_key = os.environ.get("NEWS_API_KEY")
    if not api_key:
        raise ValueError(
            "NEWS_API_KEY environment variable must be set to your newsapi.org key"
        )
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": api_key,
        "pageSize": max(30, num),
        "sources": "associated-press,reuters",
    }

    response = requests.get(url, params=params)
    data = response.json()
    selected_articles = random.sample(data.get("articles", []), num)
    print("Parodying:")
    for i, article in enumerate(selected_articles):
        print(f"{i+1}.", article.get("title"))

    # Process articles in parallel
    with Pool(processes=num or num_processes) as pool:
        outlines = pool.map(process_single_article, selected_articles)

    # Filter out None results
    return [outline for outline in outlines if outline is not None]


def extract_step_5(text) -> str | None:
    pattern = re.compile(
        r"^#+\s*Step\s*5\b.*?$\n(.*?)(?=^#+\s*Step\s*\d+\b|\Z)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )

    match = pattern.search(text)
    return match.group(1).strip() if match else None


def main():
    """CLI entrypoint"""
    import json

    parser = argparse.ArgumentParser(
        description="Convert web articles into rat-themed parodies"
    )
    parser.add_argument("--url", help="URL of the article to parody")
    parser.add_argument("--output", help="Output file path (default: print to stdout)")
    args = parser.parse_args()

    try:
        if not args.url:
            parser.error("--url is required")


        outline = process_single_article({"url": args.url})
        if not outline:
            raise ArticleExtractionError("Failed to generate outline")

        # Output handling
        if args.output:
            with open(args.output, "w") as f:
                f.write(json.dumps(outline, indent=2))
        else:
            print(outline)

    except ParodyError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

    # print(json.dumps(generate_top_story_outlines(2), indent=2))
