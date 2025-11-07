FROM node:22-slim

# Python3とpipをインストール
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ設定
WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# Node.js依存関係をインストール
RUN npm ci

# アプリケーションコードをコピー
COPY . .

# React アプリをビルド
RUN npm run build

# Python依存関係をインストール
RUN pip3 install --break-system-packages -r backend/requirements.txt

# ポート公開
EXPOSE 5000

# サーバー起動（-u でバッファリング無効化）
CMD ["python3", "-u", "backend/api_server.py"]