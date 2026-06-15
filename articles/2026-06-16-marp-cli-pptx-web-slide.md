---
title: "Markdownから「Web表示と完全一致する美しいPPTX」を作る — pptxgenjsをやめてmarp-cliにした話"
emoji: "🖼️"
type: "tech"
topics: ["marp", "pptx", "生成ai", "個人開発", "バイブコーディング"]
published: true
---

# Markdownから「Web表示と完全一致する美しいPPTX」を作る

社内で運用している「URLや原稿からスライドブログを生成するツール（uslideblog）」のPPTX出力を、何度作り直しても「Web表示はきれいなのにPPTXだけダサい」状態から抜け出せずにいた。

最終的に **アプローチそのものを捨てて作り直したら一発で解決した** ので、その過程と判断を残しておく。OSSの組み合わせ方の実例として、同じ悩みを持つ人の役に立つはずだ。

## 何が問題だったか

uslideblogは2つの表示経路を持っている。

- **Web表示**: HTML/CSSでスライドをレンダリング（きれいに作り込める）
- **PPTXダウンロード**: `pptxgenjs` で座標指定して図形・テキストを1つずつ配置

問題は後者だった。`pptxgenjs` は

```js
slide.addText(title, { x: 0.7, y: 0.35, w: 11.9, h: 0.7, fontSize: 30, ... });
slide.addShape(pres.ShapeType.rect, { x: 0.7, y: 1.1, w: 11.9, h: 0.02, ... });
```

のように、**座標を手で全部置く**。テーブル・箇条書き・引用・タイトル階層を座標計算で「それっぽく」並べることはできるが、HTML/CSSで作り込んだWeb表示の品質には構造的に追いつけない。フォントの効き方も、余白の取り方も、別物になる。

色を変えても余白を変えても「本質的に変わらない」。当然だ。**勝負している土俵が違う**のだから。

## 方針転換：HTML/CSSを画像化してPPTXに敷き詰める

答えはシンプルだった。

> Web表示と同じHTML/CSSをヘッドレスChromeでレンダリングし、各スライドを画像化してPPTXに全面配置する。

こうすれば **PPTX = Web表示** がピクセル単位で一致する。そして何より、**デザインの作り込みがCSSに集約される**。座標計算と格闘するのではなく、CSSを書けばいい。

これを自前で組んでもいいが、Marpエコシステムの `marp-cli` がまさにこれをやってくれる。`--pptx` で各スライドをChromeのスクリーンショットにして埋め込む。

### 構成

```
Markdown（front matterでテーマ指定）
  ↓ marp-cli + ヘッドレスChrome
各スライドを高解像度画像にレンダリング
  ↓
画像を全面配置したPPTX
```

サーバ側（Node.js）はリクエストを受けたら一時ディレクトリにMarkdownを書き出し、`marp-cli` を子プロセスで呼ぶだけになった。

```js
import { spawn } from "node:child_process";

function runMarp(args) {
  return new Promise((resolve, reject) => {
    const child = spawn(MARP_BIN, args, {
      env: { ...process.env, CHROME_PATH, CHROME_NO_SANDBOX: "true" },
    });
    let stderr = "";
    child.stderr.on("data", (d) => (stderr += d));
    child.on("close", (code) =>
      code === 0 ? resolve() : reject(new Error(stderr.slice(-500)))
    );
  });
}

// slides.md → slides.pptx
await runMarp([mdPath, "--theme", THEME_PATH, "--pptx",
              "--allow-local-files", "--no-stdin", "-o", outPath]);
```

ポイント:

- `CHROME_PATH` でシステムのChromeを指定（`marp-cli` は内蔵Chromiumも使えるが、サーバに入っている `google-chrome` を使うのが軽い）
- `--allow-local-files` はローカルのテーマCSSを読むために必要
- 生成は45枚で約12秒、ファイルは数MB（高解像度画像のため）。リアルタイム性より品質を取る用途なら十分

### デザインはCSSに全部寄せる

`pptxgenjs` 時代の座標ロジックは全部消えた。代わりに `@theme` 付きのCSSファイル1枚で、表紙・章区切り・本文・テーブル・引用のスタイルを定義する。

```css
/* @theme exbridge */
section { width: 1280px; height: 720px; padding: 78px 90px; ... }
section::before { content:''; position:absolute; top:0; height:6px;
  background: linear-gradient(90deg,#2563EB,#60A5FA); }
table { border-collapse:separate; border-radius:10px; overflow:hidden; ... }
th { background:#2563EB; color:#fff; }
tr:nth-child(even) td { background:#F8FAFF; }
blockquote { background:#EFF6FF; border-left:8px solid #2563EB; border-radius:0 14px 14px 0; }
```

Web表示とPPTXで同じテーマCSSを共有できるので、**1か所直せば両方変わる**。これが最大の利点だ。

## ハマったところ：データにテーブルの区切り行が無い

既存データのテーブルが、GFMの区切り行（`|---|---|`）無しで保存されていた。

```
| 項目 | 内容 |
| 代表ツール | GitHub Copilot |
```

markdown-itは2行目が区切り行でないとテーブルと認識しないので、`| 項目 | 内容 |` が生のテキストとして表示されてしまう。データ側を全部直すのは現実的でないので、Markdown生成時に**区切り行を自動補完**した。

```js
function normalizeTables(body) {
  const lines = body.split("\n");
  const out = [];
  let inTable = false;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const isRow = /^\s*\|.*\|\s*$/.test(line);
    const isDelim = /^\s*\|[\s:|-]+\|\s*$/.test(line);
    if (isRow && !inTable && !isDelim) {
      out.push(line);
      const cols = (line.match(/\|/g).length) - 1;
      const next = lines[i + 1] || "";
      if (!/^\s*\|[\s:|-]+\|\s*$/.test(next)) {
        out.push("|" + Array(cols).fill("---").join("|") + "|");
      }
      inTable = true;
    } else if (isRow) {
      out.push(line);
    } else {
      inTable = false;
      out.push(line);
    }
  }
  return out.join("\n");
}
```

これでテーブルが角丸・ヘッダー色付き・ゼブラ縞で正しくレンダリングされるようになった。

## 1スライドに収める検証は「画像を見て」やる

座標を捨てたぶん、「内容がスライドに収まっているか」はレンダリング結果を**目で見て**確かめるのが確実だ。`marp-cli` は `--images png` で各スライドをPNG出力できるので、

```bash
marp slides.md --theme exbridge.css --images png --allow-local-files -o /tmp/s.png
```

で1枚ずつ確認しながら、テーブルの行数・タイトルの行数・本文量を調整した。タイトルが2行に折り返すと縦が一気に詰まるので、長いタイトルは短くするか本文を削る、という地味な調整が効く。

## 学び

- **「色や余白を変えても本質が変わらない」ときは、土俵を疑う。** pptxgenjsの座標配置という土俵自体が、HTML/CSSの品質と勝負できなかった。
- **既にきれいに作れている経路（Web）があるなら、それを再利用する。** 画像化してPPTXに敷くだけで、二重メンテも消える。
- **OSSは「何ができるか」ではなく「どう組み合わせるか」。** Marp + ヘッドレスChrome + Node.jsの子プロセス呼び出し、という枯れた部品の組み合わせで十分だった。
- **データの非互換（テーブル区切り行欠落）は入口で正規化する。** データ全件修正より、生成パイプラインで吸収するほうが速い。

同じように「自動生成スライドのPPTXがダサい」で止まっている人は、座標を積むのをやめて、HTML/CSS→画像→PPTXに切り替えるのを勧めたい。

---

この種の「自社プロダクトを内製しながら、その技術を顧客向けに還元する」開発を、株式会社エクスブリッジでは継続的にやっています。バイブコーディング・AI内製化の相談は [exbridge.jp](https://exbridge.jp) まで。
