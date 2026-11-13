# YouTube downloader

## Short command in Git Bash

The `yt-download` command is installed in this project's `.venv`.
In each new Git Bash terminal, activate the environment once:

```bash
cd ~/repos/ytbdownload
source .venv/Scripts/activate
```

Then run:

```bash
yt-download "@guru_talks"
# Or preview without downloading:
yt-download "@guru_talks" --preview --limit 5
```

All `download.py` options work with this command. Downloads and their history
stay in the same folder. Run `deactivate` to leave the environment.

`pyproject.toml` defines `yt-download = "download:main"`: the command calls
the `main()` function in `download.py`. To install the command on a fresh setup,
or reinstall it after changing the command definition, run from this folder:

```bash
./.venv/Scripts/python.exe -m pip install -e .
```

The editable install keeps using this project's source file and bundled FFmpeg
location when you edit the code. No reinstall is needed for edits to `download.py`.

## Running the script directly in PowerShell

Run these commands in PowerShell from this project folder. Python dependencies
have already been installed in `.venv` on this computer. The script automatically
finds the FFmpeg ZIP you extracted here and uses an installed Deno or Node executable.

Download a channel using its handle (the `@name` shown on its YouTube page):

```powershell
cd C:\Users\murat\repos\ytbdownload
.\.venv\Scripts\python.exe .\download.py "@CHANNEL_HANDLE"
```

Replace `@CHANNEL_HANDLE` with the actual handle, for example `@YouTube`.
Bare handles such as `YouTube` work too. Display names with spaces aren't unique:
use the channel's handle or paste its URL instead.

With no argument, the script prompts for a handle or link:

```powershell
.\.venv\Scripts\python.exe .\download.py
```

Other examples:

```powershell
# Preview the first five entries without downloading media
.\.venv\Scripts\python.exe .\download.py "@YouTube" --preview --limit 5

# Download only the first three videos, up to 1080p
.\.venv\Scripts\python.exe .\download.py "https://www.youtube.com/@YouTube/videos" --limit 3 --max-height 1080

# A single video (replace VIDEO_ID)
.\.venv\Scripts\python.exe .\download.py "https://www.youtube.com/watch?v=VIDEO_ID"

# A playlist (replace PLAYLIST_ID)
.\.venv\Scripts\python.exe .\download.py "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Save to another drive
.\.venv\Scripts\python.exe .\download.py "@YouTube" --output "D:\YouTube"
```

A channel root includes the video tabs yt-dlp finds, including Shorts and completed
streams. Use `/videos`, `/shorts`, or `/streams` to select a specific tab. Active and
upcoming streams are skipped. `--limit` applies at each playlist level (including
the channel's list of tabs) and counts entries examined, including entries already
downloaded or unavailable. Use a specific tab URL for a predictable limit. It is
not a count of new successful downloads. A watch URL that also contains `list=` can download
the playlist; remove the `list` parameter if you want only that video.

Files are saved under `downloads\CHANNEL\` by default, beside the script, with the
best available video and audio. The container extension depends on the available
formats. `downloads\downloaded.txt` remembers successful downloads across runs.
Keep that file to skip completed videos. If you delete a media file and want to
download it again, remove its corresponding line from the archive too.
Press Ctrl+C to stop; run the same command to resume partial downloads and retry
failed entries. Private, removed, or otherwise inaccessible videos may fail.

`--dry-run --limit 1` checks video extraction and format selection without saving
media. `--preview` lists entries without checking every video's playable formats.

## Setup on another computer or update

Install Python 3.11+, FFmpeg (including ffprobe), and Deno or Node.js 22+.
Then run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
```

Keep the extracted FFmpeg folder in this project, add its `bin` folder to PATH,
or pass `--ffmpeg-location "C:\path\to\ffmpeg\bin"`. No PowerShell activation or
execution-policy change is needed. If YouTube extraction starts failing, update
with the pip command above and retry.

Implementation references: [yt-dlp documentation](https://github.com/yt-dlp/yt-dlp)
and [YouTube JavaScript runtime setup](https://github.com/yt-dlp/yt-dlp/wiki/EJS).
