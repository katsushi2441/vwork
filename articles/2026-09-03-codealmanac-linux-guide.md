---
title: "CodeAlmanacとは？AIエージェントに「コードに書けない文脈」を持たせるYC発OSS——使い方と、macOS専用だったのでLinux対応を本家に送った話"
emoji: "📚"
type: "tech"
topics: ["codealmanac", "claudecode", "codex", "oss", "systemd"]
published: true
---

Claude CodeやCodexでコードを書いていると、必ずぶつかる問題があります。**エージェントは「なぜこの設計になっているか」「過去に何が壊れたか」を知らない**。コードには現在の形しか書かれていないからです。

[CodeAlmanac](https://github.com/AlmanacCode/codealmanac)（Y Combinator S26・Apache-2.0・GitHubスター約1,000で急伸中）は、この問題への回答です。この記事は、その仕組みと使い方、そして**現状macOS専用だったため、当社（名古屋のAIシステム開発会社・エクスブリッジ）がLinux対応を実装して本家にプルリクエストを送るまで**の記録です。

## CodeAlmanacとは

「**AIコーディングエージェントが維持する、コードベースの生きたwiki**」です。

- リポジトリ内の `almanac/` ディレクトリに、**プレーンなmarkdown**で知識を蓄積します——設計判断の理由、過去の障害、守るべき不変条件、ファイルやサービスを横断するワークフロー
- ページはGitで普通にレビューされ、コードと一緒にバージョン管理されます
- バックグラウンドジョブが3つ動きます: **Sync**（5時間ごとにCodex/Claude Codeの会話ログを走査して有用な知識をwikiへ収穫）、**Garden**（24時間ごとに古い・重複した知識を手入れ）、**Update**（CLI自動更新）

つまり「エージェントとの会話で得られた文脈が、会話の終了とともに消える」のを止める道具です。

## 使い方（macOS）

```bash
uv tool install codealmanac@latest
codealmanac setup          # 対話セットアップ（Claude Code利用なら --yes --runner claude）

cd your-repo
codealmanac init           # wikiを作る
codealmanac search "検索語"
codealmanac serve          # ローカルWebビューア
```

必要環境はPython 3.12+。セットアップでエージェント向けの指示と、上記3ジョブが登録されます。

## 実測: Linuxでは動かなかった

当社の開発機はLinuxです。導入してみると、CLI自体は動くものの、**バックグラウンド3ジョブがmacOSのlaunchd専用実装**のため登録できません。READMEにも「Supported today: macOS」と明記されています。

コードを読むと、スケジューラは `SchedulerAdapter` というポートで綺麗に抽象化されていて、launchdアダプタが1実装として刺さっている設計でした。**この形なら、systemdアダプタを1枚足せばLinux対応になる**。

## Linux対応を実装して、本家にPRを送りました

- `SystemdSchedulerAdapter` — launchdアダプタと1対1対応（ジョブごとにsystemdユーザータイマー+oneshotサービス。`RunAtLoad`は`OnActiveSec=0`、`StartInterval`は`OnUnitActiveSec`で再現）
- プラットフォーム自動選択（macOS→launchd／Linux→systemd）と、定義ファイルパスのXDG対応
- テスト: 新規4本+既存テストのプラットフォーム非依存化で、**Linux上で568件全パス**。実機でもインストール→即時実行→クリーン削除まで確認

提出したPRはこちらです: [AlmanacCode/codealmanac#73 — feat: add Linux support via systemd user timers](https://github.com/AlmanacCode/codealmanac/pull/73)

### マージまでの間、Linuxで今すぐ使うには

当社フォークのブランチからインストールできます。

```bash
uv tool install "git+https://github.com/katsushi2441/codealmanac@feat/linux-systemd-scheduler"
codealmanac setup --yes --runner claude
codealmanac automation status   # systemdユーザータイマーとして登録されているか確認
```

## Krayin・Zammadに続く「本家に返す」3周目

当社はこの型で、8月にCRMの[Krayin日本語化(2,066キー・本家マージ済み)](2026-08-18-krayin-crm-japanese-guide.html)、今週ヘルプデスクの[Zammad日本語化(5,123エントリ・本家Weblate 100%)](2026-09-03-zammad-japanese-guide.html)を本家に還元してきました。今回は翻訳ではなく**機能実装での貢献**です。OSSの「日本の会社が使えない理由」を実測で特定し、直して本家に返す——保守は本家に引き継がれ、日本のユーザー全員が使えるようになります。

AIエージェントに社内の判断・文脈を記憶させる運用（CLAUDE.mdやメモリの書式設計）は当社が日々実践している領域です。導入や運用設計の相談は[こちら](https://kurage.exbridge.jp/)からどうぞ。
