from pathlib import Path
import dotenv

if not dotenv.load_dotenv(".env"):
    print("WARNING: Could not load env file")

root = Path(__file__).resolve().parent.parent

DEFAULT_SITE_DIR = root / 'out' / 'site'

DEFAULT_ARTICLE_DIR = root / 'out' / 'articles'

TEMPLATES_DIR = root / 'templates'

PROMPTS_DIR = root / "prompts"