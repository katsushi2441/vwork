---
title: "文字起こしAI「Haas-ja-v1.0」とは——日本語の公開モデルで最高精度・Whisperの15倍速。使い方と弱点、AI議事録の自社サーバー版に組み込む計画"
emoji: "🎧"
type: "tech"
topics: ["haas", "文字起こし", "音声認識", "議事録", "oss"]
description: "2026年10月に公開された日本語の文字起こしAI「Haas-ja-v1.0」（Apache 2.0）を解説します。公開モデルで最も低い文字誤り率6.12%、Whisper large-v3の15〜17倍の速さという公表値、使い方、NVIDIAのGPUが必須などの弱点、当社のAI議事録システムに組み込む Kurage AI MOM Pro（Haas版）の計画までまとめました。"
seo_title: "文字起こしAI Haas-ja-v1.0とは｜精度・使い方と弱点"
head_keyword: "Haas-ja-v1.0"
published: true
title_hatena: "日本語の文字起こしAI「Haas-ja-v1.0」——Whisperより速くて正確な公開モデルを、自社サーバーの議事録に使えるか"
title_blogger: "会議の録音を社外に出さずに、速く正確に文字起こしする。新しい公開モデル Haas-ja-v1.0 を調べた記録"
---

日本語に特化した文字起こしAI **Haas-ja-v1.0** が、2026年10月に公開されました。GIGAZINE が「オープンモデルの中で最高性能」と紹介し、X でも6万回近く見られています。

当社は、会議の録音を社外に出さずに文字起こしして議事録の下書きを作る買い切り製品 [Kurage AI MOM](https://kappstore.exbridge.jp/app.php?id=cd1eda3248c87920#ref=vwork-haas) を出しています。文字起こしには、これまで [whisper.cpp](2026-09-04-whisper-cpp-japanese-transcription.html) を使ってきました。Haas-ja-v1.0 は、その置き換えの有力な候補です。この記事では、公開された情報から Haas-ja-v1.0 の中身・使い方・弱点を整理し、当社の製品にどう組み込むかを書きます。

結論を先に書きます。

- **ライセンスは Apache 2.0**。商用で使えて、製品に組み込んで売ることもできます
- **公開されている日本語の文字起こしモデルの中で、いちばん誤りが少ない**（文字誤り率6.12%・公表値）。有料の文字起こしAPI「GPT-Transcribe」（6.07%）とほぼ同じです
- **速さは Whisper large-v3 の15〜17倍**（公表値）
- 社名・人名を登録して、その書き方で出させる機能があります
- 弱点は、**NVIDIA の GPU が無いと動かない**こと。CPU だけのサーバーや Mac では動きません
- 当社は、GPU のあるサーバー向けに **Kurage AI MOM Pro（Haas版）を税別220,000円で出す予定**です。GPU の無いサーバー向けには、これまでどおり whisper.cpp 版を続けます

ここに書く精度と速さの数字は、すべて開発元の公表値です。当社のサーバーではまだ測っていません。

## Haas-ja-v1.0 とは

[Haas-ja-v1.0](https://huggingface.co/third-intelligence/Haas-ja-v1.0) は、Third Intelligence が Hugging Face で公開した日本語の音声認識モデルです。公開は2026年10月8日です。名前は *Hear Anything At Speed*（何でも速く聞き取る）の頭文字で、ステレオ音響で使われる「ハース効果」の研究者 Helmut Haas にもかけています。

中身は、NVIDIA の音声認識モデル **Parakeet-TDT** の作りをもとにしています。

- **音を読む部分（エンコーダー）**：FastConformer という型で、24層・6.1億パラメータあります
- **文字を出す部分（デコーダー）**：TDT という方式です。文字を1つ出すたびに「その音がどれだけ続くか」も予測するので、音のコマを1つずつ見ずに何コマか先へ飛ばせます。これが速さの理由です
- **予測ネットワーク**：Parakeet では LSTM だったところを、Kimi Delta Attention という仕組みに替えています。速さはほぼそのままで、精度が上がったと説明されています

全体で6.2億パラメータです。Whisper large-v3（約15億）の半分以下の大きさです。

学習には、約4万6,000時間の音声を使っています。ReazonSpeech・Common Voice・YODAS という公開の日本語音声と、開発元が持っている音声です。評価に使う音声は、学習に一切入れていないと書かれています。

## 精度：公開モデルで最も誤りが少ない

開発元は、性格の違う5種類の公開音声（合計23.4時間）を集めて、各モデルを比べています。

- 常用漢字の読みを網羅するように作った文の朗読
- 感情をこめた話し声
- TEDx の日本語の講演
- 翻訳した文の朗読
- ビジネスの場面の会話

日本語は、同じ言葉を漢字でもかなでも、数字でも漢数字でも書けます。そこで、表記をそろえてから「文字誤り率」を出しています。いちばん厳しい数え方（漢字とかなの違いも誤りに数える）で、Haas-ja-v1.0 は **6.12%** でした。評価した公開モデルの中で最も低い値です。

有料の API と比べると、次のようになっています。

- **GPT-Transcribe（6.07%）** とほぼ同じ
- MAI-Transcribe 2、Scribe v2、Gemini 3.1 Pro はこれより正確

つまり「いちばん正確な有料APIには届かないが、公開モデルの中では最も良く、有料APIの一部と並ぶ」という位置です。

## 速さ：Whisper large-v3 の15〜17倍

速さは「1秒間に何秒分の音声を文字にできるか」で比べています。Haas-ja-v1.0 は **約3,236倍** で、次に正確な公開モデル（NVIDIA の Nemotron 3.5 Transcribe と Whisper large-v3）の15〜17倍の速さです。

ただし、この数字は **NVIDIA H200 という最上位のデータセンター向け GPU で、512本の音声をまとめて処理したとき** のものです。中小企業の社内サーバーで会議の録音を1本ずつ処理するときは、この数字にはなりません。あくまで「同じ条件で比べると、Whisper よりずっと速い」という読み方をしてください。

開発元は、1時間の音声を約0.003〜0.004ドルで文字にできるとも試算しています。こちらも、H200 をずっと動かし続けたときの計算です。

参考までに、当社が9月に whisper.cpp を GPU 無しで測ったときは、47.4秒の音声に27.1秒かかりました（音声の長さの0.57倍）。この比率なら、1時間の会議で約34分です。

## 使い方

公式の手順は、**Linux・NVIDIA の GPU・Python 3.11 以上・NeMo 2.7** が前提です。

1. 推論用のパッケージを入れる

```bash
pip install "haas-asr @ git+https://github.com/third-intelligence/Haas-ASR.git"
```

2. 文字起こしする（30秒以内の短い音声）

```python
import haas_asr

model = haas_asr.load_model("third-intelligence/Haas-ja-v1.0")
audio = haas_asr.load_audio("example.wav")   # WAV・FLAC・MP3・OGG。16kHz・モノラルに自動で直す
output = model.transcribe([audio])
print(output[0].text)
```

3. 会議の録音のような長い音声は、`transcribe_longform` を使う

```python
audio = haas_asr.load_audio("meeting.flac")
text = haas_asr.transcribe_longform(model, audio, batch_size=64)
```

音量から静かなところを見つけて区切り、区切った断片をまとめて処理します。

### 社名・人名を登録する

議事録でいちばん困るのは、社名・人名・社内の言葉の誤変換です。Haas-ja-v1.0 では、書き方と読みを登録できます。

```python
vocabulary = haas_asr.Vocabulary(
    {"エクスブリッジ": ["えくすぶりっじ"], "kaimom": ["かいもむ"]}
)
text = haas_asr.transcribe_longform(model, audio, vocabulary=vocabulary)
```

登録した読みを、認識の途中で出やすくします。そして、見つかったところを登録した書き方に置き換えます。登録した言葉が出てこないところまで書き換えてしまわないように、登録なしでも一度認識し、登録した言葉がまるごと入るところだけを採用する作りになっています。処理時間は約1.3倍になります。

### 話している人を分ける

Haas-ja-v1.0 だけでは、「だれが話したか」は分かりません。NVIDIA の話者分離モデル [Nemotron-3-Diarization](https://huggingface.co/nvidia/Nemotron-3-Diarization) と組み合わせると、話者のラベル付きで出せます。組み合わせ方の見本は、開発元のリポジトリにあります。

## 弱点と、使う前に確かめること

- **NVIDIA の GPU が必須です。** デコーダーの計算に、CUDA と Triton が要る部品（flash-linear-attention）を使っているからです。CPU だけのサーバーや Mac では動きません。有志が ONNX・GGUF・Core ML などの形式に変えたものも Hugging Face に出ていますが、当社ではまだ動かしていません
- **リアルタイムの字幕向けではありません。** 録音済みの音声をまとめて文字にする前提で学習しています。話しながら字幕を出すこともできますが、遅れを小さくするには調整が要ると書かれています
- **口ぐせ（「えー」「あのー」）は消えやすく、出し方は選べません。** 漢字・かな・数字の書き方も、学習した音声の書き方に寄ります。登録で直せるのは、1語ずつの書き方だけです
- **話者分離は、日本語で使えるか確かめが要ります。** 当社が9月に Nemotron-3-Diarization を調べたとき、モデルの説明に日本語の記載はありませんでした。日本語の会議は「はい」「ええ」の相づちが多く、短い発話が重なります。これは話者分離が最も苦手な形です。実際の録音で試してから決める必要があります

## whisper.cpp との違い

**動く場所**
- whisper.cpp：CPU だけで動く。GPU の無い普通のサーバーに置ける
- Haas-ja-v1.0：NVIDIA の GPU が必須

**速さ**
- whisper.cpp：CPU で、音声の長さの0.57倍（当社の実測・1時間の会議で約34分）
- Haas-ja-v1.0：Whisper large-v3 の15〜17倍（公表値・H200 で測ったもの）

**精度**
- Whisper large-v3：公開モデルの中では Haas-ja-v1.0 に次ぐ位置
- Haas-ja-v1.0：公開モデルの中で最も誤りが少ない（6.12%）

**言葉の登録**
- whisper.cpp：最初に言葉を渡して、出やすくする程度
- Haas-ja-v1.0：書き方と読みを登録して、置き換えまでする

**言語**
- Whisper：約100言語
- Haas-ja-v1.0：日本語だけ

## 当社の製品にどう組み込むか：Kurage AI MOM Pro（Haas版）

Kurage AI MOM は、次の流れの議事録システムです。

1. 会議の録音を上げる
2. 同じサーバーの中で文字起こしする
3. AI が議事録の下書き（概要・決定事項・ToDo・課題・次回）を作る
4. 人が録音・全文と見比べて直し、承認したものだけが議事録になる

いちばんの売りは、**録音を外のクラウドサービスに送らないこと** です。対面の会議や IC レコーダーの録音を、社内の決まりで外に出せない会社に向けています。いまは whisper.cpp を使っていて、GPU の無いサーバーでも動きます（税込55,000円）。

ここに Haas-ja-v1.0 を入れた版を **Kurage AI MOM Pro（Haas版）** として、**税別220,000円で出す予定** です。GPU のあるサーバーをお持ちの会社や、これから用意する会社に向けた版です。

- **速さ**：長い会議の録音でも、文字起こしの待ち時間を短くできます
- **精度**：公開モデルの中で最も誤りが少ないモデルを使います
- **社名・人名の登録**：お客さまの社名、取引先、製品名、社内の言葉を登録して、誤変換を減らします
- **話者のラベル**：話者分離のモデルと組み合わせて、「だれが話したか」を付けることを目指します。日本語で使えるかは、お客さまの録音で試してから決めます
- **録音を外に出さない**ことは、いまの版と同じです

GPU の無いサーバーで使う会社には、これまでどおり whisper.cpp 版をおすすめします。どちらの版が合うかは、会議の長さ・本数・お持ちのサーバーで変わります。

Pro 版について知りたい方、自社の録音で試してから決めたい方は、[お問い合わせ](https://exbridge.jp/contact.php?subject=%E3%83%96%E3%83%AD%E3%82%B0%E3%80%8CHaas-ja-v1.0%E3%80%8D%E3%82%92%E8%AA%AD%E3%81%BF%E3%81%BE%E3%81%97%E3%81%9F%E3%80%82Kurage%20AI%20MOM%20Pro%EF%BC%88Haas%E7%89%88%EF%BC%89%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6#ref=vwork-haas)からご連絡ください。いまの版は [Kurage App Store](https://kappstore.exbridge.jp/app.php?id=cd1eda3248c87920#ref=vwork-haas) にあります。

## 参考

- [Haas-ja-v1.0（Hugging Face のモデルカード）](https://huggingface.co/third-intelligence/Haas-ja-v1.0)
- [Haas-ASR（推論のコード・GitHub）](https://github.com/third-intelligence/Haas-ASR)
- [whisper.cppで日本語の文字起こしを自社サーバーで動かす（当社の実測）](2026-09-04-whisper-cpp-japanese-transcription.html)
