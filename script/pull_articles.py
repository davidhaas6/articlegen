import json
import glob
from pathlib import Path

PARENT_DIR = (Path(__file__).parent / "..").resolve()

def getArticleText(article):
    return f'# {article["title"]}\n\n_{article["overview"]}_\n\n{article["body"]}'


def main():
    output_dir = Path("out/textDataset/")
    output_dir.mkdir(parents=True, exist_ok=True)


    print((PARENT_DIR / "out/articles/**/*.json").as_posix() )
    files = glob.glob( (PARENT_DIR / "out/articles/**/*.json").as_posix(), recursive=True )
    corpus = []
    for file in files:
        with open(file, "r") as f:
            text = getArticleText(json.load(f))
            corpus.append(text)

        filename = Path(file).name.replace('.json', '.txt')
        with open(output_dir / filename, "w", encoding="utf-8") as f:
            f.write(text)


    all_articles = '\n\n---\n\n'.join(corpus)
    with open(output_dir / "_all_articles.txt", "w", encoding="utf-8") as f:
        f.write(all_articles)
    print(len(corpus))

    # process data

if __name__ == "__main__":
    main()
