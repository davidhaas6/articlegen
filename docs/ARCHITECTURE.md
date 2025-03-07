# Rat News Network Architecture

This document provides a technical overview of the Rat News Network (RNN) static site generator, which creates AI-generated satirical news content in the style of news for rats.

## 1. System Overview

The RNN static site generator is a Python-based system that:
- Generates satirical news articles using LLMs (OpenAI's GPT models)
- Creates accompanying images using DALL-E
- Renders content into a static website using Jinja2 templates
- Deploys the site to GitHub Pages via CI/CD

### High-Level Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│   Content   │     │     Site     │     │   GitHub    │     │  Published  │
│ Generation  │────▶│  Generation  │────▶│ Repository  │────▶│   Website   │
│  (gen.py)   │     │(templater.py)│     │ Deployment  │     │             │
└─────────────┘     └──────────────┘     └─────────────┘     └─────────────┘
```

### Core Components

- **deploy.py**: Main entry point that orchestrates the entire pipeline
- **gen.py**: Content generation engine using LLMs
- **templater.py**: Renders content into HTML using Jinja2 templates
- **text_processing.py**: Text utilities for content processing
- **util.py**: General utility functions
- **src/parody.py**: Specialized module for creating parody articles based on real news

## 2. Content Generation Pipeline

The content generation process is handled primarily by `gen.py` and follows these steps:

1. **Idea Generation**: Creates article ideas using LLMs
2. **Article Creation**: Expands ideas into full articles with titles, overviews, and body content
3. **Image Generation**: Creates relevant images using DALL-E
4. **Comments Generation**: Adds simulated user comments to increase engagement
5. **Parody Creation**: Optionally transforms real news articles into rat-themed parodies

### Key Functions in gen.py

- `article_ideas(n)`: Generates n article ideas
- `article_from_idea(idea)`: Creates a complete article from an idea
- `article_image(title, outline)`: Generates an image for an article
- `article_body(idea, outline, num_words)`: Generates the article content
- `new_parody_articles(num)`: Creates parody articles based on real news

### Parody Generation (src/parody.py)

The parody system:
1. Fetches real news articles from external sources
2. Converts HTML to markdown
3. Extracts key content
4. Transforms the content into rat-themed parodies

## 3. Site Generation Process

The site generation is handled by `templater.py` through the `ArticleSiteGenerator` class:

1. **Template Loading**: Loads Jinja2 templates from the templates directory
2. **Content Rendering**: Renders articles into HTML pages
3. **Index Generation**: Creates the homepage with article previews
4. **Asset Management**: Copies and organizes static assets (CSS, JS, images)

### Site Structure

```
site/
├── index.html                # Homepage with article previews
├── [article-id].html         # Individual article pages
├── subscribe.html            # Subscription page
├── qr.html                   # QR code page
└── static/                   # Static assets
    ├── styles.css            # Site styling
    ├── script/               # JavaScript files
    │   ├── news-broadcast.js # News broadcast animation
    │   └── temperature-updater.js # Temperature widget
    └── img/                  # Images including article images
```

### Template System

The templating system uses Jinja2 with a base template (`base.html`) that defines the overall structure, and specialized templates for different page types:
- `article.html`: Individual article pages
- `index.html`: Homepage with article previews
- `subscribe.html`: Subscription options
- `qr.html`: QR code display

## 4. Deployment Pipeline

The deployment process is orchestrated by `deploy.py`:

1. **Content Generation**: Generates articles if requested (`--num` parameter)
2. **Site Building**: Renders the static site using the templating system
3. **Git Operations**: 
   - Clones the target repository
   - Replaces content with newly generated site
   - Commits and pushes changes
4. **CI/CD**: The target repository has CI/CD hooks that publish the content to the web

### Deployment Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Generate   │     │   Render    │     │    Push     │     │   CI/CD     │
│  Articles   │────▶│    Site     │────▶│ to GitHub   │────▶│  Publishes  │
│             │     │             │     │             │     │    Site     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

## 5. Key Components in Detail

### deploy.py

The main entry point that:
- Parses command-line arguments
- Orchestrates article generation
- Manages site building
- Handles GitHub deployment

Key functions:
- `generate_and_push_articles()`: Main pipeline function
- `git_deploy()`: Handles Git operations
- `auth_repo_url()`: Manages GitHub authentication

### gen.py

The content generation engine that:
- Creates article ideas
- Generates full articles
- Produces images
- Manages parody content

Key classes:
- `ArticleIdea`: Represents an article concept
- `ParodyIdea`: Specialized idea for parody articles

### templater.py

The site generation system that:
- Renders templates
- Manages static assets
- Creates the site structure

Key class:
- `ArticleSiteGenerator`: Handles the entire site generation process

### text_processing.py

Utilities for text manipulation:
- `estimate_reading_time()`: Calculates article reading time
- `markdown_to_html()`: Converts markdown to HTML

## 6. Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for LLM and image generation
- `GITHUB_PAT`: GitHub Personal Access Token for deployment
- `NEWS_API_KEY`: Used for fetching real news for parody articles

### Prompt Templates

Located in the `prompts/` directory:
- `system.yaml`: System prompts for LLMs
- `article.yaml`: Article generation prompts
- `ideas.yaml`: Idea generation prompts
- `images.yaml`: Image generation prompts
- `parody.yaml`: Parody generation prompts

## 7. Testing Strategy

The project includes unit tests for key components:

- `tests/test_deploy.py`: Tests for the deployment pipeline
- `tests/test_parody.py`: Tests for the parody generation system

The testing approach uses:
- Mock objects for external dependencies
- Isolated component testing
- Exception handling verification

## 8. Future Development

As mentioned in the README, planned features include:
- Generating non-RNN content using the same pipeline
- Creating custom prompt systems for different publications or topics
- Expanding the parody system to cover more news sources

## 9. Technical Considerations

- **Performance**: Article generation is parallelized using Python's multiprocessing
- **Error Handling**: Robust error handling throughout the pipeline
- **Modularity**: Clear separation of concerns between components
- **Extensibility**: Designed to be extended for different content types
