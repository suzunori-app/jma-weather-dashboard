# sandbox

気象庁（JMA）の防災情報APIを利用した、簡易天気情報ダッシュボード（Flask製）。

## ページ

| パス | 内容 |
|---|---|
| `/overview` | 予報区（全58区）ごとの気象概況テキストを一覧表示 |
| `/temperature` | 都道府県ごとの最高・最低気温を日本地図（Leaflet.js）上にプロット |
| `/weekly` | 都道府県を選択して7日分の週間天気予報を表示（土曜・日曜・祝日は色分け） |

いずれのページも右上（各ページ上部）のタブから切り替えられます。

## セットアップ

依存関係のインストール:
```
pip install -r requirements.txt
```

アプリをローカルで実行:
```
python app.py
```
`http://0.0.0.0:5000` で提供されます。

## Testing

テストの実行:
```
pytest
```

単一テストの実行:
```
pytest tests/test_app.py::test_index
```

lint チェックの実行（ruff）:
```
ruff check .
```

## Docker

イメージのビルド:
```
docker build -t sandbox .
```

アプリの実行（デフォルトの `CMD`）:
```
docker run -p 5000:5000 sandbox
```

デフォルトの `CMD` を上書きして、アプリの代わりにテストを実行:
```
docker run sandbox pytest
```

デフォルトの `CMD` を上書きして、アプリの代わりに lint チェックを実行:
```
docker run sandbox ruff check .
```

`docker-compose` を使う場合は `web` / `test` / `lint` サービスが定義されています:
```
docker compose up -d web       # http://localhost:5001 で起動
docker compose run --rm test
docker compose run --rm lint
```

## 構成

```
app.py                  Flask ルーティング
jma.py                  気象概況API（overview_forecast）の取得
forecast.py             天気予報API（forecast）から気温・週間予報を抽出
areas.py                予報区コード一覧（58区）
prefectures.py          都道府県ごとの代表予報区コードと緯度経度（47都道府県）
build_static.py         GitHub Pages公開用の静的HTMLスナップショット生成
templates/base.html     共通レイアウト・タブナビゲーション
templates/overview.html /overview ページ
templates/temperature.html /temperature ページ
templates/weekly.html   /weekly ページ
tests/                  pytest によるテスト
```

## GitHub Pages への公開

GitHub Pagesは静的ファイルのみ配信可能でFlaskサーバーを実行できないため、`.github/workflows/deploy-pages.yml` が毎時（cron）・`main`へのpush・手動実行のタイミングで以下を行う。

1. `build_static.py` がFlaskアプリを内部的に呼び出し、`/`・`/overview`・`/temperature`・`/weekly/`・都道府県ごとの`/weekly/{code}`をHTMLファイルとして`build/`以下に書き出す（そのため、表示される気象データはビルド時点のスナップショット）。
2. `build/`をGitHub Pagesとしてデプロイする。

初回のみ、リポジトリの Settings → Pages → Source を **GitHub Actions** に設定する必要がある。

ローカルで同じスナップショットを生成する場合:
```
python build_static.py
```
`build/` に出力される。プロジェクトページ（`https://<user>.github.io/<repo>/`）以外のパスで公開する場合は、`PAGES_BASE_PATH`環境変数でベースパスを指定する（未設定時は空文字＝ルート直下）。

## 使用しているJMA API

- `https://www.jma.go.jp/bosai/forecast/data/overview_forecast/{予報区コード}.json` — 気象概況
- `https://www.jma.go.jp/bosai/forecast/data/forecast/{予報区コード}.json` — 天気予報（今日・明日・週間）

いずれも気象庁が公式にドキュメント化しているAPIではなく、非公式に利用されているエンドポイントです。予告なく仕様が変わる可能性があります。
