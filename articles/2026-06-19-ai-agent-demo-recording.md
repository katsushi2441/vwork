---
title: "AIエージェントに自社プロダクトを操作させて、デモ動画を自動録画する"
emoji: "🎬"
type: "tech"
topics: [browseruse, ollama, ffmpeg, 生成ai, oss]
published: true
---

「プロダクトのデモ動画を作りたい。でも毎回手で画面操作して録画するのは面倒」——そこで、**AIブラウザエージェントに自社プロダクトのWeb UIを操作させ、その様子をそのまま動画として録画する**仕組みを作りました。すべてローカル・OSSで完結し、外部APIの従量課金はゼロです。

この記事では、そのパイプラインで使ったOSSと技術、そして実際にハマった点を解説します。

## 何を作ったか

題材は自社のAI動画ローカライズツール「Kurage Voice Pro」（海外動画のURLを入れると、文字起こし→翻訳→字幕→吹き替えまで自動化するOSS）。これに対して、

1. AIエージェントが管理画面を開く
2. 動画URLを入力欄に打ち込む
3. 「翻訳・吹替」ボタンを押してジョブを開始させる

という一連の操作を**人間の手を介さず**実行し、その画面を録画して `demo.mp4` を生成します。

## 使ったOSS / 技術

| 役割 | 採用したもの |
|---|---|
| ブラウザ操作エージェント | [browser-use](https://github.com/browser-use/browser-use) |
| エージェントの頭脳（LLM） | [Ollama](https://github.com/ollama/ollama) + Gemma 4 (`gemma4:12b-it-qat`) |
| 画面録画 | Chrome DevTools Protocol (CDP) `Page.startScreencast` |
| 動画エンコード | ffmpeg |
| ブラウザ | Chromium / Google Chrome |

ポイントは、**「操作するAI」と「録画する仕組み」を1つのChromeに同居させる**ことです。

## 技術ポイント①：頭脳はローカルLLM（gemma4:12b）

browser-useは画面を見て「次にどこをクリック/入力するか」を毎ステップ判断します。これには視覚（vision）とツール呼び出しに対応したモデルが要ります。

GPT-4oやClaudeをAPIで使うのが王道ですが、ここではコストゼロにこだわり、ローカルのOllamaで動く **Gemma 4（`gemma4:12b-it-qat`）** を使いました。`ollama show` で `vision` / `tools` capability があることを確認しています。

```python
from browser_use import Agent, BrowserProfile, ChatOllama

llm = ChatOllama(model="gemma4:12b-it-qat", host="http://127.0.0.1:11434", timeout=600)
```

正直に書くと、12BクラスはフロンティアモデルよりGUIの「クリック位置当て」が甘く、ラジオボタンを取りこぼすことがあります。**重要操作は人が最終確認する前提**で、コストとのトレードオフで選ぶのが現実的です。

> Ollamaは古いバージョンだとGemma 4を引けません（`Please download the latest version`）。最新へ更新してから `ollama pull gemma4:12b-it-qat` してください。

## 技術ポイント②：録画は x11grab ではなく CDP screencast

最初は「仮想ディスプレイ(Xvfb)を ffmpeg の `x11grab` で画面録画」を考えましたが、環境の ffmpeg が x11grab 非搭載でした（`Unknown format 'x11grab'`）。browser-useが内部で使うPlaywrightの動画録画（`record_video_dir`）も、このバージョンでは出力されませんでした。

そこで **Chrome DevTools Protocol の `Page.startScreencast`** に切り替えました。これはChromeがレンダリング中のフレームをJPEGで流してくれる機能で、

- x11grab不要・追加バイナリ不要（エンコードは既存ffmpegで十分）
- デスクトップ全体でなく「ブラウザの中身だけ」が録れる＝デモとして見やすい
- headlessでも録れる

という利点があります。WebSocketでCDPに繋ぎ、フレームを受けては保存→ackを返すだけです。

```python
await send("Page.enable")
await send("Page.startScreencast", {"format": "jpeg", "quality": 80, "everyNthFrame": 1})
# ...受信ループ...
if d.get("method") == "Page.screencastFrame":
    p = d["params"]
    (frames_dir / f"f{n:06d}.jpg").write_bytes(base64.b64decode(p["data"]))
    frame_times.append(time.time() - t0)
    await send("Page.screencastFrameAck", {"sessionId": p["sessionId"]})
```

## 技術ポイント③：操作するChromeに「相乗り」して録る

screencastで録るページと、browser-useが操作するページを一致させる必要があります。やり方はシンプルで、**remote-debugging付きでChromeを起動し、browser-useをそのChromeに `cdp_url` で接続させる**だけです。

```python
# 1) Chrome を remote debugging 付きで起動
chrome = subprocess.Popen([
    "/usr/bin/google-chrome", "--headless=new",
    "--remote-debugging-port=9224", "--remote-debugging-address=127.0.0.1",
    "--no-sandbox", "--disable-gpu", "about:blank",
])

# 2) browser-use は同じChromeに相乗り
profile = BrowserProfile(cdp_url="http://127.0.0.1:9224", headless=True)
agent = Agent(task=task, llm=llm, browser_profile=profile)
```

録画用のCDP接続と、browser-use用の接続は別々ですが、同じChromeを見ているので、エージェントの操作がそのままフレームに乗ります。

## 技術ポイント④：ログインは「Cookie注入」で突破する

つまずいたのが認証でした。Kurage Voice Proの管理画面は **「Xでログイン」（X/Twitter OAuth）**。AIエージェントにX.comのログインを自動で突破させるのは現実的でなく（強力なbot対策）、そもそもXログイン画面を録画してもデモになりません。

解決策は、**ログイン済みセッションのCookieをCDPで注入し、認証済み状態から操作を始める**ことです。ログインという退屈な前段を録画対象から外せるメリットもあります。

```python
await send("Network.enable")
await send("Network.setCookie", {
    "name": "EXBRIDGESESSID", "value": SESSION_VALUE,
    "domain": "example.com", "path": "/",
    "secure": True, "httpOnly": True, "sameSite": "Lax",
})
```

これで「URL入力 → 実行ボタン → ジョブ開始」という**デモの本体だけ**をクリーンに録画できます。

## 技術ポイント⑤：可変フレーム間隔を正確に動画化

screencastのフレームは等間隔では届きません（ページが静止している間はフレームが来ない）。そこで各フレームの実時刻を記録し、ffmpegの **concat demuxer** に `duration` 付きで渡して、実時間に忠実な動画を作ります。libx264は幅・高さが偶数でないと失敗するので、スケールフィルタで偶数化もします。

```python
# frames/list.txt : file 'fNNNNNN.jpg' / duration 0.137 ... の繰り返し
subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "frames/list.txt",
    "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
    "-vsync", "vfr", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
    "demo.mp4",
])
```

> 出力パスは**絶対パス**で渡すのが安全です。concat demuxerは作業ディレクトリ基準で相対パスを解決するため、相対パスだとエンコードが失敗します（地味にハマりました）。

## できあがり

`Cookie注入 → browser-useがURL入力 → 実行ボタン → ジョブ開始（downloading 5%）` までを完全自動で実行し、その全工程を `demo.mp4` に記録できました。録画された動画には、AIが実際に自社プロダクトを操作する様子がそのまま映っています。

ナレーション（VTuberキャラの解説など）は別撮りして、ffmpegで合成する想定です。

## まとめ

- **browser-use × ローカルLLM(Gemma 4) × CDP screencast** で、「AIが自社プロダクトを操作するデモ動画」をコストゼロ・OSSだけで自動生成できる。
- 画面録画は x11grab に頼らず **CDP `Page.startScreencast`** が確実。
- 操作と録画は **remote-debugging + `cdp_url` 相乗り**で同じChromeに。
- OAuthログインは自動突破せず **Cookie注入**で回避するのが現実的。
- ローカル12B LLMは安いが精度はそこそこ。重要操作は人の確認を挟む。

「AIに道具（自社プロダクト）を使わせて、その実演を記録する」という発想は、デモ・チュートリアル・回帰テストの動画化など、いろいろ応用が効きそうです。

---

- browser-use: https://github.com/browser-use/browser-use
- Ollama: https://github.com/ollama/ollama
- Kurage Voice Pro（題材）: https://github.com/katsushi2441/kuragevp
