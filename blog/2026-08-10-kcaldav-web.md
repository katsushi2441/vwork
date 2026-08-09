---
title: "アプリを入れずに、ブラウザで予定を読み書き — 1ファイルのカレンダー kcaldav に WEB画面を付けました"
description: "先日出した1ファイルのCalDAVサーバー kcaldav を大きく更新しました。ブラウザで予定を一覧・追加・編集・削除できるWEBカレンダー画面を同梱。アプリを入れなくても、スマホのブラウザから予定を書き込めます。iPhone標準カレンダー・AndroidのKashCal・PCのThunderbirdとも同じ予定表で同期。Kurage App Storeで税込55,000円・MIT・デモあり。"
date: 2026-08-10
layout: default
permalink: /blog/2026-08-10-kcaldav-web.html
---

先日、[1ファイルのCalDAVサーバー kcaldav](https://katsushi2441.github.io/vwork/blog/2026-08-10-kcaldav.html) を公開しました。Thunderbirdの予定をスマホから見られるように、と作ったものです。

ところが実際に自分で使ってみて、要件を取り違えていたことに気づきました。**Androidで予定を「書き込む」には、結局DAVx5のような同期アプリが要る。** ユーザーが本当に欲しかったのは「アプリを入れずに、ブラウザで読み書きしたい」でした。

そこで大きく更新しました。**ブラウザだけで予定を読み書きできるWEBカレンダー画面**を同梱しています。

▶ [デモを触る](https://proto.exbridge.jp/kcaldav/kcaldav.php)（demo / demo） ／ [kappstoreで見る（税込55,000円）](https://kappstore.exbridge.jp/app.php?id=43950141618ddb02) ／ [GitHub（MIT）](https://github.com/katsushi2441/kcaldav)

## ブラウザを開くだけ、アプリは要らない

本体URLをブラウザで開くと、ログインのあと、そのままカレンダー画面になります。

- これからの予定が一覧で並ぶ（過去は折りたたみ）
- 上のフォームでタイトル・日付・時刻・終日・場所を入れて「追加」
- 各予定に「編集」「削除」

スマホのブラウザでも同じで、日付や時刻はスマホのネイティブな選択UIが出ます。アプリのインストールも、ストアでの購入も要りません。これが一番の追加点です。

## それでいて、標準アプリとも全部つながる

WEB画面で足した予定は、裏側のCalDAVと同じデータに入ります。だから、次のどれから足しても全部に反映されます。

- **ブラウザのWEBカレンダー**（同梱・アプリ不要）
- **iPhone / iPad**：OS標準のカレンダー（アプリ不要）
- **Android**：KashCal（アプリ単体でCalDAV対応）や、DAVx5＋いつものカレンダーアプリ
- **PC**：Thunderbird 内蔵のCalDAVクライアント

出先はスマホのブラウザで、自宅はPCのThunderbirdで。同じ予定表を、好きな入口から読み書きできます。

## 「読み取り専用になる」を直した話

開発中、AndroidのKashCalでつないだら、予定に「複製」「共有」しか出ず、編集できませんでした。原因はサーバー側で、CalDAVには「あなたはこのカレンダーに書き込めます」という権限情報（`current-user-privilege-set`）を返す決まりがあり、これが無いと厳しめのクライアントはカレンダーを読み取り専用扱いにします。

kcaldav はカレンダーと予定の両方でread/write/bind権限を返し、OPTIONSのDAVヘッダに`access-control`も含めるようにしました。これで対応クライアントからちゃんと編集できます。CalDAVは仕様が大きいので、こういう「一言足りないと動かない」箇所を潰していくのが実装の勘所でした。

## 中身は相変わらず1ファイル

sabre/davやNextcloudのような巨大フレームワークは使っていません。CalDAVで実際に必要な処理（OPTIONS/PROPFIND/REPORT/GET/PUT/DELETE）とWEBカレンダー画面を、素のPHPで約600行の1ファイルにまとめています。保存はSQLite1ファイル、DBサーバー不要。PHPが動くレンタルサーバーにFTPで置くだけです。

- 設定ファイルで宣言したユーザー・カレンダーだけが使える（宣言外は触れない）
- Basic認証、パスワードはハッシュ保存、全SQLはプレースホルダ、WEB画面はCSRF対策
- CalDAV 18項目＋WEB 15項目の自動チェックを同梱
- 「全部読めるサイズ」なので、設定変更や機能追加はAI（Claude Code）に頼める（設計マニュアル同梱）

## まずデモを

[デモ](https://proto.exbridge.jp/kcaldav/kcaldav.php)（demo / demo）をブラウザで開けば、予定の追加・編集・削除をその場で試せます。買い切り・ソース渡し・MITライセンス。

やりたいことが小さいなら、道具も小さくていい。前回そう書きましたが、今回はさらに「そもそもアプリを入れなくていい」ところまで削りました。

▶ [kappstoreで見る（税込55,000円）](https://kappstore.exbridge.jp/app.php?id=43950141618ddb02) ／ [Kurage App Store](https://kappstore.exbridge.jp/) — AIエージェントが見つけて、導入し、AIエージェントで育てる業務システムのお店
