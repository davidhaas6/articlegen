import re


def count_syllables(word):
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
        count += 1
    if count == 0:
        count += 1
    return count


def count_sentences(text):
    # More robust sentence counting
    return len(
        re.findall(
            r"\w+[.!?](?:\s|$)(?<![A-Z][a-z]\.)(?<!Mr\.)(?<!Mrs\.)(?<!Ms\.)(?<!Dr\.)",
            text,
        )
    )


def estimate_reading_time(text, words_per_minute=200):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input must be a non-empty string")

    # Method 1: Word count
    words = text.split()
    word_count = len(words)
    word_count_estimate = word_count / words_per_minute

    # Method 3: Flesch-Kincaid
    sentences = count_sentences(text)
    syllables = sum(count_syllables(word) for word in words)

    if sentences == 0 or word_count == 0:
        flesch_reading_ease = 0
        flesch_kincaid_grade = 0
    else:
        flesch_reading_ease = (
            206.835 - 1.015 * (word_count / sentences) - 84.6 * (syllables / word_count)
        )
        flesch_kincaid_grade = (
            0.39 * (word_count / sentences) + 11.8 * (syllables / word_count) - 15.59
        )

    # Adjust word count estimate based on Flesch-Kincaid Grade Level
    fk_adjusted_estimate = word_count_estimate * (
        1 + max(0, flesch_kincaid_grade) / 100
    )

    return fk_adjusted_estimate


# Example usage


def markdown_to_html(text: str) -> str:
    # Convert headers to h1, h2, h3 based on the number of #s
    text = re.sub(
        r"^(#{1,6})\s(.+)$",
        lambda m: f"<h{len(m.group(1))}>{m.group(2)}</h{len(m.group(1))}>",
        text,
        flags=re.MULTILINE,
    )

    # Convert **bold** to <strong>bold</strong>
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    # Convert *italic* to <em>italic</em>
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)

    # Convert line breaks to <br>
    text = text.replace("\n", "<br>")
    text = text.replace("</h3><br><br>", "</h3>")

    # Convert --- to <hr>
    text = re.sub(r"---", "<hr>", text)

    return text


if __name__ == "__main__":
    main()
