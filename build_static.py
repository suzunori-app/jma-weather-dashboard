"""GitHub Pages公開用に、Flaskアプリの各ページをHTMLファイルへスナップショットする。

JMA APIはサーバーサイドでのみ呼び出し可能な想定のため、GitHub Actions上で
このスクリプトを定期実行し、生成したHTMLをそのままGitHub Pagesとして配信する。
"""

import os
from pathlib import Path

from app import app
from prefectures import PREFECTURES

BASE_PATH = os.environ.get("PAGES_BASE_PATH", "")
OUTPUT_DIR = Path(os.environ.get("PAGES_OUTPUT_DIR", "build"))


def _save(path: str, destination: Path) -> None:
    client = app.test_client()
    response = client.get(
        path, environ_overrides={"SCRIPT_NAME": BASE_PATH}, follow_redirects=True
    )
    if response.status_code != 200:
        raise RuntimeError(f"{path} の取得に失敗しました（status={response.status_code}）")

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(response.data)


def build() -> None:
    _save("/", OUTPUT_DIR / "index.html")
    _save("/overview", OUTPUT_DIR / "overview.html")
    _save("/temperature", OUTPUT_DIR / "temperature.html")
    _save("/weekly/", OUTPUT_DIR / "weekly" / "index.html")
    for pref in PREFECTURES:
        _save(f"/weekly/{pref['code']}", OUTPUT_DIR / "weekly" / f"{pref['code']}.html")

    (OUTPUT_DIR / ".nojekyll").touch()


if __name__ == "__main__":
    build()
