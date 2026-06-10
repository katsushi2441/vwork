---
title: "kgrowth：GSCとアクセスログを統合した週次グロース自動化パイプライン"
emoji: "📈"
type: "tech"
topics: ["python", "googleanalytics", "seo", "自動化", "oss"]
published: true
---

# kgrowth：GSCとアクセスログを統合した週次グロース自動化パイプライン

kgrowthは、Google Search Console（GSC）とWebサーバーのアクセスログを統合し、検索流入の分析から改善ジョブの提案・実行まで自動化するPythonパイプラインです。AIxEC / AIxSNS / AIxTubeなどのコンテンツサービスのグロースを自動化するために開発しました。

コードは約1,300行のPythonで書かれており、外部ライブラリへの依存を最小限に抑えた設計になっています。

## アーキテクチャ概要

パイプライン全体の流れは次のとおりです。

```
Google Search Console API
FTP（Webサーバー access.log）
    ↓ fetch
data/gsc_latest.json
data/access_logs/
    ↓ analyze
data/analysis_latest.json
data/improvement_jobs_latest.json
reports/growth_plan_latest.md
    ↓ 実行
kdeck Goal Queue → rqdb4ai → AIxEC / BuzBlogger / AIxTube
```

CLIは4つのサブコマンドで構成されています。

```bash
python3 -m kgrowth.cli fetch-gsc    # GSCデータ取得
python3 -m kgrowth.cli fetch-logs   # アクセスログFTP取得
python3 -m kgrowth.cli analyze      # 分析・レポート生成
python3 -m kgrowth.cli weekly       # 上記をまとめて実行
```

常駐運用はsystemdユーザーサービス（`kgrowth-hermes-commander.service`）として動かしています。

## GSC認証：標準ライブラリだけでJWT署名する

GSCのService Account認証で、`google-auth`などのライブラリを使わずに実装した点が特徴です。

JWT（RS256）の生成は次のように行っています。

```python
def _sign_rs256(private_key: str, signing_input: str) -> bytes:
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
    except Exception:
        # cryptographyがない場合はopenssl CLIにフォールバック
        with tempfile.NamedTemporaryFile("w", delete=True) as key_file:
            key_file.write(private_key)
            key_file.flush()
            proc = subprocess.run(
                ["openssl", "dgst", "-sha256", "-sign", key_file.name],
                input=signing_input.encode("utf-8"),
                stdout=subprocess.PIPE,
            )
        return proc.stdout
    key = serialization.load_pem_private_key(private_key.encode("utf-8"), password=None)
    return key.sign(signing_input.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
```

`cryptography`がインストールされていれば使い、なければ`openssl dgst`コマンドにフォールバックします。これにより、環境に応じて依存ライブラリなしでも動作します。

認証モードは設定ファイルで切り替えられます。

```json
{ "gsc_auth": "service_account" }  // デフォルト
{ "gsc_auth": "gcloud" }           // gcloud CLIのADCを使う
```

GSCのsearchAnalytics APIは25,000行/リクエストの上限があるため、`startRow`を使ったページネーションで全データを取得しています。

## アクセスログ解析：2種類のフォーマットに対応

サーバーのアクセスログには、Apache Combined Log形式とsimpletrack独自形式の2種類があります。

```python
# Apache Combined Log
LOG_RE = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>[^"]*?) (?P<proto>[^"]*)" '
    r'(?P<status>\d{3}) (?P<bytes>\S+) "(?P<referer>[^"]*)" "(?P<ua>[^"]*)"'
)

# simpletrack形式（パイプ区切り）
# 2026-01-01 12:00:00|1.2.3.4|https://example.com/path|https://referer.com|UA文字列
if "|" in line and line[:4].isdigit():
    parts = line.rstrip("\n").split("|", 4)
```

行頭が数字4文字かつパイプ区切りならsimpletrack形式、そうでなければ正規表現でApache形式として解析しています。

### ボット除外

ボット判定は50以上のUserAgent文字列との部分一致で行っています。

```python
BOT_WORDS = (
    "bot", "crawler", "spider", "curl", "wget", "python",
    "googlebot", "bingbot", "gptbot", "claudebot", "ccbot",
    ...
)

def is_bot_ua(ua: str) -> bool:
    ua = ua.lower().strip()
    if not ua:
        return True
    return any(word in ua for word in BOT_WORDS)
```

### アフィリエイトクリック追跡

`/go.php`へのリクエストを追跡し、実クリック（likely_human）とrawクリック（ボット除外後）を分けて集計します。

```python
def _track_go_click(parsed, referer, ...):
    quality = first("click_quality").lower()
    likely_human = quality == "likely_human"
    if not quality:
        likely_human = bool(referer)  # refererがあれば人間と判定
```

`click_quality=likely_human`が明示されているか、Refererが存在する場合に実クリックとして計上します。商品ごとに`pid`・`jan`・`asin`・`model`・`keyword`でキーを構成し、どのページから何がクリックされたかを記録します。

## GSC分析：CTRベンチマークで改善候補を特定する

GSCデータの分析では、位置別の期待CTRとの乖離を使って改善候補クエリを抽出しています。

```python
def expected_ctr(pos: float) -> float:
    if pos <= 1:  return 0.28
    if pos <= 2:  return 0.15
    if pos <= 3:  return 0.10
    if pos <= 5:  return 0.06
    if pos <= 10: return 0.025
    return 0.005

# 検索順位10位以内で、期待CTRの50%未満ならタイトル改善候補
if entry["pos"] <= 10 and entry["imp"] >= title_min and entry["ctr"] < expected_ctr(entry["pos"]) * 0.5:
    title_fixes.append(...)

# 11〜30位で表示回数があれば、コンテンツ強化候補
if 10 < entry["pos"] <= 30 and entry["imp"] >= boost_min:
    boost_queries.append(...)
```

クエリをトークナイズしてクラスタリングし、複数クエリにまたがるテーマ語を抽出してハブ記事の候補にする機能もあります。

```python
def tokenize(query: str) -> list[str]:
    parts = re.split(r"[\s　]+", query.strip())
    tokens = []
    for part in parts:
        if len(part) >= 2:
            tokens.append(part)
        if re.match(r"^[A-Za-z0-9-]{4,}$", part):
            tokens.append(part.upper())  # 英数字は大文字正規化
    return tokens
```

## 改善ジョブ：SHA1で内容一致型IDを生成する

分析結果から生成する改善ジョブは、ジョブの種別とペイロードからSHA1ハッシュでIDを生成します。

```python
def _job_id(kind: str, payload: dict) -> str:
    raw = json.dumps({"kind": kind, "payload": payload}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]
```

同じ内容のジョブは常に同じIDになるため、重複提案の検出がシンプルに行えます。

生成されるジョブの種類は現在4種類です。

| kind | 目的 | target_app |
|---|---|---|
| `search_query_answer_article` | 11〜30位クエリへの回答記事 | aixec |
| `affiliate_product_article` | 実クリック商品の記事化 | aixec |
| `amazon_hub_article` | クエリクラスタからハブ記事 | aixec |
| `buzblogger_search_intent` | BuzBlogger生成仕様の調整 | buzblogger |

各ジョブには`success_rule`（完了条件）、`cooldown_minutes`、`max_attempts_per_day`が設定されており、kdeck Goal Queueが管理します。

```json
{
  "id": "a3f2b1c9d4e5f678",
  "kind": "search_query_answer_article",
  "title": "検索意図回答記事を作る: python おすすめ 本",
  "priority": 10,
  "status": "proposed",
  "target_app": "aixec",
  "action": "enqueue:search_query_answer_article",
  "payload": {
    "query": "python おすすめ 本",
    "position": 14.3,
    "impressions": 420,
    "preferred_affiliate": "amazon"
  },
  "cooldown_minutes": 120,
  "max_attempts_per_day": 1
}
```

## FTPログ取得：タイムスタンプ付きスナップショット管理

Webサーバーのアクセスログは`ftplib`で定期的にダウンロードします。ファイル名にはダウンロード時刻のタイムスタンプを付加します。

```
data/access_logs/20260610_095935_web__aixec_exbridge_jp__access.log
```

`parse_mode: latest_snapshot`（デフォルト）では、同じ時刻プレフィックスを持つ最新セットのみを解析対象にします。これにより、複数回ダウンロードした場合でも重複カウントを防ぎます。

FTPの認証情報は環境変数、設定ファイル、既存ヘルパーファイルの優先順位で解決します。機密情報をリポジトリにコミットしない設計です。

## レポート生成

週次レポートはMarkdownで生成し、`reports/growth_plan_latest.md`に保存します。内容は次のセクションで構成されます。

- Context（GSC集計値・アクセスログ集計値）
- 改善1: BuzBlogger検索クエリ対応（優先度最高）
- 改善2: 重複ページのnoindex
- 改善3: ハブ記事候補一覧
- 改善4: AIxTube動画の外部配信候補
- アフィリエイト実クリック集計
- アクセスログ詳細（ページタイプ・404上位）
- 今週の実行順と次週の比較観点

## まとめ

kgrowthの設計で意図したのは次の点です。

- **外部ライブラリ依存を最小化**：標準ライブラリだけで動くため、サーバー環境の制約を受けにくい
- **2種類のログ形式に透過的に対応**：simpletrackとApache Combined Logを同一パーサーで処理
- **実クリックとbotを分離**：SEO指標とアフィリエイト成果の両方を正確に把握する
- **内容一致型ジョブID**：同じ分析結果から同じジョブIDが生成されるため、重複管理がシンプル
- **提案と実行の分離**：kgrowthはジョブを提案するだけで、実行はkdeck + rqdb4aiが担う

週次で分析・提案を自動化し、人間はジョブ承認と結果評価に集中できる構成を目指しています。

ソースは `/home/kojima/work/kgrowth` にあります。AIxEC / AIxSNSなど複数サービスの成長改善に継続運用中です。
