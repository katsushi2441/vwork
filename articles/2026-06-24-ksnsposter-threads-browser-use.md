---
title: "Kurage SNS Poster：browser-useとログイン済みChromeでThreads自動投稿まで到達した実装メモ"
emoji: "🧵"
type: "tech"
topics: ["browseruse", "playwright", "threads", "ollama", "aiagent"]
published: true
---

# Kurage SNS Poster：browser-useとログイン済みChromeでThreads自動投稿まで到達した実装メモ

Meta系SNSへ自動投稿しようとすると、最初にぶつかるのはAPIそのものよりも、OAuth、審査、権限、トークン管理です。

とくにThreads、Instagram、TikTokのような投稿系プラットフォームは、APIで綺麗に自動化しようとすると、アプリ審査やビジネスアカウント設定、権限申請、長期トークン管理などが必要になります。

そこで今回は、APIトークンに依存せず、**人間が一度ログインしたChromeプロファイルをAI/ブラウザ自動化から再利用する**ための小さなプロダクトとして、Kurage SNS Poster (`ksnsposter`) を作りました。

今回の到達点は、Threadsへの投稿です。

実際に、Kurageショート動画のYouTube Shorts投稿告知を、ログイン済みChromeプロファイル経由でThreadsに投稿できました。

```text
Kurageショート動画をYouTube Shortsに投稿しました。

大河ドラマ「豊臣兄弟！」中野太賀が語る！秀長役トークライブレポート

Kurage動画: https://kurage.exbridge.jp/kuragev.php?id=bf78cea761bd49fc
YouTube Shorts: https://youtu.be/sbSalP_gaU8

#Kurage #AI動画生成 #Shorts #エクスブリッジ
```

## リポジトリ

Kurage SNS Posterは、次のGitHubリポジトリで管理しています。

- [katsushi2441/ksnsposter](https://github.com/katsushi2441/ksnsposter)

このリポジトリの役割は、Kurage本体、kdeck、rqdb4ai、AIxSNSなどから独立した、**SNS投稿用のブラウザ自動化レイヤー**です。

動画を作る、YouTubeへ投稿する、AIxSNSへ投稿する、といった処理は既存のKurage/kdeck側に残し、Threads、Instagram、TikTokなど「Web UIで投稿するしかない/そのほうが現実的」な部分だけを `ksnsposter` に分離しています。

## なぜAPIではなくブラウザ自動化なのか

SNS投稿の自動化では、本来は公式APIを使うのが理想です。

しかし、実運用では次の問題があります。

- API利用にアプリ審査が必要
- 投稿権限の取得に時間がかかる
- 個人/ビジネスアカウントの条件が複雑
- 長期トークンの更新と保管が運用負荷になる
- プラットフォームごとにAPI仕様が大きく違う

一方で、Web UIはすでに人間が使える状態になっています。

そこで、今回の設計では次の割り切りをしました。

- 認証は人間がVNC上のChromeで一度行う
- ログイン済みChromeプロファイルを保存する
- 投稿時はそのプロファイルを使ってWeb UIを開く
- デフォルトは下書き作成までにして、明示オプションがあるときだけ投稿する
- 成功/失敗はスクリーンショットとログに残す

これは「API自動化」ではなく、**human-authenticated browser-session automation**です。

人間が認証したブラウザセッションを、AI AgentやPlaywrightが安全に再利用する発想です。

## 全体構成

`ksnsposter` は大きく4つの部品で構成しています。

```text
ksnsposter/
  cli.py                  # 投稿CLI
  browser_runner.py       # browser-use実行レイヤー
  tasks.py                # Threads/Instagram/TikTok向けタスク生成
scripts/
  ksnsposter              # 実行ラッパー
  start-login-chrome      # VNCログイン用Chrome起動
  post-threads-playwright.py # Threads投稿の決定的実行ルート
storage/
  chrome-profile/         # ログイン済みChromeプロファイル（git管理外）
runs/
  ...                     # スクリーンショット、結果JSON（git管理外）
```

CLIの基本形は次のようにしています。

```bash
./scripts/ksnsposter post \
  --platform threads \
  --text-file /tmp/post.txt \
  --confirm-post \
  --headful
```

デフォルトでは、`--confirm-post` がなければ最終投稿ボタンを押しません。

SNS投稿は失敗時の影響が大きいので、最初から「勝手に投稿するツール」ではなく、**下書き確認を標準、明示したときだけ投稿**という設計にしました。

## ローカルLLMはOllamaのGemma 4

browser-use側のLLMには、既存のローカルOllamaサーバを使っています。

```python
DEFAULT_OLLAMA_HOST = "http://192.168.0.3:11434"
DEFAULT_MODEL = "gemma4:12b-it-qat"
```

API課金を増やさず、ローカルLLMでWeb UI操作の判断をさせる構成です。

`browser_runner.py` では、browser-useの `Agent`、`BrowserProfile`、`ChatOllama` を使っています。

```python
llm = ChatOllama(model=config.model, host=config.host, timeout=900)
profile = BrowserProfile(**profile_kwargs)
agent = Agent(task=config.task, llm=llm, browser_profile=profile, max_actions_per_step=3)
```

この構成により、Threads、Instagram、TikTokそれぞれに対して、自然言語タスクを組み立ててブラウザ操作を任せられます。

## ログイン済みChromeプロファイルを使う

今回の肝は、ログイン済みChromeプロファイルです。

```text
/home/kojima/work/ksnsposter/storage/chrome-profile
```

このプロファイルはgit管理対象外にしています。

SNSのCookieやセッション情報はコードリポジトリに入れてはいけません。そこで、プロダクトのコードと、実運用のログイン状態を分離しています。

VNC上でログインするときは、専用スクリプトでChromeを起動します。

```bash
./scripts/start-login-chrome
```

中ではChrome for TestingまたはGoogle Chromeを、専用プロファイル、X11、安定化オプション付きで起動します。

```bash
setsid env DISPLAY="$DISPLAY_VALUE" "$CHROME" \
  --user-data-dir="$PROFILE" \
  --profile-directory=Default \
  --disable-dev-shm-usage \
  --disable-gpu \
  --enable-unsafe-swiftshader \
  --no-sandbox \
  --disable-setuid-sandbox \
  --password-store=basic \
  --use-mock-keychain \
  --ozone-platform=x11 \
  --window-size=1280,900 \
  "${1:-https://www.threads.net/}" \
  >/tmp/ksnsposter-login-chrome.log \
  2>/tmp/ksnsposter-login-chrome.err.log \
  < /dev/null &
```

ポイントは、通常利用のChromeプロファイルを汚さず、`ksnsposter` 専用のログイン状態を作ることです。

これにより、Threadsへログインした状態を次回の自動投稿に引き継げます。

## browser-useだけで完結しなかった理由

最初は、browser-useだけでThreads投稿まで完結させる設計にしました。

実際、browser-useは次の用途では有効でした。

- ログイン状態の確認
- Threadsの画面遷移確認
- 投稿タスクの自然言語化
- Instagram/TikTokなど横展開可能な共通タスク生成
- 画面のスクリーンショット保存

ただし、ThreadsのSPAでは、最終投稿までの細かい操作で不安定さがありました。

具体的には、投稿本文が正しく入っているかの確認、投稿ボタンの特定、リダイレクト後の状態判定などで、LLMエージェントがループしやすい場面がありました。

そこで、最終的にはハイブリッド構成にしています。

- 汎用のSNS投稿タスク設計: browser-use
- Threadsの決定的な投稿処理: Playwright

これは妥協ではなく、実運用ではかなり重要な判断です。

AI Agentは柔軟ですが、毎回同じDOMを相手にする最終クリックでは、Playwrightのような決定的スクリプトのほうが安定します。

## Threads投稿はintent URLとPlaywrightで安定化

Threadsには投稿文を事前入力できる intent URL があります。

```python
url = f'https://www.threads.net/intent/post?text={quote(text)}'
```

`post-threads-playwright.py` では、このURLをログイン済みプロファイルで開きます。

```python
context = p.chromium.launch_persistent_context(
    str(profile),
    headless=not args.headful,
    executable_path=str(chrome),
    viewport={'width': 1280, 'height': 940},
    args=[
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--enable-unsafe-swiftshader',
        '--password-store=basic',
        '--use-mock-keychain',
    ],
)
```

本文が空になるケースに備えて、見えている `contenteditable` へ明示的に入力するフォールバックも入れています。

```python
if text.splitlines()[0] not in body_text:
    editor = page.locator('[contenteditable="true"]').first
    editor.click(timeout=10000)
    page.keyboard.press('Control+A')
    page.keyboard.type(text, delay=1)
```

投稿ボタンは日本語UIと英語UIの両方を探します。

```python
candidates = [
    page.get_by_role('button', name='投稿'),
    page.get_by_role('button', name='Post'),
    page.locator('div[role="button"]').filter(has_text='投稿'),
    page.locator('div[role="button"]').filter(has_text='Post'),
]
```

これにより、日本語UI/英語UIどちらでも投稿できるようにしています。

## threads.net と threads.com の違い

実装中に地味に重要だったのが、Threadsのドメインです。

当初は `threads.net` だけを許可していましたが、実際には `threads.com` へリダイレクトされるケースがあります。

そのため、allowed domainsには両方を入れています。

```python
allowed_domains=(
    "threads.net",
    "www.threads.net",
    "threads.com",
    "www.threads.com",
    "instagram.com",
    "www.instagram.com",
    "accountscenter.instagram.com",
)
```

browser-useで `allowed_domains` を使う場合、こうしたリダイレクト先を漏らすと、エージェントが途中で止まります。

SNS自動化では、公式ドメインだけでなく、ログイン、アカウントセンター、リダイレクト先の整理がかなり大事です。

## 実行結果を残す

投稿処理は、成功したかどうかを標準出力だけで判断しないようにしています。

実行ごとに `runs/` 以下へ次の情報を保存します。

- 投稿前スクリーンショット
- 投稿後スクリーンショット
- bodyテキスト
- result JSON

今回のThreads投稿では、次のような結果を得ました。

```json
{
  "ok": true,
  "status": "posted",
  "url": "https://www.threads.com/",
  "out_dir": "/home/kojima/work/ksnsposter/runs/threads_playwright_20260624_172329"
}
```

ここで注意すべき点は、`url` が必ずしも投稿個別URLではないことです。

Threadsの投稿完了後にホーム/フィードへ戻る場合があるため、現時点では「投稿完了画面とスクリーンショットで確認する」実装です。

今後は、投稿後にプロフィールや最新投稿をたどって公開URLを取得する処理を追加すると、より運用しやすくなります。

## 安全設計：勝手に投稿しない

`ksnsposter` は、デフォルトでは最終投稿ボタンを押さない設計です。

```bash
# 下書きまで
./scripts/ksnsposter post --platform threads --text-file /tmp/post.txt --headful

# 実際に投稿
./scripts/ksnsposter post --platform threads --text-file /tmp/post.txt --confirm-post --headful
```

理由は単純で、SNS投稿は間違えると外部に出るからです。

AIエージェントが「できた」と言っても、実際には下書きのまま、ログイン切れ、投稿ボタン未クリック、CAPTCHA停止、文面欠落などがあり得ます。

そのため、状態は次のように分類しています。

- `posted`
- `draft_ready`
- `not_authenticated`
- `verification_required`
- `upload_processing_timeout`
- `failed`

「ブラウザ操作をキューに入れた」だけでは成功扱いしない、というのが大事です。

## 今回の技術的な価値

今回の実装で得られた価値は、Threadsへ1回投稿できたことだけではありません。

重要なのは、次の実運用パターンを確立できたことです。

1. API/OAuthが重いSNSでも、ログイン済みブラウザセッションを使って運用できる
2. browser-useで汎用的なWeb UI操作を組み立てられる
3. 最終投稿のような決定的処理はPlaywrightに逃がせる
4. VNCで人間がログインし、以後は自動化できる
5. Kurage、YouTube、AIxSNS、Threads投稿を同じパイプラインに接続できる

この構成は、Threadsだけでなく、Instagram、TikTokにも広げられます。

もちろん、各プラットフォームのUI変更、CAPTCHA、2FA、アカウント制限には注意が必要です。

それでも、API申請で止まるより、まず人間がログインできるWeb UIを活用して小さく運用を始めるほうが、個人開発や小規模事業では現実的な場面が多いです。

## 今後の拡張

次にやるべきことは、次のあたりです。

- Threads投稿後の個別URL取得
- AIxSNS投稿内容をそのままThreadsへクロスポスト
- Instagram Reels投稿の専用Playwrightルート
- TikTokアップロードの専用Playwrightルート
- kdeck / rqdb4ai からのジョブ実行管理
- 投稿結果をKurage側の履歴に戻す
- 投稿失敗時の再実行キュー

特に、Kurageではすでに動画生成、YouTube投稿、AIxSNS告知までの流れがあります。

そこへ `ksnsposter` を接続すると、動画生成後にSNS告知まで自動化できます。

```text
Kurage動画生成
  -> YouTube Shorts投稿
  -> AIxSNS告知
  -> ksnsposterでThreads/Instagram/TikTokへ投稿
  -> 結果ログ保存
```

## まとめ

Kurage SNS Posterは、APIトークンに依存せず、ログイン済みChromeプロファイルを使ってSNS投稿を自動化するための小さなブラウザ自動化プロダクトです。

今回、Threadsへの実投稿まで到達しました。

実装上のポイントは、browser-useにすべてを任せるのではなく、柔軟な探索やタスク化にはbrowser-useを使い、最終投稿のような再現性が必要な部分はPlaywrightで固めることです。

AI Agent時代のブラウザ自動化は、「AIに全部任せる」よりも、**AIの柔軟さと決定的スクリプトの安定性を組み合わせる**ほうが実運用に向いています。

`ksnsposter` は、そのためのKurage系SNS投稿レイヤーとして育てていきます。
