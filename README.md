# ChatGPT History Import & AI Memory Tools

A toolkit for extracting, summarizing, and porting your ChatGPT conversation history to other AI platforms.

---

## Prerequisites

- **Python 3.8+** (no external dependencies required)
- Your ChatGPT data export (conversation JSON files)

---

## Project Structure

```
ChatGPTImport/
├── README.md                        # You are here
├── inputs/
│   ├── ChatGPT-Conversations/       # Your exported conversation files
│   │   ├── chat.html               # Static HTML viewer (not used by scripts)
│   │   ├── conversations-000.json
│   │   ├── conversations-001.json
│   │   └── ...
│   └── ChatGPT-overview/
│       └── chatgpt_overview.md      # Your AI-generated overview (from ChatGPT)
├── scripts/
│   ├── extract_summary.py           # Parses conversation JSONs into a summary
│   └── convert_to_gemini.py         # Converts overview into Google Gemini Instructions
├── outputs/
│   ├── chatgpt_summary.md           # Generated conversation summary
│   └── gemini_instructions.txt      # Generated Gemini Instructions
└── .windsurf/
    └── workflows/                   # Windsurf slash command workflows
        ├── extract-summary.md
        └── generate-gemini-instructions.md
```

---

## Step 1: Export Your ChatGPT Data

1. Go to [ChatGPT Settings > Data Controls > Export Data](https://chatgpt.com/#settings/DataControls)
2. Request and download your export
3. Extract the ZIP file
4. Place your `conversations-*.json` files and `chat.html` into `inputs/ChatGPT-Conversations/`

---

## Step 2: Generate Conversation Summary

This script parses all your conversation JSON files and produces a categorized markdown summary including conversation titles, topics, tech keywords, monthly activity, and personal details.

```bash
python3 scripts/extract_summary.py
```

**Output:** `outputs/chatgpt_summary.md`

The summary includes:
- Total conversation and message counts
- Models used and date range
- Technology keywords mentioned
- Top words from your messages
- All conversation titles organized by month with first messages
- Potential personal details extracted from your messages

---

## Step 3: Generate Your AI Overview (via ChatGPT)

Use this prompt in ChatGPT to generate a portable overview of your preferences and history:

> **Prompt to use in ChatGPT:**
>
> ```
> Please give me an easily copy and pasted overview of my chat history and preferences to educate other Al. Please format as markdown
> ```

Once ChatGPT generates the overview:

1. Copy the full markdown output
2. Paste it into **`inputs/ChatGPT-overview/chatgpt_overview.md`**
3. Save the file

This file serves as the source of truth for porting your preferences to other AI platforms.

---

## Step 4: Port to Google Gemini

Convert your ChatGPT overview into a format compatible with Google Gemini's custom instructions.

### Gemini Constraints

- **1,500 character limit** per instruction entry (hard UI limit — exceeding this causes a POST error)
- **~10 logic blocks** soft limit — if you have 20+ bullet points, Gemini drops the middle ones
- Use **consistent Markdown** (## headers + bullets) — don't mix with XML tags
- Gemini 3 responds best to a **hierarchical structure**: Identity → Stack → Protocol → Constraints → Context

The conversion script handles all of this automatically, splitting into multiple files if needed.

### 4a. Generate the Gemini Instructions file(s)

```bash
python3 scripts/convert_to_gemini.py
```

**Output:** `outputs/gemini_instructions.txt` (single file) or `outputs/gemini_instructions_1.txt`, `gemini_instructions_2.txt`, etc. (if content exceeds 1,500 chars)

### 4b. Paste into Gemini

1. Open [Gemini Settings](https://gemini.google.com/app/settings)
2. Find **"About me"** or **"Things Gemini should know"**
3. If there is **one file**: paste its contents and save
4. If there are **multiple files**: create a separate entry for each file, pasting one per entry

### 4c. Alternative: Use ChatGPT to Format Directly

If you prefer, you can also ask ChatGPT to reformat the overview for Gemini in one step. Use this prompt in ChatGPT with your `inputs/ChatGPT-overview/chatgpt_overview.md` content:

> **Prompt to use in ChatGPT:**
>
> ```
> Please format chatgpt_overview.md into a format that works with and can be pasted into Google Gemini Instructions
> ```

Then paste the result into Gemini Settings as described above.

---

## Step 5: Port to Claude

Claude has a built-in memory import feature. No conversion needed.

1. Go to **[claude.com/import-memory](https://claude.com/import-memory)**
2. Follow the prompts to import your conversation history and preferences directly

---

## Step 6: Port to Windsurf / Cascade

For Windsurf's Cascade AI, memories are stored automatically during conversations. To bulk-import context from your ChatGPT history:

1. Open this project in Windsurf
2. Ask Cascade to read `outputs/chatgpt_summary.md` and/or `inputs/ChatGPT-overview/chatgpt_overview.md`
3. Ask it to save the relevant information as memories

---

## Windsurf Workflows

If you're using this project in Windsurf, two workflows are available as slash commands:

| Command | Description |
|---|---|
| `/extract-summary` | Parses all conversation JSONs and generates the summary |
| `/generate-gemini-instructions` | Converts `inputs/ChatGPT-overview/chatgpt_overview.md` into Gemini Instructions format |

Just type the command in Cascade's chat to run the full workflow.

---

## Quick Reference

| Platform | Method |
|---|---|
| **ChatGPT** | Already has your history — generate the overview with the prompt above |
| **Google Gemini** | Run `scripts/convert_to_gemini.py` → paste into Gemini Settings |
| **Claude** | Use [claude.com/import-memory](https://claude.com/import-memory) |
| **Windsurf / Cascade** | Open project in Windsurf, ask Cascade to memorize the summary |
