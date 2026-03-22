"""Generate TTS audio files for all words in a week using edge-tts.

For each word, generates two MP3 files:
- {id}_cs.mp3 — Czech pronunciation
- {id}_en.mp3 — English pronunciation
"""

import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_VOICE_CS = "cs-CZ-VlastaNeural"
DEFAULT_VOICE_EN = "en-GB-SoniaNeural"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--week", required=True, help="Week ID (e.g. 2026-W13)")
    parser.add_argument("--force", action="store_true", help="Regenerate existing audio")
    parser.add_argument("--voice-cs", default=DEFAULT_VOICE_CS, help="Czech TTS voice")
    parser.add_argument("--voice-en", default=DEFAULT_VOICE_EN, help="English TTS voice")
    args = parser.parse_args()

    # TODO: Implement in Phase 3
    print(f"[generate_audio] Would generate audio for week {args.week}")
    print(f"  Czech voice: {args.voice_cs}")
    print(f"  English voice: {args.voice_en}")
    print(f"  Force: {args.force}")

    output_dir = PROJECT_ROOT / "site" / "assets" / "audio" / f"week-{args.week}"
    print(f"  Output: {output_dir}")


if __name__ == "__main__":
    main()
