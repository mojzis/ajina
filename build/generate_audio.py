"""Generate TTS audio files for all words in a week using edge-tts.

For each word, generates two MP3 files:
- {id}_cs.mp3 — Czech pronunciation
- {id}_en.mp3 — English pronunciation
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

import edge_tts

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_VOICE_CS = "cs-CZ-VlastaNeural"
DEFAULT_VOICE_EN = "en-GB-SoniaNeural"
DEFAULT_RATE = "-15%"


async def generate_audio_file(
    text: str, voice: str, output_path: Path, rate: str = DEFAULT_RATE
) -> None:
    """Generate a single audio file using edge-tts."""
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(str(output_path))


async def generate_word_audio(
    word: dict[str, str],
    output_dir: Path,
    voice_cs: str,
    voice_en: str,
    force: bool,
) -> dict[str, bool]:
    """Generate both CS and EN audio for a single word. Returns which files were generated."""
    results: dict[str, bool] = {"cs": False, "en": False}

    cs_path = output_dir / word["audio_cs"]
    en_path = output_dir / word["audio_en"]

    if not cs_path.exists() or force:
        await generate_audio_file(word["czech"], voice_cs, cs_path)
        results["cs"] = True

    if not en_path.exists() or force:
        await generate_audio_file(word["english"], voice_en, en_path)
        results["en"] = True

    return results


async def run(args: argparse.Namespace) -> None:
    """Main async entry point."""
    # Read week JSON
    data_dir = PROJECT_ROOT / "site" / "data"
    week_path = data_dir / f"week-{args.week}.json"

    if not week_path.exists():
        print(f"  ERROR: Week data not found: {week_path}", file=sys.stderr)
        sys.exit(1)

    week_data = json.loads(week_path.read_text(encoding="utf-8"))
    words = week_data["words"]

    # Create output directory
    output_dir = data_dir / args.week
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[generate_audio] Generating audio for week {args.week}")
    print(f"  Czech voice: {args.voice_cs}")
    print(f"  English voice: {args.voice_en}")
    print(f"  Output: {output_dir}")
    print(f"  Words: {len(words)}")

    generated = 0
    skipped = 0

    for word in words:
        results = await generate_word_audio(
            word, output_dir, args.voice_cs, args.voice_en, args.force
        )
        if results["cs"] or results["en"]:
            parts = []
            if results["cs"]:
                parts.append("CS")
            if results["en"]:
                parts.append("EN")
            print(f"    {word['english']}: generated {', '.join(parts)}")
            generated += 1
        else:
            skipped += 1

    print(f"  Done: {generated} words generated, {skipped} skipped (already exist)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--week", required=True, help="Week ID (e.g. 2026-W13)")
    parser.add_argument("--force", action="store_true", help="Regenerate existing audio")
    parser.add_argument("--voice-cs", default=DEFAULT_VOICE_CS, help="Czech TTS voice")
    parser.add_argument("--voice-en", default=DEFAULT_VOICE_EN, help="English TTS voice")
    args = parser.parse_args()

    asyncio.run(run(args))


if __name__ == "__main__":
    main()
