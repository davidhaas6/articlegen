
import gen
import job
import templater

import os
from datetime import datetime
import shutil
import subprocess
from typing import List, Dict


def process_article(article: dict, article_dir: str):
    article_id = article['article_id']  # new articles have article_id
    if 'img_path' in article:
        local_imgpath = os.path.join(article_dir, f'{article_id}.png')
        try:
            if job.download_file(article['img_path'], local_imgpath):
                article['url'] = article['img_path']
                article['img_path'] = local_imgpath
        except Exception as e:
            print('Error downloading images' + str(e))


def git_operations(site_dir: str, repo_url: str, github_token: str) -> None:
    os.chdir(site_dir)

    # Initialize git if not already a repository
    if not os.path.exists(os.path.join(site_dir, '.git')):
        subprocess.run(["git", "init"], check=True)

    # Extract username and repo name from URL
    _, _, username, repo_name = repo_url.rstrip('.git').rsplit('/', 3)
    
    # Set up remote
    push_url = f"https://{github_token}@github.com/{username}/{repo_name}.git"
    try:
        subprocess.run(["git", "remote", "add", "origin", push_url], check=True)
    except subprocess.CalledProcessError:
        # If remote already exists, update it
        subprocess.run(["git", "remote", "set-url", "origin", push_url], check=True)

    # Fetch the latest changes from the remote
    subprocess.run(["git", "fetch", "origin"], check=True)

    # Check if the 'main' branch exists remotely
    remote_branch_exists = subprocess.run(
        ["git", "ls-remote", "--exit-code", "--heads", "origin", "main"],
        capture_output=True
    ).returncode == 0

    if remote_branch_exists:
        # If the branch exists, fetch and reset to it
        subprocess.run(["git", "fetch", "origin", "main"], check=True)
        subprocess.run(["git", "reset", "--hard", "origin/main"], check=True)
    else:
        # If the branch doesn't exist, create it
        subprocess.run(["git", "checkout", "-b", "main"], check=True)

    # Add all new files
    subprocess.run(["git", "add", "-A"], check=True)

    # Commit changes
    subprocess.run(["git", "commit", "-m", "Update site"], check=True)

    # Push changes
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)


def generate_and_push_articles(repo_url: str, num_articles: int = 5) -> str:
    site_dir = f"out/site/{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"
    image_dir = f"out/images/{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"
    os.makedirs(site_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)
    print(f"Current working directory: {os.getcwd()}")
    # articles = gen.new_articles(num_articles)
    articles = [
        {'title': 'Green Paws Initiative: Ratopolis Commits to a Greener Future', 'overview': "In a groundbreaking step toward environmental stewardship, Ratopolis City Council has announced the 'Green Paws Initiative,' a comprehensive plan aimed at reducing waste and promoting sustainable living through community gardens and renewable energy sources starting today.", 'body': "The 'Green Paws Initiative' aims to transform Ratopolis into a greener, healthier city. Community gardens will spring up across neighborhoods, providing fresh produce and fostering community ties. Solar panels and wind turbines will appear atop buildings, reducing our carbon footprint.\n\nCouncilmember Whisker Greenpaw, a key proponent, stated, “Our city must lead the way in sustainable living. This initiative will not only beautify Ratopolis but also ensure a healthier future for our residents.” The council believes the plan will establish Ratopolis as a model of environmental responsibility.\n\nCommunity gardens are at the heart of the Initiative. Five initial sites have been chosen, including Old Cheese Park and the Riverside Alley. These gardens will offer residents the chance to grow their own vegetables and herbs. Gardeners will also benefit from workshops teaching sustainable gardening techniques.\n\nWhiskers McCheese, a local shop owner, shared his excitement: “This initiative is a breath of fresh air for our city. It's about time we put our paws to work for a greener future!” His fellow residents echoed this positive sentiment, expressing enthusiasm for the new green spaces.\n\nThe initiative extends beyond gardens. Ratopolis will integrate renewable energy sources like solar panels and wind turbines. This move is expected to cut the city's energy consumption by 30% within the next five years. Solar panels will grace Ratopolis High School’s roof by summer, followed by other public buildings.\n\nCheddar Chomp, an environmental activist, praised the council's vision: “Renewable energy is the way forward. I can't wait to see Ratopolis leading the way in sustainability.” He believes the Initiative sets a standard for rat cities everywhere.\n\nCity planners predict the Initiative will face challenges. Some residents fear the costs involved, while others worry about the maintenance of gardens and energy systems. However, the council has outlined strategies to address these concerns. Fundraisers and partnerships with local businesses will cover costs. Volunteers and educational programs will ensure community members can maintain the gardens.\n\nInvolve yourself in Ratopolis' green revolution! Your participation is crucial. Residents can join their local community gardens, attend workshops, or volunteer for upkeep. The City Council plans monthly forums for citizens to voice their thoughts and suggestions.\n\nSqueaky Clean, a community gardener, added, “I'm excited to see more green spaces in Ratopolis. It's going to make our city more beautiful and healthier.” His optimism highlights the anticipated benefits of the Initiative.\n\nHowever, some critics argue that changing city infrastructure is costly and complex. They suggest smaller-scale projects might be more feasible. Despite these concerns, City Council remains confident in their plan’s potential.\n\nRatopolis isn't alone in this venture. Other cities, like Squeaktown and Whiskerville, have implemented similar greening projects with notable success. These examples provide valuable insights and best practices.\n\n“This Initiative is vital for our future,” emphasized Councilmember Whisker Greenpaw. “Together, we can build a sustainable Ratopolis.” The long-term vision includes expanding the project to more locations and incorporating more innovative solutions.\n\nAs Ratopolis embarks on this significant journey, it's clear that the 'Green Paws Initiative' will positively impact our community and environment. By working together, we can create a legacy of sustainability for generations to come.\n\nJoin us in making Ratopolis a shining example of green living. Get involved, support the effort, and watch as our city transforms. The future is green, and it starts with us.\n\nSo, Ratopolis, are you ready to embrace a greener future? The choice is ours. Let’s put our paws to work and make it happen.", 'generator': 'article_gen', 'img_path': 'out/articles/2024-07-15/21893258-0dc9-4c19-b622-d5fefc72b96c.png', 'timestamp': '2024-07-15 01:07:09', 'article_id': '21893258-0dc9-4c19-b622-d5fefc72b96c', 'url': 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-H25SdYjElqF0b9FGzZ6gj1m6/user-FwuBUCdpb4zLtXICUkT5JjN0/img-ogYkg8qQgjBm7FXBxxRTXY9J.png?st=2024-07-15T05%3A07%3A09Z&se=2024-07-15T07%3A07%3A09Z&sp=r&sv=2023-11-03&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-07-15T01%3A49%3A44Z&ske=2024-07-16T01%3A49%3A44Z&sks=b&skv=2023-11-03&sig=Wr1upxwB7TyGjfdOba3Q5Q2KOhApDZ5JpHGNQG22z6w%3D'}]
    for article in articles:
        process_article(article, image_dir)
        
    # Generate site
    os.makedirs(site_dir, exist_ok=True)
    templater.ArticleSiteGenerator(
        image_dir, 
        "templates/", 
        site_dir
    ).generate_site(articles)
    print(site_dir)

    if not os.path.exists(site_dir) or not os.listdir(site_dir):
        raise ValueError(f"Site directory {site_dir} does not exist or is empty")
        
    # Perform Git operations
    github_token = get_github_token()
    git_operations(site_dir, repo_url, github_token)

    print(f"Site generated and pushed to {repo_url}")
    return site_dir

def get_github_token() -> str:
    token = os.environ.get('GITHUB_PAT')
    if not token:
        raise ValueError("GitHub Personal Access Token not found in environment variables")
    return token


# def generate_and_push_articles(repo_url: str, num_articles: int = 5, ):
#     image_dir = f"out/articles/{datetime.now().strftime('%Y-%m-%d')}"
#     articles = gen.new_articles(num_articles)
#     for article in articles:
#         process_article(article, image_dir)
        
#     # Generate site
#     site_dir = f"out/site/{datetime.now().strftime('%Y-%m-%d')}"
#     templater.ArticleSiteGenerator(
#         image_dir, 
#         "templates/", 
#         site_dir
#     ).generate_site(articles)
    
#     os.chdir(site_dir)
#     os.system("git init")
#     os.system("git add .")
#     os.system('git commit -m "Update site"')
    
#     github_token = get_github_token()
    
#     # Extract username and repo name from URL
#     _, _, username, repo_name = repo_url.rstrip('.git').rsplit('/', 3)
    
#     # Set up remote and push
#     push_url = f"https://{github_token}@github.com/{username}/{repo_name}.git"
#     os.system(f"git remote add origin {push_url}")
#     os.system("git branch -M main")
#     os.system("git push -u origin main")

#     print(f"Site generated and pushed to {repo_url}")
#     return site_dir

# Usage example
if __name__ == "__main__":
    default_repo = "https://github.com/davidhaas6/rat-news-network-frontend.git"
    generate_and_push_articles(default_repo, 1)