---
title: "kvtuberでYouTube Live配信まで到達した：PNGアバター、配信用viewer、RTMP送信の技術メモ"
emoji: "🪼"
type: "tech"
topics: [youtube, ffmpeg, vite, aituber, oss]
published: true
---

kvtuberで、PNGアバターの「VTuberくらげ」をYouTube Liveへ配信するところまで実装しました。

最終的な構成は、かなり素朴です。

```text
番組データ
  ↓
配信用viewer（/viewer?broadcast=1）
  ↓
Chrome + Xvfb
  ↓
ffmpeg
  ↓
YouTube Live RTMP
```

ただ、実際に動かしてみると、単に `ffmpeg` で画面を流せば終わり、ではありませんでした。黒画面、ffmpegビルド差、Chromeプロファイル、LLM生成待ち、台本と指示文の混同など、ライブ配信らしい落とし穴が一通り出ました。

この記事では、kvtuberでYouTube Live配信ができるようになるまでの技術構成と、そこに至った発想を整理します。

## kvtuberの発想：オンデマンドではなく「配信用viewer」を1つ固定する

最初に整理したのは、kvtuberの配信モデルです。

通常のWebアプリなら、視聴者ごとにブラウザを開いて、それぞれがAIキャラクターと対話する形になります。しかし、毎日決まった時間に同じ番組を流したい場合、それは「視聴者ごとのオンデマンド体験」ではなく、1つの番組を多人数へ届ける配信です。

そこで、設計をこう分けました。

- `admin`: 番組登録、配信開始、停止、スケジュール、コメント割り込み
- `viewer`: 通常視聴用
- `viewer?broadcast=1`: OBS/RTMP/YouTubeへ送る専用の配信用画面

YouTube Liveへ直接流すのは、視聴者のブラウザではありません。サーバー側で1つだけ起動した配信用viewerです。

```text
http://127.0.0.1:18308/viewer?broadcast=1
```

この画面は、画面サイズ、字幕位置、アバター位置、音量を固定します。配信で重要なのは、自由度より再現性です。

## AITuber OnAirをベースに、PNGアバター配信へ寄せる

kvtuberは、AITuber OnAir系の構成をベースにしています。ただし、今回の目的はLive2Dや3Dモデルを本格的に動かすことではありません。

まず欲しかったのは、次のMVPです。

- クラゲのPNGアバターを表示する
- TTS音声に合わせて口パクする
- 字幕を出す
- adminから番組を開始・停止できる
- YouTube Liveへ送れる

PNGアバターは、口閉じ・口開きの差分を用意し、音声のRMSに応じて口パク表示を変えます。Live2Dほど滑らかではありませんが、「VTuberくらげ」として番組を進行するには十分でした。

ここで大事なのは、VTuber機能を「対話アプリ」ではなく「配信パイプライン」の部品として扱ったことです。

## YouTube Live送信の基本構成

YouTube Liveへの送信はRTMPです。実装したスクリプトは `scripts/youtube-live-rtmp.mjs` で、admin画面から開始・停止できるようにしました。

起動するものは3つです。

```text
Xvfb     : 仮想ディスプレイ
Chrome   : 配信用viewerを表示
ffmpeg   : 仮想画面とPulseAudioをRTMPへ送信
```

ffmpegのイメージは次のような形です。

```bash
/usr/bin/ffmpeg \
  -f x11grab -video_size 1280x720 -framerate 30 -i :98.0 \
  -f pulse -i kurage_live.monitor \
  -c:v libx264 -preset veryfast -tune zerolatency \
  -b:v 2500k -maxrate 2500k -bufsize 5000k \
  -pix_fmt yuv420p -g 60 \
  -c:a aac -b:a 128k -ar 44100 \
  -f flv rtmp://a.rtmp.youtube.com/live2/STREAM_KEY
```

ストリームキーは設定ファイルに保存しますが、画面やAPIレスポンスには表示しません。Gitにも当然出しません。

## ハマりどころ1：`ffmpeg` が2つあり、片方は x11grab 非対応だった

最初に詰まったのはここです。

`which ffmpeg` が指す `/usr/local/bin/ffmpeg` では、次のエラーになりました。

```text
Unknown input format: 'x11grab'
```

一方、kargovで使っていた `/usr/bin/ffmpeg` は `x11grab` に対応していました。

```text
D  x11grab  X11 screen capture, using XCB
```

つまり、同じサーバーに複数のffmpegがあり、機能が違っていたわけです。ライブ配信スクリプトでは、明示的に `/usr/bin/ffmpeg` を使うように変更しました。

これは地味ですが、実運用ではかなり重要です。動画生成や配信系では、`ffmpeg` のパスを環境任せにしない方が安全です。

## ハマりどころ2：RTMP送信は動いているのに、YouTube側は黒画面

次に起きたのは、ffmpegは動いているのに、YouTubeへ流れている映像が黒画面になる問題です。

原因はChromeでした。

最初は、仮想ディスプレイ上でChromeを起動しているつもりでした。しかし、専用の `--user-data-dir` を指定していなかったため、既存ChromeプロセスにURLが吸われ、`:98` の仮想画面には何も描画されていませんでした。

結果として、ffmpegは正常に黒画面をYouTubeへ送り続けていました。

修正は、配信用Chromeに専用プロファイルを与えることです。

```bash
google-chrome \
  --no-sandbox \
  --no-first-run \
  --no-default-browser-check \
  --autoplay-policy=no-user-gesture-required \
  --user-data-dir=/tmp/kurage-youtube-chrome-profile-98 \
  --window-position=0,0 \
  --window-size=1280,720 \
  --app=http://127.0.0.1:18308/viewer?broadcast=1
```

さらに、配信開始後に `x11grab` で1フレームだけPNG保存し、黒画面ではないかを確認しました。

```bash
/usr/bin/ffmpeg -y \
  -f x11grab -video_size 1280x720 -i :98.0 \
  -frames:v 1 /tmp/kurage-youtube-frame.png
```

ライブ配信のデバッグでは、「YouTube側で見えない」より先に「自分が何を送っているか」を確認する方が早いです。

## ハマりどころ3：配信用viewerにスクロールバーが出る

配信用viewerは1280x720想定でしたが、CSSに `min-width: 1280px` と `min-height: 720px` が入っていたため、Chromeの実viewportが少しでも小さいとスクロールバーが出ました。

配信画面ではスクロールバーは事故です。

そこで `broadcast-viewer-app` は100vw/100vh固定にし、html/body/rootにもoverflow hiddenをかけました。

```css
html:has(.broadcast-viewer-app),
body:has(.broadcast-viewer-app),
#root:has(.broadcast-viewer-app) {
  height: 100%;
  max-height: 100%;
  max-width: 100%;
  overflow: hidden;
  width: 100%;
}

.broadcast-viewer-app {
  width: 100vw;
  height: 100vh;
  max-width: 100vw;
  max-height: 100vh;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}
```

これで、字幕とアバターが必ず配信画面内に収まるようになりました。

## kargovの発想をどう活かしたか

直前に作っていたkargovでは、browser-useがブラウザを自律操作し、その画面をCDP `Page.startScreencast` で録画していました。

kargovのポイントは、`x11grab` に依存せず、ブラウザの中身だけを録画できることです。

```text
browser-use + Chrome DevTools Protocol + screencast
```

今回のkvtuberでは、最終的にはXvfb + ffmpegでYouTube Liveへ送る形にしました。理由は、ライブ配信では連続した映像と音声をRTMPへ流し続ける必要があり、ffmpegの方が素直だからです。

ただし、発想としてはkargovと同じです。

- ブラウザを1つ起動する
- AI/番組システムがそのブラウザを動かす
- そのブラウザを録画または配信のソースにする

録画ならCDP screencast。ライブならXvfb + ffmpeg。ここを使い分ければよい、という整理になりました。

将来的には、browser-useが操作しているChromeをそのまま配信対象にし、「AIがブラウザ操作する様子をライブで見せる」こともできます。

## ハマりどころ4：LLM生成待ちで番組が止まる

YouTubeへ画面が出るようになった後、次に止まったのは番組進行でした。

viewer状態を見ると、ずっとこうです。

```json
{
  "phase": "generating",
  "label": "生成中",
  "isProcessing": true,
  "isSpeaking": false
}
```

原因はOllama側でした。`/v1/chat/completions` に投げても20秒以上返ってこない状態になり、番組が最初の話題で止まりました。

ライブ配信では、ここにLLMを挟むと不安定です。そこで、番組配信だけはLLMを迂回し、登録済み台本をそのままKurage TTSで読む方式に変更しました。

```text
番組の1行セリフ
  ↓
/kurage-tts/v1/audio/speech
  ↓
AudioContextで再生
  ↓
RMS解析で口パク
```

コメント割り込みなど、即興応答が必要な場面ではLLMを使えます。しかし、毎日決まった番組を配信する部分は、LLMではなく確定台本の方が強いです。

## ハマりどころ5：「台本」ではなく「指示文」を読んでしまった

LLMを迂回したことで、別の問題が露出しました。

もともと番組データには、次のような行が入っていました。

```text
オープニング。VTuberくらげとして自己紹介し、今日の入門編のゴールを伝える
バイブコーディングとは何か。AIに作業を頼みながら人間が方向を決める開発スタイルとして説明する
```

これはLLMに渡す「指示文」としては自然です。しかし、TTSで直接読むと不自然です。

実際に配信すると、くらげが「今日の入門編のゴールを伝える」と読んでしまいました。

そこで番組データを、実際に読むセリフへ修正しました。

```text
こんにちは、VTuberくらげです。今日は、AIと一緒に開発するバイブコーディングの入門編をお届けします。ゴールは、初心者でも最初の一歩を踏み出せるようになることです。
バイブコーディングは、AIに作業を頼みながら、人間が目的と方向を決めて進める開発スタイルです。全部丸投げではなく、一緒に作る感覚が大事です。
```

admin画面のラベルも `台本 1行1トピック` から `台本 1行1セリフ` に変えました。

これは地味ですが、設計上かなり大きいです。

- LLMへ渡すなら「指示文」
- TTSで読むなら「セリフ」
- ライブ配信で安定させるなら「セリフ」

この区別をUIにも出しておかないと、運用で必ず混乱します。

## admin画面でできること

今回のadmin画面は、最初は機能が増えすぎて複雑になりました。最終的には、ライブ運用に必要なものへ絞りました。

- 番組を作る
- 番組を選ぶ
- 配信開始/停止
- 番組ごとの配信予定を登録する
- YouTube RTMP送信を開始/停止する
- 視聴者コメントを割り込みで送る

指定時間配信では、番組ごとに時刻を保存し、配信予定一覧に追加します。

```json
{
  "enabled": true,
  "items": [
    { "id": "vibe-coding-intro-10:00", "programId": "vibe-coding-intro", "time": "10:00" }
  ],
  "keepYoutubeArchive": false
}
```

YouTubeのアーカイブを残すかどうかは、YouTube Studio側の設定で管理します。kvtuber側は、決まった時刻に番組を開始し、RTMPへ送るところまでを担当します。

## 今回得た設計の教訓

今回の実験で、ライブ配信AIキャラクターの設計が少し整理できました。

### 1. 視聴者ごとのAI対話と、番組配信は分ける

視聴者ごとに動くAIチャットと、全員に同じものを届けるライブ番組は別物です。

ライブ番組は、配信用viewerを1つだけ固定し、それをOBS/RTMP/YouTubeへ流す方が安定します。

### 2. ライブ本編はLLMに依存しすぎない

LLMは即興応答には便利です。しかし、番組進行そのものをLLM生成にすると、遅延や停止がそのまま放送事故になります。

本編はセリフ台本で進め、コメント返答だけLLMを使う構成が現実的です。

### 3. ブラウザ配信では、Chromeプロファイルが重要

既存ChromeにURLが吸われると、仮想画面は黒いままです。配信用Chromeには必ず専用 `--user-data-dir` を指定するべきです。

### 4. 送信成功と、見える映像は別

ffmpegが生きていても、黒画面を送っているだけかもしれません。配信中の仮想画面を1フレームキャプチャして確認する仕組みは必須です。

### 5. 台本は「制作指示」ではなく「発話文」にする

AI動画生成では、指示文と台本が混ざりがちです。ライブ配信では、TTSに渡すものは必ず発話文にする。これはUIの文言にも反映すべきです。

## まとめ

kvtuberでは、PNGアバター、Kurage TTS、配信用viewer、Xvfb、ffmpeg、YouTube Live RTMPをつなぎ、YouTube経由のライブ配信まで到達しました。

技術的には派手な3D VTuberではありません。しかし、重要なのはそこではありません。

**AIが作った番組を、決まった時間に、キャラクターが読み上げ、YouTube Liveへ流す。**

この一連の流れが、OSSとローカル実装の組み合わせで動いたことに意味があります。

今後は、次の方向に伸ばせます。

- browser-useが操作するブラウザをそのままライブ配信する
- YouTubeコメントを取得し、admin承認で割り込み返答する
- 番組表を整え、毎日決まった時間に自動配信する
- 収録動画、ライブ配信、ショート動画生成を同じKurage系パイプラインに統合する

VTuberというより、企業や個人が自分の情報発信を自動化するための「AI番組配信基盤」に近づいてきました。

kvtuberは、その入口としてかなり手応えのある実験になりました。
