import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import shutil

import text_processing
import src.config


class ArticleSiteGenerator:
    def __init__(self, articles_dir, template_dir, output_dir, archive_src_dir):
        self.articles_dir = articles_dir
        self.template_dir = template_dir
        self.output_dir = output_dir
        self.article_output_dir = os.path.join(self.output_dir, "article")
        self.archive_src_dir = archive_src_dir
        self.site_img_dir = os.path.join("static", "img")
        self.img_output_dir = os.path.join(output_dir, self.site_img_dir)
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_site(self):
        os.makedirs(self.output_dir, exist_ok=True)
        # new_articles = self._load_articles(article_jsons)
        all_articles = self.generate_content_pages()
        self.copy_template_dir()
        # self.generate_article_pages(articles)
        # self.generate_index_page(articles)
        self.copy_images(all_articles)
        self.generate_qr_code_page()
        self.generate_404_page()
        self.generate_subscribe_page()

    def copy_template_dir(self):
        """Copies the template directory to the output directory."""
        shutil.copytree(
            os.path.join(self.template_dir, "site_template"),
            self.output_dir,
            dirs_exist_ok=True,
        )

    def generate_article_pages(self, articles):
        template = self.env.get_template("article.html")
        for article in articles:
            self._write_article(article, self.article_output_dir, template=template)

    def copy_images(self, articles):
        for article in articles:
            src_path = article['img_path']
            dst_path = os.path.join(self.img_output_dir, article["img_filename"])
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
            else:
                print(f"Warning: {article['article_id']} - Image file not found: {src_path}")

    def generate_index_page(self, articles, edition, is_latest, dst_path=None):
        if dst_path is None:
            dst_path = os.path.join(self.output_dir, "index.html")
        template = self.env.get_template("index.html")
        output = template.render(articles=articles, edition=edition, is_latest=is_latest)
        with open(dst_path, "w") as f:
            f.write(output)

    def generate_qr_code_page(self):
        template = self.env.get_template("qr.html")
        output = template.render()
        with open(os.path.join(self.output_dir, "qr.html"), "w") as f:
            f.write(output)
    
    def generate_404_page(self):
        template = self.env.get_template("404.html")
        output = template.render()
        with open(os.path.join(self.output_dir, "404.html"), "w") as f:
            f.write(output)

    def generate_subscribe_page(self):
        """Generates the subscription page."""
        template = self.env.get_template("subscribe.html")
        output = template.render(title="Subscribe")
        with open(os.path.join(self.output_dir, "subscribe.html"), "w") as f:
            f.write(output)

    def generate_content_pages(self):
        archive_dst_dir = os.path.join(self.output_dir, "edition")
        if not os.path.exists(archive_dst_dir):
            os.makedirs(archive_dst_dir, exist_ok=True)

        all_articles = self._load_articles(
            article_dir=self.archive_src_dir,
            recursive=True
        )
        articles_by_date = {}
        for article in all_articles:
            date = article["timestamp"].strftime("%Y-%m-%d")
            if date not in articles_by_date:
                articles_by_date[date] = []
            articles_by_date[date].append(article)

        # mapping of dates to edition numbers
        # This could be loaded from a configuration file
        sorted_dates = sorted(articles_by_date.keys())
        date_to_edition = {}
        for edition_num, date in enumerate(sorted_dates, 1):
            date_to_edition[date] = edition_num
        
        # Generate archive pages using the edition numbers
        for date, articles in articles_by_date.items():
            edition_num = date_to_edition[date]
            latest_edition = edition_num == max(date_to_edition.values())
            if latest_edition:
                # its convenient for navigation to write the index content to two pages
                file_path = os.path.join(self.output_dir, "index.html")
                self.generate_index_page(
                    articles, 
                    edition_num, 
                    latest_edition, 
                    file_path
                )
                
            file_path = os.path.join(archive_dst_dir, f"{edition_num}.html")
            self.generate_index_page(
                articles, 
                edition_num, 
                latest_edition, 
                file_path
            )
            for article in articles:
                self._write_article(article, self.article_output_dir)
        
        return all_articles

    def _load_articles(self, articles=None, article_dir=None, recursive=False):
        if article_dir is None:
            article_dir = self.articles_dir

        if isinstance(articles, list):
            for article in articles:
                self._process_article(article)
        else:
            articles = []
            for filename in os.listdir(article_dir):
                file_path = os.path.join(article_dir, filename)
                if filename.endswith(".json"):
                    with open(file_path, "r") as f:
                        article = json.load(f)
                        self._process_article(article)
                        articles.append(article)
                elif recursive and os.path.isdir(file_path):
                    articles += self._load_articles(
                        article_dir=file_path, 
                        recursive=True
                    )

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
        article["img_filename"] = os.path.basename(article["img_path"])
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
            img_path=article["img_filename"],
            reading_time=article["reading_time_minutes"],
            comments=article.get("comments", []),
            parody_src=article.get('parody_src')
        )
        
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
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
        default=src.config.root / f"out/templater-output/{day_timestamp}/site_{full_timestamp}",
        nargs="?",
    )
    parser.add_argument(
        "template_dir",
        help="Directory containing HTML templates",
        default=src.config.TEMPLATES_DIR.as_posix(),
        nargs="?",
    )
    args = parser.parse_args()

    generator = ArticleSiteGenerator(
        args.articles, 
        args.template_dir, 
        f"{args.output_dir}", 
        src.config.DEFAULT_ARTICLE_DIR
    )
    generator.generate_site()
    print(args.output_dir)
