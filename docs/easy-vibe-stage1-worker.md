# easy-vibe Stage 1 Worker

VWork Blogで公開している easy-vibe Stage 1 の続きを、1セクションずつ日本語記事化し、Kurageショート動画へつなぐworkerです。

## 方針

- 1 RQDB4AIジョブ = 1セクション。
- 既存記事の「学習マップ」と「AIの時代：話せればコードが書ける」は処理済みとして扱う。
- 残りのStage 1本編を順番に処理する。
- VWork記事公開は `scripts/publish.py --no-sns` を使い、AIxSNS告知は動画生成後に `author=kurage` で行う。
- Kurage動画URLは必ず `https://kurage.exbridge.jp/kuragev.php?id={JOB_ID}` を使う。
- 古い `horizonv.php` や `aiknowledgecms.exbridge.jp` を告知URLに使わない。

## 対象セクション

1. 学習マップ: 既存記事あり
2. AIの時代：話せればコードが書ける: 既存記事あり
3. AIプログラミングツールの使い方
4. よいアイデアの見つけ方
5. プロダクトプロトタイプの作り方
6. プロトタイプにAI能力を組み込む
7. 完成プロジェクトの実践

## RQDB4AI投入

次の未処理セクションを投入する。

```bash
cd /home/kojima/work/vwork
RQDB4AI_API_TOKEN=... ./easy_vibe_enqueue.py
```

特定セクションだけ投入する。

```bash
cd /home/kojima/work/vwork
RQDB4AI_API_TOKEN=... ./easy_vibe_enqueue.py --section-id ai-ide-tools
```

dry-runで記事プレビューだけ確認する。

```bash
python3 - <<'PY'
import easy_vibe_jobs
print(easy_vibe_jobs.process_next_section_job(dry_run=True)['preview'][:1200])
PY
```

## RQDB4AI function

```text
easy_vibe_jobs.process_next_section_job
easy_vibe_jobs.process_section_job
```

## 注意

- easy-vibeは Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License。記事には出典とライセンス表記を残す。
- VWork向け記事は公式教材を丸写しにせず、出典つきで読みやすく整理する。
- 公開・動画生成・SNS告知は別々に成功確認する。RQDB4AIへの投入成功だけを業務成功とみなさない。
