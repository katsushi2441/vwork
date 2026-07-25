---
title: "story-to-handdrawn-video 動作確認サンプル"
description: "gnipbao/story-to-handdrawn-videoをこのサーバーで実行して生成した、ページめくり動画の動作確認サンプルです。"
permalink: /samples/story-to-handdrawn-video/
---

# story-to-handdrawn-video 動作確認サンプル

[gnipbao/story-to-handdrawn-video](https://github.com/gnipbao/story-to-handdrawn-video)をこのサーバーで実行し、リポジトリに同梱された2枚の手描き参照画像から生成したプレビューです。

<video controls playsinline preload="metadata" style="display:block;width:min(100%,540px);height:auto;margin:1.5rem auto;background:#f4f7f9;border:1px solid #d9e5ec;border-radius:16px;box-shadow:0 12px 30px rgba(32,72,96,.12)">
  <source src="{{ '/assets/videos/story-to-handdrawn-video-preview.mp4' | relative_url }}" type="video/mp4">
  このブラウザでは動画を再生できません。
</video>

- 長さ：3.3秒
- サイズ：720×960（3:4）
- 形式：H.264 MP4
- 音声：なし
- 遷移：右下からのページめくり

[MP4ファイルを直接開く]({{ '/assets/videos/story-to-handdrawn-video-preview.mp4' | relative_url }})

これはリポジトリ同梱画像を使ったレンダラーの動作確認です。日本語ストーリーから新しくイラストを生成した完成動画ではありません。
