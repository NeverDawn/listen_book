import hashlib
import re

SENTENCE_END_RE = re.compile(
    r"([^\u3002\uff01\uff1f!?]+[\u3002\uff01\uff1f!?]+[\"\u201d\u2019\u300d\u300f\u300b\u3011\uff09)]*)"
)


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(line for line in lines if line)


def split_paragraphs(text: str) -> list[str]:
    normalized = normalize_text(text)
    return [part.strip() for part in re.split(r"\n{1,}", normalized) if part.strip()]


def split_sentences(paragraph: str) -> list[str]:
    sentences: list[str] = []
    last_end = 0
    for match in SENTENCE_END_RE.finditer(paragraph):
        if match.start() > last_end:
            prefix = paragraph[last_end : match.start()].strip()
            if prefix:
                sentences.append(prefix)
        sentences.append(match.group(1).strip())
        last_end = match.end()

    tail = paragraph[last_end:].strip()
    if tail:
        sentences.append(tail)
    return [sentence for sentence in sentences if sentence]


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
