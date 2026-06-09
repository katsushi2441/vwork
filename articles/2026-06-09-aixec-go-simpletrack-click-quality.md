---
title: "AIxEC go.phpとsimpletrack.phpでAmazonクリックをrawと実クリックに分けた"
emoji: "🧭"
type: "tech"
topics: ["php", "analytics", "affiliate", "amazon", "tracking"]
published: true
---

# AIxEC go.phpとsimpletrack.phpでAmazonクリックをrawと実クリックに分けた

AIxECの商品ページでは、Amazonや楽天への外部遷移を `go.php` 経由にしています。

目的は、商品ページからどの外部ECへ送客できているかを `simpletrack.php` の簡易アクセス解析で見ることです。

しかし今回、`go.php` 側のログではAmazon遷移が直近24時間で100件以上あるのに、Amazonアソシエイト側では1件程度しかクリックとして見えていない、というズレが出ました。

最初に疑ったのは、`go.php` のリダイレクト処理でAmazonアソシエイトタグが消えている可能性です。

実際に `Location:` ヘッダーを確認すると、Amazonへの遷移先には次のようにタグが残っていました。

```text
https://www.amazon.co.jp/...&tag=bittensorman-22
```

つまり、問題はAmazonタグではありませんでした。

問題は、AIxEC側のアクセス解析が「Amazonに飛ばしたリクエスト」をそのままクリックとして数えていたことです。Amazonアソシエイト側は、bot、プレビュー、無効な連続アクセス、参照元のない自動アクセスを除外します。そのため、こちらのrawログとAmazon側の有効クリックが大きくズレていました。

---

## 起きていたこと

直近24時間のログでは、`go.php -> Amazon` が100件以上ありました。

ただし中身を見ると、ほとんどが次のようなアクセスでした。

- `Referer` が空
- `from` パラメータだけが付いている
- User-Agent は一見ブラウザ風だが、毎回ばらばら
- サイト内ページ閲覧の直後にクリックした痕跡がない

この状態で `go.php` が全部をクリックとして記録すると、ダッシュボード上は「Amazon 107クリック」のように見えます。

一方で、Amazonアソシエイト側が実クリックとして認識するのは、人間のブラウザ操作に近い1件だけでした。

この差分を潰すために、AIxEC側のクリック集計を次の2種類に分けました。

```text
raw
  go.phpに来た外部遷移リクエストの総数

likely_human
  人間のクリックである可能性が高いもの
```

ダッシュボードでは、`Amazon 実クリック / raw` のように表示します。

---

## go.phpでクリック品質を付ける

`go.php` は外部ECへ302リダイレクトする前に、`simpletrack.php` へ内部記録を送ります。

今回、ここに `click_quality` と `click_signal` を追加しました。

```php
$seen_cookie = go_recent_seen_cookie();
$valid_ref = go_valid_referrer($ref);

$click_url .= (strpos($click_url, '?') === false ? '?' : '&')
    . 'click=' . rawurlencode($to)
    . '&product_id=' . rawurlencode($pid)
    . '&model_number=' . rawurlencode($model)
    . '&jan=' . rawurlencode($jan)
    . '&asin=' . rawurlencode($asin)
    . '&from=' . rawurlencode($from)
    . '&click_quality=' . rawurlencode(($valid_ref || $seen_cookie) ? 'likely_human' : 'raw')
    . '&click_signal=' . rawurlencode($valid_ref ? 'referrer' : ($seen_cookie ? 'seen_cookie' : 'none'));
```

判定はシンプルです。

- `Referer` が `aixec.exbridge.jp` または `*.exbridge.jp` なら `likely_human`
- 直近24時間以内にサイト閲覧Cookieがあれば `likely_human`
- どちらもなければ `raw`

`from=` だけで来たアクセスは、呼び出し元情報としては残します。ただし、それだけでは実クリック扱いにしません。

---

## simpletrack.phpで閲覧Cookieを発行する

`simpletrack.php` は各ページからJavaScriptとして呼ばれます。

そこで、通常のページ閲覧時に `aixec_st_seen` Cookieを発行するようにしました。

```php
function st_set_seen_cookie(){
    $secure = (!empty($_SERVER["HTTPS"]) && $_SERVER["HTTPS"] !== "off");
    $cookie = "aixec_st_seen=" . time()
        . "; Path=/; Max-Age=2592000; SameSite=Lax"
        . ($secure ? "; Secure" : "")
        . "; HttpOnly";
    header("Set-Cookie: " . $cookie, false);
}
```

`go.php` 側ではこのCookieの時刻を見て、直近24時間以内の閲覧履歴があるかを確認します。

これで、Refererがブラウザや環境によって落ちた場合でも、サイトを見たあとにクリックした可能性があるアクセスを実クリック候補にできます。

---

## ダッシュボードは実クリックとrawを並べる

`simpletrack.php?dashboard=1` では、従来の `clicks` だけではなく `raw_clicks` も持つようにしました。

```php
$go_from_count[$from_key]["raw_clicks"]++;
if($is_likely_human_click) $go_from_count[$from_key]["clicks"]++;
```

商品別集計も同じです。

```php
$go_product_count[$key]["raw_clicks"]++;
if($is_likely_human_click) $go_product_count[$key]["clicks"]++;
```

トップ表示も次のように変えました。

```text
Amazon 実クリック / raw
楽天 実クリック / raw
```

今回の修正後、直近24時間の表示は次のような見え方になりました。

```text
Amazon: 2 / 104
楽天: 0 / 94
```

この表示なら、内部的に `go.php` が何回呼ばれたかと、広告側のクリックに近い数字がどれかを分けて読めます。

---

## アフィリエイト計測で重要なのは「同じ定義で見る」こと

自前のアクセス解析は、ログに来たものを全部数えられます。

一方で、Amazonアソシエイトや楽天アフィリエイトは、広告ネットワーク側のルールで有効クリックだけを数えます。

この2つを同じ「クリック」と呼ぶと、運用判断を間違えます。

今回の修正で、AIxECでは次のように見ることにしました。

- rawは異常検知用
- 実クリックは送客評価用
- Amazonや楽天の管理画面と比較するのは実クリック
- rawが急増して実クリックが増えない場合はbotや自動アクセスを疑う

小さなPHPの修正ですが、ECやアフィリエイトの運用では重要です。

アクセス解析は、数字を増やすためではなく、現実に近い判断をするためにあります。

今回の `go.php` と `simpletrack.php` の修正は、そのための一歩です。
