---
title: "公開6日で6,900スター。trycompai/crm——「AIに自己採点させない」エージェント主導CRMの設計を読む"
emoji: "📇"
type: "tech"
topics: [生成ai, oss, typescript, agent, crm]
published: true
---

2026年7月31日に公開され、**6日で6,900スター**を集めているリポジトリがあります。コンプライアンス自動化OSSのComp AIが出した **[trycompai/crm](https://github.com/trycompai/crm)**——「agentic-first CRM」を名乗る、MITライセンスのCRMです。

READMEの一文が、このプロダクトの全部を説明しています。

> A durable research agent is the product. The database is just where it writes things down.
> （常駐する調査エージェントが製品であり、データベースはそいつのメモ帳にすぎない）

普通の「AI CRM」はデータベースにチャット箱を付けたものですが、これは主従が逆です。設計を読んでいくと、AIエージェントを実務に組み込むときの答えがいくつも書かれていました。

## 逆転の設計：入力する人間がいない

従来のCRMの弱点は「営業が入力しない」ことに尽きます。trycompai/crm では、調査エージェントが**自分のスケジュールで常駐稼働**し、会社や人物を調べてレコードを埋め、次に見る対象を自分で決め、再確認の予定を自分で入れ、調査予算を使い切ったら止まります。リクエスト・レスポンス型ではないので、**ブラウザを閉じても働き続けます**。

## いちばんの読みどころ：確信度スコアが存在しない

このリポジトリで最も感心した設計判断です。

> No tool accepts a confidence score, because a model asked to grade its own certainty will, and it will be wrong in the direction that makes it look useful.
> （確信度を受け取るツールは1つもない。モデルに自己採点させれば採点はする——ただし「役に立って見える方向」に間違える）

代わりにこうなっています。

- ツールは**観測した事実だけ**を報告する（`crm.signature-block`＝署名欄にこう書いてあった、`github.account-identity`＝GitHubアカウントがこうだった）
- **証拠台帳（ledger）が証拠の強さを値付け**する。強い証拠だけがレコードに書かれる
- 弱い証拠はレコードに書かれず、**「人間が裁く提案」**に格下げされる

理由も明快です。「顧客について自信満々に間違った事実は、空欄より悪い。誰も間違いだと気づけないから」。

LLMの出力をそのままDBに書くシステムを作ったことがある人なら、この設計の意味が分かるはずです。**AIの自己申告を信用せず、観測と判定を分離する**——弊社でも決済APIの入金検証（ブラウザの「支払いました」を信じず、決済事業者に照会して4条件を突き合わせる）で同じ構造を採りましたが、それをCRMのデータ品質に適用した例は初めて見ました。

## 自走の仕組み：cronではなくリース付きワークキュー

エージェント本体は [eve](https://eve.dev)——Vercelの「ファイルシステム・ファースト」な永続エージェントフレームワーク上に作られています。ツールはファイル、スキルはMarkdown、スケジュールもファイルで、再デプロイをまたいでセッションが生き残ります。

- ワークキューは Postgres の `FOR UPDATE SKIP LOCKED` でリース取得。ディスパッチャが複数いても仕事が重複せず、**死んだ実行はリース期限切れで自動的に行を解放**する
- 「N分ごとに古い順で10件」のような処理は cron 式ではなく、タスク行の `dueAt` に持たせる
- エージェントが再確認したいときは `schedule_recheck` を呼ぶが、**理由の記述が必須**で、その理由は営業担当に表示される。READMEいわく「14日後に戻ってくる理由を言えないエージェントは、理由ではなくデフォルト値を持っているだけ」

## APIキーがゼロでも動く

外部データソースはすべてオプションで、**キーが1つも無くても動作します**。`read_crm_history` が自社のメールスレッド・会議・署名欄を読む——READMEはこれを「本人のアドレスからの返信ほど上等な証拠は、どんなデータベンダーも売ってくれない」と表現します。

キーを足すごとに「見える場所」が増える設計（LinkedIn=RapidAPI、Web調査=Perplexity）で、セッション開始時に**この環境で使える手段の一覧をエージェントに渡す**ため、無い機能を呼んで失敗しながら学ぶ無駄がありません。

```
[agent] on   LinkedIn (RAPIDAPI_KEY)
[agent] off  Web research (PERPLEXITY_API_KEY)
[agent] off  Company brand data (Settings → General)
```

## サンドボックスの引き算

エージェントには `bash` / `grep` / `glob` と `/workspace` を持つサンドボックスが与えられますが、**外部通信は deny-all、そして `DATABASE_URL` を渡しません**。

> A shell with credentials and egress is exfiltration-shaped even in an internal tool; a shell with neither is a text processor.
> （認証情報と外部通信を持つシェルは、社内ツールであっても「漏洩装置の形」をしている。両方を持たないシェルは、ただのテキスト処理器だ）

Web取得はアプリ側ランタイムで、Web検索はモデルプロバイダ側で実行されるため、シェルから顧客のメール本文が外に出る経路そのものが存在しない。**機能を足すのではなく経路を消す**タイプのセキュリティ設計です。

## 動かすには

スタックは TypeScript / **Bun** / Postgres / turborepo。`docker-compose.yml` が同梱されており、必須の環境変数は `DATABASE_URL`・`BETTER_AUTH_SECRET`・Google OAuth（ログイン用）程度。エージェントUIは各レコードの「Agent」タブに現れ、調査の手順・捨てたリードとその理由・判断に迷ったときの質問がそこに流れてきます。

生後6日のプロジェクトなので、仕様は今後も速く動くはずです。本番採用は追従コストを覚悟する段階ですが、**設計ドキュメントとして読む価値はいますでにあります**（[docs/agent.md](https://github.com/trycompai/crm/blob/main/docs/agent.md) が本体です）。

## 所感：バイブコーディングへの示唆

このリポジトリから持ち帰れるのは CRM の作り方ではなく、**AIを実務システムに組み込むときの規律**です。

1. **AIの自己申告（確信度）を信用しない。**観測だけ報告させ、判定は別の仕組みが行う
2. **弱い証拠は書き込まず、人間の裁定に回す。**「自信満々の間違い」は空欄より高くつく
3. **エージェントに渡さないものを先に決める。**DBの接続情報と外部通信を持たないシェルは、それだけで安全になる

私たちが業務システムを作るときに守っている「AIは文案を書く、決定は人間がする」「決済はサーバー側で裏取りする」と同じ思想が、より徹底した形でここにあります。6日で6,900スターという数字は、この規律への需要の大きさだと読んでいます。

リポジトリ: <https://github.com/trycompai/crm>（MIT License）
