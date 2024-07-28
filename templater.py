import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import shutil
import re

import text_processing


class ArticleSiteGenerator:
    def __init__(self, articles_dir, template_dir, output_dir):
        self.articles_dir = articles_dir
        self.template_dir = template_dir
        self.output_dir = output_dir
        self.site_img_dir = os.path.join("static", "img")
        self.img_output_dir = os.path.join(output_dir, self.site_img_dir)
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_site(self, article_jsons=None):
        os.makedirs(self.output_dir, exist_ok=True)
        articles = self.load_articles(article_jsons)
        self.copy_template()
        self.generate_article_pages(articles)
        self.generate_index_page(articles)
        self.copy_images(articles)
        self.generate_qr_code_page(articles)

    def load_articles(self, articles=None):
        def _process_article(article):
            article["timestamp"] = datetime.strptime(article["timestamp"], "%Y-%m-%d %H:%M:%S")
            article["img_path"] = os.path.basename(article["img_path"])
            if 'reading_time_minutes' not in article:
                article['reading_time_minutes'] = text_processing.estimate_reading_time(article['body'])
            article['reading_time_minutes'] = round(article['reading_time_minutes'])

        if isinstance(articles, list):
            for article in articles:
                _process_article(article)
        else:
            articles = []
            print("Loading articles from directory")
            for filename in os.listdir(self.articles_dir):
                if filename.endswith(".json"):
                    with open(os.path.join(self.articles_dir, filename), "r") as f:
                        article = json.load(f)
                        _process_article(article)
                        articles.append(article)

        return sorted(articles, key=lambda x: x["timestamp"], reverse=True)

    def generate_article_pages(self, articles):
        template = self.env.get_template("article.html")
        
        for article in articles:
            output = template.render(
                title=article["title"],
                overview=article["overview"],
                # lead=article['overview'],  # Using overview as lead, adjust if needed
                body=text_processing.markdown_to_html(article["body"]),
                img_path=article["img_path"],
                reading_time=article["reading_time_minutes"],
            )
            filename = f"{article['article_id']}.html"
            with open(os.path.join(self.output_dir, filename), "w") as f:
                f.write(output)

    def copy_template(self):
        shutil.copytree(os.path.join(self.template_dir, "site_template"), self.output_dir, dirs_exist_ok=True)

    def copy_images(self, articles):
        for article in articles:
            src_path = os.path.join(self.articles_dir, article["img_path"])
            dst_path = os.path.join(self.img_output_dir, article["img_path"])
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
            else:
                print(f"Warning: Image file not found: {src_path}")

    def generate_index_page(self, articles):
        template = self.env.get_template("index.html")
        output = template.render(articles=articles)
        with open(os.path.join(self.output_dir, "index.html"), "w") as f:
            f.write(output)

    def generate_qr_code_page(self, articles):
        template = self.env.get_template("qr.html")
        output = template.render(articles=articles)
        with open(os.path.join(self.output_dir, "qr.html"), "w") as f:
            f.write(output)

# Usage
if __name__ == "__main__":
    import argparse
    day_timestamp = datetime.now().strftime("%Y-%m-%d")
    full_timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")

    parser = argparse.ArgumentParser(description="Generate a static website from article JSON files.")
    parser.add_argument("--articles", help="Directory containing article JSON files")
    parser.add_argument(
        "output_dir",
        help="Directory to output the generated site",
        default=f"out/templater-output/{day_timestamp}/site_{full_timestamp}",
        nargs="?",
    )
    parser.add_argument("template_dir", help="Directory containing HTML templates", default=f"templates/", nargs="?")
    args = parser.parse_args()

    ArticleSiteGenerator(args.articles, args.template_dir, f"{args.output_dir}").generate_site()
    print(args.output_dir)
