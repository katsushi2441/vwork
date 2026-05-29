---
title: "HorizonでAIニュースを収集してGitHub Pagesに投稿し、KurageでAIショート動画を自動生成する仕組み"
emoji: "🪼"
type: "tech"
topics: ["ai", "python", "githubpages", "vibecoding", "oss"]
published: true
---

## 概要

本記事では、OSSのニュース収集システム **Horizon** を使って収集したAIニュースをGitHub Pagesのブログに自動投稿し、その内容をもとに **Kurageプロジェクト** がショート動画を自動生成するパイプラインの実装を解説します。

すべてバイブコーディングで構築しており、LLM・画像生成AI・TTS・動画合成を組み合わせた完全自動パイプラインです。

---

## システム全体構成

```
Horizon（ニュース収集）
  ↓ RSS / HackerNews / Reddit から記事収集
  ↓ Ollama（gemma4:e4b）でスコアリング
  ↓ 上位記事をMarkdownサマリーに
    ↓
    ├── post_to_zenn.py
    │     Ollamaで日本語翻訳 → Zenn形式MD作成
    │     → vwork/articles/ に保存 → GitHub push
    │     → GitHub Actions が自動デプロイ
    │     → GitHub Pages + Zenn に公開
    │
    └── generate_news_videos.py
          上位5記事をKurage backendへ送信
              ↓
          Kurage pipeline
          ├── Ollama (gemma4:e4b) → 12シーン脚本生成
          ├── ERNIE-Image-Turbo → 12枚の画像生成
          ├── edge-tts → 日本語ナレーション音声合成
          └── HyperFrames → 字幕付きMP4動画合成
              ↓
          horizonv.php で公開
```

---

## Horizon の設定

`data/config.json` でニュースソースとLLMを設定します。

```json
{
  "ai": {
    "provider": "ollama",
    "model": "gemma4:e4b",
    "base_url": "http://192.168.0.14:11434/v1",
    "enrichment_concurrency": 0,
    "languages": ["ja"]
  },
  "sources": {
    "hackernews": { "enabled": true, "fetch_top_stories": 10, "min_score": 100 },
    "rss": [
      { "name": "HuggingFace Blog", "url": "https://huggingface.co/blog/feed.xml", "fetch_limit": 3 },
      { "name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "fetch_limit": 5 },
      { "name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "fetch_limit": 3 }
    ]
  },
  "filtering": { "ai_score_threshold": 7.0 }
}
```

**ポイント：** `enrichment_concurrency: 0` で2次AI処理をスキップし、ローカルOllamaでの処理時間を大幅短縮しています。

---

## GitHub Pages への自動投稿（post_to_zenn.py）

Horizonが生成したMarkdownサマリー（英語）を、Ollamaで日本語ブログ記事に変換してGitHub Pagesへ投稿します。

```python
def translate_to_japanese(summary_text: str, post_date: str) -> str:
    prompt = f"""以下はHorizonが収集したニュースまとめ（英語）です。
日本語のブログ記事に書き直してください。
- 記事全体のタイトルは「AI・Web3ニュースまとめ」に統一する
- 重要なニュース上位5〜7件に絞る
- Markdown形式（## 見出し + 本文）で出力する

元データ:
{summary_text[:3000]}"""
    # Ollama API呼び出し
    ...
```

生成されたMarkdownは `vwork/articles/YYYY-MM-DD-ai-news.md` に保存し、`articles.md` のインデックスにリンクを追加してGitHubにpushします。GitHub ActionsがJekyllビルドを実行してGitHub Pagesに自動デプロイされます。

---

## Kurage でのニュース動画生成（generate_news_videos.py）

Horizonサマリーから上位5記事を抽出し、Kurage backendの `/generate_from_news` エンドポイントに送信します。

```python
top_items = parse_news_items(summary_md)[:5]
job_id = requests.post(
    "http://exbridge.ddns.net:18200/generate_from_news",
    json={"news_items": top_items, "title": f"AIニュース {today}"}
).json()["job_id"]
```

Kurage backendは以下のパイプラインを非同期実行します：

### 1. 脚本生成（Ollama gemma4:e4b）

複数記事から12シーン（約2分）のニュース番組風脚本を生成します。

```
オープニング1シーン → 各記事2〜4シーン → クロージング1シーン
```

各シーンに日本語ナレーション（50〜60字）と英語の画像プロンプトを付与します。

### 2. 画像生成（ERNIE-Image-Turbo）

シーンごとに縦型（576×1024）画像を生成。3秒インターバルでAPI呼び出し。

### 3. 音声合成（edge-tts）

`ja-JP-NanamiNeural` ボイスで各シーンのナレーションをMP3に変換。

### 4. 動画合成（HyperFrames）

画像＋ナレーション音声をHyperFrames APIで合成し、字幕付きMP4を生成。

---

## 日次自動化（horizon_worker.py）

毎日16:30にcronで `horizon_worker.py` が実行されます。

```bash
30 16 * * * cd /home/kojima/exdirect/horizon && python3 horizon_worker.py
```

実行フロー：
1. Horizon でニュース収集・スコアリング・サマリー生成
2. GitHub Pagesにブログ記事を投稿
3. AIxSNSで記事を告知（`author=kurage`）
4. Kurageでニュース動画を生成
5. AIxSNSで動画を告知（`author=kurage`）
6. ダッシュボードに実行結果を報告

---

## 成果物の公開先

| コンテンツ | URL |
|---|---|
| GitHub Pages ブログ | https://katsushi2441.github.io/vwork/articles/ |
| Zenn記事 | https://zenn.dev/katsushi2441 |
| ニュース動画一覧 | https://aiknowledgecms.exbridge.jp/horizonv.php |

---

## まとめ

- Horizonはローカルのgem ma4モデルでニュースを無料でスコアリング・要約
- GitHub Pagesへの自動投稿はgit pushだけでデプロイまで完結
- Kurageは12シーン・2分の動画を1記事ごとに自動生成
- すべてバイブコーディングで実装し、外部サービス費用はほぼゼロ

コードはすべてOSSで公開しています：
- Kurage: https://github.com/katsushi2441/kurage
- VWork: https://github.com/katsushi2441/vwork

株式会社エクスブリッジ https://exbridge.jp/
