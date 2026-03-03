#!/usr/bin/env python3
"""
Extract and summarize ChatGPT conversation history into a structured profile.
Parses all conversations-*.json files and produces a categorized summary.
"""

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BASE_DIR = os.path.join(PROJECT_ROOT, "inputs", "ChatGPT-Conversations")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "chatgpt_summary.md")


def load_all_conversations():
    convos = []
    for fname in sorted(os.listdir(BASE_DIR)):
        if fname.startswith("conversations-") and fname.endswith(".json"):
            with open(os.path.join(BASE_DIR, fname)) as f:
                convos.extend(json.load(f))
    return convos


def extract_messages(convo):
    """Walk the mapping tree and return ordered list of (role, text) tuples."""
    messages = []
    mapping = convo.get("mapping", {})
    for node_id, node in mapping.items():
        msg = node.get("message")
        if not msg:
            continue
        role = msg["author"]["role"]
        parts = msg.get("content", {}).get("parts", [])
        text_parts = []
        for p in parts:
            if isinstance(p, str) and p.strip():
                cleaned = p.strip().replace("\u2028", " ").replace("\u2029", "\n")
                text_parts.append(cleaned)
        if text_parts:
            messages.append({
                "role": role,
                "text": "\n".join(text_parts),
                "time": msg.get("create_time"),
            })
    messages.sort(key=lambda m: m["time"] or 0)
    return messages


def ts_to_date(ts):
    if ts:
        try:
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
        except:
            pass
    return "unknown"


def ts_to_month(ts):
    if ts:
        try:
            return datetime.fromtimestamp(ts).strftime("%Y-%m")
        except:
            pass
    return "unknown"


def main():
    convos = load_all_conversations()
    print(f"Loaded {len(convos)} conversations")

    # ---- Collect stats ----
    titles = []
    models = Counter()
    origins = Counter()
    months = Counter()
    all_user_messages = []
    all_assistant_messages = []
    convo_summaries = []

    for convo in convos:
        title = convo.get("title", "Untitled")
        model = convo.get("default_model_slug", "unknown")
        origin = convo.get("conversation_origin", "unknown")
        create_time = convo.get("create_time")

        titles.append(title)
        models[model] += 1
        origins[origin] += 1
        months[ts_to_month(create_time)] += 1

        messages = extract_messages(convo)
        user_msgs = [m["text"] for m in messages if m["role"] == "user"]
        assistant_msgs = [m["text"] for m in messages if m["role"] == "assistant"]

        all_user_messages.extend(user_msgs)
        all_assistant_messages.extend(assistant_msgs)

        # Build per-conversation summary
        first_user = user_msgs[0][:300] if user_msgs else ""
        convo_summaries.append({
            "title": title,
            "date": ts_to_date(create_time),
            "model": model,
            "origin": origin,
            "num_user_msgs": len(user_msgs),
            "num_assistant_msgs": len(assistant_msgs),
            "first_user_msg": first_user,
        })

    # ---- Keyword / topic extraction (simple word frequency on user messages) ----
    # Combine all user messages
    all_user_text = " ".join(all_user_messages).lower()
    # Extract meaningful words (3+ chars, skip common stop words)
    stop_words = set(
        "the and for are but not you all any can had her was one our out day get has him his how its may "
        "new now old see way who did got let say she too use what with this that from have will been each "
        "than them then some could other into more also back just only come made over such take than very "
        "after before being below between down during here there these those through under where which while "
        "about would their first after again most know when even your just like does don doing should because "
        "really think going right well still want need make sure thing things going".split()
    )
    words = re.findall(r'\b[a-z]{3,}\b', all_user_text)
    word_freq = Counter(w for w in words if w not in stop_words)

    # ---- Detect personal info patterns in user messages ----
    personal_patterns = {
        "name_mentions": [],
        "location_mentions": [],
        "work_mentions": [],
        "tech_mentions": [],
        "hobby_mentions": [],
    }

    tech_keywords = [
        "python", "javascript", "typescript", "react", "node", "nextjs", "next.js",
        "angular", "vue", "svelte", "tailwind", "css", "html", "sql", "postgres",
        "mongodb", "redis", "docker", "kubernetes", "aws", "azure", "gcp", "firebase",
        "swift", "kotlin", "java", "csharp", "c#", ".net", "dotnet", "rust", "golang",
        "flutter", "django", "flask", "fastapi", "express", "nest", "spring",
        "git", "github", "gitlab", "vercel", "netlify", "heroku",
        "openai", "chatgpt", "gpt", "llm", "api", "rest", "graphql",
        "linux", "macos", "windows", "ios", "android",
        "raspberry", "arduino", "terraform", "jenkins", "ci/cd",
        "wordpress", "shopify", "stripe", "twilio", "supabase", "prisma",
        "tailwindcss", "shadcn", "vite", "webpack", "babel", "eslint",
    ]

    tech_freq = Counter()
    for msg in all_user_messages:
        msg_lower = msg.lower()
        for kw in tech_keywords:
            if kw in msg_lower:
                tech_freq[kw] += 1

    # ---- Write output ----
    with open(OUTPUT_FILE, "w") as out:
        out.write("# ChatGPT History Summary\n\n")
        out.write(f"**Total Conversations:** {len(convos)}\n")
        out.write(f"**Total User Messages:** {len(all_user_messages)}\n")
        out.write(f"**Total Assistant Messages:** {len(all_assistant_messages)}\n\n")

        # Date range
        sorted_months = sorted(months.keys())
        if sorted_months:
            out.write(f"**Date Range:** {sorted_months[0]} to {sorted_months[-1]}\n\n")

        # Models used
        out.write("## Models Used\n\n")
        for model, count in models.most_common():
            out.write(f"- **{model}**: {count} conversations\n")
        out.write("\n")

        # Origins
        out.write("## Conversation Origins\n\n")
        for origin, count in origins.most_common():
            out.write(f"- **{origin}**: {count}\n")
        out.write("\n")

        # Monthly activity
        out.write("## Monthly Activity\n\n")
        for month in sorted(months.keys()):
            out.write(f"- **{month}**: {months[month]} conversations\n")
        out.write("\n")

        # Tech stack
        out.write("## Technology Keywords Mentioned\n\n")
        for tech, count in tech_freq.most_common(40):
            if count >= 2:
                out.write(f"- **{tech}**: {count} mentions\n")
        out.write("\n")

        # Top words (interests)
        out.write("## Top Words in Your Messages (interests/topics)\n\n")
        for word, count in word_freq.most_common(80):
            if count >= 5:
                out.write(f"- **{word}**: {count}\n")
        out.write("\n")

        # All conversation titles grouped by month
        out.write("## All Conversation Titles (by date)\n\n")
        by_month = defaultdict(list)
        for cs in convo_summaries:
            month = cs["date"][:7] if cs["date"] != "unknown" else "unknown"
            by_month[month].append(cs)

        for month in sorted(by_month.keys()):
            out.write(f"### {month}\n\n")
            for cs in sorted(by_month[month], key=lambda x: x["date"]):
                out.write(f"- **{cs['title']}** ({cs['date']}, {cs['model']})\n")
                if cs["first_user_msg"]:
                    preview = cs["first_user_msg"][:150].replace("\n", " ")
                    out.write(f"  - First message: _{preview}_\n")
            out.write("\n")

        # Extract user messages that mention personal details
        out.write("## Potential Personal Details (messages mentioning 'I am', 'I work', 'my name', 'I live', 'my job', etc.)\n\n")
        personal_keywords = [
            "i am ", "i'm ", "my name", "i work", "i live", "my job", "my wife",
            "my husband", "my kids", "my son", "my daughter", "my dog", "my cat",
            "my car", "my house", "my apartment", "i moved", "my company",
            "my team", "my boss", "my salary", "i graduated", "my degree",
            "my school", "my college", "my university", "i started", "my project",
            "my business", "i bought", "my favorite", "i prefer", "i hate",
            "i love ", "my hobby", "my hobbies", "i enjoy", "my family",
            "my brother", "my sister", "my mom", "my dad", "my parents",
            "my friend", "my girlfriend", "my boyfriend", "my partner",
            "my address", "my phone", "my email", "my age", "years old",
        ]
        seen = set()
        for msg in all_user_messages:
            msg_lower = msg.lower()
            for pk in personal_keywords:
                if pk in msg_lower and msg[:80] not in seen:
                    seen.add(msg[:80])
                    preview = msg[:300].replace("\n", " ")
                    out.write(f"- _{preview}_\n")
                    break
        out.write("\n")

    print(f"\nSummary written to: {OUTPUT_FILE}")
    print(f"File size: {os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
