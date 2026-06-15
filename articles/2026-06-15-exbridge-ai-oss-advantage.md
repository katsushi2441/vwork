---
title: "AI導入支援企業が増える中、AI × OSSで戦うエクスブリッジの競争優位性"
emoji: "🔧"
type: "tech"
topics: ["aiagent", "oss", "生成ai", "個人開発", "バイブコーディング"]
published: true
---

# AI導入支援企業が増える中、AI × OSSで戦うエクスブリッジの競争優位性

「AI導入支援」を謳うIT企業が急増している。ChatGPTを組み込んだSaaS、社内ドキュメント検索ツール、コールセンター向けの応答自動化——多くは既存のクラウドAI APIを接続するだけで、提供価値の差別化が難しい。

株式会社エクスブリッジは別の路線を選んだ。**AIとOSSを組み合わせて自社プロダクトを内製し、その過程で培った技術を顧客向けソリューションに還元する**。

この記事では、エクスブリッジがどんなOSSをどのプロジェクトで使ってきたか、そしてなぜその蓄積が競争優位になるのかを整理する。

---

## AI導入支援の「層」の違い

現在市場にある「AI導入支援」はざっくり3層に分かれる。

| 層 | 内容 | 技術依存先 |
|----|------|-----------|
| API接続層 | OpenAI/Claudeを既存システムに繋ぐ | クラウドAI API |
| ラッパー層 | SaaSを組み合わせてワークフローを構築 | NoCodeツール群 |
| OSS活用層 | ローカルLLM・OSS群でシステムを自作 | OSSエコシステム |

エクスブリッジが狙うのはOSS活用層だ。プロプライエタリAPIへの依存を最小化しながら、OSS群を組み合わせてゼロから動くシステムを作る。API料金の上昇やサービス終了があっても、代替OSSに切り替えればいい。

---

## 実際に使ってきたOSSと開発事例

### Kurage — AI動画自動生成システム

記事URLを渡すと2分のAI解説動画を自動生成するシステム。以下のOSSをパイプライン状に組み合わせている。

| OSS | 役割 |
|-----|------|
| **FastAPI + Uvicorn** | バックエンドAPI |
| **edge-tts** | Microsoft無償TTSによるナレーション生成 |
| **Pillow** | 画像合成・サムネイル生成 |
| **BeautifulSoup4** | 記事URL解析・テキスト抽出 |
| **ffmpeg** | 音声・静止画からMP4動画を合成 |
| **Ollama** | ローカルLLMによるスクリプト生成 |
| **yt-dlp** | YouTube字幕抽出・動画情報取得 |

クラウドAIは動画スクリプト生成にのみ使用し、TTS・画像・動画合成はすべてローカルOSSで完結させている。API料金を最小限に抑えながら、1本あたり数分で動画が生成できる。

### kbookorbit — 自社向け電子書籍管理システム

epub/cbz/pdf対応の電子書籍リーダー。SaaSを使わず完全自前で構築した。

| OSS | 役割 |
|-----|------|
| **NestJS + Fastify** | バックエンド（REST API + WebSocket） |
| **Vue 3 + Pinia** | フロントエンド |
| **TailwindCSS** | UI |
| **PostgreSQL** | 書籍・ファイルメタデータ管理 |
| **Socket.io** | リアルタイム通知 |
| **@embedpdf/vue-pdf-viewer** | PDFium WebAssemblyによるブラウザPDF表示 |
| **pdftoppm** | PDF→JPEG変換（CBZ形式への変換に使用） |

大容量PDFがWebAssemblyのメモリ制限で開けないという問題に直面した際、PDFをCBZ（画像ZIP）に変換して解決した。外部SaaSでは不可能な対処法で、OSS活用ならではの柔軟性が活きた。

### RQDB4AI — 非同期AIジョブ基盤

LLM処理など重い処理をHTTPリクエストのタイムアウト内で完結させず、非同期キューに逃がすための基盤。

| OSS | 役割 |
|-----|------|
| **FastAPI** | ジョブ投入・ステータス確認API |
| **Redis + RQ** | ジョブキューと非同期ワーカー |
| **Pydantic** | リクエスト・レスポンスの型管理 |

AIワーカーとWebサーバを分離することで、「LLMが処理中でもUIがフリーズしない」体験を安価なインフラで実現した。

### URL2AI / MCP — AIエージェント外部ツール基盤

URLからコンテンツを抽出・変換してAIエージェントに渡すツール群。

| OSS | 役割 |
|-----|------|
| **FastMCP** | MCP（Model Context Protocol）サーバ実装 |
| **FastAPI** | 各種変換API |
| **Jina Reader** | Webページを読みやすいテキストに変換 |

Claude CodeなどのAIエージェントがMCP経由でWeb・GitHub・YouTubeを自律的に操作できる環境を構築した。

### Agent Reach + twitter-cli — X API不要のSNS連携

X（旧Twitter）の公式APIは月$100〜と個人開発には重い。twitter-cliというOSSをCookieベース認証で使うことで、X検索・投稿をAPIコストゼロで実現した。

| OSS | 役割 |
|-----|------|
| **Agent Reach** | AIエージェントへのインターネット能力付与 |
| **twitter-cli** | CookieベースX検索・投稿 |
| **feedparser** | RSS/Atom購読 |

AIエージェントがXでトレンドを調査し、その結果をもとにコンテンツを生成→投稿する流れを自動化している。

### airadio-scripted-mv — YouTube自動投稿

Kurage生成動画のYouTube投稿を自動化するツール。

| OSS | 役割 |
|-----|------|
| **google-api-python-client** | YouTube Data API v3 |
| **google-auth-oauthlib** | OAuth2認証 |

---

## OSSを「追いかける」仕組み：oss.php

GitHub Trendingから毎日AI系OSSをピックアップし、LLMで技術考察を生成して蓄積するページ（[AIGM OSS Timeline](https://aiknowledgecms.exbridge.jp/oss.php)）を運営している。

このページ自体もFastAPI + Vue 3 + PostgreSQLで構築したOSSベースのシステムだ。毎日OSSをトラッキングし続けることで、「今どのOSSが使えるか」の感度を実務チームが持ち続けられる。

AI導入支援企業の多くは、ベンダーのソリューションを販売する立場であるため、特定OSSへの深い知見を持ちにくい。エクスブリッジは自社で使って壊して直した経験が、そのまま知見として蓄積される。

---

## 競争優位性のまとめ

| 観点 | 一般的なAI導入支援 | エクスブリッジ |
|------|------------------|---------------|
| コスト構造 | クラウドAPI従量課金 | ローカルOSS中心 |
| 柔軟性 | ベンダー制約あり | OSS切り替え可能 |
| 技術深度 | 接続設定レベル | システム設計・実装レベル |
| OSS知見 | 限定的 | 日常業務で継続蓄積 |
| カスタマイズ | 困難 | ソース変更可能 |

「AIを使える会社」は増えた。「AIとOSSで実際に動くシステムを作り続けている会社」はまだ少ない。

エクスブリッジが目指すのは後者であり、OSSへの深い理解と実装経験が、汎用的な「AI導入支援」との差になる。
