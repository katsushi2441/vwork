---
title: "株式会社エクスブリッジの取り組み — URL2AI・AIxEC・Kurageプロジェクト・VWork"
emoji: "🌉"
type: "idea"
topics: ["ai", "vibecoding", "ec", "動画生成", "スタートアップ"]
published: true
---

株式会社エクスブリッジ（名古屋）は、「AIの価値と収益を社会へ循環させる」をミッションに、複数のAIプロジェクトを並行して開発・運営しています。プログラマー社長が自らバイブコーディングで構築し、すべてOSSまたは実サービスとして公開しています。

---

## URL2AI — URLをAIの入力に

**https://exbridge.jp/vwork.html**

URLを入力として、AIがあらゆるコンテンツを生成するプラットフォームです。

- **画像生成**: URLのコンテンツから画像プロンプトを生成し、ERNIE-Image-Turboで生成
- **動画生成**: Kurageパイプラインと連携してショート動画を生成
- **小説生成**: URLの内容からショートフィクションを生成
- **スライド生成**: URLからプレゼンテーション用スライドを自動構成

さらに、これらの機能を **x402 AI Agent** としてAPIマーケット（PayAPI Market）に公開。`x402` プロトコルに対応した「使った分だけ支払う」マイクロペイメント型のAPIを提供しています。

```
URL → URL2AI → 画像 / 動画 / 小説 / スライド
                   ↓
           x402 AI Agent として公開
           PayAPI Market に掲載
```

---

## AIxEC — ECサイト運営のAI化

**https://aixec.exbridge.jp**

楽天市場・Amazonの商品を自動登録・管理し、AIを使って発信力・集客力・収益力を高めるECプラットフォームです。

### 商品登録の自動化
- 楽天市場ランキングを定期巡回してAIxECに自動登録
- JANコードから商品詳細・説明文をAIが生成
- 書籍・AI PC・トレカ・サプリ等のジャンルに対応

### 発信力強化（AIxSNS・AIxTube）
- **AIxSNS**: 内製SNSで商品情報・ニュース・生成コンテンツを自動投稿
- **AIxTube**: 商品説明動画・Reels動画を自動生成して一覧表示
- Buzbloggerがトレンド投稿を収集 → AIが紹介文を生成 → AIxSNSに投稿

### アフィリエイト自動収益化
- go.phpでAmazon・楽天へのアフィリエイトリンクを管理
- 全投稿の末尾に自動でアフィリエイトリンクを付加
- simpletrack.phpでクリック数・流入元を計測

---

## Kurageプロジェクト — 動画生成AIシステム

**https://aiknowledgecms.exbridge.jp/kuragev.php**
**https://github.com/katsushi2441/kurage**

URLや音楽ファイルから、AIが自動で動画を生成するシステムです。

### 3つの動画生成機能

**① X投稿 → ショート動画（kuragev.php）**
XのバズりツイートURLを入力すると、AIが脚本・画像・ナレーション・動画を自動生成。

**② 音楽ファイル → 歌詞字幕MV（scripted-mvv.php）**
MP3をアップロードすると、Demucsでボーカル分離→ faster-whisperで歌詞抽出→AI画像生成→歌詞字幕付き動画を生成。

**③ Horizon-AIニュース → ニュース動画（horizonv.php）**
Horizonが収集したAI・Web3ニュースから、毎日自動でニュース番組風動画（12シーン・約2分）を生成。

### 技術スタック
- **脚本生成**: Ollama（gemma4:e4b）
- **画像生成**: ERNIE-Image-Turbo（LAN内GPUサーバー）
- **音声合成**: edge-tts（日本語TTS）
- **動画合成**: HyperFrames API
- **バックエンド**: Python FastAPI（port 18200）
- **フロントエンド**: PHP on heteml

---

## VWork — バイブコーディングフレームワーク

**https://exbridge.jp/vwork.html**
**https://katsushi2441.github.io/vwork/**

「システム開発のアウトソーシング時代は終わる」という確信のもと、経営者が自らAIと対話しながらシステムを内製できるよう支援するフレームワークです。

### 提供内容

- **セミナー**: 入門編・基礎編（名古屋）で経営者向けバイブコーディングを実践指導
- **VWorkフレームワーク**: Claude Code・Codex等との協働手順・テンプレート・プロンプト集
- **ブログ**: GitHub Pages / Zenn / はてなブログで技術知識と実践例を継続発信

### 発信媒体

| 媒体 | URL | 内容 |
|---|---|---|
| GitHub Pages | https://katsushi2441.github.io/vwork/articles/ | AI OSS技術解説 |
| Zenn | https://zenn.dev/katsushi2441 | 同上（Zenn連携） |
| はてなブログ | 経営者向け記事 | バイブコーディング・内製化 |

---

## まとめ

エクスブリッジは「AIを使う会社」ではなく、**「AIシステムを自分たちで育てる会社」** です。

- URLから動画・画像・小説を生成し、APIとして公開（URL2AI）
- ECサイトの商品登録・発信・収益化をAIで自動化（AIxEC）
- あらゆるコンテンツを動画化するパイプラインを構築（Kurage）
- その開発ノウハウをバイブコーディングとして経営者に提供（VWork）

すべてのシステムはバイブコーディングで内製し、外注コストゼロで動いています。

**株式会社エクスブリッジ**
https://exbridge.jp/
