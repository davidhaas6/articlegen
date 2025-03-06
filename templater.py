import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import shutil

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
        articles = self._load_articles(article_jsons)
        self.copy_template_dir()
        self.generate_article_pages(articles)
        self.generate_index_page(articles)
        self.copy_images(articles)
        self.generate_qr_code_page(articles)
        self.generate_subscribe_page()

    def copy_template_dir(self):
        """Copies the template directory to the output directory."""
        shutil.copytree(
            os.path.join(self.template_dir, "site_template"),
            self.output_dir,
            dirs_exist_ok=True,
        )

    def generate_article_pages(self, articles, dst_dir=None):
        if dst_dir is None:
            dst_dir = self.output_dir
        template = self.env.get_template("article.html")
        for article in articles:
            self._write_article(article, dst_dir, template=template)

    def copy_images(self, articles):
        for article in articles:
            src_path = os.path.join(self.articles_dir, article["img_path"])
            dst_path = os.path.join(self.img_output_dir, article["img_path"])
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
            else:
                print(f"Warning: Image file not found: {src_path}")

    def generate_index_page(self, articles, dst_path=None):
        if dst_path is None:
            dst_path = os.path.join(self.output_dir, "index.html")
        template = self.env.get_template("index.html")
        output = template.render(articles=articles)
        with open(dst_path, "w") as f:
            f.write(output)

    def generate_qr_code_page(self, articles):
        template = self.env.get_template("qr.html")
        output = template.render(articles=articles)
        with open(os.path.join(self.output_dir, "qr.html"), "w") as f:
            f.write(output)

    def generate_subscribe_page(self):
        """Generates the subscription page."""
        template = self.env.get_template("subscribe.html")
        output = template.render(title="Subscribe")
        with open(os.path.join(self.output_dir, "subscribe.html"), "w") as f:
            f.write(output)

    def generate_archive(self, src_article_dir: str):
        # UNFINISHED

        dst_dir = os.path.join(self.output_dir, "archive")
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir, exist_ok=True)
            print("WARNING: Archive directory does not exist. Creating it.")
        # load jsons from archive_dir
        articles = self._load_articles(article_dir=src_article_dir)
        # group them by their date
        articles_by_date = {}
        for article in articles:
            # article = self._process_article(article)
            # get the day of the week
            # day = article['timestamp'].strftime('%A')
            date = article["timestamp"].strftime("%Y-%m-%d")
            if date not in articles_by_date:
                articles_by_date[date] = []
            articles_by_date[date].append(article)

        # generate the archive page for each date
        for date, articles in articles_by_date.items():
            print(date)
            self.generate_index_page(articles, os.path.join(dst_dir, date + ".html"))
            for article in articles:
                # print(f"  {article['article_id']} {article['title']}")
                self._write_article(article, dst_dir)

    def _load_articles(self, articles=None, article_dir=None):
        if article_dir is None:
            article_dir = self.articles_dir

        if isinstance(articles, list):
            for article in articles:
                self._process_article(article)
        else:
            articles = []
            print("Loading articles from directory")
            for filename in os.listdir(article_dir):
                if filename.endswith(".json"):
                    with open(os.path.join(article_dir, filename), "r") as f:
                        article = json.load(f)
                        self._process_article(article)
                        articles.append(article)

        return sorted(articles, key=lambda x: x.get("category") != 'Featured')

    def _process_article(self, article):
        """Does misc cleaning, data conversion, and imputation on an article object
        Args:
            article (dict): The article to process.
        Returns:
            dict: The processed article.
        """
        article["timestamp"] = datetime.strptime(
            article["timestamp"], "%Y-%m-%d %H:%M:%S"
        )
        article["img_path"] = os.path.basename(article["img_path"])
        if "reading_time_minutes" not in article:
            article["reading_time_minutes"] = text_processing.estimate_reading_time(
                article["body"]
            )
        article["reading_time_minutes"] = round(article["reading_time_minutes"])
        if "comments" not in article:
            article["comments"] = []
        return article

    def _write_article(self, article, out_dir, template=None):
        """Inserts an article into a template and writes it to a file.
        Args:
            article (dict): The article to insert into the template.
            out_dir (str): The directory to write the file to.
            template (jinja2.Template): The template to use. 
                                        If None, uses the default template.
        Returns:
            str: The rendered template as a string.
        """

        if template is None:
            template = self.env.get_template("article.html")

        output = template.render(
            title=article["title"],
            overview=article["overview"],
            body=text_processing.markdown_to_html(article["body"]),
            img_path=article["img_path"],
            reading_time=article["reading_time_minutes"],
            comments=article.get("comments", []),
        )
        filename = f"{article['article_id']}.html"
        with open(os.path.join(out_dir, filename), "w") as f:
            f.write(output)
        return output


# Usage
if __name__ == "__main__":
    import argparse

    day_timestamp = datetime.now().strftime("%Y-%m-%d")
    full_timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")

    parser = argparse.ArgumentParser(
        description="Generate a static website from article JSON files."
    )
    parser.add_argument("--articles", help="Directory containing article JSON files")
    parser.add_argument(
        "output_dir",
        help="Directory to output the generated site",
        default=f"out/templater-output/{day_timestamp}/site_{full_timestamp}",
        nargs="?",
    )
    parser.add_argument(
        "template_dir",
        help="Directory containing HTML templates",
        default="templates/",
        nargs="?",
    )
    args = parser.parse_args()

    generator = ArticleSiteGenerator(
        args.articles, args.template_dir, f"{args.output_dir}"
    )
    generator.generate_site()
    print(args.output_dir)
