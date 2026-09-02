---
title: "ヘルプデスクOSS「Zammad」の日本語は23%しかなかった——5,123エントリを全訳して本家Weblateを100%にするまでと、今すぐ日本語化する手順"
emoji: "🎫"
type: "tech"
topics: ["zammad", "helpdesk", "oss", "翻訳", "weblate"]
published: true
---

Zendeskの代替を探すと必ず候補に挙がるオープンソースヘルプデスク [Zammad](https://github.com/zammad/zammad)（Ruby on Rails製・AGPL-3.0・GitHubスター5,800超）。メール・電話・チャットの問い合わせをチケットとして一元管理でき、セルフホストで月額ゼロ運用ができます。

ただし導入した日本の会社がまず突き当たるのが「**画面のかなりの部分が英語のまま**」という問題です。この記事は、その原因の実測から、当社（名古屋のAIシステム開発会社・エクスブリッジ）が全エントリを翻訳して本家の翻訳基盤（Weblate）へ投入するまでの記録と、**いま使っているZammadを今日日本語化する手順**をまとめたものです。

## 実測: 日本語カバレッジは23%だった

Zammadの翻訳は gettext の po ファイル（`i18n/zammad.ja.po`）で管理されています。developブランチのja.poをpolibで解析すると:

```
有効エントリ: 5,123
翻訳済み(非fuzzy): 約1,260 = 約23%
```

本家の翻訳プラットフォーム（Weblate）上の表示では **18.8%** でした。管理画面・トリガー設定・メール通知テンプレートなど、運用の中核部分の多くが英語のまま表示されるのはこのためです。

## 全訳の方法: ローカルLLM＋機械検証

未訳の約4,100エントリを、ローカルGPUで動くLLM（gemma系12B）でバッチ翻訳しました。API費用はゼロです。品質はプロンプトではなく**検証で**担保します:

- **プレースホルダの逐語一致検証**: `%s` `%{name}` `#{ticket.title}` などの変数、HTMLタグ、URL、改行を原文と訳文で機械照合し、**一致しない訳は自動で不採用**（リトライ後も不一致なら未訳のまま残す）
- 用語統一（Ticket=チケット/Agent=担当者/Overview=一覧/Escalation=エスカレーション など）を対訳表としてシステムプロンプトに固定
- fuzzyフラグの罠: fuzzy付きエントリは訳があっても実行時に使われないため、自分が訳を入れたものだけフラグを外す（本家由来の訳とfuzzyには一切触れない）
- 最後まで検証に弾かれた4件のみ手訳

結果、**有効5,123エントリの100%**が翻訳済みになりました。gettext互換はmoコンパイルで確認しています。

## 今すぐ日本語化する手順（セルフホスト向け）

完成したpoは [katsushi2441/zammad-jp](https://github.com/katsushi2441/zammad-jp) で公開しています（AGPL-3.0）。

```bash
# 1. poを差し替え（パッケージ版の例）
sudo cp zammad.ja.po /opt/zammad/i18n/zammad.ja.po

# 2. 翻訳をDBへ同期
zammad run rails r 'Translation.sync'

# 3. ブラウザを再読み込み（プロフィールの言語=日本語を確認）
```

個別の文言はZammad管理画面の翻訳カスタマイズでも上書きできます。

## 本家への還元: 直接PRは「拒否」と明文化されている

前回の [Krayin日本語化](2026-08-18-krayin-crm-japanese-guide.html) ではGitHubへのPRがそのままマージされましたが、Zammadは開発者ドキュメントに **「翻訳ファイルを直接変更するPRは拒否する」** と明記されています。正規ルートは翻訳プラットフォームの [Weblate](https://translations.zammad.org/)（要アカウント）です。

そこでWeblateにアカウントを作り、REST APIの翻訳アップロード（`POST /api/translations/zammad/zammad-development/ja/file/`・`method=translate`）でpoを投入しました。`method=translate`は**既存の訳を上書きせず未訳だけを埋める**ので、本家の翻訳者の仕事を壊しません。結果:

```
zammad-development/ja: 18.8% → 100.0%（受理4,158件・既存965件はスキップ）
zammad-stable/ja:      20.2% →  99.1%（developmentから自動伝播）
```

Weblateの翻訳は本家のリリースフローで`i18n/zammad.ja.po`へ同期されるため、**今後のZammadリリースには日本語がほぼ完全な状態で同梱される見込み**です。マージ後の保守は本家の翻訳フローに引き継がれます。

## まとめ

- Zammadの日本語が中途半端なのは実測23%のカバレッジが原因
- いま使っているZammadは [zammad-jp](https://github.com/katsushi2441/zammad-jp) のpoで今日日本語化できる
- 本家Weblateには全訳を投入済み（development 100%）。次のリリース以降は本家だけで日本語が揃う見込み
- OSSの日本語化は「配って終わり」ではなく「本家に返して保守を手放す」ところまでやると、日本のユーザー全員の資産になります

Zendesk代替としての比較・導入支援は[こちらのページ](https://kurage.exbridge.jp/zendesk-helpdesk.php)にまとめています。
