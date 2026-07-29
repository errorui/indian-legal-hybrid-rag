# import re

# HEADING_RE = re.compile(r"^(#{1,6})\s+")
# TABLE_RE = re.compile(r"^\|")
# SUP_RE = re.compile(r"<sup>.*?</sup>", re.IGNORECASE)
# with open("cr.md", "r", encoding="utf-8") as f:
#     data = f.read()

# def get_block_type(block: str):
#     """Return the block type."""

#     block = block.strip()

#     if not block:
#         return "blank"

#     if HEADING_RE.match(block):
#         return "heading"

#     if TABLE_RE.match(block):
#         return "table"

#     if SUP_RE.match(block):
#         return "sup"

#     if block.startswith(("-", "*", "+")):
#         return "list"

#     return "paragraph"


# def parent_chunk_markdown(md_text: str):
#     """
#     Parent chunking based on:

#     - Push everything into current stack.
#     - Once a paragraph appears, has_text=True.
#     - Next heading => emit entire stack.
#     """

#     blocks = md_text.split("\n\n")

#     stack = []
#     has_text = False
#     parent_chunks = []

#     for block in blocks:
#         block = block.strip()

#         if not block:
#             continue

#         block_type = get_block_type(block)

#         if block_type == "heading":

#             if has_text:
#                 parent_chunks.append("\n\n".join(stack))

#                 stack = []
#                 has_text = False

#             stack.append(block)

#         else:
#             stack.append(block)

#             if block_type == "paragraph":
#                 has_text = True

#     if stack:
#         parent_chunks.append("\n\n".join(stack))

#     return parent_chunks

# import json

# chunks = parent_chunk_markdown(data)

# with open("parentchunks.json", "w", encoding="utf-8") as f:
#     json.dump(chunks, f, ensure_ascii=False, indent=2)
# print(parent_chunk_markdown(data)[7])

import re
import json

HEADING_RE = re.compile(r"^(#{1,6})\s+")
TABLE_RE = re.compile(r"^\|")
SUP_RE = re.compile(r"<sup>.*?</sup>", re.IGNORECASE)

# -----------------------------
# Read files
# -----------------------------
with open("cr.md", "r", encoding="utf-8") as f:
    data = f.read()

with open("blockpage.json", "r", encoding="utf-8") as f:
    blockpage = json.load(f)

# -----------------------------
# Block detection
# -----------------------------
def get_block_type(block: str):
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


def extract_heading(block):
    m = HEADING_RE.match(block)
    return {
        "level": len(m.group(1)),
        "text": block[m.end():].strip()
    }


# -----------------------------
# Sequential heading lookup
# -----------------------------
search_pos = 0


def find_heading(blocks, heading_text):
    global search_pos

    for i in range(search_pos, len(blocks)):
        block = blocks[i]

        if (
            block.get("type") == "text"
            and block.get("text") == heading_text
            and "text_level" in block
        ):
            search_pos = i + 1
            return block

    return None


# -----------------------------
# Parent Chunking
# -----------------------------
def parent_chunk_markdown(md_text, blockpage):

    global search_pos
    search_pos = 0

    blocks = md_text.split("\n\n")

    stack = []

    # persistent hierarchy
    heading_path = []

    has_text = False

    page_start = None
    page_end = None

    parent_chunks = []

    for block in blocks:

        block = block.strip()

        if not block:
            continue

        block_type = get_block_type(block)

        # ----------------- Heading -----------------

        if block_type == "heading":

            # Close previous chunk
            if has_text:

                parent_chunks.append({
    "parent_id": f"parent_{len(parent_chunks):04d}",
    "doc_id": "constitution_of_india",
    "heading_path": heading_path.copy(),
    "text": "\n\n".join(stack)
})

                stack = []
                heading_path = []      # reset for new parent
                has_text = False
                page_start = None
                page_end = None

            h = extract_heading(block)
            # print(h)
            # print(type(h))
            heading_path.append(h['text'])

            # Find page from blockpage.json
            meta = find_heading(blockpage, h["text"])

            if meta:

                if page_start is None:
                    page_start = meta["page_idx"]

                page_end = meta["page_idx"]

            stack.append(block)

        # ----------------- Other Blocks -----------------

        else:

            stack.append(block)

            if block_type == "paragraph":
                has_text = True

    # Last chunk
    if stack:
        parent_chunks.append({
    "parent_id": f"parent_{len(parent_chunks):04d}",
    "doc_id": "constitution_of_india",
    "heading_path": heading_path.copy(),
    "text": "\n\n".join(stack)
})

    return parent_chunks


# -----------------------------
# Run
# -----------------------------
chunks = parent_chunk_markdown(data, blockpage)
print(len(chunks))
cnt=0
for i in chunks:
    if len(i["text"])<=400:
        cnt+=1
print("chunks less or equal to 400",cnt)

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-base-en-v1.5")

def token_count(text: str) -> int:
    return len(tokenizer.encode(text, add_special_tokens=False))
# lengths = [token_count(p["text"]) for p in chunks]

# print(f"Min: {min(lengths)}")
# print(f"Max: {max(lengths)}")
# print(f"Mean: {sum(lengths)/len(lengths):.1f}")
parents=chunks
lengths = [token_count(p["text"]) for p in parents]

idx = max(range(len(lengths)), key=lambda i: lengths[i])

print(idx)
print(lengths[idx])
print(parents[idx]["heading_path"])

with open("largest_parent.md", "w", encoding="utf-8") as f:
    f.write(parents[idx]["text"])