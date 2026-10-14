"""Create or update the ElevenLabs voice-conversation agents (one per level and voice).

Writes agents.json next to the page: {"levels": {"basic": {"f": "<agent_id>", "m": "<agent_id>"}}}
The page opens https://elevenlabs.io/app/talk-to?agent_id=<id> for the child's level and teacher voice.

Needs ELEVENLABS_API_KEY with the "ElevenLabs Agents: Write" permission.

Usage:
    python tools/agents.py            # create missing agents, update existing ones
    python tools/agents.py --show     # print the prompts only, no API calls
"""
import argparse
import json
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_audio as g  # noqa: E402  (shared key/voice helpers)

ROOT = g.ROOT
AGENTS = ROOT / "agents.json"
VOICES = {"f": "Jessica", "m": "Liam"}
MAX_SECONDS = 600

STYLE = {
    "tiny": ("a 3 to 5 year old who does not read and knows almost no English",
             "Speak mostly Hebrew. Teach one English word at a time, say it twice, and ask the child to say it after you. "
             "Use only the simplest words (colors, animals, numbers to five, fruit, toys, hello, thank you). Lots of praise, sound effects and tiny games."),
    "starter": ("a 6 to 8 year old beginner who reads Hebrew and knows a few English words",
                "Mix Hebrew and English: say the English, then explain in Hebrew. Practice short phrases like 'I like…', 'This is a…', colors, numbers, animals, food and family. "
                "Ask simple questions the child can answer in one or two words."),
    "basic": ("an 8 to 10 year old who knows basic English words and is starting simple grammar",
              "Speak mainly simple English, with a short Hebrew explanation only when the child is stuck. Practice full sentences with am/is/are, have/has, a/an, "
              "this/that, can/can't, in/on/under and question words. Ask the child to answer in a full sentence and gently model the correct sentence when they make a mistake."),
    "explorer": ("a 9 to 11 year old who can make simple English sentences",
                 "Speak English, short and clear. Practice present simple and present progressive, do/does questions, there is/are, telling time, weather and comparisons. "
                 "Use Hebrew only to explain a new word."),
    "reader": ("a 10 to 12 year old who reads simple English",
               "Speak English. Practice past simple, going to, superlatives and frequency words through little stories and questions about the child's day. "
               "Use Hebrew only if the child asks."),
}

FIRST = {
    "tiny": "Hello! שלום! אני המורה שלך לאנגלית. איך קוראים לך?",
    "starter": "Hello! שלום! I am your English teacher. What is your name? איך קוראים לך?",
    "basic": "Hi! I am your English teacher. What is your name?",
    "explorer": "Hi there! I'm your English teacher. What's your name?",
    "reader": "Hi! I'm your English teacher. What's your name, and how was your day?",
}


def vocabulary(content, level):
    words = []
    for l in content["lessons"]:
        if l["level"] == level:
            words += [w["en"].rstrip(".!") for w in l["words"]]
    seen, out = set(), []
    for w in words:
        if w.lower() not in seen:
            seen.add(w.lower()); out.append(w)
    return out[:150]


def prompt_for(content, level, voice):
    who, how = STYLE[level]
    gender = "a woman" if voice == "f" else "a man"
    grammar = [l["grammar"]["title"] for l in content["lessons"] if l["level"] == level and l.get("grammar")]
    vocab = ", ".join(vocabulary(content, level)) or "basic everyday words"
    lines = [
        f"You are a warm, playful, patient English teacher ({gender}) in a children's English-learning app. You are talking by voice with {who}. "
        "The child's home language is Hebrew (Israel).",
        how,
        f"Words the child is learning at this level: {vocab}.",
        f"Grammar topics at this level: {', '.join(grammar)}." if grammar else "",
        "Rules:",
        "- Keep every turn short: one or two short sentences, then wait for the child. Children speak slowly; be patient.",
        "- Ask one question at a time. Turn practice into games: guessing games, 'I spy', counting, describing pictures, little role plays (shop, zoo, picnic).",
        "- Praise effort often. Never say 'wrong'; instead repeat the correct form cheerfully and ask the child to try again.",
        "- When you speak Hebrew to the child, use plural or gender-neutral forms unless the child tells you their gender.",
        "- Stay on child-safe learning topics: animals, colors, food, family, school, games, feelings, numbers, weather, hobbies. If the child brings up anything else, "
        "gently steer back to an English game.",
        "- Never ask for or repeat personal details such as last name, address, school name, phone number, passwords or photos.",
        "- If the child seems tired or wants to stop, say a happy goodbye in English and Hebrew.",
    ]
    return "\n".join(x for x in lines if x)


def body(content, level, voice, voice_id):
    return {
        "name": f"English teacher · {level} · {VOICES[voice]}",
        "conversation_config": {
            "agent": {"first_message": FIRST[level], "language": "he",
                      "prompt": {"prompt": prompt_for(content, level, voice)}},
            "tts": {"model_id": "eleven_v3_conversational", "voice_id": voice_id},
            "conversation": {"max_duration_seconds": MAX_SECONDS},
            "language_presets": {"en": {"overrides": {"agent": {"first_message": FIRST[level]}}}},
        },
        "platform_settings": {"auth": {"enable_auth": False}},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()
    content = g.load_content()
    levels = [lv["id"] for lv in content["levels"] if any(l["level"] == lv["id"] for l in content["lessons"])]
    if a.show:
        for lv in levels:
            print(f"===== {lv}\n{prompt_for(content, lv, 'f')}\n")
        return
    key = g.api_key()
    voices = g.list_voices(key)
    vid = {v: g.resolve_voice(voices, name)["voice_id"] for v, name in VOICES.items()}
    saved = json.loads(AGENTS.read_text(encoding="utf-8")) if AGENTS.exists() else {"levels": {}}
    for lv in levels:
        for v in ("f", "m"):
            b = body(content, lv, v, vid[v])
            agent_id = saved["levels"].get(lv, {}).get(v)
            try:
                if agent_id:
                    g.request(key, "PATCH", f"{g.API}/convai/agents/{agent_id}", b)
                    print(f"updated {lv}/{v}: {agent_id}")
                else:
                    agent_id = json.loads(g.request(key, "POST", f"{g.API}/convai/agents/create", b))["agent_id"]
                    saved["levels"].setdefault(lv, {})[v] = agent_id
                    print(f"created {lv}/{v}: {agent_id}")
            except urllib.error.HTTPError as e:
                msg = e.read().decode("utf-8", "replace")[:400]
                AGENTS.write_text(json.dumps(saved, indent=1), encoding="utf-8")
                sys.exit(f"{e.code} on {lv}/{v}: {msg}")
    AGENTS.write_text(json.dumps(saved, indent=1), encoding="utf-8")
    print(f"saved {AGENTS}")


if __name__ == "__main__":
    main()
