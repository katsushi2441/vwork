---
title: "Kurage GEOの技術設計：GEO Optimizerを監査エンジンに、日本語AEO採点とグラウンデッドLLM評価を重ねる"
emoji: "🔍"
type: "tech"
topics: [生成ai, seo, oss, python, fastapi]
published: true
---

「AI検索に、見つけてもらえるサイトへ。」——[Kurage GEO](https://kurage.exbridge.jp/kgeo.php)（kgeo）は、WebサイトがChatGPTやAI検索に理解・引用されやすいかを日本語で診断するGEO（Generative Engine Optimization）ワークスペースです。

この記事では、kgeoの開発で行った技術的な判断を解説します。ポイントは3つあります。

1. **監査エンジンはOSSをそのまま使う**（GEO Optimizer Skillをvendorして決定論的監査を実行）
2. **日本語AEOはLLMを使わず正規表現で独立採点する**（再現性とコストのため）
3. **LLM評価は「グラウンデッド・シミュレーション」に限定する**（外部AI検索の実測と混同させない）

- アプリ: https://kurage.exbridge.jp/kgeo.php
- サービス紹介LP: https://kgeo.exbridge.jp/kgeo.html （英語版: https://kgeo.exbridge.jp/ ）
- リポジトリ: https://github.com/katsushi2441/kgeo

## 全体アーキテクチャ

```
ブラウザ
  └─ kgeo.php (Heteml / PHP)
       ├─ X共通ログイン (セッション)
       ├─ CSRF検証 + ルートallowlist
       ├─ 課金ゲート (PayPal / URLAI on Base)
       └─ FastAPI バックエンド (内部トークン + X-KGeo-User)
            ├─ audit_service  … GEO技術監査 + 日本語AEO
            ├─ monitor_service … グラウンデッドLLM評価
            │     ├─ 管理者: RQDB4AI経由 Gemma 4 (192.168.0.14)
            │     └─ 一般: DeepSeek API
            └─ ストレージ (SQLite / Heteml MySQL via kgeo_store.php)
```

フロントは静的HTML+素のJavaScriptで、PHPゲートウェイが認証・CSRF・課金・プロキシだけを担当します。FastAPI側はブラウザから直接触れず、内部トークンと信頼済みユーザーヘッダー（`X-KGeo-User`）でのみ呼び出されます。許可するAPIルートはPHP側で正規表現のallowlistとして明示し、それ以外は404にします。

```php
function kgeo_route_allowed($path, $method) {
    if ($path === '/billing/status') { return $method === 'GET'; }
    if (preg_match('#^/api/sites/[a-f0-9]{12}/audits$#', $path)) {
        return in_array($method, array('GET', 'POST'), true);
    }
    // ...
    return false;
}
```

## 1. 監査エンジン：GEO Optimizer Skillをvendorする

GEOの技術監査（robots.txtのAIクローラー許可、llms.txt、JSON-LD構造化データ、メタ情報、本文構造、更新シグナル、AI発見性、ブランド整合性）は、MITライセンスのOSS [GEO Optimizer Skill](https://github.com/Auriti-Labs/geo-optimizer-skill) の`run_full_audit`をそのまま使っています。Git submoduleで固定コミットをvendorし、`sys.path`に追加してimportする方式です。

```python
VENDOR_SRC = Path(__file__).resolve().parents[1] / "vendor" / "geo-optimizer-skill" / "src"
sys.path.insert(0, str(VENDOR_SRC))

from geo_optimizer.core.audit import run_full_audit
from geo_optimizer.utils.validators import validate_public_url

def run_audit(url: str) -> dict:
    target = validate_target(url)          # 公開URL検証・認証情報入りURL拒否
    result = run_full_audit(target, use_cache=False)
    data = dataclasses.asdict(result)
    data["japanese_aeo"] = analyze_japanese_aeo(response.text, data)  # 独自レイヤー
    return data
```

この監査は**決定論的**です。同じページに同じ結果を返すので、改善前後の差分がそのままスコア差分になります。「LLMに聞いたら今日は点が違った」が起きない、というのが監査基盤としての最重要要件でした。

もう1つの参照OSSである[AiCMO](https://github.com/AICMO/ai-cmo)は、コードを実行せず「企業・競合・監視質問・実行履歴・AI可視性」というプロダクト設計の参照元として使い、必要なデータモデルだけを軽量に再実装しました。両OSSとも公式日本語版ではなく、kgeoはMITライセンスに基づく独立プロダクトです。

## 2. 日本語AEOはLLMを使わず正規表現で採点する

GEO Optimizerの監査は英語圏の慣行が前提のため、日本語ページの「回答エンジンへの答えやすさ（AEO）」は別レイヤーとして独立採点しています。ここで意図的に**LLMを使いませんでした**。

```python
QUESTION_RE = re.compile(
    r"(?:[？?]|とは|なぜ|どうして|どのように|どうやって|いくら|料金|費用|"
    r"おすすめ|選び方|違い|比較|どこ|いつ|誰|何を|何が|できますか|でしょうか)"
)
DEFINITION_RE = re.compile(
    r"(?:とは[、,\s]*|を指します|を指す|のことです|のことをいう|意味します|"
    r"意味する|定義されます|定義される|という(?:手法|方法|仕組み|概念|サービス))"
)
ABSOLUTE_CLAIM_RE = re.compile(
    r"(?:必ず|絶対(?:に)?|完全(?:に)?|確実(?:に)?|唯一|業界初|日本初|世界初|"
    r"日本一|世界一|No\.?\s*1|100[%％]|間違いなく|誰でも)"
)
```

判定項目は7つ——結論先出し、定義文、質問と回答、根拠・出典、日本語の読みやすさ、検索意図カバレッジ（informational / navigational / transactional / commercial）、主張リスク（断定表現の検出、これは低いほど安全）。すべて正規表現とHTML構造の解析で決定論的に採点します。

理由は監査エンジンと同じで、**再現性**です。加えて、1診断200円という価格で全ページ本文をLLMに読ませると原価が合いません。「AI検索に評価されやすい日本語の型」は言語パターンとしてかなり明確に書き下せるので、ここはルールベースが正解でした。

## 3. LLM評価は「グラウンデッド・シミュレーション」に限定する

一方で「このページは実際に質問へ答えられるのか」はルールでは測れないので、ここだけLLMを使います。ただし設計上の一線を引きました。**対象ページの本文だけを根拠（grounding）として渡し、外部知識での補完を禁止する**ことです。

```python
{
    "role": "system",
    "content": (
        "あなたは日本語AEO（回答エンジン最適化）の評価者です。"
        "与えられた対象ページ本文だけを根拠に質問へ回答し、ページが質問へどの程度"
        "答えられるかを評価してください。本文にない事実を補わないでください。"
        "必ずJSONのみを返し、answerability_scoreは0〜100の整数にしてください。"
    ),
}
```

返答はJSONで、回答可能性スコア・本文で確認できた根拠・不足情報・改善案を構造化して保存します。さらに結果画面には必ず「対象ページ本文を与えたLLMシミュレーションであり、外部AI検索での掲載結果ではありません」という注記を出します。ChatGPTの実検索結果を取ってきたかのように見せるのは、このジャンルのツールで一番やってはいけない誤認だと考えているためです。

### LLMプロバイダーの振り分けとGPUキュー

LLMは利用者によって振り分けます。

- **一般ユーザー**: DeepSeek API（従量課金・スケールする）
- **管理者**: ローカルGPUのGemma 4 12B。ただしOllamaを直接叩かず、**RQDB4AIのリソースキュー経由**で実行

ローカルGPU（192.168.0.14）は複数サービスが共有しているため、直接叩くとVRAM競合で共倒れになります。RQDB4AIがホスト別キューで直列化し、kgeoはジョブをenqueueして結果をポーリングするだけです。

```python
def enqueue_payload(messages):
    return {
        "queue": "auto",
        "kwargs": {"messages": messages, "model": config.OLLAMA_MODEL,
                   "temperature": 0.2, "num_predict": 1600},
        "meta": {"resource_key": f"ollama:192.168.0.14:{config.OLLAMA_MODEL}",
                 "source": "web_online", "priority_class": "interactive"},
    }
```

## 4. 課金：成功した診断だけクレジットを消費する

料金はXアカウントごとに初回無料、2回目以降は**1診断200円または20,000 URLAI**（Baseチェーンのプロジェクトトークン）です。実装で重視したのは「失敗した診断に課金しない」ことで、フローはこうなっています。

1. 監査POSTの前に課金ゲートを通す（無料枠 or クレジット残があるか）。なければHTTP 402
2. バックエンドの監査が**2xxで成功した場合だけ**、無料枠の確定またはクレジット消費をコミット
3. PayPalは注文IDをサーバー側で検証、URLAIはBaseチェーン上の送金をオンチェーンで確認してからクレジット付与。まとめて送金された場合は20,000 URLAIごとに1クレジット

```php
$res = kgeo_proxy($method, $path, $session_user, $gate);
// kgeo_proxy内: 2xxのときだけ kgeo_bill_commit($user, $billing_mode)
```

決済手段を「法定通貨200円 = 20,000 URLAI」の統一レートで並べるのは、Kurageエコシステム共通の設計です（[URLAIが使える場所一覧](https://katsushi2441.github.io/vwork/blog/2026-07-29-urlai-where-to-use.html)）。

## 5. UIとi18n：ロジック1本、文言テーブル差し替え

UIは直近でLP系デザイン（Zen Maru Gothic + tealパレット、ダークモード対応）に統一し、日英切替を実装しました。方式はKurageシリーズ共通で、`?lang=en/ja` + Cookieで言語を保持し、PHP側は`$T_ALL['ja'|'en']`の文言テーブル、SPA側は`window.KGEO_LANG`を注入して`data-i18n`属性とJS辞書で差し替えます。条件分岐でHTMLを二重管理せず、**ロジックは1本のまま文言だけ差し替える**のが原則です。

## まとめ

kgeoの設計判断を一言でまとめると「**測れるものは決定論的に測り、LLMは根拠つきの評価にだけ使い、両者を混ぜない**」です。

- 技術監査 = OSS（GEO Optimizer Skill）の決定論的エンジン
- 日本語AEO = 正規表現ベースの独立採点（再現性・原価優先）
- LLM = 対象ページ本文だけを根拠にした回答可能性シミュレーション（注記つき）
- 課金 = 成功した診断だけ消費、200円 / 20,000 URLAIの統一レート

初回診断は無料です。自分のサイトがAI検索にどう見えているか、まず1回測ってみてください。

- アプリ: https://kurage.exbridge.jp/kgeo.php
- サービス紹介: https://kgeo.exbridge.jp/kgeo.html
