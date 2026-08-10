---
title: "『Kurage Capacitor Launcher』を作った — ThunderbirdとGoogleカレンダーの連携でつまずき、将来のAndroidアプリの土台にCapacitorを選んだ"
description: "PCのThunderbirdのカレンダーを、外出先のスマホから読み書きしたい。素直な道はThunderbirdとGoogleカレンダーの連携でしたが、これがすんなりいかず、結局1ファイルのCalDAVサーバー kcaldav を自作しました。あわせて『今後Androidアプリのニーズが出たらCapacitorで開発する』ための土台・技術検証として、Kurage Capacitor Launcher を作りました。Capacitorを土台に選んだ理由と、DAVx5でGoogleカレンダーとも同期できた話を紹介します。"
date: 2026-08-10
layout: default
permalink: /blog/2026-08-10-kurage-capacitor-launcher.html
---

PCの[Thunderbird](https://www.thunderbird.net/)でカレンダーを管理しています。やりたかったのは「外出先のスマホから、その予定を見て・書きたい」こと。いちばん素直な道は「ThunderbirdとGoogleカレンダーを連携させて、スマホではGoogleカレンダーで見る」でした。ところが——**これがすんなりいかない**。

その回り道の末にたどり着いたのが、1ファイルのCalDAVサーバー **kcaldav** と、将来のスマホアプリの土台として作った **Kurage Capacitor Launcher（kclauncher）** です。順番に紹介します。

## 発端：ThunderbirdとGoogleカレンダーが、素直に連携しなかった

ThunderbirdからGoogleカレンダーへ双方向で同期するには、アドオン（Provider for Google Calendar など）や設定が必要で、思ったほど素直にいきませんでした。認証まわりや同期の挙動でつまずき、「PCとスマホで同じ予定を、確実に読み書きする」という当たり前のことが、意外と面倒だったのです。

そこで発想を変えました。GoogleカレンダーをPCとスマホの"あいだ"に置くのではなく、**自分のサーバーを1つ、正（せい）として置く**。CalDAVで実際に必要な処理（OPTIONS / PROPFIND / REPORT / GET / PUT / DELETE）だけを素のPHPで書いた、**約1ファイルのCalDAVサーバー kcaldav** を作りました。SQLite1ファイルで動き、データベースサーバーもいりません。PHPが動くレンタルサーバーにFTPで置くだけ。これで、Thunderbird・iPhoneの標準カレンダー・スマホのブラウザから、同じ予定を読み書きできるようになりました。

## Kurage Capacitor Launcher：将来のAndroidアプリ開発の"土台"として

カレンダーの問題とは別に、もうひとつ見据えていたことがあります。**今後、ユーザーからAndroidアプリのニーズが出てきたら、そのときはCapacitorをベースに開発していこう**、という方針です。

スマホアプリ（ネイティブ）は、Webアプリよりメリットが大きい場面があります。ホーム画面のアイコン、全画面、プッシュ通知、オフライン、端末機能へのアクセス——「Webよりアプリの方がいい」と言われたときに、すぐ応えられる土台がほしい。

そこで、その**技術検証（PoC）兼・再利用できるベース**として作ったのが Kurage Capacitor Launcher です。今日から使える実用的なランチャーであると同時に、**要望が来たら、これを土台にKurageの各サービスをネイティブアプリ化していく**ための足場です。

### なぜCapacitorを土台に選んだか

- **1つのWeb実装から、Androidネイティブアプリと、iPhoneのPWAを両方出せる**（iOSはMacが必要でストア配信こそしないが、同じ画面がPWAとして動く）
- **WebViewベースなので、Kurageの既存Webアプリ／任意URLをそのまま中で動かせる**。だから既存資産を短期間でアプリ化できる
- 「**開くURLで中身が変わる**」汎用ランチャーにできる。タイルにURLを登録するだけで、カレンダーにも、動画にも、別サービスにもなる
- **ネイティブの殻の恩恵**：ホーム画面アイコン、全画面、アプリ内ブラウザ（Custom Tabs）。この先、プッシュ通知・オフライン・端末APIを足していける
- **Web技術の使い回しで、専用のネイティブ開発なしに、速く・安く**検証・開発できる
- Androidの[TWA](https://developer.chrome.com/docs/android/trusted-web-activity)は**検証済みの1ドメインに固定**されるが、Capacitorは**任意のURLを指せる**——「自分のサーバーのkcaldavを指定して使う」がそのまま実現できる

つまり Kurage Capacitor Launcher は、「Webよりアプリの方が有利で、ユーザーの要望がある」ときに、**そこから開発を始められる土台**として位置づけています。

## できること（今できること）

土台といっても、今日から普通に使えるランチャーです。

- 既定タイル：カレンダー（kcaldav）／動画／サンプルゲーム／アプリ新着
- **自分のサーバーのカレンダーURLなど、任意のタイルを追加・編集・削除できる**
- **iPhone**：Safariで「ホーム画面に追加」すればアプリ不要（PWA）
- **Android**：署名済みAPKを配布

## そして、Googleカレンダーとも同期できた（DAVx5）

最初につまずいたGoogleカレンダーとの連携も、遠回りした結果きれいに解けました。

kcaldavはCalDAVなので、Androidに **[DAVx5](https://www.davx5.com/)**（CalDAV同期アプリ。F-Droid版は無料）を入れて、kcaldavのURLとユーザー名・パスワードを設定すると、**Android標準＝Googleカレンダーのアプリ**に自分の予定が表示・編集できます。書いた予定はThunderbirdやiPhoneにも反映され、予定の実体はkcaldavサーバー側に保存されます。「スマホではGoogleカレンダーで見たい」という当初の望みは、自分のサーバー経由で叶いました。

## 入手

**無料**です。iPhone版（PWA）とAndroid版（APK）は、公式サイトから入手できます。

- 公式サイト（LP）：[https://kclauncher.exbridge.jp/](https://kclauncher.exbridge.jp/)
- [Kurage App Store](https://kappstore.exbridge.jp/) にも無料で掲載しています

カレンダー1つのために始めた回り道が、「1ファイルのCalDAVサーバー」と「将来のアプリ開発の土台」という2つの成果になりました。Kurage Capacitor Launcher は、Kurageのサービスをネイティブアプリへ広げていくための、最初の一歩です。
