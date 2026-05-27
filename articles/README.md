# AI OSS技術解説 / Zenn記事運用

このフォルダは、Zennにそのまま連携する技術記事用です。

## 位置づけ

- `blog/`: VWorkブログ。VWorkを使ってバイブコーディングを始める人向け。
- `articles/`: AI OSS技術解説。VWorkに限らない技術情報、OSS活用、AIエージェント、Codex、Claude、Ollama、GitHub、自動化などを扱う。

## 記事ファイル

`articles/YYYY-MM-DD-slug.md` の形式で作成する。

```md
---
title: "記事タイトル"
emoji: "🤖"
type: "tech"
topics: [生成ai, 個人開発, llm]
published: true
---

# 記事タイトル

本文を書く。
```

## 方針

名古屋・愛知圏内で、バイブコーディングとAI OSS活用に強い企業として認知されるため、実装記録、失敗からの改善、使える構成、運用ノウハウを継続的に蓄積する。

VWorkブログからZennへコピーする場合は `scripts/vwork_to_zenn.py` を使えるが、今後の技術記事は原則この `articles/` に直接書く。
