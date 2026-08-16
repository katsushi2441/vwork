---
title: VWork Blog
description: VWork Blogは、バイブコーディングとバイブトレーディングを企業内に導入するための考え方・実践知・営業導入で得た気づきを、実際に運用しているシステムの記録に基づいて公開するブログです。
list_recent_posts: true
faq:
  - q: VWorkは誰向けのフレームワークですか？
    a: 社内にエンジニアが少ない、あるいはいない状態でシステムを内製化したい企業向けです。手入力業務の自動化やホームページの内製化など、小さく始められる範囲から扱っています。
  - q: 記事の内容は実運用に基づいていますか？
    a: はい。掲載しているシステムは実際に稼働しており、稼働状況は公開ダッシュボードで確認できます（暗号資産のkfreqai、FXのkfxai。いずれもdry-run／ペーパートレードで、実際の資金は動かしていません）。うまくいかなかった施策や棄却した仮説も、そのまま記事にしています。
  - q: 費用はいくらかかりますか？
    a: このブログの閲覧は無料です。記事で紹介しているKurageの各サービスは、無料枠のあるものと従量課金のものがあり、料金は各サービスのページに記載しています。例としてKurage GEOは初回診断が無料で、2回目以降は1診断200円または20,000 URLAIです。
  - q: 運営元はどこですか？
    a: 株式会社エクスブリッジ（EXBRIDGE, Inc.）です。会社情報はexbridge.jp、ご連絡はお問い合わせフォームからお願いします。
  - q: バイブコーディングとは何ですか？
    a: コードをAIに書かせ、人間は要件定義と検証に集中する開発スタイルを指します。プログラミングの手を動かす部分をAIに任せ、「何を作るか」と「正しく動いているか」に人間の時間を使う進め方です。
  - q: バイブトレーディングとは何ですか？
    a: 取引戦略のアイデアを日本語でAIに伝えてコードに落とし、バックテストの数字で検証しながら戦略を育てていく運用スタイルを指します。仮説を出すのは人間、コードにするのはAI、採否を決めるのはバックテストの数字、という分業が特徴です。
---


**VWork Blogとは、バイブコーディングを企業内に導入するための考え方・実践知・営業導入で得た気づきを蓄積するブログを指します。** 記事はすべて、株式会社エクスブリッジが実際に運用しているシステムの記録に基づいて書かれています。

## このブログで扱う2つの用語

**バイブコーディングとは、コードをAIに書かせ、人間は要件定義と検証に集中する開発スタイルを指します。** プログラミングの手を動かす部分をAIに任せ、「何を作るか」と「正しく動いているか」に人間の時間を使う進め方です。

**バイブトレーディングとは、取引戦略のアイデアを日本語でAIに伝えてコードに落とし、バックテストの数字で検証しながら戦略を育てていく運用スタイルを指します。** バイブコーディングをトレード戦略の開発・運用に応用した言葉で、仮説を出すのは人間、コードにするのはAI、採否を決めるのはバックテストの数字、という分業が特徴です。

## よくある質問

### VWorkは誰向けのフレームワークですか？

社内にエンジニアが少ない、あるいはいない状態でシステムを内製化したい企業向けです。手入力業務の自動化やホームページの内製化など、小さく始められる範囲から扱っています。

### 記事の内容は実運用に基づいていますか？

はい。掲載しているシステムは実際に稼働しており、稼働状況は公開ダッシュボードで確認できます（暗号資産: [kfreqai](https://kurage.exbridge.jp/kfreqai.php)、FX: [kfxai](https://kurage.exbridge.jp/kfxai.php)。いずれもdry-run／ペーパートレードで、実際の資金は動かしていません）。うまくいかなかった施策や棄却した仮説も、そのまま記事にしています。

### 費用はいくらかかりますか？

このブログの閲覧は無料です。記事で紹介しているKurageの各サービスは、無料枠のあるものと従量課金のものがあり、料金は各サービスのページに記載しています（例: [Kurage GEO](https://kgeo.exbridge.jp/kgeo.html) は初回診断無料、2回目以降は1診断200円または20,000 URLAI）。

### 運営元はどこですか？

株式会社エクスブリッジ（EXBRIDGE, Inc.）です。会社情報は [会社概要](https://exbridge.jp/company)、ご連絡は [お問い合わせフォーム](https://exbridge.jp/contact.php) からお願いします。

## この記事で使う用語の定義

**VWorkとは、社内にエンジニアが少ない企業がAIを使ってシステムを内製化するための作業基盤と実践知をまとめたフレームワークを指します。** ソースコードは [GitHub](https://github.com/katsushi2441/vwork) で公開しています。

**GEOとは、生成AIやAI検索が内容を理解・引用しやすいように、サイトの技術構成と情報表現を整える取り組みを指します。** Generative Engine Optimizationの略です。

**AEOとは、利用者の質問に対してページが直接答えられる状態を目指す最適化を指します。** Answer Engine Optimizationの略で、結論を先に書く・定義文を置く・質問を見出しにする、といった書き方が中心になります。

**x402とは、HTTPステータス「402 Payment Required」を使い、AIエージェントがAPIを1回ずつ従量課金で購入できるようにする決済の仕組みを指します。**

## 根拠と参照元

このブログの記述は、次の一次情報に基づいています。

- **稼働中システムの実測値**: 暗号資産の [kfreqai ダッシュボード](https://kurage.exbridge.jp/kfreqai.php)、FXの [kfxai ダッシュボード](https://kurage.exbridge.jp/kfxai.php)（いずれもdry-run／ペーパートレードの数値。実資金は動かしていません）
- **GEO診断の結果**: 本ブログ自身を [Kurage GEO](https://kgeo.exbridge.jp/kgeo.html) で監査した記録。2026年8月3日時点の再診断で、総合スコアは29点から改善しています（診断ツールの採点基準に基づく値です）
- **ソースコード**: [github.com/katsushi2441/vwork](https://github.com/katsushi2441/vwork) ほか、各記事で紹介しているリポジトリ
- **検証済みの取引戦略**: kfxaiでは方向予測モデルを約1万取引のwalk-forward検証にかけ、優位性が確認できなかったため棄却しました（詳細は該当記事に記載）

数値や比較を引用される場合は、更新日（このページ下部に記載）とあわせてご確認ください。将来の成果を保証するものではなく、投資助言でもありません。

## 記事一覧

- [ジモティーは「カテゴリ」と「新着枠」で決まる——同じ勉強会に2本目を出して分かったこと](2026-08-16-jmty-category-newarrival.html)
- [Brainに業務システムのエンジニアがいない——だから、そこで戦うことにした](2026-08-16-brain-only-one.html)
- [AIチャットボットは高すぎる——だから55,000円買い切りの『Kurage Light ChatBot』を作りました（導入は3つの入口から）](2026-08-16-klchatbot-launch.html)
- [完成品55,000円、作り方も55,000円——『3つの入口』でシステムを売る実験を始めました](2026-08-15-three-doors-model.html)
- [プロダクト名で検索してくれる人は、ほとんどいない——『複数LP×他社メディア誘導』の検証を予約管理システムで始めました](2026-08-15-multi-lp-media-mesh.html)
- [100円の記事に星1がついた——Brainで学んだ『期待値設計』の授業料](2026-08-14-brain-star1-lesson.html)
- [Brainに記事を公開するまで——一度審査に落ちて学んだ『審査があるプラットフォーム』の書き方](2026-08-14-brain-post-knowhow.html)
- [「無料で宣伝できる掲示板」が見つからない問題を、Kurage BBSで解決する](2026-08-13-muryou-senden-keijiban.html)
- [会社の困りごとは『営業・採用・資金繰り』に集約される——3つのAI活用法をまとめました](2026-08-13-ai-eigyou-saiyo-shikin.html)
- [「宣伝OK・リンクOK」の掲示板 Kurage BBS を作った理由 — 被リンク文化を取り戻したい](2026-08-12-kbbs-launch.html)
- [「名古屋AI経営勉強会」を始めました — オープンチャットで、AI経営・バイブコーディング・AIエージェントの質問にゆるく答えます（参加無料）](2026-08-12-nagoya-ai-study.html)
- [業務システムは「作る・買う・紹介する」— AIで選べる3つの道（迷ったら、まず無料相談）](2026-08-12-make-buy-refer.html)
- [システム開発、AIに相談してみませんか — 声で話せる「Kurage.AI 相談チャット」ができるまで](2026-08-11-ai-consult-chat.html)
- [AIで不労所得をつくる — 作って・売って・紹介するだけ。継続30%が積み上がる自動収益化のしくみ](2026-08-11-auto-monetization.html)
- [『Kurage Capacitor Launcher』を作った — ThunderbirdとGoogleカレンダーの連携でつまずき、将来のAndroidアプリの土台にCapacitorを選んだ](2026-08-10-kurage-capacitor-launcher.html)
- [業務システムを、実質タダで手に入れる — 作って・直して・売って・紹介する4ステップ](2026-08-10-system-free-cycle.html)
- [アプリを入れずに、ブラウザで予定を読み書き — 1ファイルのカレンダー kcaldav に WEB画面を付けました](2026-08-10-kcaldav-web.html)
- [カレンダー同期に、巨大なフレームワークはいらなかった — 1ファイルのCalDAVサーバー kcaldav を作って発売しました](2026-08-10-kcaldav.html)
- [ホットペッパーに頼らない予約ページを、自分の店に置く — 予約・受付システム kreserve を発売しました](2026-08-10-kreserve.html)
- [AIエージェントが見つけて、導入し、AIエージェントで育てる — Kurage App Storeを「AIが探せる店」にした作業の全記録](2026-08-09-kappstore-ai-agent-store.html)
- [ロゴは「気に入ったぶんだけ払う」でいい — AIロゴ生成 Kurage Logo Generator を公開しました](2026-08-09-klogogen.html)
- [データベースを、AIにも人にも安全に触らせる — 範囲を宣言する1ファイルのDB管理ツール kdbagent](2026-08-09-kdbagent.html)
- [AIクラゲが架空の政治団体を作りました — 「Kurage党」に見る、時事コンテンツとデジタル道具箱の実験](2026-08-09-kurage-political-party.html)
- [自社サイトのアクセスログを調べたら、AIが1件も記録されていなかった — ktrackgeo を公開しました](2026-08-07-ai-crawler-invisible-in-ga4.html)
- [自社の業務効率化のために作ったものを、そのまま売れるようにしました — 制作サービスとKurage App Storeがつながります](2026-08-07-prototype-to-product-loop.html)
- [「毎朝サイトを見る係」を置けない会社のために — kcheckit を公開しました](2026-08-07-kcheckit-watch-gov-sites.html)
- [請求書を発行して送り、そのまま支払ってもらう — kbilling を公開しました](2026-08-06-kbilling-invoice-collect.html)
- [自社で実際に使っている注文ページを、そのまま商品にしました — kpaylink](2026-08-06-kpaylink-order-page.html)
- [領収書をメールで送るシステムを、あえて1,180行で作った理由 — 非エンジニアが育てられる土台として](2026-08-05-kinvoice-foundation.html)
- [業務システムの「土台」を売る店を作りました — Kurage App Store](2026-08-05-kappstore-open.html)
- [AIと領収書システムを1日で作って、6回つまずいた記録 — VWork教材パッケージを公開しました](2026-08-05-kinvoice-vwork-learning-package.html)
- [AIシステムを、あなたの商材に。Kurage 販売代理店・再販パートナーを募集します](2026-08-05-kurage-reseller-program.html)
- [バイブプロトタイピングとは何か？ 設計書から、動くものを1営業日で](2026-08-05-what-is-vibe-prototyping.html)
- [設計書から動くプロトタイプを1営業日で — Kurage バイブプロトタイプ制作サービスを始めました](2026-08-06-vibe-prototype-service.html)
- [バイブトレーディングとは何か？ AIとの対話を、検証可能な取引戦略に変える方法](2026-08-03-what-is-vibe-trading.html)
- [Kurage GEOで自社サイトを38点から90点へ改善 — exbridge.jpのGEO・日本語AEO診断記録](2026-08-03-kgeo-exbridge-geo-improvement.html)
- [バイブコーディングで「バイブトレーディング」— AIに戦略を相談して自動売買を作れるツール総まとめ](2026-07-31-vibe-trading-tools-guide.html)
- [書籍『AIと作る自動取引ボット入門』をAmazonで出版しました — バイブコーディング×バイブトレーディングの実践書](2026-07-29-vibeaitrade-book-amazon.html)
- [「欲しいシステムはあるのに、頼み方がわからない」経営者へ — AIと対話して設計書を作るKurage Architectを公開しました](2026-07-29-karchitect-for-executives.html)
- [URLAIトークンが「使える場所」ができました — 対応サイト一覧（2026年7月）](2026-07-29-urlai-where-to-use.html)
- [URLAIトークノミクスの設計 — 1枚0.01円・時価総額10億円を目指す「実需」の作り方](2026-07-26-urlai-tokenomics-design.html)
- [AIの力を、独占ではなく分かち合う — Bittensorに学び、URLAIとKurageで育てるトークノミクスの全体像](2026-07-24-urlai-kurage-decentralized-tokenomics-vision.html)
- [「使ってくれてありがとう」をオンチェーンで返す：URL2Pubに10,000 URLAI利用特典を実装しました](2026-07-23-url2pub-urlai-user-reward.html)
- [AI投資委員会「KAIC」を開発しました - 投資情報からAI自動取引、x402 AI Agentへ](2026-07-19-kaic-ai-investment-committee.html)
- [1995年からずっと考えていた「OSSで食べていく方法」に、x402で初めて答えが出た — PayAPI Marketの担当者が同じ想いに共感してくれた話](2026-07-18-oss-monetization-x402-payapi.html)
- [国内の暗号資産AI自動取引を比較して見えた、Kurage FreqAI Tradeの明確な違い](2026-07-14-kfreqai-japan-competitive-advantage.html)
- [SNSで見た「今ホットな銘柄」をAIトレードボットにそのまま追加しなかった話](2026-07-10-kfreqai-hot-coin-tip-verification.html)
- [「全然取引しない」AIトレードボットに、市場全体が下げる日でも機会を拾えるロジックを追加しました](2026-07-09-kfreqai-market-wide-selloff-relative-strength.html)
- [自分で育ち、他のサイトにも客を送る。AIKnowledgeCMSを「集客の司令塔」に育て始めました](2026-07-08-aiknowledgecms-traffic-command-center.html)
- [動画を作って終わりにしない。Kurage動画をテーマ別の知識ライブラリに育てる機能を追加しました](2026-07-04-kurage-knowledge-library-business.html)
- [Kurageプロジェクト公開コンテンツ全ガイド：AIが作ったゲーム・動画・自律メディアはここで見られる](2026-07-04-kurage-public-contents-links.html)
- [人生で初めてゲームを作って公開したら、知らない人がランキングに入っていた — Claude Code（Fable 5）とのバイブコーディング記録](2026-07-02-first-game-dev-with-claude-code.html)
- [「AIエージェントに仕事をさせて稼ぐ」の実態 — x402/MCP/A2Aの本物の技術と、偽エンゲージメント系プラットフォームへの注意喚起](2026-07-01-x402-mcp-agent-economy-warning.html)
- [AIラジオの実画面を、AIがデモ動画にして公開する — Kurage Argo VideoとAIRadioの連携](2026-06-26-kargov-airadio-demo-pipeline.html)
- [Kurage AI VTuber Radio：ライブ配信しながら睡眠用・学習用動画を作るAIラジオ](2026-06-26-kurage-ai-vtuber-radio-sleep-learning.html)
- [海外の有益動画を、自社の発信資産に変える。Kurage Montageで生成したAIショート動画](2026-06-24-kurage-montage-business-video.html)
- [AIに仕事を任せる前に、仕事の進め方を入れる。VWorkにKurage Work Protocolを組み込みました](2026-06-23-vwork-kurage-work-protocol.html)
- [戦争映像を消費せず、経営資産に変える。Kurageで地政学OSINT動画を生成した理由](2026-06-23-geopolitics-osint-video-business.html)
- [初級二：AI プログラミングツールを学ぶ — easy-vibe Stage 1](2026-06-22-easy-vibe-stage1-ai-ide-tools.html)
- [Kurage AI VTuberにYouTubeライブ自動配信機能を追加しました](2026-06-22-kurage-ai-vtuber-youtube-live-automation.html)
- [AI VTuberは“話すキャラクター”から“仕事を進めるAI Agent”へ — Kurage VTuberが示す新しい企業発信](2026-06-21-kurage-agent-vtuber-business.html)
- [kvtuberにブログ投稿を頼み、kdeck経由でAI Agentが記事化するデモ](2026-06-21-kvtuber-kdeck-agent-blog-demo.html)
- [AI VTuberがライブ配信し、AIがデモ動画まで作る時代へ — Kurage AI VTuberとKurage Argo Videoが完成しました](2026-06-21-kurage-ai-vtuber-kargov-business.html)
- [「やってみせる動画」をAIが自動で作る — Kurage Argo Video と、エクスブリッジのAI×OSS内製力](2026-06-19-kurage-argo-video-business.html)
- [ブログ記事がVTuber解説動画になる：Kurageに『VTuber解説モード』を追加しました](2026-06-19-kurage-vtuber-explainer-mode.html)
- [「パソコン操作をAIに任せる」時代へ — 操作手順の自動動画化と、業務そのものを動かすAIエージェント](2026-06-19-pc-gyomu-ai-agent-jidoka.html)
- [外注より安く、SaaSより自由に。OSS×バイブコーディングで「自社のシステム」を持つ](2026-06-17-oss-vibe-coding-naisei.html)
- [経営者こそ「バイブコーディング」を知るべき理由 — セミナー資料を公開しました](2026-06-16-keieisha-vibe-coding-seminar.html)
- [「AIを入れたい」から「AIで動かしている」まで、エクスブリッジが伴走します](2026-06-15-exbridge-service-story.html)
- [「AIを安く、速く、自社仕様で」が実現できる会社がある、という話](2026-06-15-exbridge-ai-oss-business.html)
- [バイブコーディングとは？非エンジニアがAIで仕事を自動化する新しい方法](2026-06-11-vibe-coding-for-non-engineers.html)
- [海外の動画を日本語に自動翻訳・吹き替えする：Kurage Voice-Proが変えるコンテンツ活用](2026-06-11-kurage-voice-pro-for-business.html)
- [スマホからサーバーのAIに指示する：Kurage Agent Deck（kdeck）でできること](2026-06-10-kdeck-smartphone-server-control.html)
- [ジョブを時間で動かすのではなく、目標達成まで動かす](2026-06-08-kdeck-goal-based-job-operations.html)
- [外出先からスマホだけでサーバ障害を復旧できた日](2026-06-06-smartphone-incident-response-kurage-agent-deck.html)
- [メール処理もバイブコーディングで変えられる](2026-06-04-vibe-mail-order-analysis.html)
- [ホリエモンがバイブコーディングでゲームを作った日](2026-06-04-horie-ai-vwork.html)
- [AI自動化を事業で使うなら、実行結果が見える仕組みが必要です](2026-06-03-rqdb4ai-management-dashboard.html)
- [システム開発費、半額以下に抑えませんか？](2026-06-02-system-development-cost-vibe-coding.html)
- [世界最速クラスのx402 AI Agent実装者として、PayAPIに取り上げられた](2026-06-01-x402-ai-agent-payapi-interview.html)
- [AIで経営を変える — 株式会社エクスブリッジが実証するバイブコーディング内製化](2026-05-29-exbridge-for-business.html)
- [経営者こそ見るべき、AIが毎日作るニュース動画「Horizon-AI生成ニュース動画」](2026-05-29-horizonv-for-business.html)
- [Horizon-AI生成ニュース動画をYouTubeにも投稿できるようになりました](2026-05-29-youtube-ai-video-publishing.html)
- [URL2AI / OSS2API が PayAPI Market の審査を通過しました](2026-05-28-payapi-x402-ai-agent-business.html)
- [愛知・名古屋で、AI事業を一緒に作るビジネスパートナーを募集します](2026-05-27-business-partner-ai-vibe-coding.html)
- [AI革命の今、バイブコーディングを愛知の経営者に届けたい——営業パートナー募集](2026-05-26-sales-partner-recruit.html)
- [AIの時代：話せればコードが書ける — easy-vibe Stage 1](2026-05-25-easy-vibe-ai-era.html)
- [バイブコーディング学習ロードマップ：easy-vibe Stage 1 学習マップ](2026-05-25-easy-vibe-learning-map.html)
- [バイブコーディングを体系的に学ぶ：easy-vibe 教材を紹介する](2026-05-25-easy-vibe-introduction.html)
- [Hermes と OpenClaw の役割分担 — orchestration と capability を分離する](2026-05-23-hermes-openclaw-roles.html)
- [Hermes + OpenClaw + Claude + Ollama で商品登録を全自動化した](2026-05-23-autonomous-market-pipeline.html)
- [業務システムの本質は「UI中心」から「API中心」へ](2026-05-20-ui-to-api-centric-systems.html)
- [AIエージェントによる次世代ECモデルの実験 — AIxEC](2026-05-20-aixec-next-gen-ec-model.html)
- [経営者にこそ、バイブコーディングを体感してほしい](2026-05-19-message-to-business-owners.html)
- [バイブコーディングで、ホームページ制作を内製化する](2026-05-19-homepage-inhouse-vibe-coding.html)
- [バイブコーディングは、すべてのPC作業に使える](2026-05-18-vibe-coding-for-all-pc-work.html)
- [手入力をなくすことは、システム内製化の入口](2026-05-18-input-automation-and-vwork.html)
- [VWorkとは？](2026-05-18-what-is-vwork.html)
- [VWorkリポジトリを知識置き場兼ブログにする](2026-05-18-vwork-as-knowledge-blog.html)
