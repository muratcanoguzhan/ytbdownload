"""Download YouTube videos, playlists, or channels with yt-dlp."""

import argparse
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent


def youtube_url(value):
    """Treat bare names as handles, never as ambiguous search queries."""
    value = value.strip()
    if not value:
        raise ValueError("Enter a YouTube URL or channel handle, e.g. @YouTube.")
    if re.fullmatch(r"UC[A-Za-z0-9_-]{22}", value):
        return f"https://www.youtube.com/channel/{value}"
    if re.fullmatch(r"@?[\w.\-·]+", value, flags=re.UNICODE):
        return f"https://www.youtube.com/@{value.lstrip('@')}"
    if value.startswith(("youtube.com/", "www.youtube.com/", "m.youtube.com/", "youtu.be/")):
        value = "https://" + value
    parsed = urlsplit(value)
    if parsed.scheme not in ("http", "https") or parsed.hostname not in (
        "youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"
    ) or parsed.username or parsed.password:
        raise ValueError("Use a YouTube URL or the channel's @handle (not its display name).")
    return value


def find_ffmpeg(explicit=None):
    if explicit:
        folder = Path(explicit).expanduser().resolve()
        if folder.is_file():
            folder = folder.parent
        candidates = [folder]
    else:
        candidates = []
        if installed := shutil.which("ffmpeg"):
            candidates.append(Path(installed).parent)
        # Includes the nested folder produced by extracting the downloaded ZIP.
        candidates.extend(sorted(p.parent for p in ROOT.glob("ffmpeg*/**/bin/ffmpeg.exe")))
    for folder in candidates:
        suffix = ".exe" if sys.platform == "win32" else ""
        if all((folder / (name + suffix)).is_file() for name in ("ffmpeg", "ffprobe")):
            return str(folder)
    raise ValueError("FFmpeg and ffprobe were not found. Use --ffmpeg-location PATH_TO_BIN.")


def js_runtimes():
    # Use actual executables: npm's deno.ps1 shim cannot be launched by yt-dlp.
    for name in ("deno", "node"):
        executable = shutil.which(name + ".exe" if sys.platform == "win32" else name)
        if executable:
            return {name: {"path": executable}}
    deno = Path.home() / ".deno" / "bin" / ("deno.exe" if sys.platform == "win32" else "deno")
    if deno.is_file():
        return {"deno": {"path": str(deno)}}
    raise ValueError("Install Deno or Node.js 22+ for YouTube JavaScript processing.")


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive number")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", help="@handle, handle, channel ID, or YouTube URL")
    parser.add_argument("--output", type=Path, default=ROOT / "downloads", help="download folder")
    parser.add_argument("--limit", type=positive_int, help="inspect only the first N entries per playlist/tab")
    parser.add_argument("--max-height", type=positive_int, help="maximum video height, e.g. 1080")
    parser.add_argument("--preview", action="store_true", help="list titles without downloading media")
    parser.add_argument("--dry-run", action="store_true", help="check video formats without downloading media")
    parser.add_argument("--ffmpeg-location", help="folder containing ffmpeg and ffprobe")
    args = parser.parse_args(argv)

    try:
        source = youtube_url(args.source if args.source is not None else input("YouTube URL or @channel: "))
        import yt_dlp

        output = args.output.expanduser().resolve()
        video_format = "bv*+ba/b"
        if args.max_height:
            video_format = f"bv*[height<={args.max_height}]+ba/b[height<={args.max_height}]"
        options = {
            "format": video_format,
            "outtmpl": str(output / "%(uploader)s" / "%(title).150B [%(id)s].%(ext)s"),
            "download_archive": str(output / "downloaded.txt"),
            "ignoreerrors": "only_download",
            "retries": 10,
            "fragment_retries": 10,
            "continuedl": True,
            "windowsfilenames": True,
            "socket_timeout": 30,
            # Skip active/upcoming broadcasts; completed streams can be downloaded.
            "match_filter": yt_dlp.utils.match_filter_func("!is_live & !is_upcoming"),
        }
        if args.limit:
            options["playlistend"] = args.limit
        if args.preview:
            options.update({"extract_flat": "in_playlist", "simulate": True,
                            "forceprint": {"video": ["%(title)s [%(id)s]"]}})
        else:
            options["ffmpeg_location"] = find_ffmpeg(args.ffmpeg_location)
            options["js_runtimes"] = js_runtimes()
            if args.dry_run:
                options["simulate"] = True
            else:
                output.mkdir(parents=True, exist_ok=True)
        print(f"Source: {source}", flush=True)
        print(f"Download folder: {output}", flush=True)
        with yt_dlp.YoutubeDL(options) as downloader:
            result = downloader.download([source])
        if result:
            print("Finished with errors. Rerun the same command to retry failed videos.", file=sys.stderr)
        else:
            print("Preview complete." if args.preview or args.dry_run else "Download complete.")
        return 1 if result else 0
    except ImportError:
        print('Install dependencies: python -m pip install -r requirements.txt', file=sys.stderr)
        return 1
    except (ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print("\nStopped. Rerun the same command to resume.", file=sys.stderr)
        return 130
    except yt_dlp.utils.DownloadError as exc:
        print(f"Download failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
