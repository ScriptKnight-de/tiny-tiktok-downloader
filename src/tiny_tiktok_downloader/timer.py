"""Install a daily systemd user timer."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

UNIT_DIR = Path("~/.config/systemd/user").expanduser()

SERVICE = """[Unit]
Description=Download media from liked and saved TikTok videos

[Service]
Type=oneshot
EnvironmentFile=-%h/.config/tiny-tiktok-downloader/env
ExecStart={python} -m tiny_tiktok_downloader sync
"""

TIMER = """[Unit]
Description=Daily tiny-tiktok-downloader sync

[Timer]
OnCalendar=*-*-* {time}:00
Persistent=true
RandomizedDelaySec=10min

[Install]
WantedBy=timers.target
"""


def install_timer(time: str = "04:00", enable: bool = True) -> None:
    UNIT_DIR.mkdir(parents=True, exist_ok=True)
    (UNIT_DIR / "tiny-tiktok-downloader.service").write_text(SERVICE.format(python=sys.executable))
    (UNIT_DIR / "tiny-tiktok-downloader.timer").write_text(TIMER.format(time=time))
    print(f"wrote units to {UNIT_DIR}")
    if enable:
        subprocess.check_call(["systemctl", "--user", "daemon-reload"])
        subprocess.check_call(["systemctl", "--user", "enable", "--now", "tiny-tiktok-downloader.timer"])
        print("timer enabled; check with: systemctl --user list-timers tiny-tiktok-downloader.timer")
