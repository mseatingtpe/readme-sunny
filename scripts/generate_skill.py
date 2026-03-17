#!/usr/bin/env python3
"""Generate Claude Code Skill from worldview extractions."""

import argparse
import json
import os
import re
import yaml
from pathlib import Path
from urllib.request import urlopen, Request


CONTENT_DIR = Path(__file__).parent.parent / "content"
EXTRACT_DIR = CONTENT_DIR / "extractions"
PROFILE_PATH = CONTENT_DIR / "worldview-profile.yaml"
SKILL_PATH = Path(__file__).parent.parent / ".claude" / "skills" / "think-like-sunny.md"

# Layer 1: Core identity - rarely changes
CORE_IDENTITY_PATH = CONTENT_DIR / "skill-layers" / "core-identity.md"
# Layer 2: Topic stances - updated ~every 6 months
TOPIC_STANCES_PATH = CONTENT_DIR / "skill-layers" / "topic-stances.md"
# Layer 3: Recent dynamics - updated with each extraction
RECENT_DYNAMICS_PATH = CONTENT_DIR / "skill-layers" / "recent-dynamics.md"

TOKEN_BUDGET = 4000
# Rough estimate: 1 token ≈ 1.5 Chinese characters or 4 English chars
CHARS_PER_TOKEN = 2


def estimate_tokens(text):
    """Rough token estimate for mixed CJK/English text."""
    return len(text) // CHARS_PER_TOKEN


def call_claude_api(prompt):
    """Call Claude API."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set.")

    body = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
    except Exception as e:
        raise RuntimeError(f"Claude API request failed: {e}") from e

    try:
        return result["content"][0]["text"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected API response structure: {result}") from e


def load_profile():
    """Load worldview profile."""
    if not PROFILE_PATH.exists():
        return None
    with open(PROFILE_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_extractions():
    """Load all extraction files sorted by date."""
    extractions = []
    for f in sorted(EXTRACT_DIR.glob("*.yaml")):
        if f.name.startswith("_"):
            continue
        with open(f, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
            if data:
                extractions.append(data)
    extractions.sort(key=lambda x: str(x.get("timestamp", "")))
    return extractions


def generate_recent_dynamics(extractions, max_items=5):
    """Generate recent dynamics layer from latest extractions."""
    recent = extractions[-max_items:] if len(extractions) > max_items else extractions
    recent.reverse()  # Most recent first

    lines = ["## 最近動態\n"]
    for ext in recent:
        ts = ext.get("timestamp", "?")
        stance = ext.get("stance", "")
        topics = ", ".join(ext.get("topics", []))
        quote = ext.get("key_quote", "")
        lines.append(f"### {ts}｜{topics}")
        lines.append(f"\n{stance}")
        if quote:
            lines.append(f'\n> 「{quote}」')
        lines.append("")

    return "\n".join(lines)


def generate_topic_stances(profile):
    """Generate topic stances layer from worldview profile."""
    if not profile or "topics" not in profile:
        return ""

    lines = ["## 主題立場（附語境）\n"]
    lines.append("以下每個立場都有它原本的語境。回應時，只使用與當下問題語境相近的素材，不要跨語境拼貼。\n")

    for topic, entries in profile["topics"].items():
        if not entries:
            continue
        latest = entries[-1]
        lines.append(f"### {topic}")
        lines.append(f"\n**最新立場**（{latest['timestamp']}）：{latest['stance']}")
        if latest.get("tension"):
            lines.append(f"\n**張力**：{latest['tension']}")
        if len(entries) > 1:
            lines.append(f"\n**演變**：從 {entries[0]['timestamp']} 到 {entries[-1]['timestamp']} 共 {len(entries)} 筆紀錄")
        lines.append("")

    return "\n".join(lines)


def assemble_skill(core_identity, topic_stances, recent_dynamics):
    """Assemble the final skill file from three layers."""
    parts = [
        "---",
        "name: think-like-sunny",
        "description: 用 Sunny 的思考框架和語氣來回應問題",
        "---\n",
        "# Think Like Sunny\n",
        "你現在要用 Sunny 的思考框架來回應。以下是她的世界觀、推理方式和表達風格。\n",
        core_identity,
        "\n",
        topic_stances,
        "\n",
        recent_dynamics,
        "\n",
        "## 使用指引\n",
        "當用這個框架回應時：",
        "1. 先判斷問題屬於什麼語境，只拉該語境下的立場和素材",
        "2. 不要為了「聽起來豐富」而跨語境拼貼不同時期、不同場合的說法",
        "3. 先找到問題的「張力」在哪裡——不急著給答案",
        "4. 用架構思考，不用流程思考",
        "5. 承認複雜性，不做過度簡化",
        "6. 如果有立場就直說，但標註這是「現在的我」的看法",
        "7. 語氣真誠、不裝腔、不說教",
    ]

    full_text = "\n".join(parts)
    tokens = estimate_tokens(full_text)

    if tokens > TOKEN_BUDGET:
        print(f"⚠ Skill exceeds token budget ({tokens} > {TOKEN_BUDGET}), trimming recent dynamics")
        # Trim recent dynamics to fit
        while tokens > TOKEN_BUDGET and "### " in recent_dynamics:
            # Remove last entry
            last_section = recent_dynamics.rfind("### ")
            if last_section > 0:
                recent_dynamics = recent_dynamics[:last_section].rstrip()
            else:
                break
            parts[-4] = recent_dynamics  # Replace recent_dynamics in parts
            full_text = "\n".join(parts)
            tokens = estimate_tokens(full_text)

    return full_text


def main():
    parser = argparse.ArgumentParser(description="Generate Skill from extractions")
    parser.add_argument("--auto", action="store_true", help="Fully automatic generation from extractions")
    parser.add_argument("--update-dynamics", action="store_true", help="Only update the recent dynamics layer")
    args = parser.parse_args()

    profile = load_profile()
    extractions = load_extractions()

    if not extractions:
        print("No extractions found. Run extract.py first.")
        return

    # Ensure layer directory exists
    (CONTENT_DIR / "skill-layers").mkdir(parents=True, exist_ok=True)

    if args.update_dynamics:
        # Only update Layer 3 (recent dynamics), reuse existing Layer 1 & 2
        if CORE_IDENTITY_PATH.exists():
            core_identity = CORE_IDENTITY_PATH.read_text(encoding="utf-8")
        else:
            print("⚠ No existing core identity found, falling back to full generation")
            args.update_dynamics = False

        if args.update_dynamics and TOPIC_STANCES_PATH.exists():
            topic_stances = TOPIC_STANCES_PATH.read_text(encoding="utf-8")
        elif args.update_dynamics:
            print("⚠ No existing topic stances found, falling back to full generation")
            args.update_dynamics = False

    if not args.update_dynamics:
        # Full generation: Layer 1 + Layer 2 + Layer 3

        # Layer 1: Core identity - use existing if available, otherwise use current skill
        if CORE_IDENTITY_PATH.exists():
            core_identity = CORE_IDENTITY_PATH.read_text(encoding="utf-8")
        elif SKILL_PATH.exists():
            # Extract core sections from existing skill
            existing = SKILL_PATH.read_text(encoding="utf-8")
            match = re.search(r"(## 核心身份.*?)(?=## 立場|## 主題立場|$)", existing, re.DOTALL)
            if match:
                core_identity = match.group(1).strip()
            else:
                core_identity = "## 核心身份\n\n（需要手動編輯）"
            CORE_IDENTITY_PATH.write_text(core_identity, encoding="utf-8")
            print(f"✓ Extracted core identity to {CORE_IDENTITY_PATH}")
        else:
            core_identity = "## 核心身份\n\n（需要手動編輯）"

        # Layer 2: Topic stances
        topic_stances = generate_topic_stances(profile)
        TOPIC_STANCES_PATH.write_text(topic_stances, encoding="utf-8")
        print(f"✓ Generated topic stances")

    # Layer 3: Recent dynamics (always updated)
    recent_dynamics = generate_recent_dynamics(extractions)
    RECENT_DYNAMICS_PATH.write_text(recent_dynamics, encoding="utf-8")
    print(f"✓ Generated recent dynamics")

    # Assemble
    skill_text = assemble_skill(core_identity, topic_stances, recent_dynamics)
    SKILL_PATH.parent.mkdir(parents=True, exist_ok=True)
    SKILL_PATH.write_text(skill_text, encoding="utf-8")
    print(f"✓ Skill written to {SKILL_PATH}")
    print(f"  Estimated tokens: {estimate_tokens(skill_text)}")


if __name__ == "__main__":
    main()
