---
title: "Kurage Voice-Proの技術解説：UMediaとOSS Voice-Proをつないだ翻訳字幕・吹き替え動画生成"
emoji: "🎙️"
type: "tech"
topics: ["ai", "動画生成", "字幕", "tts", "ffmpeg"]
published: true
---

# Kurage Voice-Proの技術解説：UMediaとOSS Voice-Proをつないだ翻訳字幕・吹き替え動画生成

Kurage Voice-Proは、Xなどの動画URLから動画を取得し、音声認識、翻訳、翻訳字幕、翻訳音声、字幕付き吹き替え動画の生成までを行うために作った動画翻訳ワークフローです。

公開画面はこちらです。

- Kurage Voice-Pro: https://kurage.exbridge.jp/kuragevp.php
- Kurage Project: https://kurage.exbridge.jp/

今回の実装で重視したのは、最初から巨大な動画翻訳サービスを作ることではありません。

すでに動いていた複数の技術を分解し、使える部分を組み合わせて、まず実際に公開できる翻訳字幕・吹き替え動画を作れる状態にすることでした。

---

## 何を組み合わせたか

Kurage Voice-Proは、主に3つの既存技術から作っています。

```text
UMedia
  -> URL / X投稿から動画を取得する考え方

OSS Voice-Pro
  -> 音声抽出、Whisper字幕、翻訳、TTS、ffmpeg処理の考え方

Kurage
  -> FastAPI + PHP proxy + Xログイン + 動画公開UI
```

UMediaは、URLやX投稿を起点にコンテンツを取得する仕組みです。  
Kurage Voice-Proでは、X動画については `api.fxtwitter.com` を使って動画URLを解決し、`curl` で動画ファイルを取得する方式を採用しました。

OSS Voice-Proからは、音声認識、翻訳、TTS、ffmpeg合成という処理の分解方法を参考にしました。  
ただし初期実装では、重い依存をすべてそのまま抱え込むのではなく、CLIで安定して動く経路を優先しています。

Kurageからは、ジョブ投入、進捗表示、生成物の公開、スマホから使えるWeb UIの考え方を流用しました。

---

## 処理フロー

現在のKurage Voice-Proの処理は、次の順番で進みます。

```text
1. URLから動画を取得
2. ffmpegで音声を抽出
3. faster-whisperで文字起こししてSRTを作成
4. deep-translatorで字幕を翻訳
5. edge-ttsで翻訳音声を生成
6. ASS字幕を生成して動画へ焼き込み
7. 翻訳音声を動画へ合成
8. Kurageの動画として公開
```

成果物としては、次のようなファイルが生成されます。

```text
source.wav
source.srt
translated.ja.srt
translated_voice.m4a
subtitled.mp4
dubbed.mp4
translated_subtitled_dubbed.mp4
```

最後に、Kurage本体の公開ディレクトリへメタデータと動画を保存します。

```text
/home/kojima/work/kurage/storage/jobs/{job_id}.json
/home/kojima/work/kurage/storage/jobs/{job_id}/output.mp4
/home/kojima/work/kurage/storage/jobs/{job_id}/thumbnail.jpg
```

これにより、生成結果は通常のKurage動画と同じように、次の形式で見られます。

```text
https://kurage.exbridge.jp/kuragev.php?id={job_id}
```

---

## FastAPIとPHP proxyで公開する

Kurage Voice-ProのPython APIはFastAPIで動かしています。

```text
GET  /health
POST /generate
GET  /status/{job_id}
GET  /jobs
GET  /file/{job_id}/{kind}
```

ブラウザから直接APIへアクセスさせるのではなく、公開サーバ側の `kuragevp.php` がPHP proxyとしてAPIを呼び出します。

この構成にしている理由は3つあります。

- Xログインなどの共通認証をKurage側の仕組みに乗せられる
- APIポートや内部URLをブラウザに直接出さずに済む
- heteml側のPHP画面と、GPUサーバ側のPython処理を分けられる

画面は `https://kurage.exbridge.jp/kuragevp.php` に置き、Python APIは内部的に18300番台のポートで動かしています。

---

## 字幕はSRTのままではなく、Kurage風ASS字幕にする

最初は翻訳SRTをそのまま動画に焼き込めばよいように見えます。

しかしスマホ向けの縦型動画では、通常のSRT字幕は見にくくなりがちです。

そこでKurage Voice-Proでは、翻訳SRTからASS字幕を生成し、Kurageらしい縦型動画向けの字幕に変換しています。

実装上のポイントは次の通りです。

- 長い翻訳文を短い字幕チャンクに分割する
- 画面下部で読みやすいサイズと余白にする
- 翻訳音声の長さに合わせて字幕タイミングを伸縮する
- 数字の `1,000` のようなカンマを、文の区切りとして誤判定しない

とくに最後の数字カンマは、小さなバグに見えて動画品質にかなり影響します。

英語圏の動画では `1,000` や `10,000` のような数字表記がよく出ます。  
これを通常の読点と同じように分割してしまうと、字幕が不自然に切れてしまいます。

そのため、句読点で切る処理と、数値表記のカンマを区別するようにしました。

---

## 翻訳音声の長さに動画を合わせる

動画翻訳で難しいのは、翻訳後の音声が元動画より長くなることです。

英語から日本語に翻訳すると、同じ内容でも読み上げ時間が変わります。  
字幕だけなら元動画のタイムラインに合わせればよいのですが、吹き替え音声を入れる場合は、音声の長さに動画側を合わせる必要があります。

Kurage Voice-Proでは、翻訳音声の長さを取得し、字幕焼き込み後の動画をその長さに合わせて生成する方向に寄せました。

これにより、音声だけが途中で切れる、字幕だけ先に終わる、といった破綻を減らせます。

現時点ではEdge-TTSを使っています。  
つまり、元動画の声をそのままクローンしているわけではありません。

今後はOSS Voice-Pro本体が持つF5-TTS、CosyVoice、RVC系の技術を活用し、元動画の声に寄せた翻訳音声へ発展させる余地があります。

---

## まず動く経路を作る意味

OSSの動画翻訳ツールをそのまま導入しようとすると、依存関係が重くなりがちです。

GPU、CUDA、Whisper、TTS、音声変換、ffmpeg、Web UI、公開ディレクトリ、認証。  
これらを一度に完璧にそろえようとすると、実運用に届く前に詰まりやすい。

Kurage Voice-Proでは、最初に次のように割り切りました。

- 取得はUMedia方式で安定させる
- 文字起こしはfaster-whisperで行う
- 翻訳はdeep-translatorで行う
- TTSはEdge-TTSでまず成果物を作る
- 字幕と音声合成はffmpegで行う
- 公開はKurageの既存動画UIへ乗せる

この段階でも、X動画を日本語字幕・日本語音声付きの縦型動画として公開できます。

実際に生成したサンプルです。

- MrBeastが語る「休日も働く」計算とその代償  
  https://kurage.exbridge.jp/kuragev.php?id=b9b0006cde6849de

- MrBeastが語る、顔出しなしで伸びるYouTubeの知識戦略  
  https://kurage.exbridge.jp/kuragev.php?id=c6cd03bc9a2e480c

---

## Kurage UMedia Voice-ProからKurage Voice-Proへ

今回の開発は、いきなり独立した新規プロダクトを作ったというより、KurageとUMediaとVoice-Proの技術を再整理して、一つの機能としてまとめたものです。

UMediaの強みは、URLを起点に素材を取得できることです。  
Voice-Proの強みは、動画を翻訳字幕・翻訳音声へ変換する処理の部品を持っていることです。  
Kurageの強みは、生成した動画をWeb上で見せる公開導線をすでに持っていることです。

この3つをつなぐことで、Kurage Voice-Proは次のような立ち位置になりました。

```text
URLを入れる
  -> 動画を取得する
  -> 音声を文字起こしする
  -> 日本語へ翻訳する
  -> 日本語音声を作る
  -> 字幕付き吹き替え動画にする
  -> Kurageで公開する
```

これは、AI動画翻訳の実験環境であると同時に、AI OSSを実運用に落とし込むための小さな統合事例でもあります。

---

## 今後の改善

今後の改善ポイントは明確です。

- 元動画の声に寄せたTTS
- 翻訳文の品質向上
- 字幕の行分割と表示テンポのさらなる調整
- 長尺動画の分割処理
- 複数言語対応
- YouTube ShortsやSNS投稿との連携

特に、声質変換と字幕同期は動画翻訳の体験を大きく左右します。

ただし、最初から全部を作り込むより、実際に動画を生成し、公開し、失敗した字幕や音声タイミングを見ながら改善する方が速い。

Kurage Voice-Proは、そのための実験台として作っています。

AI OSSは、単体で見ると便利な部品です。  
しかし本当に価値が出るのは、既存の業務フローや公開システムに接続したときです。

Kurage Voice-Proは、UMedia、OSS Voice-Pro、Kurageをつないで、動画翻訳を「試せる」だけでなく「公開できる」形にした取り組みです。

