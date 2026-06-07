---
title: "Kurage Agent Deckをマルチサーバ対応にした：OpenClaw経由でCodex/Claudeを各サーバへ届ける"
emoji: "🕹️"
type: "tech"
topics: ["aiagent", "codex", "claude", "openclaw", "automation"]
published: true
---

# Kurage Agent Deckをマルチサーバ対応にした：OpenClaw経由でCodex/Claudeを各サーバへ届ける

スマホからAIエージェントに作業を頼むだけなら、ブラウザからローカルのCodex CLIを呼べば十分に見えます。

しかし実運用では、作業対象のサーバが1台とは限りません。

今回のKurage Agent Deck、略称kdeckでは、スマホのブラウザから、複数サーバ上のCodex CLI / Claude CLIへ作業を渡せる構成にしました。

ポイントは、kdeckから各サーバへSSHで直接コマンドを投げるのではなく、各サーバにOpenClaw gatewayを置き、kdeck APIからOpenClaw経由でAIエージェントを実行することです。

![Kurage Agent Deck system overview](https://katsushi2441.github.io/vwork/articles/kdeck-system.png)

---

## なぜマルチサーバ化が必要だったか

運用しているAIシステムが増えてくると、サーバごとに役割が分かれます。

今回の構成では、次のように役割を分けています。

```text
192.168.0.3  kdeck統合管理サーバ
192.168.0.2  Hermesスケジューラ担当
192.168.0.14 AIxEC API server担当
192.168.0.11 Hyperframes動画生成担当
```

たとえば、AIxECのAPIを移行したいとき、統合管理サーバ側のCodexが、AIxEC API server側のCodexへ「この要件で確認して」「このフォルダを見て」「このAPIを直して」と指示できる必要があります。

また、動画生成の問題を調べたいときは、Hyperframesが動いているサーバでClaudeやCodexにログや生成物を見てもらいたい。

このとき、kdeckが単に「管理サーバ上のCLIを呼ぶだけ」だと、実際に問題が起きているサーバの文脈に入れません。

そこで、kdeckをマルチサーバAIエージェントの入口にしました。

---

## 実現した構成

kdeckの入口はスマホのブラウザです。

```text
Smartphone
  -> https://kurage.exbridge.jp/kdeck.php
  -> PHP proxy with Kurage common X login
  -> kdeck FastAPI on 192.168.0.3:18301
  -> OpenClaw remote gateway selected by target_agent
     -> 192.168.0.2:18789  Hermes scheduler agent
     -> 192.168.0.14:18789 AIxEC API server agent
     -> 192.168.0.11:18789 Hyperframes video agent
```

ブラウザは直接FastAPIやOpenClaw gatewayへアクセスしません。

ブラウザから見えるのは `kurage.exbridge.jp/kdeck.php` だけです。  
PHP側で共通ログインを通し、API tokenはサーバ側に隠します。

FastAPI側は `kdeck-api.service` として常駐し、`192.168.0.3:18301` で動かしています。

各実行先サーバには、OpenClaw gatewayを `openclaw-gateway.service` として常駐させています。

---

## サーバごとのフォルダを混同しない

この構成で重要なのは、フォルダ指定の考え方です。

管理サーバの `/home/kojima/work/...` と、リモートサーバの `/home/kojima/exdirect/...` は別物です。

kdeckでは、画面上で次の情報を分けて持つ必要があります。

- `local_cwd`: kdeck統合管理サーバ側の作業フォルダ
- `target_agent`: 実行先サーバ
- `cwd`: 実行先サーバ側の作業フォルダ
- `remote_llm_backend`: Codex CLIかClaude CLIか
- `remote_model`: 実行モデル

今回の実行先ごとのルールは次の通りです。

| 実行先 | 役割 | リモート側の主な作業root |
| --- | --- | --- |
| `hermes-192-168-0-2` | Hermesスケジューラ | `/home/kojima/exdirect` |
| `aixec-api-192-168-0-14` | AIxEC API server | `/home/kojima/bittensorman/aidexx` |
| `hyperframes-192-168-0-11` | Hyperframes動画生成 | `/home/kojima/exdirect` |

ここを混同すると、管理サーバには存在するフォルダをリモートサーバで指定してしまったり、逆にリモートサーバ固有のリポジトリを管理サーバに勝手にcloneしてしまったりします。

kdeckは、単なるリモートシェルではなく「どのサーバの、どの役割のAIエージェントに頼むか」を明示するための画面です。

---

## SSH直接実行ではなくOpenClaw経由にした理由

最初にやりがちな実装は、kdeck APIからSSHでリモートサーバへ入り、そこで `codex` や `claude` コマンドを直接実行する方法です。

これは手軽ですが、今回の目的とは違います。

やりたいことは、管理サーバが別サーバのAIエージェントへ、メッセージ、要件、作業フォルダ、状態を渡すことです。

そのため、通常の作業実行ではSSHを使いません。

SSHは次の用途に限定します。

- OpenClawのインストール
- gateway serviceの設定
- systemd serviceの確認
- 認証や接続のメンテナンス

通常のAI作業はOpenClaw gateway経由にします。

成功判定も、単に「SSHコマンドが終了した」ではなく、kdeck APIの結果に `control_plane: openclaw` が含まれ、選択したエージェントが完了結果を返したことを見ます。

---

## Codex CLI / Claude CLIの扱い

kdeckの画面では、リモートLLM backendとして `codex-cli` と `claude-cli` を選べるようにしています。

内部的にはOpenClawのmodel名へ変換します。

```text
codex-cli  -> openai/gpt-5.5
claude-cli -> claude-cli/claude-sonnet-4-6
```

重要なのは、`codex-cli` は単なるOpenAI API呼び出しではなく、Codex app-server harnessを通すという点です。

つまり、リモートサーバ上でCodex CLIとして作業するための経路です。

今回、`.2`、`.14`、`.11` の各サーバで、OpenClaw gatewayからCodex CLI / Claude CLIの両方を実行できることを確認しました。

---

## service化したもの

今回のマルチサーバ対応では、プロセスを手動起動に残さず、systemd user serviceに寄せました。

管理サーバ側:

```text
kdeck-api.service
  -> /usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 18301
```

各リモートサーバ側:

```text
openclaw-gateway.service
  -> OpenClaw gateway
  -> listen: 0.0.0.0:18789
```

これにより、kdeck APIと各OpenClaw gatewayが再起動後も復帰しやすくなります。

実行確認では、次の組み合わせで `Return OK only` を投げ、すべて `OK` を返しました。

- `.2` + Codex CLI
- `.2` + Claude CLI
- `.14` + Codex CLI
- `.14` + Claude CLI
- `.11` + Codex CLI
- `.11` + Claude CLI

---

## 何ができるようになったか

この構成で、スマホのブラウザから次のような作業ができます。

- Hermesサーバのスケジュールやenqueue設定を確認する
- AIxEC API server側でAPIやdashboard reportを調査する
- Hyperframesサーバ側で動画生成やYouTube投稿の手順を確認する
- 管理サーバのCodexから、別サーバのCodex / Claudeへ要件付きで作業を渡す
- 会話履歴、対象サーバ、対象フォルダ、実行backendをセットで残す

特に大きいのは、「別サーバへ作業を頼むときに、文脈を文章で渡せる」ことです。

これまでは、サーバ移行や障害調査のとき、片方のターミナルで見た内容を別のサーバ作業へ手で伝える必要がありました。

kdeck + OpenClaw構成では、管理サーバ側のAIエージェントが、別サーバのAIエージェントへ作業対象と要件を渡せます。

これは、スマホ対応の作業画面というより、LAN内のAI作業チームを束ねる小さな操作盤に近いです。

---

## 今後の課題

今回の構成は動きましたが、まだ完成ではありません。

今後は次の整理が必要です。

- kdeck上で、サーバごとのフォルダ候補をもっと見やすくする
- タスク履歴を「どのサーバで何をしたか」で検索しやすくする
- 成功、失敗、実行中、承認待ちをUIで明確に分ける
- 秘密情報がブラウザや共有メモリへ出ないようにする
- 複数サーバ間で作業要約を共有するSwarmClaw的な記憶を強化する

ただし、今回の段階で大事な線引きはできました。

kdeck本体は、特定アプリに依存しない汎用のAgent Deckです。  
AIxEC、Hermes、Hyperframes、VWorkなどの固有ロジックは、それぞれのリポジトリに置く。

kdeckは、スマホからそれらのAIエージェントへ安全に作業を渡すための共通入口として育てます。

---

## 関連

- Kurage Agent Deck: https://github.com/katsushi2441/kdeck
- VWork: https://katsushi2441.github.io/vwork/
- AI OSS技術解説: https://katsushi2441.github.io/vwork/articles/
