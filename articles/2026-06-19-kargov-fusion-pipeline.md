---
title: "AIが操作するデモ動画、台本までAIに書かせる — 自作ツール×OSS Argo 融合パイプライン"
emoji: "🎞️"
type: "tech"
topics: [browseruse, ollama, claude, ffmpeg, oss]
published: true
---

前回、[AIブラウザエージェントに自社プロダクトを操作させ、その様子をCDP screencastで録画する](https://zenn.dev/katsushi2441/articles/2026-06-19-ai-agent-demo-recording)仕組みを作りました。動くには動くのですが、出てくるのは「ナレーションも字幕もない、ただの操作録画」。デモ動画として人に見せるには物足りない。

ちょうどそのとき、[shreyaskarnik/argo](https://github.com/shreyaskarnik/argo) というOSSを見つけました。**Playwrightスクリプト → AIナレーション付きの製品デモ動画**を作るツールで、シーン整列・字幕オーバーレイ・縦横書き出しまで揃っています。

「自作の良いところ（AIの自律操作）を残しつつ、Argoの良いところ（仕上げ）だけ融合できないか？」——そうして作った融合パイプライン **kargov** の技術メモです。すべてローカル・OSS・API課金ゼロで完結します。

## 融合の方針

両者は競合ではなく役割分担できます。Argoは「Playwrightで決め打ちした操作」を前提にしますが、こちらは「AIが自分で考えて操作する」のが核。そこは捨てない。

| 区分 | 機能 | 由来 |
|---|---|---|
| 残す | AIの自律操作（browser-use + ローカルgemma4） | 自作 |
| 残す | CDP screencast録画・Cookie注入認証 | 自作 |
| 移植 | シーンmark→ナレーション自動整列 | Argo |
| 移植 | 字幕オーバーレイ・16:9/9:16書き出し | Argo |
| **融合** | **自律操作しながら台本(scenes.json)を自動ドラフト** | 両者 |
| **融合** | **ナレ台本をOAuth Claudeで日本語に整文** | 自作流儀 |

ArgoはTypeScript/npmですが、母体がPython(uv)なので**コードを移植せず“概念”だけ取り込む**ことにしました。

## 技術ポイント①：操作しながら台本を自動で書く

browser-useは1ステップごとに「次に何をするか(next_goal)」を考えて実行します。そこに `on_step_end` フックを挿し、**各ステップの境界で録画に時刻マークを打ちつつ、その操作意図をナレーション草案として積んで**いきます。Argoは台本を手書き必須ですが、kargovは「AIが操作しながら台本も書く」。

```python
async def on_step_end(agent):
    i = next(counter)
    model_output = agent.history.history[-1].model_output
    goal = model_output.current_state.next_goal      # "Input the URL and start the job"
    rec.mark(f"step{i:02d}")                          # 録画内の時刻を記録
    draft.append({
        "scene": f"step{i:02d}", "text": goal,
        "overlay": {"type": "lower-third", "text": goal[:40],
                    "placement": "bottom-center"},
    })

agent = Agent(task=task, llm=llm, browser_profile=profile)
await agent.run(max_steps=steps, on_step_end=on_step_end)
```

録画のマーク（`recorder.mark`）はシンプルに録画開始からの経過秒を記録するだけ。これが後段の「ナレーション整列」の土台になります。

```python
def mark(self, name):
    self.marks.append({"name": name, "t": time.time() - self._t0})
```

## 技術ポイント②：ナレ台本をOAuth Claudeで日本語に整文

ここが今回の肝です。gemma4(12B)の生のnext_goalは、こんな英語混じりの機械的なメモです。

```
Input the URL into the video URL field and start the job.
Finalize the task as all requirements have been met.
```

これをそのまま読み上げてもデモになりません。そこで、台本だけを**OAuth Claude**に整文させます。APIキーは使わず、Claude Codeの `claude -p` をそのまま叩くやり方です（自分の別プロジェクトでも使っている方式）。

```python
def claude_request(prompt: str) -> str:
    cmd = [claude_bin, "-p",
           "--output-format", "text",
           "--permission-mode", "dontAsk",
           "--model", "sonnet", prompt]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    return (proc.stdout or "").strip()
```

`claude_bin` は環境にインストール済みのClaude Codeバイナリを自動解決します（拡張の `native-binary/claude` をバージョン降順で探す）。プロンプトでは「番号付き・同じ行数を厳守」「各行 `ナレーション @@@ 字幕(20字)` 形式」と制約し、字幕も同時に作らせます。`@@@` 区切りにしておくとパースが安定します。

結果はこの通り。英語の機械メモが、視聴者向けの自然な日本語ナレ＋簡潔な字幕に変わります。

| Before（gemma4の生） | After（Claude整文） |
|---|---|
| Input the URL into the video URL field and start the job. | 続いて、吹き替えたい動画のURLを専用の入力欄に貼り付け、翻訳ジョブをスタートさせます。／字幕「動画URLを入力・開始」 |
| Finalize the task as all requirements have been met. | すべての工程が正常に終わったことを確認し、AIエージェントがタスクをまとめて完了させます。／字幕「タスク完了！」 |

**「操作の判断は安いローカルLLM、言葉の仕上げは賢いClaude」**という役割分担が、コストと品質のバランスとして現実的でした。

## 技術ポイント③：ナレーションの長さに映像を合わせる

screencastの録画と、シーンごとのナレーション音声（edge-ttsで生成）は長さが一致しません。多くの場合**ナレーションのほうが長い**（AIが操作した数秒に対し、解説は十数秒になる）。

そこでArgoの「シーン時刻にクリップを整列」を拝借し、各シーン区間 `[mark_i, mark_{i+1}]` を切り出して、**ナレーション長に足りなければ最終フレームを保持（tpad）して尺を伸ばす**ようにしました。

```python
target = max(seg_dur, audio_dur, 1.2)          # ナレを絶対に切らない
pad = max(0.0, target - seg_dur)
vf = "scale=trunc(iw/2)*2:trunc(ih/2)*2"
if pad > 0:
    vf = f"tpad=stop_mode=clone:stop_duration={pad:.3f}," + vf
```

これでシーン単位で音声と映像が同期します。実際、4秒の操作映像が9.6秒のナレーションにぴたりと合いました。

## 技術ポイント④：字幕焼き込みと 16:9 / 9:16 書き出し

字幕は `drawtext` で焼き込みます。日本語が化けないよう Noto CJK を指定し、テキストは `textfile=` で渡してエスケープ地獄を回避します。

```
drawtext=fontfile='/usr/share/fonts/.../NotoSansCJK-Bold.ttc':textfile='ov.txt':
  fontcolor=white:fontsize=34:box=1:boxcolor=black@0.55:boxborderw=18:
  x=(w-text_w)/2:y=h-text_h-80
```

シーンごとに整列・字幕焼き込みしたクリップを連結して `master.mp4` を作り、そこから縦横を書き出します。横長のデスクトップUIを縦型(9:16)にする際は、潔く**レターボックス(fit)**にしました。

```
scale=576:1024:force_original_aspect_ratio=decrease,
pad=576:1024:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1
```

> なお `which ffmpeg` が指す静的ビルドには `drawtext` も `x11grab` も無いことがあります。フィルタ完備のディストリ版（`/usr/bin/ffmpeg`）を明示するのが安全です。

## ハマったところ：失効したログインCookieを復活させる

認証付きの管理画面（X OAuthログイン）に対しては、前回同様**ログイン済みCookieを注入**して認証後の状態から録画します。ところが時間が経つとセッションが切れる。

解決策は、**VNC上のChromeで一度手動ログインし、そのプロファイルのCookieを取り出す**ことです。LinuxのChrome Cookieは `v10` 暗号で、鍵は固定パスフレーズ `peanuts` から導出できます。

```python
key = PBKDF2HMAC(hashes.SHA1(), 16, b'saltysalt', 1).derive(b'peanuts')
dec = Cipher(algorithms.AES(key), modes.CBC(b' ' * 16)).decryptor()
pt  = dec.update(encrypted_value[3:]) + dec.finalize()   # 先頭3byteの "v10" を除去
pt  = pt[:-pt[-1]]                                        # PKCS7 unpad
value = pt[32:].decode()    # 新しめのChromeは先頭32byteがドメインhashなので捨てる
```

取り出した値をCDPの `Network.setCookie` で注入すれば、認証済み状態から「URL入力→ジョブ開始」というデモ本体だけをクリーンに録画できます。

## できあがり

`AIが自律操作しながら録画＋台本ドラフト → Claudeが日本語整文 → Kurageの声でナレ生成 → 字幕焼き込み → 16:9/9:16書き出し` までを、ワンコマンドで通せるようになりました。

題材にした自社の動画翻訳ツールを、AIが「①管理画面を開く ②動画URLを貼る ③生成開始を押す」まで自分で操作する様子を録画したテスト動画は、こちらで公開しています。

- 生成デモ動画: https://kurage.exbridge.jp/kuragev.php?id=979c1478e3468b93

## まとめ

- **browser-use(自律操作) × Argo(仕上げ)** の融合で、「AIが操作するデモ」を字幕・ナレ付きの動画に自動化できる。
- **操作の判断はローカルgemma4、台本の整文はOAuth Claude**——役割分担でコストと品質を両立。
- ナレーションと映像の同期は、Argo流の**シーン整列＋最終フレーム保持**で解決。
- 失効したログインは、**VNCで手動ログイン→Cookie復号→CDP注入**で再利用。
- 残課題：AIの「思考中の間」が尺を冗長にするので**gapの早送り**、横長UIの**縦型クロップ**は今後。

「決め打ちのスクリプト」と「自律エージェント」、両方の良さは融合できる、という手応えのある実験でした。

---

- browser-use: https://github.com/browser-use/browser-use
- Ollama: https://github.com/ollama/ollama
- Argo: https://github.com/shreyaskarnik/argo
