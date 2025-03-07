# Rat News Network Generator

A static site generator that creates content via LLMs instead of humans.

## Table of Contents
- [System Overview](#system-overview)
- [Environment Setup](#environment-setup)
- [Project Structure](#project-structure)
- [Usage Instructions](#usage-instructions)
  - [deploy.py](#deploypy-usage-instructions)
  - [gen.py](#genpy-usage-instructions)
- [Future Vision](#future-vision)
- [Documentation](#documentation)

## System Overview

The Rat News Network Generator is a Python-based pipeline that:

- Generates rat news articles using OpenAI's GPT models
- Creates accompanying images using DALL-E
- Renders content into a static website using Jinja2 templates
- Deploys the site to GitHub Pages via CI/CD

The system follows a three-stage pipeline:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│   Content   │     │     Site     │     │   GitHub    │     │  Published  │
│ Generation  │────▶│  Generation  │────▶│ Repository  │────▶│   Website   │
│  (gen.py)   │     │(templater.py)│     │ Deployment  │     │             │
└─────────────┘     └──────────────┘     └─────────────┘     └─────────────┘
```

The main components are:
- **deploy.py**: Main entry point that orchestrates the entire pipeline
- **gen.py**: Content generation engine using LLMs
- **templater.py**: Renders content into HTML using Jinja2 templates

## Environment Setup

### Required Environment Variables

```bash
# GitHub Personal Access Token for automated deployment
export GITHUB_PAT="your-github-personal-access-token"

# OpenAI API Key for content and image generation
export OPENAI_API_KEY="your-openai-api-key"

# News API Key (required for parody article generation)
export NEWS_API_KEY="your-newsapi-org-key"
```

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables as described above
4. Run the generator (see Usage Instructions below)

## Project Structure

```
articlegen/
├── deploy.py              # Main entry point and deployment script
├── gen.py                 # Content generation engine
├── templater.py           # Site generation and templating
├── text_processing.py     # Text utilities
├── util.py                # General utilities
├── job.py                 # Scheduled job functionality
├── docs/                  # Documentation
├── prompts/               # LLM prompt templates
├── src/                   # More source modules
├── templates/             # Jinja2 HTML templates and other static site files
└── tests/                 # Unit tests
```

## Usage Instructions

### deploy.py Usage Instructions

The main command to use this static site generator is:

```
python deploy.py [options]
```

#### Deploy Options
- `--num`: Number of articles to generate (default is 0)
- `--articles`: Directory to save or load articles
- `--branch`: Branch to deploy to (default is 'main')
- `--repo`: URL of the repository to deploy to (default is https://github.com/davidhaas6/rat-news-network-frontend.git)
- `--keep-local`: Keep the local repository after deployment (flag, no value needed)
- `--auto`: Automatically deploy without user input (flag, no value needed)

#### Deploy Usage Examples

##### 1. Generate and Deploy New Articles
To generate three new articles and push them to the 'test' branch of the default repository:

```
python deploy.py --num 3 --branch test
```

##### 2. Deploy Existing Articles
To push existing articles from a specific directory to the 'test' branch:

```
python deploy.py --articles my/article/dir/ --branch test
```

##### 3. Deploy to a Different Repository
To generate three articles and deploy them to a different repository:

```
python deploy.py --num 3 --repo https://github.com/username/my-static-frontent.git
```

##### 4. Generate Articles with Parodies
To generate five articles, including two parody articles based on real news:

```
python deploy.py --num 5 --branch main
```

##### 5. Automated Deployment
To generate articles and deploy without prompting for confirmation:

```
python deploy.py --num 3 --auto
```

#### Deploy Notes
- If `--num` is set to 0, the script will use existing articles from the specified `--articles` directory.
- The `--keep-local` flag can be added to any command to retain the local copy of the repository after deployment.
- Always ensure you have the necessary permissions for the target repository before deploying.
- When generating multiple articles (>2), the system automatically includes parody articles based on real news.

### gen.py Usage Instructions

gen.py is the core content generation script in the rat news generator. It provides several functions for generating different parts of an article or complete articles.

#### Command Structure
```
python gen.py [action] [parameters]
```

#### Actions and Parameters

1. **Generate Article Ideas**
   ```
   python gen.py idea [number_of_ideas]
   ```
   - Generates the specified number of article ideas.
   - If number_of_ideas is not provided, it defaults to 1.

2. **Generate Full Article**
   ```
   python gen.py full [idea]
   ```
   - Generates a complete article based on the provided idea.
   - The idea should be a string describing the article concept.

3. **Generate Article Image**
   ```
   python gen.py image [title] [outline]
   ```
   - Generates an image for an article based on its title and outline.

4. **Generate Article from Topic**
   ```
   python gen.py topic [topic_idea]
   ```
   - Generates an article based on a given topic idea.

5. **Generate Parody Articles**
   ```
   python gen.py parody [number_of_articles]
   ```
   - Generates parody articles based on real news stories.
   - Requires NEWS_API_KEY environment variable to be set.

#### gen.py Examples

1. Generate 5 article ideas:
   ```
   python gen.py idea 5
   ```

2. Generate a full article:
   ```
   python gen.py full "The impact of cheese scarcity on rat economy"
   ```

3. Generate an image for an article:
   ```
   python gen.py image "Whisker Fashion Trends" "Latest styles in rat whisker grooming"
   ```

4. Generate an article from a topic:
   ```
   python gen.py topic "Underground tunnel expansion project in Ratopolis"
   ```

5. Generate 3 parody articles based on current news:
   ```
   python gen.py parody 3
   ```

## Future Vision
- More interactivity
  - Enabling the users to further interact with and customize the site
- Generating non-RNN content 
  - i.e. use some other system to create the prompts that gen.py uses, for topics or publications other than Rat News Network.

## Documentation

For more detailed technical information, refer to the following documentation:

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Detailed technical architecture
- [parody.md](docs/parody.md) - Parody system documentation
- [subscribe.md](docs/subscribe.md) - Subscription feature documentation
