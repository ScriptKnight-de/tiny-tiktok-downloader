# tiny-tiktok-downloader

Keep a local copy of the **videos and photo posts** you **liked** and **saved** (TikTok's
"Favorites") on TikTok. It runs once a day (or whenever you press a button), downloads only what is new,
and never fetches the same file twice.

- **Set it and forget it:** a Docker container or a systemd timer syncs every night.
- **Or click a button:** a small desktop app (AppImage) with live progress.
- **Your files, your rules:** move, rename or delete downloads freely; the tool remembers
  what it already got.
- Built on [gallery-dl](https://github.com/mikf/gallery-dl).

> **Heads-up:** TikTok has no free API for liked and saved videos, so this uses your logged-in
> browser session (a `cookies.txt` export). Automated access may conflict with TikTok's terms.
> Use your own account, at your own risk. TikTok changes its site often; if downloads break,
> update gallery-dl (`pip install -U gallery-dl`, or pull the newest image).

## Quick start

1. **Export your cookies** (once, see [Getting your cookies](#getting-your-cookies)).
2. **Pick how you want to run it:**

| I want to… | Use |
|---|---|
| run it on a server or NAS, hands-off | [Docker](#docker) |
| click a button on my Linux desktop | [AppImage](#desktop-app-appimage) |
| use the command line / a systemd timer | [pip install](#command-line) |

## Getting your cookies

1. Log in to [tiktok.com](https://www.tiktok.com) in your browser.
2. Install a "Get cookies.txt" extension and export the cookies for `tiktok.com` as a Netscape-format
   `cookies.txt`.
3. Keep that file private: `chmod 600 cookies.txt`.

Cookies expire now and then. If a run reports login errors, export a fresh file and replace
the old one; the next run picks it up.

## Docker

```bash
git clone https://github.com/ScriptKnight-de/tiny-tiktok-downloader.git
cd tiny-tiktok-downloader

cp .env.example .env                     # set TIKTOK_USERNAME, PUID/PGID (`id -u`, `id -g`), TZ, TIKTOK_SYNC_TIME
mkdir -p config data downloads           # create these as your user, not as root
cp /path/to/cookies.txt config/cookies.txt && chmod 600 config/cookies.txt

docker compose pull && docker compose up -d     # use the published image
# docker compose up -d --build           # ...or build it yourself
docker compose logs -f
```

The container syncs once per day at `TIKTOK_SYNC_TIME` (local time, per `TZ`) and keeps running even if
a sync fails. Set `TIKTOK_RUN_ON_START=true` to also sync right after it starts.

| Host folder | In the container | What it is |
|---|---|---|
| `./config` | `/config` (read-only) | folder holding your TikTok session `cookies.txt` |
| `./data` | `/data` | the archive database, **keep this** |
| `./downloads` | `/downloads` | your media in `likes/` and `bookmarks/` (your saved videos) |

Try it without downloading anything:

```bash
docker compose run --rm tiny-tiktok-downloader sync --dry-run
```

## Desktop app (AppImage)

Download `tiny-tiktok-downloader-<version>-x86_64.AppImage` from the
[Releases](https://github.com/ScriptKnight-de/tiny-tiktok-downloader/releases) page, then:

```bash
chmod +x tiny-tiktok-downloader-*.AppImage
./tiny-tiktok-downloader-*.AppImage            # opens the window
```

Enter your TikTok username, choose your cookies file and download folder, then press **Sync now** (or **Dry run** to preview).
You can watch the current file, counters and log. Settings are saved to
`~/.config/tiny-tiktok-downloader/env`, and an optional daily sync runs while the window is open.
The AppImage bundles Python and Tk (Linux, x86_64) and also works as a CLI:
`./tiny-tiktok-downloader-*.AppImage sync --dry-run`.

## Command line

Needs Python 3.10 or newer.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install .
mkdir -p ~/.config/tiny-tiktok-downloader
cp .env.example ~/.config/tiny-tiktok-downloader/env     # then edit the paths (TIKTOK_COOKIES, ...)

tiny-tiktok-downloader sync --dry-run                    # list what would be downloaded
tiny-tiktok-downloader sync                              # likes + bookmarks
tiny-tiktok-downloader sync --source bookmarks           # only one source
tiny-tiktok-downloader sync --full                       # rescan the whole timeline
tiny-tiktok-downloader install-timer --time 04:00        # daily systemd user timer
```

Files end up in `<output dir>/likes/` and `<output dir>/bookmarks/`, named
`<author>_<video-id>_<n>.<ext>` (`n` is 0 for videos, 1, 2, ... for photo slideshows).

## Settings

Set these as environment variables, in `./.env`, or in `~/.config/tiny-tiktok-downloader/env`
(see [`.env.example`](.env.example) for a commented template).

| Variable | Default | Meaning |
|---|---|---|
| `TIKTOK_USERNAME` | none, required | your TikTok username, without `@` |
| `TIKTOK_COOKIES` | none, required | path to your `cookies.txt` |
| `TINY_TIKTOK_DOWNLOADER_OUTPUT_DIR` | `downloads` | where media is saved |
| `TINY_TIKTOK_DOWNLOADER_ARCHIVE` | `~/.local/share/tiny-tiktok-downloader/archive.sqlite3` | the "already downloaded" database |
| `TIKTOK_SYNC_TIME` | `04:00` | daily sync time for the Docker daemon (`HH:MM`) |
| `TIKTOK_RUN_ON_START` | `false` | also sync when the daemon starts |

## How "already downloaded" works

Every file is recorded (video id + media index) in an SQLite archive that lives **outside** the
download folder. Because the memory is independent of your files, you can move, rename or delete
downloads and they will not come back. Just don't delete the archive.

- **First run** per source (likes / bookmarks): full backfill of the whole timeline.
- **Later runs:** scan newest first and stop after 30 consecutive already-known files.

## Troubleshooting

| Problem | Fix |
|---|---|
| login or `You may need cookies` errors | your cookies expired; export a new `cookies.txt` |
| `unable to extract secondary user ID` | check `TIKTOK_USERNAME`; if it is right, update gallery-dl |
| `TIKTOK_USERNAME is not set`, `TIKTOK_COOKIES is not set` | set them in `.env` or `~/.config/tiny-tiktok-downloader/env` |
| Files owned by root (Docker) | create `config`, `data`, `downloads` as your user and set `PUID`/`PGID` |
| It stops early and misses old posts | run once with `sync --full` |

## Questions and bug reports

Please [open an issue](https://github.com/ScriptKnight-de/tiny-tiktok-downloader/issues). Include the command you ran, the output and your
version (`tiny-tiktok-downloader --version`). Never post your `cookies.txt`.

## Development

```bash
pip install -e ".[dev]" && pytest
./packaging/build-appimage.sh      # builds dist/tiny-tiktok-downloader-<version>-x86_64.AppImage
```

CI (`.forgejo/workflows/build.yml`) runs the tests and publishes the multi-arch Docker image
(`linux/amd64`, `linux/arm64`) to `ghcr.io/scriptknight-de/tiny-tiktok-downloader` on every push to `main` and on `v*` tags.
Tagged releases also get the AppImage attached on GitHub.

## License

[MIT](LICENSE)

---

<p align="center">
  <sub>Free and open source. If it saves you time, you can say thanks on Ko-fi.</sub><br>
  <a href="https://ko-fi.com/scriptknight"><img src="docs/kofi_logo.png" alt="Support me on Ko-fi" height="36"></a>
</p>
