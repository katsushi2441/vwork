---
title: "AIチャットボットは高すぎる——だから55,000円買い切りの『Kurage Light ChatBot』を作りました（導入は3つの入口から）"
description: "AIチャットボットの相場はSaaSで月額2〜5万円が永続、受託開発なら50〜200万円。高すぎて中小企業が手を出せない市場に、買い切り55,000円・月額なし・1ファイルPHPのナレッジチャットAI『Kurage Light ChatBot』を投入しました。sources/フォルダにMarkdownを置くだけでFAQ・AI接客・社内ChatGPTになり、LLM実費は1回答数円。完成品を買う/開発手順書で自作する/自社仕様に作ってもらう——すべてのニーズに対応する3つの入口つきで提供開始した経緯と設計判断を書きます。"
date: 2026-08-16
layout: default
permalink: /blog/2026-08-16-klchatbot-launch.html
---

AIチャットボットを入れたい。調べた会社が最初にぶつかるのは、機能ではなく**値段**です。

- SaaS型: 初期0〜30万円＋**月額2〜5万円が使い続ける限り**（年24〜60万円）
- カスタム開発: **50〜200万円**
- フルスクラッチ: 300万円〜

「営業時間を答える」「FAQに答える」がやりたいことの大半なのに、この価格帯しか選択肢がない。だから当社は、**買い切り55,000円（税込）・月額なし**のナレッジチャットAI「**[Kurage Light ChatBot](https://kappstore.exbridge.jp/app.php?id=224e141f77bd07a8&ref=vwork)**」を開発し、本日から提供を開始しました。

## 実物を先に触ってください

**デモ: <https://proto.exbridge.jp/klchatbot/>**

当社の商品知識を学習した状態の実物です。「予約システムはいくら？」と聞くと、**55,000円という価格も商品URLも一字一句正確に**答えます。この「事実を正確に引用する」が、このジャンルの品質の芯です。

## なぜ55,000円で成立するのか——3つの設計判断

**1. 「使う2割」だけに絞った。** Open WebUIのような多機能OSSは立派ですが、中小企業のFAQ窓口に必要なのはチャット画面・知識の読み込み・利用制限くらいです。本体は**PHP1ファイル（約550行）・DBサーバー不要**。レンタルサーバーにFTPで上げるだけで動きます。

**2. 知識は「フォルダにMarkdownを置くだけ」。** sources/フォルダにFAQ・商品一覧・マニュアルを置くと、その内容に基づいて答えます。管理画面での登録作業はありません。知識は毎回同じ順序でAIに渡す設計にしてあり、**LLM側のキャッシュが効いて2回目以降の実費が大きく下がります**（直近のDeepSeek値上げを織り込んだ設計です）。

**3. LLMは持たず、選べるようにした。** OpenAI互換APIなら何でも使えます（既定はDeepSeek）。APIキーは購入者自身のもの——つまり**月額のシステム利用料はゼロ、かかるのはLLM実費（1回答数円・キャッシュが効けば1円未満）だけ**。お客様向けFAQ・AI接客モードと、合言葉制の社内ChatGPTモードは設定1行で切り替えられます。

## 「すべてのニーズ」に応えるため、入口を3つ用意しました

先日書いた[『3つの入口』でシステムを売る実験](https://katsushi2441.github.io/vwork/blog/2026-08-15-three-doors-model.html)の第2弾実践です。同じゴールに、あなたに合う入口からどうぞ。

1. **完成品を買う（55,000円税込）** — すぐ使いたい方。即ダウンロード・ソースコード付き（MIT・改変再販自由）
   → [Kurage App Store](https://kappstore.exbridge.jp/app.php?id=224e141f77bd07a8&ref=vwork)
2. **開発手順書を買って自分で作る（同価格55,000円）** — 作る力を手に入れたい方。環境構築からデプロイまで、コピペで使う開発プロンプト11本付きの完全ガイド
   → [klchatbot開発手順書（Brain）](https://brain-market.com/u/bittensorman/a/b1EDNxYjMgoTZsNWa0JXY)
3. **自社仕様に作ってもらう（110,000円税込）** — 業務システム連携や作り込みが必要な方。最短1営業日で動くデモ
   → [バイブプロトタイピング](https://kurage.exbridge.jp/vibe-prototype.html?ref=vwork)

手順書が完成品と同じ値段なのは意図的です。AIエージェント（Claude Code等）が手順書を実行できる時代になり、「作り方」には完成品と同じ価値が付くようになりました。どれを選ぶか迷ったら、[無料のAI相談チャット](https://kurage.exbridge.jp/chat.php?ref=vwork)（これ自体が同系統の実物です）でどうぞ。

## 正直な注意書き

- LLMのAPIキー取得（無料登録・従量課金）はご自身で行っていただきます。手順はdocsに書きました
- 社内文書を扱う場合は「サーバーに置いてよい文書か」の判断が先です。出せない文書はローカルLLM構成の相談を
- デモには利用回数制限があります（1時間10回・API費用の防波堤です）

## 関連リンク

- 商品: [Kurage Light ChatBot（55,000円税込）](https://kappstore.exbridge.jp/app.php?id=224e141f77bd07a8&ref=vwork) ／ [無料デモ](https://proto.exbridge.jp/klchatbot/)
- 費用相場から知りたい方: [AIチャットボット開発の費用相場と「買い切り11万円」という選択肢](https://kurage.exbridge.jp/ai-chatbot-kaikiri.php?ref=vwork)
- 技術背景: [OpenKB検証記事（ベクトルDB不要RAGの得意・不得意）](https://katsushi2441.github.io/vwork/articles/2026-08-15-openkb-rag-chatai.html)
- 経営×AIをゆるく学ぶ: [名古屋AI経営勉強会（無料・匿名OK）](https://kurage.exbridge.jp/nagoya-ai-study.php?ref=vwork)
- 紹介して収益に: [販売代理店制度（最大30%）](https://kurage.exbridge.jp/reseller.html?ref=vwork)
