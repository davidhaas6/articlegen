# Rat News Network Generator: Repository Summary

The **Rat News Network (RNN) Generator** is an AI-powered static site generator that creates satirical news content themed around rats. It leverages OpenAI's GPT models for text generation and DALL-E for image creation, automating the entire pipeline from idea generation to deployment on GitHub Pages.

## 🏗️ System Architecture

The project follows a modular pipeline-based architecture:

```mermaid
graph LR
    A[Content Generation<br/>gen.py] --> B[Site Generation<br/>templater.py]
    B --> C[Deployment<br/>deploy.py]
    C --> D[GitHub Pages]
```

## 📂 Core Components

### 1. Orchestration & Deployment (`src/deploy.py`)
- **Main Entry Point**: Manages the end-to-end process of generating articles and pushing them to a static site repository.
- **Git Integration**: Clones the target frontend repo, replaces content with the new build, and pushes changes.
- **Feed Generation**: Triggers RSS (`feed.xml`) and Sitemap (`sitemap.xml`) generation after the site is built.

### 2. Content Generation (`src/gen.py`)
- **Parallel Processing**: Uses Python's `multiprocessing` to generate multiple articles simultaneously.
- **LLM Pipeline**: 
    - **Ideas**: Generates witty rat-themed article concepts.
    - **Outlines**: Structures the article flow.
    - **Body**: Writes the full satirical text using customized prompts.
    - **Images**: A specialized two-step brainstorming process to create high-quality DALL-E prompts.
    - **Comments**: Simulates a "rat community" discussion under articles.

### 3. Parody System (`src/parody.py`)
- **Real News Transformation**: Fetches real-world headlines via News API and transforms them into rat-themed satirical "Breaking News."
- **Extraction**: Uses `MarkItDown` and LLMs to clean up raw HTML/Markdown from news sources before transformation.

### 4. Site Generation & Templating (`src/templater.py`)
- **Jinja2 Templates**: Uses a robust templating system to render HTML.
- **Edition-based Archiving**: Groups articles by date into "Editions" and maintains an archive of past news.
- **Data Processing**: Imputes missing metadata like reading time (calculated in `text_processing.py`).

### 5. Utilities & Builders
- **`rss_build.py`**: Constructs a standards-compliant RSS feed.
- **`sitemap_generator.py`**: Scans the output directory to build an XML sitemap with custom priorities.
- **`text_processing.py`**: Contains syllable counters, reading time estimators, and a custom Markdown-to-HTML converter.
- **`util.py`**: Handles image downloading and WebP compression.

## 🛠️ Key Features
- **Highly Automated**: Can be run in `--auto` mode for CI/CD environments.
- **Prompt-Driven**: All LLM behaviors are configured via YAML templates in the `prompts/` directory.
- **SEO Optimized**: Automatically generates sitemaps and structured metadata.
- **Interactive Parody**: Allows users to confirm topic selections before generating parody articles in CLI mode.

## 🚀 Usage
The system is typically invoked via:
```bash
python deploy.py --num 5 --branch main
```
This single command generates 5 articles (including parodies) and deploys them to the specified branch.