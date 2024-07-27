import gen
import util
import templater

import os
from datetime import datetime
import shutil
import subprocess
import logging
from urllib.parse import urlparse
import json
import sys

import text_processing

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate and deploy articles to a GitHub Pages site")
    parser.add_argument(
        "--repo",
        help="URL of the repository to deploy to",
        default="https://github.com/davidhaas6/rat-news-network-frontend.git",
        nargs="?",
    )
    parser.add_argument("--num", type=int, default=0, help="Number of articles to generate")
    parser.add_argument("--articles", help="Directory to save or load articles")
    parser.add_argument("--branch", help="Branch to deploy to", default="main", nargs="?")
    parser.add_argument("--keep-local", help="Keep the local repository after deployment", action="store_true")
    parser.add_argument("--auto", help="Automatically deploy without user input", action="store_true")
    args = parser.parse_args()

    generate_and_push_articles(args.repo, args.num, args.articles, args.branch, args.keep_local, args.auto)


def generate_and_push_articles(
    repo_url: str,
    num_articles: int = 0,
    article_dir: str = None,
    branch: str = "main",
    keep_local: bool = False,
    force: bool = False,
) -> str:
    day_timestamp = datetime.now().strftime("%Y-%m-%d")
    full_timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    site_dir = f"out/site/{day_timestamp}/{full_timestamp}"
    if article_dir is None:
        article_dir = f"out/articles/{day_timestamp}/{full_timestamp}"
    os.makedirs(site_dir, exist_ok=True)
    os.makedirs(article_dir, exist_ok=True)

    if num_articles > 0:
        articles = gen.new_articles(num_articles)
        for article in articles:
            process_article(article, article_dir)
            # write to disk
            with open(f"{article_dir}/{article['article_id']}.json", "w") as f:
                f.write(json.dumps(article))
    else:
        # load in articles
        articles = []
        for article_file in os.listdir(article_dir):
            with open(os.path.join(article_dir, article_file), "r") as f:
                if article_file.endswith(".json"):
                    articles.append(json.load(f))

    # Generate site
    os.makedirs(site_dir, exist_ok=True)
    templater.ArticleSiteGenerator(article_dir, "templates/", site_dir).generate_site(articles)
    print(site_dir)

    if not os.path.exists(site_dir) or not os.listdir(site_dir):
        raise ValueError(f"Site directory {site_dir} does not exist or is empty")

    git_deploy(auth_repo_url(repo_url), site_dir, branch, keep_local, force)
    return site_dir


def process_article(article: dict, article_dir: str):
    article_id = article["article_id"]  # new articles have article_id
    if "img_path" in article:
        local_imgpath = os.path.join(article_dir, f"{article_id}.webp")
        try:
            if util.download_and_compress_image(article["img_path"], local_imgpath):
                article["url"] = article["img_path"]
                article["img_path"] = local_imgpath
        except Exception as e:
            print("Error downloading images" + str(e))

    if "reading_time_minutes" not in article:
        article["reading_time_minutes"] = text_processing.estimate_reading_time(article["body"])


def git_deploy(repo_url: str, site_dir: str, branch_name: str = "main", keep_local: bool = False, force=False) -> None:
    # Ensure the site directory exists
    site_dir = os.path.abspath(site_dir)
    if not os.path.isdir(site_dir):
        print(f"Error: Site directory {site_dir} does not exist.")
        sys.exit(1)

    # Clone the repository
    logging.info(f"Cloning repository {repo_url}...")
    run_command(f"git clone {repo_url} repo")
    os.chdir("repo")

    # Ensure we're on the correct branch
    run_command(f"git checkout {branch_name} || git checkout -b {branch_name}")

    # Remove all files in the repo (except .git)
    for item in os.listdir("."):
        if item != ".git":
            if os.path.isfile(item):
                os.remove(item)
            elif os.path.isdir(item):
                shutil.rmtree(item)

    # Copy new files into the repo
    for item in os.listdir(site_dir):
        src = os.path.join(site_dir, item)
        dest = os.path.join(".", item)
        if os.path.isdir(src):
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dest)

    # Stage all changes
    run_command("git add -A")

    # Commit changes if there are any
    result = subprocess.run("git diff --staged --quiet", shell=True)
    if result.returncode == 1:  # Changes are staged
        commit_message = f"Daily site update {datetime.now().strftime('%Y-%m-%d')}"
        run_command(f'git commit -m "{commit_message}"')
        run_command(f"git status")
        if not force and input("Do you want to push the changes to the remote repository? (y/n): ").lower() == "y":
            run_command(f"git push origin {branch_name}")
            print("Changes pushed.")
    else:
        print("No changes to commit.")

    os.chdir("..")
    if not keep_local:
        shutil.rmtree("repo")


def auth_repo_url(repo_url: str) -> str:
    if not repo_url:
        raise ValueError("Repository URL not provided")

    parsed_url = urlparse(repo_url)
    username, repo_name = parsed_url.path.strip("/").split("/")[:2]
    repo_name = repo_name.rstrip(".git")

    token = os.environ.get("GITHUB_PAT")
    if not token:
        raise ValueError("GitHub Personal Access Token not found in environment variables")

    return f"https://{token}@github.com/{username}/{repo_name}.git"


def run_command(command):
    try:
        output = subprocess.run(
            command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        logging.info(f"{command} -> {output.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error output: {e.stderr}")
        # sys.exit(1)


if __name__ == "__main__":
    main()
