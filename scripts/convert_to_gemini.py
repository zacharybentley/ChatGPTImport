#!/usr/bin/env python3
"""
Convert chatgpt_overview.md into Google Gemini Instructions format.

Gemini Constraints (as of late 2025 / early 2026):
  - 1,500 character limit per instruction entry (hard UI limit).
  - ~10 distinct logic blocks before middle rules get dropped.
  - Use consistent Markdown formatting (## headers + bullets).
  - Hierarchical structure works best: Identity → Stack → Protocol → Constraints → Context.

This script parses the ChatGPT overview markdown and maps it into Gemini's
optimized "Hierarchical Context" format, then splits into multiple files
if the content exceeds 1,500 characters per entry.

Usage:
    python3 scripts/convert_to_gemini.py

Input:  inputs/ChatGPT-overview/chatgpt_overview.md
Output: outputs/gemini_instructions_1.txt, outputs/gemini_instructions_2.txt, ...
"""

import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
INPUT_FILE = os.path.join(PROJECT_ROOT, "inputs", "ChatGPT-overview", "chatgpt_overview.md")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs")
CHAR_LIMIT = 1500


def read_overview():
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: {INPUT_FILE} not found.")
        print("Please create chatgpt_overview.md first. See README.md for instructions.")
        exit(1)

    with open(INPUT_FILE, "r") as f:
        content = f.read().strip()

    if not content:
        print(f"ERROR: {INPUT_FILE} is empty.")
        print("Please paste your ChatGPT overview into chatgpt_overview.md first.")
        exit(1)

    return content


def strip_md(text):
    """Remove bold, inline code, and other markdown formatting."""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    return text.strip()


def parse_sections(md_content):
    """Parse markdown into a dict of {section_title: [lines]}."""
    sections = {}
    current_section = None
    current_lines = []

    for line in md_content.split("\n"):
        stripped = line.strip()

        if not stripped or stripped == "---":
            continue

        # Top-level heading — skip
        if stripped.startswith("# ") and not stripped.startswith("## "):
            continue

        # H2 — new section
        if stripped.startswith("## "):
            if current_section:
                sections[current_section] = current_lines
            current_section = stripped.lstrip("# ").strip()
            current_lines = []
            continue

        # H3 — subsection label
        if stripped.startswith("### "):
            label = stripped.lstrip("# ").strip()
            current_lines.append(f"  {label}:")
            continue

        # Bullet points
        if stripped.startswith("- "):
            content = strip_md(stripped[2:])
            indent = len(line) - len(line.lstrip())
            prefix = "    - " if indent >= 4 else "- "
            current_lines.append(f"{prefix}{content}")
            continue

        # Plain text
        current_lines.append(strip_md(stripped))

    if current_section:
        sections[current_section] = current_lines

    return sections


def map_to_gemini_blocks(sections):
    """
    Map parsed sections into Gemini's optimized hierarchical blocks.

    Gemini 3 responds best to this order:
      1. IDENTITY & ROLE
      2. TECHNICAL STACK
      3. COMMUNICATION PROTOCOL
      4. CONSTRAINTS & STANDARDS
      5. INTERESTS (CONTEXT)
    """
    # Define mapping: gemini_block_name -> list of source section keys to pull from
    block_mapping = [
        ("IDENTITY & ROLE", [
            "Name / Handle",
        ]),
        ("TECHNICAL STACK", [
            "Professional & Technical Focus",
        ]),
        ("COMMUNICATION PROTOCOL", [
            "How Zach Likes to Work With AI",
        ]),
        ("CONSTRAINTS & STANDARDS", [
            "Key Expectations for Any AI Assisting Zach",
        ]),
        ("PROJECTS & DESIGN", [
            "Personal & Creative Projects",
        ]),
        ("INTERESTS (CONTEXT)", [
            "Miscellaneous Interests",
        ]),
    ]

    blocks = []
    used_sections = set()

    for block_name, source_keys in block_mapping:
        block_lines = [f"## {block_name}"]
        has_content = False

        for key in source_keys:
            for section_name, lines in sections.items():
                if key.lower() in section_name.lower():
                    block_lines.extend(lines)
                    used_sections.add(section_name)
                    has_content = True

        if has_content:
            blocks.append("\n".join(block_lines))

    # Catch any unmapped sections
    for section_name, lines in sections.items():
        if section_name not in used_sections:
            block_lines = [f"## {section_name.upper()}"]
            block_lines.extend(lines)
            blocks.append("\n".join(block_lines))

    return blocks


def chunk_blocks(blocks, limit=CHAR_LIMIT):
    """
    Group blocks into chunks that each fit within the character limit.
    Each block stays intact — we never split a single block across files.
    If a single block exceeds the limit, it gets its own file.
    """
    chunks = []
    current_chunk = []
    current_size = 0

    for block in blocks:
        block_size = len(block)
        separator_size = 2 if current_chunk else 0  # "\n\n" between blocks

        if current_chunk and (current_size + separator_size + block_size) > limit:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [block]
            current_size = block_size
        else:
            current_chunk.append(block)
            current_size += separator_size + block_size

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Reading: {INPUT_FILE}")
    md_content = read_overview()

    print("Parsing sections...")
    sections = parse_sections(md_content)
    print(f"  Found {len(sections)} sections: {', '.join(sections.keys())}")

    print("Mapping to Gemini hierarchical blocks...")
    blocks = map_to_gemini_blocks(sections)
    print(f"  Generated {len(blocks)} blocks")

    print(f"Chunking to ≤{CHAR_LIMIT} characters per entry...")
    chunks = chunk_blocks(blocks)
    print(f"  Split into {len(chunks)} file(s)")

    # Clean up old output files
    for f in os.listdir(OUTPUT_DIR):
        if f.startswith("gemini_instructions") and f.endswith(".txt"):
            os.remove(os.path.join(OUTPUT_DIR, f))

    # Write chunks
    output_files = []
    for i, chunk in enumerate(chunks, 1):
        suffix = f"_{i}" if len(chunks) > 1 else ""
        filename = f"gemini_instructions{suffix}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w") as f:
            f.write(chunk)
        output_files.append(filename)
        print(f"  {filename}: {len(chunk)} chars")

    print(f"\nOutput written to: outputs/")
    for fname in output_files:
        print(f"  - {fname}")

    print()
    print("To use:")
    print("  1. Open https://gemini.google.com/app/settings")
    print("  2. Under 'About me' or 'Things Gemini should know'")
    if len(chunks) == 1:
        print(f"  3. Paste the contents of outputs/{output_files[0]}")
        print("  4. Save")
    else:
        print("  3. Create a separate entry for each file:")
        for fname in output_files:
            print(f"       - Paste contents of outputs/{fname} → Save as entry")
        print(f"  4. You will have {len(chunks)} entries total")

    print()
    print(f"Gemini limits: ≤{CHAR_LIMIT} chars/entry, ≤10 logic blocks total.")
    if len(chunks) > 10:
        print("  ⚠ WARNING: You have more than 10 entries. Gemini may drop middle rules.")


if __name__ == "__main__":
    main()
