---
title: "Hermes と OpenClaw の役割分担 — orchestration と capability を分離する"
description: "Autonomous Market Pipeline を構成する際の Hermes（実行制御）と OpenClaw（スキル管理）の役割分担、および Claude と Ollama の WHY/WHAT 分離について。"
date: 2026-05-23
tags: [AIエージェント, Hermes, OpenClaw, 自動化, アーキテクチャ]
status: published
layout: default
permalink: /blog/2026-05-23-hermes-openclaw-roles.html
---

# Hermes と OpenClaw の役割分担 — orchestration と capability を分離する

[Autonomous Market Pipeline](/blog/2026-05-23-autonomous-market-pipeline.html) を構成する中で、Hermes と OpenClaw の役割分担はかなり重要だと感じている。

この2つを混ぜてしまうと、AIエージェント構成はすぐ破綻する。

今回の構成では、

- **Hermes** = 実行制御・時間管理
- **OpenClaw** = スキル・能力管理

として分離している。

---

## Hermes は「いつ動くか」を管理する

Hermes は、cron や workflow orchestration に近い役割。

- 定時実行
- Queue管理
- Retry
- Pipeline実行
- 実行順序制御

つまり「何をするか」ではなく、「いつ・どの順番で・どう流すか」を担当する。

Autonomous Market Pipeline では：

```
市場監視
↓
記事生成
↓
SEO反映
↓
SNS投稿
↓
分析
```

という一連の流れを時間軸で管理する必要がある。その役割を Hermes が担う。

---

## OpenClaw は「何ができるか」を管理する

一方 OpenClaw は Skill Registry に近い。

- Facebook投稿
- dev.to投稿
- RSS解析
- [AIxTube](https://aixec.exbridge.jp/aixtube.php) 生成
- [AIxEC](https://aixec.exbridge.jp/) 商品登録
- OGP画像生成

などの「能力」を持つ。OpenClaw は、AIエージェントが持つ「手」や「道具箱」に近い。

Hermes が「今は Facebook 投稿スキルを実行」と判断し、OpenClaw 側の capability を呼び出す。

---

## 「いつ動くか」と「何ができるか」を分離する

この分離はかなり重要。

もし OpenClaw に scheduler 的な役割まで持たせると、状態管理・実行順序・時間管理・スキル管理が全部混ざり始める。逆に Hermes 側が capability を持ち始めると、workflow engine と skill system が密結合になる。

だから、

- **Hermes** = orchestration
- **OpenClaw** = capability

に分けるのはかなり自然。

---

## Claude と Ollama の役割分担も同じ

この構成では、

- **Claude** = WHY（市場判断・戦略・文脈理解・意図決定）
- **Ollama/Gemma** = WHAT（大量バッチ処理・ローカル推論・スコアリング）

という分離もしている。

Claude が「なぜ動くか」を決め、Ollama が「実際の処理」を回す。

---

## AI が「業務」ではなく「事業サイクル」を回す

重要なのは、単なる AI 自動化ではないこと。

従来の自動化：

```
人間 → 指示 → システム
```

Autonomous Market Pipeline が目指す循環：

```
AI
↓
市場観測
↓
判断
↓
コンテンツ生成
↓
投稿
↓
流入獲得
↓
収益化
↓
次の行動
```

AI が単なる作業ツールではなく、市場サイクルそのものを回す構造。それが Autonomous Market Pipeline の本質だと思っている。

---

[エクスブリッジ](https://exbridge.jp/) / [AIxEC](https://aixec.exbridge.jp/) / [VWork](https://exbridge.jp/vwork.html)
