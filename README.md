# Rat News Network Generator
A static site generator that creates content with LLMs instead of humans.

# Future vision
 - Generating non-RNN content 
   - i.e. use some other system to create the prompts that gen.py uses, for topics or publications other than Rat News Network.
 - 

# deploy.py Usage Instructions
## Command Structure
The main command to use this static site generator is:

```
python deploy.py [options]
```

## Deploy Options
- `--num`: Number of articles to generate (default is 0)
- `--articles`: Directory to save or load articles
- `--branch`: Branch to deploy to (default is 'main')
- `--repo`: URL of the repository to deploy to (default is https://github.com/davidhaas6/rat-news-network-frontend.git)
- `--keep-local`: Keep the local repository after deployment (flag, no value needed)

## Deploy Usage Examples

### 1. Generate and Deploy New Articles
To generate three new articles and push them to the 'test' branch of the default repository:

```
python deploy.py --num 3 --branch test
```

### 2. Deploy Existing Articles
To push existing articles from a specific directory to the 'test' branch:

```
python deploy.py --articles my/article/dir/ --branch test
```

### 3. Deploy to a Different Repository
To generate three articles and deploy them to a different repository:

```
python deploy.py --num 3 --repo https://github.com/username/rat-news-network-frontend.git
```

## Notes
- If `--num` is set to 0, the script will use existing articles from the specified `--articles` directory.
- The `--keep-local` flag can be added to any command to retain the local copy of the repository after deployment.
- Always ensure you have the necessary permissions for the target repository before deploying.


## Environment variables that should be set
export GITHUB_PAT = "Your Github's personal access token. Used for automated deployment."
export OPENAI_API_KEY = "this is what it sounds like"


# gen.py Usage Instructions

gen.py is the core content generation script in the AI-Powered Static Site Generator. It provides several functions for generating different parts of an article or complete articles.

## Command Structure
```
python gen.py [action] [parameters]
```

## Actions and Parameters

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

## Examples

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

## Notes
- The script uses OpenAI's GPT models for text generation and DALL-E 3 for image generation.
- Generated articles are saved as JSON files in the output directory.
- Image URLs are included in the article JSON data.
- The script requires proper setup of API keys for OpenAI services.

