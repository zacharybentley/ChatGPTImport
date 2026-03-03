---
description: Convert ChatGPT overview into Google Gemini Instructions format
---

# Generate Google Gemini Instructions

This workflow converts `inputs/ChatGPT-overview/chatgpt_overview.md` into a plain-text format compatible with Google Gemini's custom instructions.

## Prerequisites

Before running this workflow, make sure `inputs/ChatGPT-overview/chatgpt_overview.md` has content. If it's empty, tell the user to:

1. Run this prompt in ChatGPT:
   ```
   Please give me an easily copy and pasted overview of my chat history and preferences to educate other Al. Please format as markdown
   ```
2. Copy the markdown output and paste it into `inputs/ChatGPT-overview/chatgpt_overview.md`
3. Save the file

## Steps

1. Check that `inputs/ChatGPT-overview/chatgpt_overview.md` exists and is not empty. If empty, provide the prerequisites above and stop.

// turbo
2. Run the conversion script:
```bash
python3 scripts/convert_to_gemini.py
```
Working directory: the project root.

3. Confirm the output files were created in `outputs/` (named `gemini_instructions.txt` or `gemini_instructions_1.txt`, `gemini_instructions_2.txt`, etc.) and report each file's character count.

4. Tell the user how to apply the instructions:
   - Open https://gemini.google.com/app/settings
   - Find "About me" or "Things Gemini should know"
   - If there is one file: paste its contents and save
   - If there are multiple files: create a separate entry for each file (Gemini has a 1,500 character limit per entry and ~10 entry soft limit)
