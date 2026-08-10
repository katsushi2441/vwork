---
title: "Thunderbirdの予定をスマホで — Googleに預けず自分のサーバーで持つ『Kurage Capacitor Launcher』を作った"
description: "PCのThunderbirdのカレンダーを、外出先のスマホから読み書きしたい。いちばん簡単な答えは『Googleカレンダーに全部移す』でしたが、予定表を丸ごとクラウドに預けるのは避けたい。そこでGoogleをハブにするのはあきらめ、1ファイルのCalDAVサーバー kcaldav と、ホーム画面から開くランチャー Kurage Capacitor Launcher を自作しました。Capacitorをベースに選んだ理由と、結局DAVx5でGoogleカレンダーとも同期できた話を紹介します。"
date: 2026-08-10
layout: default
permalink: /blog/2026-08-10-kurage-capacitor-launcher.html
---

PCの[Thunderbird](https://www.thunderbird.net/)でカレンダーを管理しています。困っていたのは「外出先のスマホから、その予定を見て・書きたい」こと。いちばん簡単な答えは「Googleカレンダーに全部移す」でした。でも——自分の予定表を丸ごとGoogleのクラウドに預けるのは避けたい。

そこでGoogleカレンダーを"ハブ"にするのはあきらめ、**自分のサーバーで持てる仕組み**を自作しました。それが1ファイルのCalDAVサーバー **kcaldav** と、スマホのホーム画面から開くランチャーアプリ **Kurage Capacitor Launcher（kclauncher）** です。

## 出発点：Thunderbirdの予定を、スマホから読み書きしたい

Thunderbirdのカレンダーは、iCalendar（CalDAV）で動いています。スマホからも同じ予定を読み書きするには、PCとスマホの"あいだ"に、常に正となるサーバーが1つ要ります。

最初はBaïkalのような既存のCalDAVサーバーを立てようとしましたが、カレンダーを共有したいだけなのに、巨大なフレームワークと管理画面はやりすぎでした。そこで、CalDAVで実際に必要な処理（OPTIONS / PROPFIND / REPORT / GET / PUT / DELETE）だけを素のPHPで書いた、**約1ファイルのCalDAVサーバー kcaldav** を作りました。SQLite1ファイルで動き、データベースサーバーもいりません。PHPが動くレンタルサーバーにFTPで置くだけ。これで、Thunderbird・iPhoneの標準カレンダー・スマホのブラウザから、同じ予定を読み書きできるようになりました。

## なぜGoogleカレンダーを"ハブ"にしなかったか

Googleカレンダーに全部移せば、確かにスマホからはすぐ使えます。ただしその瞬間から、予定表の"正本"はGoogleのクラウドに移り、主導権も預けることになります。バックアップも、他サービスとの連携も、Googleの都合に乗る形です。

やりたかったのは逆で、**サーバーは自分のもの、予定は自分の手元**。だからGoogleを中心に据えるのはやめました。（後述しますが、"Googleカレンダーのアプリで見たいだけ"なら、預けなくても両立できる、というのが最後のオチです。）

## スマホから"アプリのように"開きたい → Capacitorでランチャーを作った

kcaldavはブラウザでも使えます。でもスマホで日常的に使うなら、ホーム画面のアイコンから全画面で開けて、戻る導線もある"アプリ"の感触が欲しい。

Androidには [TWA（Trusted Web Activity）](https://developer.chrome.com/docs/android/trusted-web-activity) という手もありますが、TWAは**検証済みの1ドメインに固定**されてしまい、「自分のサーバーのURLを指したい」「URLで中身を切り替えたい」という今回の要件に合いません。

そこで選んだのが **[Capacitor](https://capacitorjs.com/)** です。Webアプリをネイティブの殻でくるむ、ハイブリッドアプリのフレームワークです。

### Capacitorをベースにしたメリット

- **1つのWeb実装から、Androidネイティブアプリと、iPhoneのPWAを両方出せる**。iOSはMacが必要でストア配信こそしませんが、同じ画面がPWA（ホーム画面に追加）としてそのまま動きます
- **WebViewベースなので、どんなWebアプリ／URLでもそのまま中で開ける**。作り込みが不要
- だから「**開くURLで中身が変わる**」汎用ランチャーにできる。タイルにURLを登録するだけで、カレンダーにも、動画にも、別のサービスにもなる
- **ネイティブの殻の恩恵**：ホーム画面アイコン、全画面表示、アプリ内ブラウザ（Custom Tabs＝閉じるボタン付き）。将来プッシュ通知やオフラインを足す余地もある
- **Web技術の使い回しで、専用のネイティブ開発なしに、速く・安く作れる**
- TWAと違い**任意のURLを指せる**ので、「自分のサーバーのkcaldavを指定して使う」がそのまま実現できる

## できること

Kurage Capacitor Launcher は、タイルをタップしてサービスを開くだけのシンプルなランチャーです。

- 既定タイル：カレンダー（kcaldav）／動画／サンプルゲーム／アプリ新着
- **自分のサーバーのカレンダーURLなど、任意のタイルを追加・編集・削除できる**
- **iPhone**：Safariで「ホーム画面に追加」すればアプリ不要（PWA）
- **Android**：署名済みAPKを配布

## 結局、Googleカレンダーとも同期できる（預けはしない）

面白いのはここです。Googleを"ハブ"にするのはあきらめましたが、**Googleカレンダーの"アプリ"で見て・書く**ことは、預けずに実現できました。

Androidに **[DAVx5](https://www.davx5.com/)**（CalDAV同期アプリ。F-Droid版は無料）を入れて、kcaldavのURLとユーザー名・パスワードを設定すると、**Android標準＝Googleカレンダーのアプリ**に自分の予定が表示・編集できます。書いた予定はThunderbirdやiPhoneにも反映されます。しかも**予定はGoogleのクラウドではなく、自分のkcaldavサーバーに保存**されたまま。データの持ち主は自分、見る窓口はGoogleカレンダー、という良いとこ取りができました。

## 入手

**無料**です。iPhone版（PWA）とAndroid版（APK）は、公式サイトから入手できます。

- 公式サイト（LP）：[https://kclauncher.exbridge.jp/](https://kclauncher.exbridge.jp/)
- [Kurage App Store](https://kappstore.exbridge.jp/) にも無料で掲載しています

「カレンダーくらい、巨大なサービスに預けなくても、1ファイルのサーバーと小さなランチャーで足りる」。Kurage Capacitor Launcher は、その手触りを確かめるための入口です。
