---
title: "whisper.cppで日本語の文字起こしを自社サーバーで動かす——使い方と実測（47秒の会議音声を27秒・文字誤り率2.7%）、AI議事録まで自動化する構成"
emoji: "🎙️"
type: "tech"
topics: ["whisper", "whispercpp", "文字起こし", "議事録", "oss"]
published: true
title_hatena: "GPU無しの自社サーバーで日本語文字起こし——whisper.cppの使い方と実測（誤り率2.7%・実時間の0.57倍）"
title_blogger: "会議の録音を社外に出さずに文字起こしする。whisper.cppを自社サーバーで動かした記録"
---

会議の録音を文字に起こしたい。ただし録音を外部のクラウドに送りたくない、分単位の課金も避けたい。そういう会社向けに、OpenAI の音声認識モデル **Whisper** を C++ に移植した **whisper.cpp** を自社サーバーで動かし、日本語の文字起こしがどのくらいの速さと精度で動くかを実測しました。当社の買い切り製品 [Kurage AI MOM](https://kappstore.exbridge.jp/app.php?id=cd1eda3248c87920&ref=vwork-whisper)（録音→文字起こし→AI議事録）は、この構成をそのまま製品にしたものです。

結論を先に書きます。

- **CPU だけ**（GPU 無し・12スレッド）で、47.4秒の日本語音声を **27.1秒**で文字起こしできました（実時間の0.57倍）
- モデルは **large-v3-turbo**。数字の表記ゆれを除いた**文字誤り率は 2.7%**（257文字中、実質の誤りは3か所）
- **small モデルは使い物になりませんでした**（5.8秒で速いが、文の半分を落として誤り率56%）
- 誤ったのは固有名詞と日付の読み（「進捗」→「新書」「三十日」→「時末」「見積書」→「三日」）。この種の誤りは後段の AI 要約と用語辞書で吸収します

## Whisper と whisper.cpp の違い

[Whisper](https://github.com/openai/whisper)（MIT・GitHubスター約108,000）は OpenAI が公開した音声認識モデルで、日本語を含む約100言語に対応します。本家は Python＋PyTorch で、GPU があれば large モデルでも速く動きます。

[whisper.cpp](https://github.com/ggml-org/whisper.cpp)（MIT・約53,000）は同じモデルを C/C++ で動かす実装です。PyTorch も GPU も要らず、依存が少ないので、Linux サーバーに常駐させて「録音を受け取ったら文字起こしする」サービスにしやすい。当社が製品に採用したのはこちらです。精度は同じモデルなら大きく変わりません。

## 使い方（Linux・CPU）

1. ビルドと、モデルのダウンロード

```bash
git clone https://github.com/ggml-org/whisper.cpp
cd whisper.cpp && cmake -B build && cmake --build build -j
sh ./models/download-ggml-model.sh large-v3-turbo   # 約1.6GB
```

2. 音声を 16kHz・モノラルの WAV にそろえる（whisper.cpp はこの形式を前提にします）

```bash
ffmpeg -i meeting.m4a -ar 16000 -ac 1 -c:a pcm_s16le meeting16k.wav
```

3. 日本語を指定して実行する（`-t` はスレッド数、`-nt` はタイムスタンプ無し）

```bash
./build/bin/whisper-cli -m models/ggml-large-v3-turbo.bin -l ja -t 12 -nt -f meeting16k.wav
```

これだけで本文が標準出力に出ます。会議の録音は長いので、当社の製品では前段に VAD（無音区間の検出、silero）を入れて、無音を飛ばしてから認識しています。

## 実測

音声は、当社の TTS（Audio8）で読み上げた 278文字の「定例会議」の原稿（47.4秒）です。原稿があるので、認識結果との文字単位の差分から誤り率を出せます。実際の会議録音は雑音や複数話者で条件が悪くなるので、ここでの数字は「静かな環境・1話者」の上限値として読んでください。

サーバーは当社の Linux 機（CPU 12スレッド・GPU は使わず）です。

| モデル・条件 | 処理時間（47.4秒の音声） | 文字誤り率（数字の表記ゆれを除く） | 実質の誤り |
|---|---|---|---|
| large-v3-turbo＋VAD（製品の設定） | 27.1秒 | **2.7%** | 3か所 |
| large-v3-turbo（VAD なし） | 20.1秒 | 6.2% | 4か所 |
| small | 5.8秒 | 56.4% | 文の半分を欠落 |

誤り率の計算では、「十二件」と「12件」のような数字の表記ゆれは誤りに数えていません。素の差分では 13.2% になりますが、その大半がこの表記ゆれでした。文字起こしの結果はアラビア数字で返るので、原稿側を揃えて比べています。

**実質の誤り**は次の3か所です。

- 「九月三十日」→「9月3時末」（日付の読み）
- 「進捗」→「新書」（同音に近い語）
- 「見積書」→「三日」

固有名詞と、文脈で決まる語を取り違える、という Whisper に共通の傾向です。逆に、数字・件数・日付のような「会議で大事な値」は、日付の1か所を除いてすべて正しく取れました。

## 誤りをどう吸収するか

文字起こしをそのまま議事録にはしません。当社の製品では、次の2段を後ろに置いています。

1. **AI 要約**（ローカル LLM・gemma4）に、文字起こし全文と「決定事項・宿題・期日」を抜く指示を渡す。「新書」のような誤りは文脈で「進捗」と読み直されることが多い
2. **用語辞書**で、社名・製品名・担当者名を置換する。固有名詞は文字起こし側で直らないので、会社ごとに辞書を持つのが確実

この2段を入れると、上の3か所の誤りは議事録の段階では消えていました。

## サーバーに常駐させる構成

製品の構成はこうです。

- 受付: 録音ファイルを受け取り、ffmpeg で 16kHz に変換して待ち行列に入れる
- 認識: whisper.cpp を**1本ずつ直列**で実行する（並列にすると CPU を取り合って全体が遅くなる）
- 要約: 同じサーバーのローカル LLM が決定事項・宿題・期日を書き出す
- 保存: 文字起こし・議事録・元の録音をサーバー内に置く。外部には何も送らない

録音を外に出さずに済むこと、分単位の課金が無いこと、この2つが自社サーバーで動かす理由です。GPU が無くても、47秒の音声が27秒で終わる速さなら、1時間の会議は35分ほどで文字になります。

## まとめ

- whisper.cpp は GPU 無しの自社サーバーで日本語の文字起こしが実用になります。large-v3-turbo で誤り率 2.7%、実時間の 0.57倍でした
- small は速いが精度が足りません。CPU でも large-v3-turbo を使うのが正解です
- 誤るのは固有名詞と一部の日付。AI 要約と用語辞書で吸収します

同じ構成を買い切りで提供しているのが [Kurage AI MOM（税込55,000円）](https://kappstore.exbridge.jp/app.php?id=cd1eda3248c87920&ref=vwork-whisper) です。文字起こし AI のオープンソースを実測つきで比較した一覧は [文字起こしAIのオープンソース一覧・比較](https://exbridge.jp/ai-system/c/aivoice/?ref=vwork-whisper) に、whisper.cpp そのものの解説は [whisper.cpp の紹介ページ](https://kurage.exbridge.jp/oss/whisper-cpp/) にまとめています。

## 参考

- whisper.cpp: https://github.com/ggml-org/whisper.cpp （MIT）
- Whisper（本家）: https://github.com/openai/whisper （MIT）
- 実測に使ったスクリプトと結果: 当社の kaimom リポジトリ内 `outputs/whisper-test/`（原稿・認識結果・差分）
- 関連記事: [Namazu全文検索×買い切りチャットボット×AIの開発実績](https://katsushi2441.github.io/vwork/blog/2026-09-04-namazu-ai-chat-knowledge.html)
