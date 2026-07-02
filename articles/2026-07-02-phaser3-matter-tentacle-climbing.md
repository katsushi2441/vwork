---
title: "「失敗動画がバズる」ブラウザゲームをPhaser 3 + Matter.jsで作る — ばね1本の触手物理とMediaRecorder内蔵クリップ共有"
emoji: "🪼"
type: "tech"
topics: ["phaser", "matterjs", "javascript", "sqlite", "game"]
published: true
---

クラゲの女の子が触手を伸ばして海面を目指すブラウザゲーム「[Kurageちゃん触手クライミング](https://kurage.exbridge.jp/kclimbing.html)」を1日で作って公開しました。QWOPや壺男、めっちゃカメレオンのような「操作は単純、物理はままならない、失敗が面白い」系のゲームです。

この記事では、このジャンルのゲームをOSSスタックだけで最小工数で作るための技術要素を解説します。

- 🎮 遊ぶ: https://kurage.exbridge.jp/kclimbing/
- 📖 解説ページ: https://kurage.exbridge.jp/kclimbing.html

# 設計方針: ゲーム性より「クリップ映え」

このゲームの目的はキャラクターの認知度向上です。だとすると最適化すべきは面白さそのものより「プレイ動画がSNSでシェアされること」で、技術選定がすべてそこから逆算されます。

1. **縦画面 9:16 (540x960)** — TikTok / Shorts / Reels / X にそのまま貼れるアスペクト比で作る。横画面のゲームは投稿時に黒帯がつく
2. **失敗が面白い物理** — 完璧に制御できない「ばね」を操作の中心に置く
3. **録画機能をゲームに内蔵** — プレイヤーに録画アプリを要求しない。ワンタップで動画が手に入る導線をゲームオーバー画面に置く

# 触手物理は Matter.js の constraint 1本で足りる

「触手がびよーんと伸びて岩に掴まる」表現に、ロープのセグメント物理シミュレーションは要りません。**ばね付き constraint を1本張って、見た目だけベジェ曲線で描く**のが最小構成です。多くのグラップリング系ゲームがこの方式です。

```js
// 掴んだ瞬間: プレイヤーと岩をばねで接続
// length を実距離より短くする(=0.45倍)ことで「引き寄せ」が生まれる
this.tether = this.matter.add.constraint(
  this.player.body, rock.body,
  dist * 0.45,   // 自然長: 実距離の45%まで縮もうとする
  0.02,          // stiffness: 小さいほどゴムっぽい
  { damping: 0.06 });
```

パラメータは3つだけで、手触りのほぼすべてが決まります。

| 定数 | 値 | 役割 |
|---|---|---|
| stiffness | 0.02 | ばねの硬さ。上げると即座に引き寄せられゲームが簡単になる |
| length倍率 | 0.45 | 引き寄せの強さ。下げるとカタパルトになる |
| frictionAir | 0.028 | 水中感。落下の「ふわっ」とした恐怖感を作る |

描画は物理と独立に、揺れる制御点を持つ2次ベジェで「ぷるぷる感」を偽装します。

```js
const mx = (px + rx) / 2 + Math.sin(this.time.now / 90) * 14;
const my = (py + ry) / 2 + Math.cos(this.time.now / 110) * 14;
const curve = new Phaser.Curves.QuadraticBezier(
  new Phaser.Math.Vector2(px, py),
  new Phaser.Math.Vector2(mx, my),
  new Phaser.Math.Vector2(rx, ry));
```

## 掴み判定は「方向優先スコアリング」

タップ地点に最も近い岩ではなく、**狙った方向に最も合う岩**を選ぶと操作感が良くなります。スマホの太い指では正確なタップを期待できないためです。

```js
const diff = Math.abs(Phaser.Math.Angle.Wrap(ang - aim)); // 狙いとのズレ角
if (diff > 0.85) continue;            // ±約49度の外は候補外
const score = diff * 220 + d * 0.35;  // 角度誤差を距離の約600倍重く評価
```

# クリップ共有: canvas.captureStream + MediaRecorder

このゲームの拡散装置です。ゲームのcanvasはそのまま録画ソースにできます。

```js
const stream = canvas.captureStream(30);
const mime = MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
  ? 'video/webm;codecs=vp9' : 'video/webm';
recorder = new MediaRecorder(stream, {
  mimeType: mime, videoBitsPerSecond: 2_500_000 });
recorder.ondataavailable = e => chunks.push(e.data);
recorder.start(1000);
```

ゲームオーバー時に `Blob` にまとめてダウンロードリンクを生成し、X の intent URL と並べて置きます。動画は intent に添付できないので「①動画をDL → ②ポストに添付」の2ステップを UI 文言で明示します。

ハマりどころが2つありました。

**1. 録画開始はユーザー操作起点にする。** ページロード直後に `captureStream()` を始めると、環境によっては黒画面が録れます。最初の `pointerdown` で開始するのが安全です。

**2. 「直近15秒だけ残すリングバッファ」は単純には作れない。** MediaRecorder のチャンクは独立再生できません（WebMヘッダは最初のチャンクにしかない）。古いチャンクを捨てると壊れたファイルになります。対策としてはレコーダーを2本交互に回す方式がありますが、このゲームは1プレイが短いので「プレイ全体を録画」に割り切りました。

# サーバ構成: 同一APIパスで dev=FastAPI / 本番=PHP を差し替える

ランキングAPIは開発環境と本番（PHP共有ホスティング）で実装が違いますが、**ゲーム側の fetch パスを1文字も変えない**のがポイントです。

開発は FastAPI + `pysqlite3-binary`（SQLite 3.51 同梱。標準ライブラリの sqlite3 より新しい）:

```python
try:
    import pysqlite3 as sqlite3   # SQLite 3.51.x
except ImportError:
    import sqlite3                # フォールバック
```

本番は共有ホスティングのPHPなので `api.php` 1ファイル + SQLite。`.htaccess` の rewrite で FastAPI と同じパスに見せます:

```apache
RewriteEngine On
RewriteRule ^api/(score|ranking|health)$ api.php?action=$1 [QSA,L]
```

これで `fetch('api/score')` がどちらの環境でもそのまま動きます。SQLiteファイルは Web 直下に置くことになるため、ディレクトリごと `.htaccess` で遮断します（`Require all denied`）。直URLで `scores.sqlite` を叩いて403が返ることを必ず確認してください。

# 物理ゲームらしいバグ: 円は円の上に立てない

初回実装で、ゲーム開始0.5秒後に勝手にゲームオーバーになる現象が出ました。原因はスタート地点の足場を「円形の岩」にしていたこと。**円形の剛体は円形の足場の上で静止できず、必ず転がり落ちます**。開始足場だけ平らな矩形（static rectangle）にして解決しました。物理エンジンに慣れていても、こういう「当たり前の物理」を見落とします。

# まとめ

- バズ狙いゲームは「9:16 + 失敗が面白い物理 + 録画内蔵」の3点セットで設計する
- 触手・ワイヤー系の物理は constraint 1本 + ベジェ描画で十分。調整パラメータを3つに絞れる
- `canvas.captureStream()` + MediaRecorder でシェア用クリップをゲームに内蔵できる。開始はユーザー操作起点で
- `.htaccess` rewrite でAPIパスを固定すれば、開発(FastAPI)と本番(PHP)でフロントを共通化できる

スタックはすべてOSS（Phaser 3.80 / Matter.js / FastAPI / SQLite）で、静的ファイル+PHP 1枚なので月額コストは実質ゼロです。ぜひ遊んで、失敗動画を `#Kurageクライミング` でポストしてみてください。

🎮 https://kurage.exbridge.jp/kclimbing/
