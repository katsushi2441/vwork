---
title: "Sora2に近い動画をOSSだけで無料生成：Wan2.1 + Ollama + ffmpegで作るAI動画パイプライン"
emoji: "🎬"
type: "tech"
topics: ["ai", "wan21", "ollama", "ffmpeg", "vibecoding"]
published: true
---

> OSSのAI動画生成モデル **Wan2.1** と **Ollama（Gemma4:e4b）**、**HyperFrames**、**ffmpeg** を組み合わせ、X（Twitter）の投稿URLから約30秒のショート動画を自動生成するパイプラインを構築した。商用サービスに近いクオリティをローカル環境・ゼロコストで実現した事例として紹介する。

---

## 生成された動画

- 使用ツイートURL: `https://x.com/i/status/2047148322067263744`
- 生成タイトル: 「マサイの戦士と人生を賭けた愛の物語」
- 確認URL: https://aiknowledgecms.exbridge.jp/kuragev.php?id=f9b46cf0c42f45cd

6シーンのリアルなAI映像が連結され、日本語ナレーション音声と字幕が付いた約30秒の縦型ショート動画が生成された。

---

## アーキテクチャ概要

```
X(Twitter) URL
    ↓
【脚本生成】 Ollama（Gemma4:e4b）
    → 6シーン分の英語image_prompt + 日本語ナレーション
    ↓
【音声生成】 edge-tts（ja-JP-NanamiNeural）
    → 全シーン連結ナレーション MP3（約28秒）
    ↓
【AI動画生成】 Wan2.1-T2V-1.3B（RTX 3090）
    → 6シーン × 約3秒のMP4映像
    ↓
【尺延長】 ffmpeg tpad（freeze last frame）
    → 各シーンをナレーション尺に合わせて引き伸ばし（約5秒/シーン）
    ↓
【連結 + 字幕】 ffmpeg concat + ASS字幕
    → タイトルオーバーレイ（冒頭1.5秒）
    → シーンごとのナレーション字幕
    ↓
【音声ミックス】 ffmpeg
    → 完成：約30秒縦型MP4（480×832）
```

バックエンドはPython（FastAPI）、LLMはローカルOllama、動画生成はLAN内のGPUサーバーで動く。**外部APIへの依存はゼロ**。

---

## 使用技術スタック

### Wan2.1-T2V-1.3B

Meta / Wan Videoが開発したオープンソースの動画生成モデル。

- モデルサイズ: 1.3B パラメータ
- ハードウェア: RTX 3090（24GB VRAM）
- 生成設定: `size=480*832`（縦型9:16）、`frame_num=49`（約3秒）、`sample_steps=50`
- 1シーン生成時間: 約5分（高品質モード）
- テストモード: `/api/test/story` で既存動画を即返却（開発・デバッグ用）

GPT-4oのImage Generationが静止画を返すのに対し、Wan2.1は**数秒の動画クリップ**を生成する。Soraに近い映像品質をローカルGPUで実現している点が最大の特徴。

### Ollama + Gemma4:e4b

ツイート本文から脚本を生成するLLM。

```json
{
  "scenes": [
    {
      "index": 0,
      "image_prompt": "Kenya savanna golden hour, Swiss woman meets Maasai warrior",
      "narration": "ケニアのサバンナ。黄金色に染まる夕暮れ時、運命の出会いが始まった。",
      "label": "出会い"
    },
    ...
  ],
  "title": "マサイの戦士と人生を賭けた愛の物語"
}
```

`image_prompt` は英語でWan2.1に渡し、`narration` は日本語でTTSに渡す。ローカルで動くGemma4:e4bがこの構造化JSONを一発で生成する。

### edge-tts

MicrosoftのEdge TTSをローカルから呼び出す。`ja-JP-NanamiNeural` 音声で全シーンのナレーションを1本のMP3に連結し、動画の尺の基準にする。

```python
narration_dur = get_audio_duration(narration.mp3)  # → 27.8s
total_dur = ceil(narration_dur) + 1                 # → 29s
per_scene = total_dur / num_scenes                  # → 4.83s/scene
```

### ffmpeg: tpad + ASS字幕 + concat

Wan2.1の生成動画（約3秒）をナレーション尺（約5秒）に合わせて引き伸ばす。

```bash
# 最終フレームをフリーズして尺を延長
ffmpeg -i scene.mp4 -vf "tpad=stop_mode=clone:stop_duration=2.0" \
       -c:v libx264 extended.mp4

# 連結
ffmpeg -f concat -safe 0 -i concat.txt -c:v libx264 concat_only.mp4

# ASS字幕を焼き込み（タイトル + ナレーション）
ffmpeg -i concat_only.mp4 \
       -vf "subtitles='subtitles.ass':fontsdir=/usr/share/fonts/opentype/noto" \
       -c:v libx264 subtitled.mp4

# 音声ミックス
ffmpeg -i subtitled.mp4 -i narration.mp3 \
       -c:v copy -c:a aac -shortest output.mp4
```

### ASS字幕フォーマット

タイトルと字幕はASS（Advanced SubStation Alpha）形式で管理する。

```
[V4+ Styles]
Style: Title,Noto Sans CJK JP,30,...,5,...  # 中央揃え
Style: Narr,Noto Sans CJK JP,24,...,2,...   # 下部揃え

[Events]
Dialogue: 1,0:00:00.00,0:00:01.50,Title,,,,,,{\an5}マサイの戦士と人生を賭けた愛の物語
Dialogue: 0,0:00:01.50,0:00:06.33,Narr,,,,,,ケニアのサバンナ。...
```

冒頭1.5秒は黒半透明のボックス付きタイトルが中央表示され、以降は各シーンのナレーション字幕が下部に表示される。

---

## 2系統モードの比較

kurageには2つの動画生成モードがある。

| | HyperFramesモード | Wan2.1モード |
|---|---|---|
| 映像 | ERNIE静止画（384×384） | Wan2.1 AI動画（3秒/シーン） |
| レンダリング | HyperFrames（GSAP + HTML → MP4） | ffmpeg concat + tpad |
| 字幕 | GSAPアニメーション | ASS字幕（libass焼き込み） |
| 生成時間 | 約5〜10分 | テスト: 即時 / 本番: 約30分 |
| GPU要件 | なし（ERNIE APIに依存） | RTX 3090推奨 |

HyperFramesモードはERNIEの静止画をGSAPでアニメーションさせた動画で、Wan2.1モードはリアルなAI映像クリップを連結した動画。用途や生成時間に応じて選択できる。

---

## 実装の工夫点

### スクリプト生成のキャッシュ

同じURLを再投入したとき、LLM呼び出しをスキップして前回のスクリプトを再利用する。失敗したジョブを再開できるため、30分かかるWan本番生成の途中でエラーが出ても最初からやり直さなくて済む。

### テストモードの分離

`WAN_TEST_MODE=1`（環境変数）のときは `/api/test/story` を使い、既存テスト動画を即返却するWan APIを使う。開発中は字幕・音声の調整をゼロ待ち時間でテストできる。

### 字幕フォントの安定化

`fontsdir` でNoto Sans CJK JPが入ったディレクトリを明示指定し、サーバー環境によるフォント解決の失敗を防いでいる。

---

## まとめ

- Wan2.1（1.3B、RTX 3090）でSoraに近いリアルな動画クリップを生成できる
- Ollama（Gemma4:e4b）でツイートから6シーン構成の脚本を完全ローカルで生成できる
- ffmpegのtpad + concat + ASS字幕で既存のショート動画と同品質のフォーマットを実現できる
- 外部API・課金ゼロで約30秒のAI動画パイプラインが動く

商用クラウドなしでここまで作れるのが2026年現在のOSSの水準。バイブコーディングで数時間で実装した。

---

株式会社エクスブリッジ https://exbridge.jp/
