---
title: "AIラジオの実画面を、AIがデモ動画にして公開する — Kurage Argo VideoとAIRadioの連携"
description: "Kurage Argo VideoがKurage AI VTuber Radioの実画面を録画し、機能解説付きのデモ動画としてKurageに公開しました。AIラジオ、ブラウザ自動録画、動画公開基盤を組み合わせたエクスブリッジの技術的優位性を経営者向けに解説します。"
date: 2026-06-26
layout: default
permalink: /blog/2026-06-26-kargov-airadio-demo-pipeline.html
status: published
---

# AIラジオの実画面を、AIがデモ動画にして公開する — Kurage Argo VideoとAIRadioの連携

株式会社エクスブリッジでは、AIを「文章を書く道具」としてだけではなく、実際の業務画面を動かし、録画し、動画として公開するところまでを一つのパイプラインとして開発しています。

今回、**Kurage Argo Video** を使って、**Kurage AI VTuber Radio（AIRadio）** の実画面を録画し、機能解説付きのデモ動画として **Kurage** に公開しました。

デモ動画はこちらです。

- [Kurage AI VTuber Radio デモ：話す・記録する・コメントを受けるAIラジオ](https://kurage.exbridge.jp/kuragev.php?id=4ae09591e7994ef0)
- [Kurage Argo Video GitHub](https://github.com/katsushi2441/kargov)
- [Kurage AI VTuber Radio GitHub](https://github.com/katsushi2441/airadio)
- [Kurage AI VTuber GitHub](https://github.com/katsushi2441/kvtuber)

これは単なる画面録画ではありません。

**AIラジオを実際に動かし、その様子をAIが録画し、解説動画に編集し、Kurage上で公開する**という、企業の情報発信を内製化するための実証です。

## AIRadioとは何か

Kurage AI VTuber Radio、通称AIRadioは、AI VTuberがラジオDJのように話し続けるシステムです。

編集者のプロフィールや指定テーマに合わせて台本を作り、AI VTuberが音声で話し、画面には次のような情報が表示されます。

- AI VTuberのアバター
- 現在話している内容
- コメント欄
- Loop Log
- YouTube Live配信操作
- テーマ割込み用の入力欄

AIRadioの役割は、単に音声を読み上げることではありません。

企業が発信したいテーマを、ラジオ番組のように継続的に話し続けることです。たとえば、AI活用、バイブコーディング、Web3、社内教育、サービス紹介、採用広報などを、AI VTuberが穏やかに話す番組にできます。

## 今回のデモ動画で見せた機能

今回のデモ動画では、AIRadioの画面をスクロールしながら、単なるトップ画面ではなく、実際に運用で重要になる部分を見せています。

具体的には、次の機能を動画内で確認できるようにしました。

- プロフィールに合わせた台本生成
- AI VTuberによるラジオ音声
- 「今話している内容」の表示
- コメント欄
- Loop Logによる処理状況の可視化
- テーマ割込み機能
- YouTube Live配信へつなげる操作領域

経営者にとって重要なのは、「AIが話します」という説明だけではありません。

実際の画面で、何を話しているのか、運用ログがどう見えるのか、コメントや配信操作がどこにあるのかが分かることです。今回のデモでは、そこを見せるために画面スクロールを入れています。

## Kurage Argo Videoの役割

Kurage Argo Videoは、ブラウザ操作を録画し、デモ動画として仕上げるための仕組みです。

Webサービスのデモ動画を作る場合、通常は次のような作業が必要です。

1. ブラウザを開く
2. 操作手順を決める
3. 画面録画する
4. ナレーションを作る
5. 不要部分をカットする
6. テロップや説明カードを入れる
7. 動画として書き出す
8. 公開ページにアップする

Kurage Argo Videoは、この流れをAIと自動化で短縮するためのプロダクトです。

今回のデモでは、AIRadioの実画面を録画し、前後に機能説明を加え、縦型ショート形式の動画としてKurageに公開しました。

ここで大事なのは、架空の画面を作ったのではなく、**実際に動いているAIRadioの画面を録画している**ことです。

## Kurage公開基盤の役割

録画した動画は、Kurageの動画公開ページで見られるようにしました。

- [公開デモ動画](https://kurage.exbridge.jp/kuragev.php?id=4ae09591e7994ef0)

Kurageは、動画生成・動画公開・サムネイル・タイトル・説明文を扱うための基盤です。今回のようなデモ動画を、単にローカルファイルとして残すのではなく、URLで共有できる状態にします。

営業、採用、投資家向け説明、社内共有では、動画ファイルを送るよりも、公開URLで見せられる方が使いやすくなります。

## 技術的には何をしているのか

今回の連携は、複数のシステムをつないでいます。

```text
AIRadio
  ↓ 実ブラウザで動作
Kurage Argo Video
  ↓ 画面と音声を録画
動画編集パイプライン
  ↓ 機能説明カードと実音声区間を結合
Kurage
  ↓ 公開用URLとして配信
VWork Blog / SNS
  ↓ 事例として説明・発信
```

AIRadio側では、AI VTuberの画面、台本生成、TTS音声、コメント、Loop Logなどを表示します。

Kurage Argo Video側では、ブラウザの画面と音声を録画します。今回の録画では、画面スクロールを入れて、上部の見た目だけでなく、実際の運用情報が見える下部セクションも映しました。

Kurage側では、完成した動画をジョブID付きで公開し、タイトルや説明文も整えています。

この一連の流れにより、**プロダクトの実画面を、説明可能な動画コンテンツへ変換する**ことができます。

## なぜ経営者に重要なのか

企業が新しいシステムを作っても、それを社内外に伝えるのは意外と難しいものです。

- 営業資料だけでは伝わりにくい
- 長いマニュアルは読まれにくい
- デモ動画を毎回作るのは手間がかかる
- 担当者が説明しないと価値が伝わらない

しかし、AIが実画面を録画し、機能を説明する動画まで作れるようになれば、状況が変わります。

新機能を作ったら、すぐにデモ動画を作る。社内ツールを更新したら、操作説明動画を作る。営業で見せたい画面を、短い動画にして共有する。

これを少人数で回せるようになります。

## エクスブリッジの技術的優位性

エクスブリッジの強みは、単体のAIツールを使うことではありません。

**AI、OSS、ブラウザ自動化、VTuber、TTS、動画生成、公開基盤、ブログ/SNS発信を、業務で使える形につなげていること**です。

今回のデモには、少なくとも次の技術要素が入っています。

- AI VTuber画面
- AIラジオ台本生成
- TTS音声生成
- ブラウザ自動操作
- 画面録画
- 音声付き動画生成
- 縦型ショート動画化
- Kurageでの公開
- VWork Blogでの事例化

これは、AIに文章を書かせるだけの導入とは違います。

実際に画面を動かし、動画にし、公開し、説明記事にする。ここまでを一つの仕組みにできるから、企業の情報発信と業務改善に直結します。

## 今後の活用例

この仕組みは、AIRadioだけでなく、さまざまな業務に応用できます。

- 新サービスのデモ動画
- 社内システムの操作説明
- 採用向けの仕事紹介
- 研修コンテンツ
- 営業提案用のプロトタイプ動画
- 顧客向けの導入説明
- AI Agentが実行した作業の証跡動画

企業にとって、動画は「広報用の特別な制作物」から、「日々の業務を説明するための標準出力」になっていきます。

エクスブリッジは、そのためのAI×OSSプロダクト群を実装し続けています。

## 関連リンク

- デモ動画: [https://kurage.exbridge.jp/kuragev.php?id=4ae09591e7994ef0](https://kurage.exbridge.jp/kuragev.php?id=4ae09591e7994ef0)
- Kurage Argo Video: [https://github.com/katsushi2441/kargov](https://github.com/katsushi2441/kargov)
- Kurage AI VTuber Radio: [https://github.com/katsushi2441/airadio](https://github.com/katsushi2441/airadio)
- Kurage AI VTuber: [https://github.com/katsushi2441/kvtuber](https://github.com/katsushi2441/kvtuber)
- 株式会社エクスブリッジ: [https://exbridge.jp/](https://exbridge.jp/)
