---
title: "Kurage Montageの技術設計：参照動画から日本語ショート動画を生成するAI OSSパイプライン"
emoji: "🎞️"
type: "tech"
topics: [生成ai, aiagent, video, oss, python]
published: true
---

Kurage Montage、略して `kmontage` は、X URLまたはYouTube URLを入力すると、参照動画の内容を解析し、日本語のショート解説動画としてKurageへ投稿するためのパイプラインです。

今回の実装で重要だったのは、「OpenMontageをそのまま移植すること」ではなく、OpenMontageが持っている参照動画ベースの制作思想を、既存のKurage / Kurage Voice Pro / Kurage Blogの実運用基盤に接続することでした。

現時点の公開リポジトリはこちらです。

- [katsushi2441/kmontage](https://github.com/katsushi2441/kmontage)
- [Kurage動画一覧](https://kurage.exbridge.jp/kuragev.php)
- [OpenMontage](https://github.com/calesthio/OpenMontage)

実際に、X上の長尺解説動画を入力し、動画本文を文字起こししたうえで、日本語ショート動画として生成するところまで動作確認しました。

- [生成されたKurage動画: AIで実現するユーチューブ自動収益化の仕組み](https://kurage.exbridge.jp/kuragev.php?id=636bfd4210c84f2a)

## kmontageで実現したいこと

`kmontage` の目的は、単なる動画要約ではありません。

参照動画を入力として受け取り、その内容、構成、フック、主張、視聴者への見せ方を解析し、日本語圏向けの短い解説動画に再構成することです。

処理の流れは次のようになります。

```text
X URL / YouTube URL
  ↓
参照動画の取得
  ↓
音声抽出
  ↓
文字起こし
  ↓
LLMによる要点・構成・台本生成
  ↓
Kurage /generate_from_news へ投入
  ↓
Kurage Blog動画として生成
  ↓
kuragev.php の一覧に表示
```

この流れにより、英語圏で話題になっている動画、X上で拡散されている解説動画、YouTubeの長尺動画などを、日本語の短尺コンテンツとして再編集できます。

## OpenMontageをそのまま使わなかった理由

OpenMontageは非常に興味深いOSSです。

特徴は、AIエージェントが動画制作全体をパイプラインとして扱う点にあります。READMEや設計ドキュメントを見ると、次のような考え方が中心になっています。

```text
idea -> script -> scene_plan -> assets -> edit -> compose -> publish
```

さらに、参照動画を入力として、次のような分析を行う思想があります。

- transcript
- pacing
- scenes
- keyframes
- style
- hook
- tone
- cost estimate
- production plan

これは `kmontage` にとってかなり参考になります。

ただし、OpenMontageの実装をそのまま使うには、いくつかの前提が違いました。

1つ目は、レンダリング基盤です。OpenMontageはRemotionやHyperFramesを含む複数のレンダリングランタイムを選択する設計です。一方、Kurage側にはすでにHyperFramesベースの動画生成、TTS、字幕、サムネイル、公開一覧が存在します。

2つ目は、既存資産です。Kurage Voice Proには、X動画取得、音声抽出、Faster-Whisperによる文字起こし、CUDA実行設定がすでにあります。ここを捨ててOpenMontage側の仕組みに寄せると、動いている部品をわざわざ壊すことになります。

3つ目は、プロダクトの焦点です。OpenMontageは汎用的なAI動画制作スタジオを目指していますが、`kmontage` はまず「参照動画から日本語ショート解説動画を生成する」ことに特化しています。

そのため、今回の判断は次の通りです。

```text
OpenMontageのコードを移植するのではなく、
OpenMontageの設計思想を参考にし、
実装はKurageシリーズの既存機能を再利用する。
```

## 今回実装で使ったKurage側の既存機能

`kmontage` の初期実装では、動画取得や文字起こしを独自に作ろうとして失敗しました。

特に、Faster-Whisperを直接起動したところ、`libcublas.so.12` が見えずに落ちました。

原因は、ライブラリが存在しないことではありませんでした。Kurage Voice Proのsystemd serviceでは、次のようにCUDA関連ライブラリのパスを明示していました。

```text
LD_LIBRARY_PATH=/home/kojima/work/kuragevp/.venv/lib/python3.10/site-packages/nvidia/cublas/lib:
/home/kojima/work/kuragevp/.venv/lib/python3.10/site-packages/nvidia/cudnn/lib:
/home/kojima/work/kuragevp/.venv/lib/python3.10/site-packages/nvidia/cuda_nvrtc/lib
```

`kmontage` 側がこの実行環境を使っていなかったため、CUDA版Faster-Whisperが必要なライブラリを見つけられなかったのです。

そこで、独自の文字起こしワーカーを削除し、Kurage Voice Proの既存pipelineを再利用する方針に変更しました。

現在の構成では、主に次の既存機能を利用しています。

- X動画取得: `kuragevp/backend/pipeline.py` のfxtwitter経由取得
- 音声抽出: `kuragevp.pipeline.extract_audio()`
- 文字起こし: `kuragevp.pipeline.transcribe_audio()`
- Whisper実行環境: Kurage Voice ProのvenvとCUDA設定
- 動画生成: Kurageの `/generate_from_news`
- 公開: `kuragev.php`

つまり、`kmontage` は新しい動画生成エンジンではなく、既存Kurage資産を組み合わせた「参照動画理解レイヤー」として作るのが正しい設計でした。

## OpenMontageから取り入れるべき設計思想

OpenMontageから本当に学ぶべきなのは、個々のコードよりも、中間成果物を明確に分ける設計です。

今の `kmontage` は、LLMが返した `analysis` をそのまま持っています。しかし今後、品質を上げるには、OpenMontage的に次のような成果物へ分割した方がよいです。

```text
reference_analysis.json
scene_plan.json
render_report.json
```

## reference_analysis.json

参照動画を解析した結果を保存します。

ここには、動画そのものの情報を入れます。

```json
{
  "source_url": "https://x.com/...",
  "duration": 2877,
  "language": "en",
  "transcript_preview": "...",
  "hook": "faceless YouTube channel built with AI",
  "main_claims": [
    "AIで顔出しなしYouTubeチャンネルを運営できる",
    "低コストで動画制作を自動化できる",
    "ただし継続と設計が必要"
  ],
  "reference_style": {
    "tone": "practical tutorial",
    "pacing": "long-form explanatory",
    "audience": "creators and side-business beginners"
  }
}
```

重要なのは、参照動画から何を読み取ったのかを保存することです。

これがないと、後から見たときに「本当に動画を読んだのか」「投稿文だけで作ったのか」が分かりません。

## scene_plan.json

次に、日本語ショート動画としてどう再構成するかを保存します。

```json
{
  "title": "AIで実現するユーチューブ自動収益化の仕組み",
  "target_duration": 90,
  "scenes": [
    {
      "index": 0,
      "role": "hook",
      "narration": "AI技術の進化により、ユーチューブでの収益化の形が大きく変化しています。",
      "visual_direction": "white studio, AI avatar presenter",
      "duration": 10
    },
    {
      "index": 1,
      "role": "case study",
      "narration": "実際に、AI歴史系チャンネルが短期間で成果を出した事例があります。",
      "visual_direction": "growth chart, channel analytics",
      "duration": 10
    }
  ]
}
```

OpenMontageの強いところは、「いきなり動画を作る」のではなく、制作計画を段階的に明文化することです。

この考え方はKurageにも相性がよいです。

Kurageはすでにシーン単位で画像、ナレーション、字幕、動画を生成できます。だから、`scene_plan.json` を明示的に持つだけで、制作の再現性がかなり上がります。

## render_report.json

最後に、生成後の検証結果を残します。

```json
{
  "job_id": "636bfd4210c84f2a",
  "video_file": "output.mp4",
  "thumbnail_file": "thumbnail.jpg",
  "duration_sec": 122,
  "has_audio": true,
  "has_thumbnail": true,
  "has_subtitles": true,
  "listed_on_kuragev": true,
  "warnings": []
}
```

今回の運用では、途中失敗したジョブがバックグラウンドで完了し、不要な動画が `kuragev.php` の一覧に出る問題がありました。

この種の問題は、生成完了時に `render_report.json` を作り、どのジョブが本命で、どれがキャンセル済みかを明示すれば防ぎやすくなります。

## kmontageの有益性

`kmontage` の価値は、参照動画を単に翻訳することではありません。

価値は次の3つです。

1つ目は、海外・X・YouTubeの長尺コンテンツを、日本語ショート動画に再構成できることです。

2つ目は、既存のKurage資産をそのまま利用できることです。動画取得、文字起こし、TTS、動画生成、公開一覧まで、すでに動いている部品を再利用できます。

3つ目は、参照動画から制作プランを作ることで、単なるニュース要約やブログ動画よりも、動画らしい構成に近づけることです。

これは、AI動画制作において大きな違いです。

```text
記事を読む動画
  ↓
参照動画の構成を理解して再編集する動画
```

この差は、視聴維持率やコンテンツの説得力に直結します。

## 今後の仕様として入れたいもの

`kmontage` を本格的な参照動画制作パイプラインにするなら、次の仕様を入れたいです。

- 参照動画の解析結果を `reference_analysis.json` として保存する
- LLMが「動画から読み取った事実」と「考察」を分けて出力する
- 生成前にタイトル、要約、台本、想定尺をUIで確認できるようにする
- 生成後に `render_report.json` を保存する
- キャンセル済みジョブがKurage一覧に復活しないようにする
- YouTube URLとX URLで取得経路を明確に分ける
- OpenMontageのように、保持する要素と変更する要素を明示する

特に重要なのは、次の分離です。

```text
参照動画の事実
  と
日本語ショート動画としての再構成
```

ここが混ざると、ただのLLM作文になります。

## まとめ

OpenMontageは、`kmontage` にとってそのまま移植する対象というより、参照動画ベースのAI動画制作における設計のお手本です。

一方で、Kurageシリーズにはすでに実運用で動いている強い部品があります。

- Kurage Voice Proの動画取得・文字起こし
- KurageのTTS・字幕・動画生成
- Kurage Blogの動画公開
- `kuragev.php` の一覧表示

そのため、`kmontage` の正しい方向性は、OpenMontage的な設計思想を取り入れながら、実装はKurageの既存資産を最大限再利用することです。

```text
OpenMontage = 制作パイプライン設計の参考
KurageVP = 参照動画の取得・文字起こし基盤
Kurage = 日本語ショート動画生成・公開基盤
kmontage = それらをつなぐ参照動画理解レイヤー
```

この構成にすると、AI OSSの良いところを活かしながら、すでに動いている自社基盤を壊さずに拡張できます。

`kmontage` はまだ初期実装ですが、参照動画を起点にした日本語ショート動画生成パイプラインとして、かなり有益な方向性が見えてきました。
