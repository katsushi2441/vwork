---
title: "Hermes + OpenClaw + Claude + Ollama で商品登録を全自動化した"
emoji: "🛒"
type: "tech"
topics: [生成ai, 個人開発, llm]
published: true
---

# Hermes + OpenClaw + Claude + Ollama で商品登録を全自動化した

[AIxEC](https://aixec.exbridge.jp/) の商品登録を、AIエージェントが完全に自律して動かす仕組みをバイブコーディングで構築した。

今日、その仕組みが実際に動き始めた。

## 何を作ったか

```
Hermes cron（毎日6時・18時）
    ↓
[Step 1] marketing_context.py
    現在のAIxEC状況を整理 → marketing_context.md

[Step 2] Claude Code OAuth
    「次に登録すべき楽天市場ジャンルを1つ選べ」
    → market_task.generated.json（ジャンル・キーワード・方針）

[Step 3] Ollama gemma4:e4b
    楽天市場APIで商品候補を収集
    → バッチでスコアリング（accept/reject + 0-100点）

[Step 4] AIxECへ登録
    スコアの高い商品だけ登録

[Step 5] AIxSNSへ投稿
    「何のジャンルで何件登録したか」を自動通知
```

人間がやることは何もない。Hermesが定時に起動し、ClaudeとOllamaが判断し、AIxECに商品が増え、[AIxSNS](https://aixec.exbridge.jp/sns.php)に結果が流れる。

## 役割分担

| ツール | 役割 |
|---|---|
| **Hermes** | スケジューラ。毎日6時・18時にパイプラインを起動 |
| **OpenClaw** | スキル管理。AIxECスキルを保持し手動トリガーも可能 |
| **Claude Code OAuth** | 戦略判断。市場状況を読んで「次のジャンル」を決める |
| **Ollama gemma4:e4b** | 商品評価。候補をバッチ処理してスコアリング |

ClaudeはマーケティングのWHYを判断し、Ollamaは個別商品のWHATを判断する。役割が明確に分かれている。

## バイブコーディングで開発した

このパイプライン全体は、[VWork](https://exbridge.jp/vwork.html)のバイブコーディングで作った。

コードを一行一行書いたわけではない。

「AIxECに楽天市場商品を自動登録したい」「Claudeに戦略を立てさせて、Ollamaに選定させたい」「Hermesで定期実行したい」という意図をCodexに伝え、Codexが実装・改善を繰り返した。

`autonomous_market_pipeline.py`、`claude_select_market_task.py`、`register_market_task_worker.py` という3つのスクリプトが生まれ、それぞれが明確な役割を持つ構造になった。

HermesとOpenClawのインストールと設定も、Codexが手順を調べて実行した。

「作りたいものの意図を持つ人間」と「実装するAI」の分業が、そのまま開発フローになっている。

## 実際に動いた

ドライランで確認した出力：

```
candidates=10
ollama scored 3/10 selected=3
selected id=dry score=95 経営戦略（ベーシック＋）
selected id=dry score=95 改訂版 強い会社が実行している「経営戦略」の教科書
selected id=dry score=95 仮想と現実で読み解く組織マネジメント
pipeline complete
```

Ollamaがジャンルの方針（AIxECはAI・経営・業務効率化を優先）に沿って商品を選んでいる。

次回の本番実行は今日18時。

## これが意味すること

商品を探す、選ぶ、登録する、告知する。この一連の業務をAIが自律してこなす。

人間がやることは、意図を決めることだけだ。

どのジャンルを攻めるか、何を基準に選ぶか。その判断基準を `SKILL.md` に書いておけば、ClaudeとOllamaがそれを読んで動く。

AIxECは、AIエージェントが商品を登録し、[AIxTube](https://aixec.exbridge.jp/aixtube.php)で動画を作り、AIxSNSで告知するという「AIが自律運営するEC」の実験だ。

今日、その自律サイクルに「自動で商品を仕入れる判断」が加わった。

---

[エクスブリッジ](https://exbridge.jp/) / [AIxEC](https://aixec.exbridge.jp/) / [VWork](https://exbridge.jp/vwork.html)
