---
title: "Kurage Mail — Roundcubeをhetemlに導入し、Codexからメール処理できる入口を作る"
emoji: "📬"
type: "tech"
topics: ["php", "roundcube", "imap", "smtp", "codex"]
published: true
---

# Kurage Mail — Roundcubeをhetemlに導入し、Codexからメール処理できる入口を作る

Kurage Mail は、heteml上にRoundcubeを配置し、既存メールアカウントをWebから読めるようにしたうえで、Codexからもメール処理を実行できるようにするための実験です。

目的は、単なるWebメールではありません。

メールを「人間が読む画面」に閉じ込めず、AIエージェントが確認、分類、抽出、転送、分析できる業務データとして扱えるようにすることです。

今回構築した構成では、Roundcube本体を `kurage.exbridge.jp/roundcube/` に置き、hetemlのIMAP/SMTPアカウントでログインできるようにしました。さらに外部POPアカウントの簡易ビューを追加し、Yahooメールや別ドメインの注文メールも同じ運用画面から確認できるようにしています。

---

## 構成

基本構成は次の通りです。

```text
Browser / Codex
  ↓
https://kurage.exbridge.jp/roundcube/
  ↓
Roundcube on heteml
  ├─ IMAP: imap4.hetemail.jp
  ├─ SMTP: smtp.hetemail.jp
  └─ custom PHP views
       ├─ recipient filter inbox
       ├─ external POP inbox
       └─ message forward via SMTP
```

Roundcubeは、hetemlのPHP環境で動かしやすいOSS Webメールです。IMAPでサーバ上のメールを残したまま閲覧でき、SMTPで送信もできます。

今回はRoundcube本体に加えて、次のカスタマイズを入れました。

- 宛先別に絞り込む受信箱ビュー
- 外部POPアカウントの一覧表示
- 外部POPメールの本文表示
- multipartメールの本文抽出
- ISO-2022-JPメールのUTF-8変換
- CodexからSMTP転送できる処理

---

## なぜRoundcubeを使うか

メール処理をAI化したいだけなら、最初からIMAP/SMTPを直接叩くPythonスクリプトでも実現できます。

それでもRoundcubeを置いた理由は、人間の確認画面を残したかったからです。

AIエージェントにメールを処理させる場合でも、最初から完全自動化するのは危険です。

- どのメールを対象にしたか
- 本文が正しく読めているか
- 文字化けしていないか
- 転送先や処理対象が正しいか
- 人間が確認すべきメールを除外できているか

これらを確認できる画面が必要です。

Roundcubeは、人間用のメール画面として使えるだけでなく、PHPカスタマイズを追加しやすいので、AI処理の入口として扱いやすいと感じました。

---

## 外部POPビューを追加する

今回のポイントは、Roundcubeログイン対象のhetemlメールだけでなく、外部アカウントも読めるようにしたことです。

たとえばYahooメールはPOPで取得し、サーバ上のメールを削除せずに最新メールを一覧表示します。

```text
kurage_external.php?account=yahoo
kurage_external.php?account=yahoo&msg=16
```

このビューでは、POPの `STAT`、`TOP`、`RETR` を使っています。

- `STAT`: 件数確認
- `TOP`: ヘッダだけ取得して一覧表示
- `RETR`: 本文取得

本文表示では、メールを削除しないことを前提にしています。AI処理の検証中に元メールを消してしまう事故を避けるためです。

---

## multipartと文字化けへの対応

日本語メールで必ず出てくる問題が文字コードです。

今回も、Yahoo側のメールで `multipart/alternative` かつ `charset="iso-2022-jp"` のメールがあり、そのまま表示するとMIME boundaryやISO-2022-JPのエスケープ文字が画面に出てしまいました。

そこで、本文抽出を次の順序にしました。

1. メールヘッダと本文を分離する
2. `Content-Type` からboundaryを読む
3. multipartをpartごとに分解する
4. `text/plain` を優先する
5. なければ `text/html` をテキスト化する
6. `Content-Transfer-Encoding` をdecodeする
7. `charset` を見てUTF-8へ変換する

これで、楽天カード利用通知のようなISO-2022-JPメールも、UTF-8の日本語本文として表示できるようになりました。

メール処理では、AIモデルに投げる前の正規化が重要です。文字化けした本文をLLMに渡すと、分類や抽出の精度以前に、入力データとして壊れています。

---

## Codexからメールを転送する

さらに、Codexから特定メールをSMTPで転送できることも確認しました。

流れは次の通りです。

```text
POPで対象メールを取得
  ↓
件名・From・To・Date・本文をdecode
  ↓
転送用メールを生成
  ↓
Yahoo SMTPで送信
  ↓
SMTP応答を確認
```

実際に、Yahooメールの特定メッセージを取得し、送信者をYahooアドレスにしてGmailへ転送できました。

ここで重要なのは、「Codexからメール本文を読める」だけではなく、「必要に応じてメール処理を実行できる」ことです。

たとえば次のような処理に広げられます。

- 特定条件のメールを抽出して転送
- 注文メールから商品名、金額、個数を抽出
- 問い合わせメールを分類
- 重要メールだけSlackやSNSに通知
- メール本文をCSVやJSONへ変換
- 売上分析用データとして蓄積

---

## メールはAI業務自動化の重要な入口

多くの業務データは、いまだにメールに届きます。

ECの注文通知、問い合わせ、請求、予約、配送、アカウント通知、決済通知。これらはWeb管理画面の中だけでなく、メールとしても流れてきます。

つまりメールをAIで扱えるようにすると、既存システムを大きく作り替えなくても、業務データの入口を作れます。

今回のKurage Mailは、そのための小さな基盤です。

Roundcubeで人間が確認できる。  
PHPで外部メールも読める。  
CodexからPOP/SMTPを操作できる。  
文字化けを直してLLMに渡せる。

この状態になると、メールは単なる受信箱ではなく、AIエージェントが処理できる業務イベントになります。

---

## まとめ

今回の構築で、Kurage Mailは次の状態になりました。

- heteml上でRoundcubeが動作する
- IMAPでメールを残したまま閲覧できる
- SMTP送信できる
- 外部POPメールも一覧・本文表示できる
- multipart / ISO-2022-JPメールをUTF-8で読める
- Codexからメール転送できる

これは、バイブコーディング的なメール処理の入口です。

人間がメールを見て、必要な処理を言葉で指示し、CodexがPOP/SMTPやPHPコードを操作して処理する。  
そこから、分類、集計、転送、売上分析、問い合わせ対応へ広げられます。

メールは古い技術ですが、AIエージェントにとっては今でも非常に重要な業務インターフェースです。

Kurage Mailは、そのメールをAI時代の操作対象にするための実装です。

## 関連リンク

- [Roundcube](https://roundcube.net/)
- [VWork バイブコーディングフレームワーク](https://katsushi2441.github.io/vwork/)
- [AI OSS技術解説](https://katsushi2441.github.io/vwork/articles/)
