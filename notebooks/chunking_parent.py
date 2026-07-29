from __future__ import annotations

import json
import re
from pathlib import Path

from transformers import AutoTokenizer


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
EXTRACTED_DIR = PROJECT_ROOT / "data" / "extracted" / "auto"
CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"

MARKDOWN_PATH = PROCESSED_DIR / "cr.md"
BLOCKPAGE_PATH = EXTRACTED_DIR / "blockpage.json"
PARENT_CHUNKS_PATH = CHUNKS_DIR / "parentchunks2.json"
LARGEST_PARENT_PATH = CHUNKS_DIR / "largest_parent.md"

DOC_ID = "constitution_of_india"
TOKENIZER_MODEL="nomic-ai/nomic-embed-text-v1.5"
# TOKENIZER_MODEL = "BAAI/bge-base-en-v1.5"

HEADING_RE = re.compile(r"^(#{1,6})\s+")
TABLE_RE = re.compile(r"^\|")
SUP_RE = re.compile(r"<sup>.*?</sup>", re.IGNORECASE)


def get_block_type(block: str) -> str:
    block = block.strip()

    if not block:
        return "blank"
    if HEADING_RE.match(block):
        return "heading"
    if TABLE_RE.match(block):
        return "table"
    if SUP_RE.match(block):
        return "sup"
    if block.startswith(("-", "*", "+")):
        return "list"

    return "paragraph"


def extract_heading(block: str) -> dict[str, str | int]:
    match = HEADING_RE.match(block)
    if match is None:
        raise ValueError(f"Block is not a markdown heading: {block[:80]}")

    return {
        "level": len(match.group(1)),
        "text": block[match.end() :].strip(),
    }


def parent_chunk_markdown(md_text: str, blockpage: list[dict]) -> list[dict]:
    search_pos = 0

    def find_heading(heading_text: str) -> dict | None:
        nonlocal search_pos

        for index in range(search_pos, len(blockpage)):
            block = blockpage[index]
            if (
                block.get("type") == "text"
                and block.get("text") == heading_text
                and "text_level" in block
            ):
                search_pos = index + 1
                return block

        return None

    def append_chunk(chunks: list[dict], heading_path: list[str], stack: list[str]) -> None:
        chunks.append(
            {
                "parent_id": f"parent_{len(chunks):04d}",
                "doc_id": DOC_ID,
                "heading_path": heading_path.copy(),
                "text": "\n\n".join(stack),
            }
        )

    parent_chunks: list[dict] = []
    stack: list[str] = []
    heading_path: list[str] = []
    has_text = False

    for raw_block in md_text.split("\n\n"):
        block = raw_block.strip()
        if not block:
            continue

        block_type = get_block_type(block)

        if block_type == "heading":
            if has_text:
                append_chunk(parent_chunks, heading_path, stack)
                stack = []
                heading_path = []
                has_text = False

            heading = extract_heading(block)
            heading_text = str(heading["text"])
            heading_path.append(heading_text)
            find_heading(heading_text)
            stack.append(block)
            continue

        stack.append(block)
        if block_type == "paragraph":
            has_text = True

    if stack:
        append_chunk(parent_chunks, heading_path, stack)

    return parent_chunks


def token_count(tokenizer: AutoTokenizer, text: str) -> int:
    return len(tokenizer.encode(text, add_special_tokens=False))


def main() -> None:
    md_text = MARKDOWN_PATH.read_text(encoding="utf-8")
    with BLOCKPAGE_PATH.open("r", encoding="utf-8") as file:
        blockpage = json.load(file)

    chunks = parent_chunk_markdown(md_text, blockpage)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    PARENT_CHUNKS_PATH.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(len(chunks))
    short_chunks = sum(1 for chunk in chunks if len(chunk["text"]) <= 400)
    print("chunks less or equal to 400", short_chunks)

    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_MODEL)
    lengths = [token_count(tokenizer, chunk["text"]) for chunk in chunks]
    largest_index = max(range(len(lengths)), key=lambda index: lengths[index])

    print(largest_index)
    print(lengths[largest_index])
    print(chunks[largest_index]["heading_path"])

    LARGEST_PARENT_PATH.write_text(chunks[largest_index]["text"], encoding="utf-8")


if __name__ == "__main__":
    main()
