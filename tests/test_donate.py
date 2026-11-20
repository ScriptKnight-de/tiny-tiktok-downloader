from tiny_tiktok_downloader.cli import main
from tiny_tiktok_downloader.donate import DONATE_URL


def test_donate_command_prints_link(capsys):
    assert main(["donate"]) == 0
    assert DONATE_URL in capsys.readouterr().out


def test_donate_url_is_kofi():
    assert DONATE_URL == "https://ko-fi.com/scriptknight"
