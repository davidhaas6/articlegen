from pathlib import Path
import dotenv

dotenv.load_dotenv()

root = Path(__file__).resolve().parent.parent

DEFAULT_SITE_DIR = root / 'out' / 'site'

DEFAULT_ARTICLE_DIR = root / 'out' / 'articles'

TEMPLATES_DIR = root / 'templates'

PROMPTS_DIR = root / "prompts"