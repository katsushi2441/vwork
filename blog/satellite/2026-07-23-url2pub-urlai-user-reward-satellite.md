---
title: "URLをAIで発信すると10,000 URLAI：URL2Pubの利用特典が始まりました"
description: "はてなブログ向け要約記事：URL2Pub利用者へ10,000 URLAIを自動配布する仕組みと、サービス利用をオンチェーンの還元につなげる狙いを紹介します。"
date: 2026-07-23
status: published
---

# URL2Pubの利用者へ10,000 URLAIを自動配布

URLを入力すると、AI VTuberのKurageさんがページを読み、告知文とブログ記事を生成して複数メディアへ配信する**Kurage URL2AI Publisher（URL2Pub）**に、利用者向けのURLAI特典が追加されました。

現在、URL2Pubを利用し、XアカウントとBaseウォレットを接続した方へ、**1人1回10,000 URLAIを先着1,000人に自動配布**しています。

[Kurage URL2AI Publisherを使う](https://url2ai.exbridge.jp/url2pub.php)

## サービスを使ってくれた人へ、オンチェーンで感謝を返す

今回の取り組みは、単にトークンを配るキャンペーンではありません。

URL2Pubを試してくれた人、実際の利用を通じて動作確認に協力してくれた人、URL2Pubから情報を発信してくれた人へ、感謝をURLAIとして返す仕組みです。

利用者がURL2Pubを使うことで紹介したい情報が発信され、運営側は実利用から改善点を見つけられます。そして、協力してくれた利用者へURLAIを届けます。

- URLを入力して告知文とブログ記事を生成
- AIxSNS、Bluesky、はてなブックマーク、ブログなどへ配信
- XアカウントとBaseウォレットごとに1回だけ申請
- RQDB4AIのキューへ送金ジョブを登録
- ローカルworkerがBankr APIを通じてURLAIを送金
- 送金結果を画面とBasescanで確認

配信先の一時的な障害など、利用者に責任がない理由で一部の投稿が失敗しても、URL2Pubを使ってくれたこと自体が特典の対象です。

## Webサーバーへ送金権限を置かない設計

公開Webサーバーは申請を受け付け、RQDB4AIへジョブを登録しますが、トークン送金は行いません。

実際の送金はローカル環境の専用workerが担当します。BankrのAPIキーはブラウザや公開Webサーバーへ渡さず、Xアカウント、ウォレット、申請ID、送金台帳を照合して二重送金を防ぎます。

実装後には1 URLAIの自己送金を行い、APIの成功応答だけでなく、Base上でトランザクションが成功したことまで確認しました。

[検証トランザクションをBasescanで確認する](https://basescan.org/tx/0x3451badfa8805cff131691cfcf944870150461db0b0708a34c908bf6ec357f85)

## トークン発行より先に、使う理由を作る

URLAIは、URLを起点にAIが情報を読み、生成し、発信するURL2AIプロジェクトから生まれたトークンです。

価格の話だけを先行させるのではなく、実際に動くサービスを利用した人との接点を作る。利用、発信、改善、還元が一つの循環になるように運営する。今回の利用特典は、そのための最初の仕組みです。

詳しい配布フロー、RQDB4AIによるキュー管理、二重送金を防ぐ設計、バイブコーディングで事業の循環まで実装した過程は、VWork Blogの本編にまとめています。

**本編：** [「使ってくれてありがとう」をオンチェーンで返す：URL2Pubに10,000 URLAI利用特典を実装しました](https://katsushi2441.github.io/vwork/blog/2026-07-23-url2pub-urlai-user-reward.html)

関連リンク：

- [Kurage URL2AI Publisher](https://url2ai.exbridge.jp/url2pub.php)
- [URL2AIプロジェクト](https://url2ai.exbridge.jp/)
- [URL2Pub GitHubリポジトリ](https://github.com/katsushi2441/url2pub)

URLAIの価格や将来の利益を保証するものではありません。実際のサービス利用とプロジェクト参加をつなぐための利用特典です。
