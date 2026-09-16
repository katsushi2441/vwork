---
title: "Sunoの代わりを自前GPUで——ACE-Step 1.5 Turbo XL と HeartMuLa oss-3B を同じ日本語歌詞で計測した（速度・VRAM・歌詞の一致率）"
emoji: "🎵"
type: "tech"
topics: ["acestep", "heartmula", "音楽生成", "oss", "rtx3090"]
published: true
title_hatena: "ローカル曲生成 ACE-Step 1.5 と HeartMuLa 3B を RTX 3090 で実測——60秒曲が54秒と81秒、VRAM 17.6GB と 14.1GB"
title_blogger: "日本語の歌詞で歌う OSS 音楽モデル2つ（ACE-Step 1.5 XL / HeartMuLa 3B）を1台の GPU で並べて測った"
---

Suno で作っていた BGM やデモ曲を、手元の GPU で回せないか。2026年9月時点で「歌詞＋曲調の指示から、ボーカル入りのフル曲」を出せて商用利用もできるオープンなモデルは、実質 **ACE-Step 1.5**（MIT）と **HeartMuLa oss-3B**（Apache 2.0、重みも）の2つに絞れます。YuE2 は重みが CC BY-NC（非商用）、MiniMax Music 3 は商用可ですが 57GB で UI にモデル名の表示義務があります。

この記事は、その2つを **同じ日本語の歌詞・同じ曲調の指示・同じ GPU（RTX 3090 24GB）** で回して、速度・VRAM・RAM・歌詞がどれだけそのまま歌われたかを数えた記録です。数字はすべてスクリプトが測ったもので、聴いた印象は最後に短く書くだけにします。

## 結論を先に

| | ACE-Step 1.5 Turbo XL | HeartMuLa oss-3B |
|---|---|---|
| 60秒曲の所要（投入→mp3 到着） | **54秒** | 81秒（生成 80秒） |
| 180秒指定の所要 | 75秒（180.0秒ぶん生成） | 生成 88秒（**71.2秒で自ら終了**） |
| VRAM ピーク | 17.6GB（尺によらず一定） | 14.1GB（60秒）→ **22.7GB**（180秒指定） |
| RAM 増分 | +6.7〜8.0GB | +2.1〜2.7GB |
| 歌詞が原文どおり聞き取れた行（8行中） | 3行 | **6行** |
| ライセンス | MIT | Apache 2.0（重みも） |
| 重み | 30GB（本体10GB＋XL 20GB） | 21GB |

速さは ACE-Step、歌詞の忠実さと VRAM/RAM の軽さは HeartMuLa。ただし HeartMuLa は「指定した長さ」ではなく「歌詞が終わったら曲が終わる」ので、3分の曲が欲しければ3分ぶんの歌詞が要ります。

## 1. 何を比べたか

- 歌詞: 日本語 8行（[Verse] 4行＋[Chorus] 4行）。両方に同じ行を渡し、見出しだけ各モデルの流儀（ACE-Step は `[verse]/[chorus]`、HeartMuLa は `[Intro]/[Verse]/[Chorus]/[Outro]`）に合わせました。
- 曲調: 「Japanese lo-fi pop, soft female vocal, warm Rhodes piano, gentle drums, vinyl texture, 80 BPM」。HeartMuLa はタグ形式なので `lo-fi,pop,female vocal,rhodes piano,soft drums,calm,night,japanese`。
- 尺: 60秒と180秒の2本ずつ、計4本。
- 環境: RTX 3090 24GB、ドライバ 555（CUDA 12.5）、torch 2.10.0+cu128。この GPU は動画生成（MiniMax H3）と Ollama も共有しているので、ジョブは RQ のキューで直列化し、他の処理と重ならないようにしました（後述）。
- 計測: 所要時間はジョブの投入から mp3 が手元に届くまで。VRAM・GPU 使用率・RAM は GPU 側で 2 秒ごとに `nvidia-smi` と `free` を記録し、各ジョブの時間帯のピークを取りました。歌詞は whisper.cpp（large-v3-turbo、日本語）で聞き取り、原文との文字誤り率（CER）と「行がそのまま出た数」を数えました。

## 2. 中身の違い

**ACE-Step 1.5** は拡散系です。4B の DiT（XL）が Flow Matching で音の潜在表現を作り、VAE が 48kHz に戻します。その前段に 5Hz の言語モデル（1.7B、Qwen3 系）があって、歌詞と説明から BPM・キー・構成と「音のコード」を先に考える（`thinking`）。Turbo は 8 ステップに蒸留した版で、CFG は使わず `shift=3.0` を指定します。対応言語は 50 以上、10〜600 秒。

**HeartMuLa oss-3B** は言語モデル系です。3B のモデルが歌詞とタグから音のトークンを自己回帰で吐き、HeartCodec（fp32 推奨）が波形に戻します。Suno と同じ系統の作りで、作者は「内部の 7B は Suno 相当」と書いていますが、公開されているのは 3B です。「ほぼ全言語」対応、既定の上限は 4 分。

## 3. 速さ

| 指定 | ACE-Step | HeartMuLa |
|---|---|---|
| 60秒 | 54秒（API 起動＋XL のロード込み） | 81秒（生成 80秒、ロード込み） |
| 180秒 | 75秒 | 生成 88秒（実尺 71.2秒） |
| 初回（コールド） | 50秒（30秒曲） | 75秒（60秒曲） |

ACE-Step は拡散なので、尺が3倍になっても時間は 1.4 倍。HeartMuLa は自己回帰なので歌った長さに比例します。HeartMuLa の 180 秒指定は、8 行の歌詞を歌い終えた 71 秒で自分から止まりました（`max_audio_length_ms` は上限であって目標ではない、と README にもあります）。ACE-Step は逆に、8 行しかなくても 180 秒を埋めにいきます。その分、間奏やハミングが長くなります。

なお HeartMuLa 180 秒の「投入→到着」は 168 秒でしたが、うち 79 秒はキューの優先順で先に走った別ジョブ（GPU を使わない市場データ処理）の待ちで、生成自体は 88 秒です。

## 4. 負荷

| | ACE-Step 60秒 | ACE-Step 180秒 | HeartMuLa 60秒 | HeartMuLa 180秒指定 |
|---|---|---|---|---|
| VRAM ピーク | 17.6GB | 17.6GB | 14.1GB | 22.7GB |
| GPU 使用率（平均） | 19% | 34% | 59% | 34%（LM 72%→コーデック 99%） |
| RAM 増分 | +6.7GB | +8.0GB | +2.1GB | +2.7GB |

ACE-Step は尺に関係なく 17.6GB で一定。HeartMuLa は KV キャッシュが伸びるので、長い曲ほど VRAM を食い、180 秒指定では 22.7GB まで行きました。24GB の GPU で既定上限の 4 分を歌わせるのは危ないので、長尺は分割するか `--lazy_load` に加えてコーデックを CPU に逃がす設定が要ります。

RAM は ACE-Step の方が重く（XL の重み 20GB をステージングする）、GPU 使用率は HeartMuLa の方が高い（GPU をきちんと使い切っている）という読み方ができます。

## 5. 歌詞はどれだけそのまま歌われたか

| | CER | 原文どおりの行 | 備考 |
|---|---|---|---|
| ACE-Step 60秒 | 0.295 | 3/8 | 「ノートを開いて」が「喉を開いて」など、語が置き換わる |
| HeartMuLa 60秒 | 0.398 | **6/8** | サビを2回歌ったぶん CER は膨らむが、行は原文どおり |
| ACE-Step 180秒 | 2.93 | 0/8 | 歌の無い区間が長く、whisper が「作詞・作曲 初音ミク」と幻聴 |
| HeartMuLa 180秒指定 | 0.227 | 5/8 | 71秒で終了。歌った部分はほぼ原文 |

CER は「繰り返し」や「幻聴」で簡単に崩れるので、「行がそのまま出たか」の方が実感に近い指標です。それで見ると HeartMuLa は 8 行中 6 行を一字違わず歌い、ACE-Step は 3 行でした。ACE-Step でも、先に別の設定（LM なし・`shift=1.0`）で回したときは 1 行しか出なかったので、`thinking=true`・`shift=3.0` は必須です。

## 6. 1台の GPU で他の生成と同居させる

この GPU は動画（MiniMax H3、ピーク 23.4GB）と LLM（Ollama の gemma）も使うので、曲生成を素直に常駐させると衝突します。実際に一度、曲の API を常駐させたまま別のジョブが gemma（6.3GB）を読み込み、ACE-Step の常駐分 16.6GB と合わせて「Insufficient free VRAM」で落ちました。

そこで次の形にしました。

1. GPU 1台につき RQ のワーカーを 1 プロセスにして、Ollama・H3・ACE-Step・HeartMuLa のキューをその 1 プロセスが順に処理する（同時に 2 つ走らない）。
2. ジョブの冒頭で Ollama のモデルを `keep_alive: 0` で降ろす。
3. ACE-Step の API サーバーはモデルを降ろす口が無く、待機中も 16.6GB を握るので、**ジョブの間だけ systemd の user unit を起動し、`finally` で止める**。
4. HeartMuLa は CLI が 1 回ごとにロードして終了するので、そのまま ssh で実行するだけでよい（終了後 VRAM 6.2GB→0.01GB を確認）。

## 7. 入れるときに踏んだ穴

- **torch と CUDA**: 両方とも torch 2.10.0+cu128 が、ドライバ 555（CUDA 12.5）のままで動きました。CUDA 12 系のマイナー互換の範囲です。
- **HeartMuLa の保存が落ちる**: torchaudio 2.10 は保存に torchcodec を要求します。PyPI の torchcodec は CUDA 13 用（`libnvrtc.so.13` が無い）、cu128 版は FFmpeg 4.4 と噛み合わず読み込めませんでした。生成は成功しているのに保存で例外、という形で出ます。本体は触らず、`torchaudio.save` を soundfile（wav）→ ffmpeg（mp3）に差し替えた 40 行のランナーを実行時に送り込んで回避しました。
- **Python**: ACE-Step は 3.11〜3.12、HeartMuLa は 3.10 推奨。venv を分けます。
- **タグの書式**: HeartMuLa のタグは「半角カンマ区切り・空白なし」。

## 8. どちらを使うか

- **BGM・インスト・「30秒ぴったり」が欲しい**（動画の尺に合わせる）: ACE-Step。指定した長さを埋めてくれて、速く、VRAM が一定。
- **歌詞を聴かせたい**（歌もの、歌詞ありの紹介曲）: HeartMuLa。歌詞がそのまま出る率が高く、RAM も軽い。長さは歌詞で決まると割り切る。
- 24GB で 3 分以上の歌ものを HeartMuLa に歌わせるなら、VRAM の伸びに注意。

聴き比べ（同じ歌詞・同じ指示）:

- ACE-Step 60秒: https://kurage.exbridge.jp/pv/bench-acestep-60s.mp3
- HeartMuLa 60秒: https://kurage.exbridge.jp/pv/bench-heartmula-60s.mp3
- ACE-Step 180秒: https://kurage.exbridge.jp/pv/bench-acestep-180s.mp3
- HeartMuLa 180秒指定（71秒で終了）: https://kurage.exbridge.jp/pv/bench-heartmula-180s.mp3

耳の印象を一つだけ書くと、どちらも Suno v4.5 前後の「それらしさ」はありますが、歌詞の聞き取りやすさは HeartMuLa、伴奏のまとまりは ACE-Step、という差があります。用途で使い分けるのが現実的です。

## 出典

- ACE-Step 1.5: https://github.com/ace-step/ACE-Step-1.5 （技術報告 https://arxiv.org/abs/2602.00744 ）
- HeartMuLa: https://github.com/HeartMuLa/heartlib （論文 https://arxiv.org/abs/2601.10547 ）
- 重み: ACE-Step/Ace-Step1.5・ACE-Step/acestep-v15-xl-turbo（MIT）、HeartMuLa/HeartMuLa-oss-3B-happy-new-year・HeartMuLa/HeartCodec-oss-20260123（Apache 2.0）

この構成（GPU 共有・キューでの直列化・ジョブ単位の起動停止）は、名古屋の中小企業向け AI-IT 顧問契約で組んでいる型と同じものです: https://exbridge.jp/outsourcing/?ref=vwork-music
