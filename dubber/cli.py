import argparse
import logging
import sys

from .pipeline import Pipeline
from .utils.language import get_supported_languages


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def _print_languages() -> None:
    langs = get_supported_languages()
    print("\nSupported target languages:\n")
    for name, code in sorted(langs.items()):
        print(f"  {code:<12} {name.title()}")
    print()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="video-dubber",
        description="Automatically dub a video into another language (GPU-accelerated).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("video", nargs="?", metavar="VIDEO",
                        help="Path to the input video file.")
    parser.add_argument("-s", "--source", default="en-US", metavar="LANG",
                        help="Source language code (default: en-US).")
    parser.add_argument("-t", "--target", default="ar", metavar="LANG",
                        help="Target language code (default: ar).")
    parser.add_argument("-o", "--output", metavar="PATH",
                        help="Output path (auto-generated if omitted).")
    parser.add_argument("--whisper-model",
                        choices=["tiny", "base", "small", "medium", "large"],
                        default="base", metavar="SIZE",
                        help="Whisper model size: tiny|base|small|medium|large (default: base).")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable debug logging.")
    parser.add_argument("--list-languages", action="store_true",
                        help="List all supported target languages and exit.")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    _setup_logging(args.verbose)

    if args.list_languages:
        _print_languages()
        return

    if not args.video:
        parser.print_help()
        sys.exit(1)

    try:
        result = Pipeline(whisper_model=args.whisper_model).run(
            video_path=args.video,
            target_lang=args.target,
            output_path=args.output,
            source_lang=args.source,
        )
        print("\n✅  Dubbing complete!")
        print(result)

    except (RuntimeError, ValueError, FileNotFoundError) as exc:
        logging.error(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
