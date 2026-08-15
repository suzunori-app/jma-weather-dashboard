# コード設計

- 関心の分離を保つ
- 状態とロジックを分離する
- 可読性と保守性を重視する

# コマンド

依存関係のインストール:
```
pip install -r requirements.txt
```

アプリをローカルで実行:
```
python app.py
```
`http://0.0.0.0:5000` で提供されます。


# Testing

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

# Docker

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

`docker-compose` を使う場合は `web` / `test` に加えて `lint` サービスも定義されています:
```
docker compose run --rm lint
```

# Git
- .env / 鍵・トークン等のシークレットは絶対にコミットしない
- 一時ファイル・個人設定 (/settings.local.jsonなど) は .gitignore で除外する