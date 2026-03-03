---
description: Extract and summarize ChatGPT conversation history from JSON files
---

# Extract ChatGPT Summary

This workflow runs the extract_summary.py script to parse all conversation JSON files in `ChatGPT-Conversations/` and generate a categorized summary.

## Steps

1. Verify that `inputs/ChatGPT-Conversations/` contains at least one `conversations-*.json` file. If not, tell the user to place their exported ChatGPT conversation JSON files in that folder first.

// turbo
2. Run the extraction script:
```bash
python3 scripts/extract_summary.py
```
Working directory: the project root.

3. Confirm the output file was created at `outputs/chatgpt_summary.md` and report the file size and number of conversations parsed.

4. Ask the user: "Would you like me to read the summary and save key findings (personal details, tech stack, interests, work projects, preferences) as Cascade memories?" If they say yes, read `outputs/chatgpt_summary.md` and create categorized memories covering: personal identity, family/relationships, location, professional role, technical skills, hobbies/interests, personality/communication style, and any active projects.
