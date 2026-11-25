---
title: "AI-OCRをオンプレミスで。インターネットにつながない環境で手書きFAX・スキャンPDFを読む「Kurage OCR Work」"
title_aixsns: "個人情報を扱う書類を、インターネットに一度も出さずに読み取るAI-OCR「Kurage OCR Work」を紹介します。OCRのエンジンも生成AIも社内のサーバーで動き、注文書・手書きFAX・スキャンしたPDFを読んで、項目を取り出し、受注登録やCSV出力まで行います。読み方は書類ごとに切り替えて読み比べられます"
title_hatena: "AI-OCRをオンプレミスで。手書きFAX・スキャンPDFを社内だけで読む"
title_blogger: "オンプレミスのAI-OCR Kurage OCR Work"
tags: [AI-OCR, オンプレミス, OCR, 手書きOCR, FAX, スキャンPDF, PaddleOCR, Tesseract, Docling, ローカルLLM, 個人情報, 業務システム]
description: "インターネットにつながない環境で使えるAI-OCR「Kurage OCR Work」を紹介します。OCRのエンジンと生成AIを社内のサーバーで動かし、手書きFAXやスキャンしたPDFから項目を取り出してCSVや受注登録にします。読み方の切り替えと、実測の一致率も載せます。"
seo_title: "AI-OCRをオンプレミスで｜手書きFAX・スキャンPDFを社内で"
head_keyword: "AI-OCR オンプレミス"
og_stat: "AI-OCR オンプレミス"
og_stat_label: "手書きFAX・スキャンPDFを社内のサーバーだけで読む"
og_stat_note: "Kurage OCR Work（株式会社エクスブリッジ）"
date: 2026-11-25
layout: default
permalink: /blog/2026-11-25-ai-ocr-onpremise-tegaki-fax-kocrwork.html
---

名古屋でAIシステムの開発をしている、株式会社エクスブリッジの小嶋です。当社のAI-OCR「Kurage OCR Work」を紹介します。注文書や手書きのFAX、スキャンしたPDFを読み取り、項目を取り出して受注登録やCSV出力まで行うシステムで、**インターネットにつながない環境で動かせる**のが特長です。

Kurage OCR Work（デモ）
https://proto.exbridge.jp/kocrwork.php/

どんなものかを、50秒ほどの動画にまとめています（音声が出ます）。

<div style="width:100%;max-width:960px;margin:16px auto;border-radius:10px;overflow:hidden;background:#000">
  <video src="https://kurage.exbridge.jp/pv/kocrwork-pv.mp4" poster="https://kurage.exbridge.jp/pv/kocrwork-pv-poster.jpg" controls playsinline preload="none" style="display:block;width:100%;height:auto"></video>
</div>

## 書類を外に出せない会社のために

AI-OCRのサービスの多くは、書類の画像をクラウドに送って読み取ります。手軽ですが、申込書や届出書のように個人情報が載っている書類では、「外部のサービスに送ってよいのか」がいつも問題になります。社内の決まりで、インターネットにつながる端末で扱えない書類もあります。

Kurage OCR Work は、OCRのエンジンも生成AIも、すべて御社のサーバーの中で動きます。書類の画像も読み取った文字も、社外に出ません。社内LANにつながった端末のブラウザから使い、サーバーはインターネットにつながなくても動きます。

## 書類ごとに、読み方を切り替えられる

書類の種類によって、合う読み方が違います。Kurage OCR Work は、OCRのエンジンと生成AIの使い方を切り替えて、同じ書類を読み比べられます。

- **OCRのエンジン**：PaddleOCR、Tesseract、OCRmyPDF（スキャンしたPDFに文字の層を付ける）、Docling（文字の入ったPDF向け）など
- **生成AIの使い方**：使わない（決まりで項目を拾う）／OCRの文字から項目に直す／画像を直接見て項目にする
- **生成AI**：社内で動かすローカルのモデル（既定は gemma4）

当社の見本の書類で、正解とどれだけ一致したかを測った結果です。

- 印刷の注文書（画像）：PaddleOCR＋決まりで拾う → 100%
- 文字の入ったPDF：Docling＋決まりで拾う → 100%
- スキャンしたPDF：PaddleOCR → 100%、Tesseract＋OCRmyPDF → 81%前後
- 手書きで記入したFAX：PaddleOCRだけ → 33%、生成AIで文字から直す → 73%、**生成AIで画像を見る → 93〜97%**

手書きは、生成AIに画像を見せる読み方で大きく上がります。ただし、この見本の手書きは手書き風のフォントで作ったもので、本物の手書きではありません。導入の前に、その会社の本物の書類で測り直します。手書きを生成AIで読むには、GPUのあるサーバーがあると速く読めます。

## 読んだあとまでつなぐ

取り出す項目（注文番号・日付・取引先・明細・合計など）は、書類の種類ごとに設定ファイル1つで決めます。読み取った結果は画面で確かめて直してから登録でき、台帳にたまった分は CSV で書き出せます。基幹システムや kintone へは、登録のたびに JSON を送る形でつなげます。

AIエージェントから呼び出す口（MCP）も付けているので、「このPDFを読んで受注に登録して」といった使い方もできます。

## ソースコードごと納品します

Kurage OCR Work は買い切りで、ソースコード一式をお渡しします。月額の利用料も、読み取り枚数に応じた料金もかかりません。中身を御社で確かめられるので、セキュリティの審査にも出しやすい形です。

組み込んでいる部品は、どれも商用で使えるオープンソース（Apache-2.0・MIT・BSD など）にそろえています。PDFを画像にする部品は、利用に条件のあるものから pypdfium2 に入れ替えました。

## よくある質問

### インターネットに一度もつながないサーバーで使えますか

使えます。設置用の一式（プログラム・AIのモデル・手順書）を用意して、オフラインのまま入れられます。

### 手書きの書類はどのくらい読めますか

書類によって大きく変わります。当社の見本では、生成AIで画像を見る読み方で93〜97%でしたが、本物の手書きではまだ測っていません。御社の書類（個人情報を伏せたもの）で試してから、合う読み方を決めます。

### Excelで書き出せますか

今はCSVで書き出します。Excelでの書き出しが必要な場合は、作り足します。

Kurage OCR Work（導入版・Kurage App Store）
https://kappstore.exbridge.jp/app.php?id=ef52a62e1c6bbe7a#ref=vibeblog-kocrwork

御社の書類に合わせた設定や、オフライン環境への設置は、AI-IT顧問やご相談で承ります。

AI-IT顧問
https://exbridge.jp/ai-it-komon.html#ref=vibeblog-kocrwork
