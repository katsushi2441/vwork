---
title: "化学試験報告書の「数値を変えない」AI校正・照査を作った――FastAPI、Pandera、Pint、textlint、Gemma 4の役割分担"
emoji: "🧪"
type: "tech"
topics: [生成ai, 品質管理, oss, python, fastapi]
published: true
---

化学試験結果報告書をAIに読ませれば、文章の校正だけでなく、試料番号の不一致、必須項目の欠落、規格値と測定値の矛盾まで見つけられます。しかし、一般的な文章生成と同じ感覚でLLMに「直して」と頼むと、測定値や合否判定まで自然な文章へ書き換えられる危険があります。

そこで開発したのが、日本語の化学試験結果報告書に特化した **Kurage Proofread（Kurage 校正・照査システム）** です。

- プロダクト: [Kurage Proofreadを使う](https://kurage.exbridge.jp/kproofread.php)
- 日本語LP: [Kurage 校正・照査システム](https://kproofread.exbridge.jp/kproofread.html)
- English LP: [Kurage Proofread](https://kproofread.exbridge.jp/)
- 自社向けカスタマイズ: [バイブプロトタイピング](https://kurage.exbridge.jp/vibe-prototype.html?ref=vwork-kproofread)

この記事では、開発に活用したOSSと、決定論的なルール・日本語校正・ローカルLLMをどう分担したかを解説します。

## 化学報告書では「文章」と「事実」を分ける

Kurage Proofreadが最も重視する原則は、**AIに測定事実を決定させない**ことです。

システムは、次の項目を自動変更しません。

- 測定値
- 規格値
- 単位
- 合否判定

数値や判定に疑義があれば、位置・根拠・重要度・確認事項を指摘として残し、最終判断は人間の照査者が行います。安全に置換するのは、`㎎`を`mg`へ直すような意味を変えない表記ゆれに限定しました。

この線引きを実現するため、処理を3層に分けています。

```text
DOCX / XLSX / PDF / TXT / CSV
  |
  +-- 1. 決定論的照査
  |      必須項目、識別番号、表構造、単位、規格と結果、合否の整合
  |
  +-- 2. 日本語校正
  |      textlintによる技術文書の表記・文体チェック
  |
  +-- 3. AI意味照査
         Gemma 4による表と本文の矛盾、論理的欠落、考察不足の指摘
```

同じ入力から同じ結果を得たい検査はコードで行い、文脈を読まないと判断できない部分だけをLLMに任せます。

## 活用したOSSと役割

Kurage Proofreadは、用途の明確なOSSを小さく組み合わせて構築しました。

| OSS | ライセンス | Kurage Proofreadでの役割 |
|---|---|---|
| [FastAPI](https://github.com/fastapi/fastapi) | MIT | アップロード、照査、履歴、ダウンロードを扱うWeb API |
| [python-docx](https://github.com/python-openxml/python-docx) | MIT | DOCXの段落・表の抽出、照査結果付きDOCXの生成 |
| [openpyxl](https://foss.heptapod.net/openpyxl/openpyxl) | MIT | XLSXのセル抽出、指摘コメント・色・照査結果シートの追加 |
| [pypdf](https://github.com/py-pdf/pypdf) | BSD-3-Clause | テキストPDFからページ・行単位で文章を抽出 |
| [Pint](https://github.com/hgrecco/pint) | BSD-3-Clause | 単位表記の解釈と妥当性確認 |
| [Pandera](https://github.com/unionai-oss/pandera) | MIT | 測定項目と測定値を持つ表データのスキーマ検証 |
| [textlint](https://github.com/textlint/textlint) | MIT | 日本語文章の校正基盤 |
| [textlint-rule-preset-ja-technical-writing](https://github.com/textlint-ja/textlint-rule-preset-ja-technical-writing) | MIT | 技術文書向けの日本語ルール |
| [Ollama](https://github.com/ollama/ollama) | MIT | Gemma 4をローカルで呼び出すOpenAI互換推論基盤 |

複雑な表や画像PDFの抽出については、MITライセンスの [Docling](https://github.com/docling-project/docling) を任意拡張の候補として設計に含めています。ただし、現在の基本処理は軽量な `pypdf` などで動作しており、**Doclingを使ったように見せるのではなく、現時点では参考・拡張候補として明確に区別**しています。

## 1. 文書形式ごとに位置を失わず抽出する

照査結果で重要なのは、「問題があります」ではなく「どこを確認すべきか」が分かることです。

- DOCX: `本文 段落3`、`表1 R4C2`
- XLSX: `試験結果!D12`
- PDF: `PDF 2ページ 8行`
- CSV: `CSV R5C3`

のように、抽出時点で位置情報を付与します。XLSXでは問題のあるセルへコメントと重要度別の色を付け、別シートにも指摘一覧を生成します。DOCXでは原文の末尾に照査結果を追加します。PDF、TXT、CSVは原本を変更せず、抽出内容と照査結果をDOCXへ出力します。

画像だけで作られたPDFを文字抽出できなかった場合は、成功したように扱わず「OCRが必要」と明示して停止します。抽出失敗をLLMの推測で埋めないことも、照査システムでは重要です。

## 2. PanderaとPintで、LLMの前に事実を検査する

測定表は見出しの表記が一定ではありません。「試験項目」「測定項目」「成分」を分析対象名として扱い、「測定値」「試験結果」「結果」を数値列として認識するエイリアスを用意しました。

抽出した行はPanderaで、少なくとも次の構造を満たすか検証します。

```python
MEASUREMENT_SCHEMA = pa.DataFrameSchema(
    {
        "analyte": pa.Column(
            str,
            checks=pa.Check.str_length(min_value=1),
            nullable=False,
        ),
        "result": pa.Column(float, nullable=False, coerce=True),
    },
    strict=False,
    coerce=True,
)
```

Pintは、`mg`、`mL`、`ppm`、`ppb`、`%`などの単位を機械的に解釈するために使います。ここで扱えない単位は即座に誤りと断定せず、「試験法で定めた表記か確認してください」という指摘に留めます。化学分野固有の単位が存在するからです。

規格範囲と測定値の比較、記載された合否との不一致、試料番号・ロット番号の不一致もルールで判定します。これらはLLMよりも、根拠を追跡できるコードの方が向いています。

## 3. textlintとGemma 4は役割を重ねない

日本語の表記・文体はtextlintへ任せます。一方、Gemma 4は次のような意味上の確認に限定しています。

- 表と本文の記述が矛盾していないか
- 結論に対する考察や根拠が不足していないか
- 文書内だけでは説明できない論理的な飛躍がないか
- 照査者が読むべき日本語上の問題がないか

LLMへのシステム指示にも、次の制約を明記しています。

```text
測定値、規格値、単位、合否判定の変更を決定してはいけません。
推測で値を補わないでください。
根拠がない指摘は出さず、最大12件にしてください。
```

LLMの出力は自由文ではなくJSONへ固定し、`severity`、`category`、`location`、`title`、`suggestion`、`reason`、`evidence`を保存します。AIが返した指摘にも `auto_fixable=false` を設定し、勝手な修正を防ぎます。

現在の本番構成では、このマシンのOllamaで `gemma4:12b-it-qat` を実行しています。元ファイルそのものではなく抽出テキストだけをローカル推論基盤へ渡し、AI照査を外して決定論的照査だけを実行することもできます。

## 実際の出力で確認したこと

公開前のサンプルDOCXを使った動作確認では、決定論的ルールによる指摘5件とAIによる指摘4件が返り、次の2種類のファイルをダウンロードできることを確認しました。

1. 原文に安全な表記修正と照査結果を加えたファイル
2. 指摘事項を独立してまとめた照査レポートDOCX

ただし、指摘が0件でも「無欠陥」を保証する結果にはしません。画面と出力ファイルの双方で、最終判断は照査者が行うことを明示しています。

## 自社帳票へはバイブプロトでカスタマイズできる

化学試験報告書は、会社・部門・試験法ごとに必須項目、帳票、用語、承認手順が異なります。そのためKurage Proofreadは、完成形を一律に押し付けるのではなく、実際の帳票と業務を見ながら **バイブプロトタイピングで自社仕様へカスタマイズ**できます。

例えば、次の拡張が可能です。

- 自社帳票に合わせた必須項目・規格・用語・表記ルール
- Word、Excel、PDFの独自テンプレート対応
- 試験者、照査者、承認者の権限とワークフロー
- LIMS、QMS、ファイルサーバー、社内システムとの連携
- 監査ログ、差分履歴、通知、再照査フロー
- 社内認証、画面デザイン、ブランド表記の統合

[バイブプロトタイピング](https://kurage.exbridge.jp/vibe-prototype.html?ref=vwork-kproofread)では、まず動くデモで業務との相性を確認し、その場でAIと相談しながら仕様を詰められます。長い要件定義書を先に作るのではなく、「この帳票なら、どこまで自動化し、どこを人間に残すか」を実物で判断できる進め方です。

## まとめ

Kurage Proofreadの設計を一言で表すと、**事実は決定論的に検査し、意味だけをLLMに読ませ、修正の決定は人間に残す**です。

- FastAPIで照査パイプラインと履歴・ダウンロードを構成
- python-docx、openpyxl、pypdfで位置情報を保って文書を抽出
- PanderaとPintで表構造・数値・単位を再現可能なルールとして検査
- textlintで日本語技術文書を校正
- Gemma 4は矛盾・欠落・考察不足の意味照査に限定
- 測定値、規格値、単位、合否判定は自動変更しない

まずは公開版で、サンプル報告書または手元の文書を使って照査の流れを確認できます。

- [Kurage Proofreadを使う](https://kurage.exbridge.jp/kproofread.php)
- [日本語の製品紹介を見る](https://kproofread.exbridge.jp/kproofread.html)
- [English product page](https://kproofread.exbridge.jp/)
- [自社向けカスタマイズを相談する](https://kurage.exbridge.jp/vibe-prototype.html?ref=vwork-kproofread)
