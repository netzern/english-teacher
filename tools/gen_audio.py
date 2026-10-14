"""Generate the teacher's voice clips with ElevenLabs and pack them for the page.

Reads every speakable line from content.json (fields "he"/"en" for both voices,
"heF" for the female voice only, "heM" for the male voice only), creates the
missing clips with the eleven_v3 model, and writes audio packs + an index:

    audio/f-0.mp3, audio/m-0.mp3, ...   concatenated mp3 clips
    audio/index.json                    {"clips": {"f": {key: [pack, offset, length]}}}

The API key is read from the ELEVENLABS_API_KEY environment variable
(also from the Windows user environment, so `setx` works without a new shell).

Usage:
    python tools/gen_audio.py --dry-run          # count clips and characters only
    python tools/gen_audio.py --list-voices      # show the voices in your account
    python tools/gen_audio.py --sample 6         # generate a few clips to listen to
    python tools/gen_audio.py                    # generate everything (asks first)
    python tools/gen_audio.py --voice-f Jessica --voice-m Liam
"""
import argparse
import concurrent.futures as cf
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content.json"
CACHE = ROOT / "tools" / "cache"
AUDIO = ROOT / "audio"
API = "https://api.elevenlabs.io/v1"
MODEL = "eleven_v3"
FORMAT = "mp3_44100_64"
PACK_LIMIT = 6 * 1024 * 1024
DEFAULT_VOICES = {"f": "Jessica", "m": "Liam"}


def fnv1a(s: str) -> str:
    h = 0x811C9DC5
    for b in s.encode("utf-8"):
        h ^= b
        h = (h * 0x01000193) & 0xFFFFFFFF
    return f"{h:08x}"


def clip_key(lang: str, text: str) -> str:
    return fnv1a(lang + "|" + text)


def load_content() -> dict:
    s = CONTENT.read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rstrip().rindex("}") + 1])


def collect_clips(content: dict) -> dict:
    clips = {"f": {}, "m": {}}

    def add(voices, lang, text):
        for v in voices:
            clips[v][clip_key(lang, text)] = (lang, text)

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str):
                    if k in ("he", "en"):
                        add("fm", k, v)
                    elif k == "heF":
                        add("f", "he", v)
                    elif k == "heM":
                        add("m", "he", v)
                else:
                    walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(content)
    return clips


def api_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key and sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                key = str(winreg.QueryValueEx(k, "ELEVENLABS_API_KEY")[0]).strip()
        except OSError:
            pass
    if not key:
        sys.exit("ELEVENLABS_API_KEY is not set. Run: setx ELEVENLABS_API_KEY \"<your key>\"")
    return key


def request(key, method, url, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("xi-api-key", key)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def list_voices(key):
    return json.loads(request(key, "GET", f"{API}/voices"))["voices"]


def resolve_voice(voices, wanted):
    for v in voices:
        if v["voice_id"] == wanted or v["name"].lower() == wanted.lower():
            return v
    for v in voices:
        if v["name"].lower().startswith(wanted.lower()):
            return v
    sys.exit(f'Voice "{wanted}" not found. Use --list-voices to see the names in your account.')


def tts(key, voice_id, lang, text):
    url = f"{API}/text-to-speech/{voice_id}?output_format={FORMAT}"
    body = {"text": text, "model_id": MODEL, "language_code": lang,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
    for attempt in range(4):
        try:
            return request(key, "POST", url, body)
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")
            if e.code == 400 and "language" in msg and "language_code" in body:
                body.pop("language_code")
                continue
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(f"{e.code} for {lang}:{text!r}: {msg[:300]}")
        except urllib.error.URLError:
            if attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise


def build_packs(clips, voice_dirs):
    AUDIO.mkdir(exist_ok=True)
    for old in AUDIO.glob("*-*.mp3"):
        old.unlink()
    index = {"model": MODEL, "format": FORMAT, "clips": {}}
    for v, items in clips.items():
        index["clips"][v] = {}
        pack_no, buf = 0, bytearray()

        def flush():
            nonlocal pack_no, buf
            if buf:
                (AUDIO / f"{v}-{pack_no}.mp3").write_bytes(bytes(buf))
                pack_no, buf = pack_no + 1, bytearray()

        for k in sorted(items):
            f = voice_dirs[v] / f"{k}.mp3"
            if not f.exists():
                continue
            data = f.read_bytes()
            if buf and len(buf) + len(data) > PACK_LIMIT:
                flush()
            index["clips"][v][k] = [f"{v}-{pack_no}.mp3", len(buf), len(data)]
            buf.extend(data)
        flush()
    (AUDIO / "index.json").write_text(json.dumps(index, separators=(",", ":")), encoding="utf-8")
    return index


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--list-voices", action="store_true")
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--voice-f", default=os.environ.get("ET_VOICE_F", DEFAULT_VOICES["f"]))
    ap.add_argument("--voice-m", default=os.environ.get("ET_VOICE_M", DEFAULT_VOICES["m"]))
    ap.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    a = ap.parse_args()

    clips = collect_clips(load_content())
    if a.dry_run:
        for v, items in clips.items():
            print(f"voice {v}: {len(items)} clips, {sum(len(t) for _, t in items.values())} characters")
        return

    key = api_key()
    voices = list_voices(key)
    if a.list_voices:
        for v in voices:
            labels = v.get("labels") or {}
            print(f'{v["name"]:<24} {v["voice_id"]}  {labels.get("gender", "")} {labels.get("accent", "")} {labels.get("age", "")}')
        return

    chosen = {"f": resolve_voice(voices, a.voice_f), "m": resolve_voice(voices, a.voice_m)}
    voice_dirs = {v: CACHE / chosen[v]["voice_id"] for v in chosen}
    todo = []
    for v, items in clips.items():
        voice_dirs[v].mkdir(parents=True, exist_ok=True)
        missing = [(k, *items[k]) for k in sorted(items) if not (voice_dirs[v] / f"{k}.mp3").exists()]
        if a.sample:
            missing = missing[: a.sample]
        todo += [(v, *m) for m in missing]

    chars = sum(len(t) for *_, t in todo)
    print(f'Female voice: {chosen["f"]["name"]}  |  Male voice: {chosen["m"]["name"]}')
    print(f"To generate: {len(todo)} clips, {chars} characters (model {MODEL}).")
    if todo and not a.yes:
        if input("Continue? [y/N] ").strip().lower() != "y":
            return

    done, failed = 0, []

    def work(item):
        v, k, lang, text = item
        data = tts(key, chosen[v]["voice_id"], lang, text)
        (voice_dirs[v] / f"{k}.mp3").write_bytes(data)
        return item

    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(work, t): t for t in todo}
        for fut in cf.as_completed(futs):
            try:
                fut.result()
                done += 1
                if done % 25 == 0 or done == len(todo):
                    print(f"  {done}/{len(todo)}")
            except Exception as e:  # keep going; report at the end
                failed.append(str(e))

    index = build_packs(clips, voice_dirs)
    total = {v: len(index["clips"][v]) for v in index["clips"]}
    print(f"Packed: {total}. Files in {AUDIO}")
    if failed:
        print(f"{len(failed)} clips failed:")
        for f in failed[:10]:
            print("  ", f)
        sys.exit(1)


if __name__ == "__main__":
    main()
