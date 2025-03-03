import argparse
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from openai import OpenAI
from pydantic import BaseModel
import sys
import yaml
from pathlib import Path
print("done importing")

client = OpenAI()
PROMPT_PATH = Path(__file__).parent.parent / 'prompts' / 'parody.yaml'
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

class CleanArticle(BaseModel):
    """Represents a cleaned article with title, body and author"""
    title: str
    body: str
    author: str

def article_to_md(url: str) -> str:
    """Converts the text from a website into markdown

    Args:
        url (str): the website url

    Returns:
        str: the markdown text

    Raises:
        DocumentConversionError: If conversion fails
        ValueError: If URL is invalid
    """
    try:
        converter = DocumentConverter(allowed_formats=[InputFormat.HTML])
        result = converter.convert(url)
        return result.document.export_to_markdown()
    except Exception as e:
        raise DocumentConversionError(f"Failed to convert document: {str(e)}")


def clean_article_md(website_md: str) -> CleanArticle:
    """Uses a language model to extract structured data from markdown text
    
    Args:
        website_md (str): Markdown text of the article
        
    Returns:
        CleanArticle: Structured article data
        
    Raises:
        ArticleExtractionError: If extraction fails
    """
    try:
        print("starting completion...")
        chat_completion = client.beta.chat.completions.parse(
            messages=[
                {
                    "role": "system",
                    "content": PROMPTS['clean_article_md'],
                },
                {"role": "user", "content": website_md},
            ],
            model="gpt-4o-mini",
            response_format=CleanArticle
        )
        article = chat_completion.choices[0].message.parsed
        if article is None:
            raise ArticleExtractionError("Failed to extract article data")
        return article
    except Exception as e:
        raise ArticleExtractionError(f"Failed to clean article: {str(e)}")


def generate_parody_outline(article: CleanArticle) -> str:
    """Transform a normal article into an outline for a Rat News Network article

    Args:
        article (CleanArticle): The article title, author, and body

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
                    "content": PROMPTS["convert_article"]
                    .replace("{{title}}", article.title)
                    .replace("{{article}}", article.body),
                },
            ],
            model='gpt-4o',
            temperature=0.3,
        )
        rat_article_overview = chat_completion.choices[0].message.content
        if rat_article_overview:
            return rat_article_overview
    except Exception as e:
        print(e)
    return ''



def main():
    """CLI entrypoint"""
    parser = argparse.ArgumentParser(description="Convert web articles into rat-themed parodies")
    parser.add_argument("url", help="URL of the article to parody")
    parser.add_argument("--output", help="Output file path (default: print to stdout)")
    args = parser.parse_args()

    try:
        # Convert article to markdown
        md_text = article_to_md(args.url)
        
        # Extract clean article data
        article = clean_article_md(md_text)
        
        # Format output
        output = f"# {article.title}\n\nBy {article.author or 'Unknown'}\n\n{article.body}"
        
        # Write or print result
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)            
        else:
            print(output)
        
        outline = generate_parody_outline(article)

        if args.output:
            with open(args.output, "w") as f:
                f.write(outline)            
        else:
            print('\n\n\n---\n\n',outline)

    except ParodyError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
