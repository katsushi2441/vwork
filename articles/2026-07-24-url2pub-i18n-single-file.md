---
title: "1ファイルで多言語化：url2pub を日英対応にしたi18n実装（PHP + Cookie + JS + 生成AI）"
emoji: "🌐"
type: "tech"
topics: ["php", "i18n", "oss", "ai", "web"]
published: true
---

Kurage の OSS「[url2pub](https://url2ai.exbridge.jp/url2pub.php)」（URLを1つ渡すと記事を解析して告知文とブログを書き、5媒体へ自動配信するツール）を日英対応にした。本記事はその **i18n（多言語化）実装の技術解説**。ポイントは2つ:

1. **ファイルを分けずに1ファイルで多言語化した**（`url2pub-en.php` を作らなかった）
2. **UIだけでなく、AIが生成する成果物（告知文・ブログ本文）も言語対応した**

## 1. 設計判断：`url2pub-en.php` に分けない

まず最初の分岐点。「英語版は別ファイルにするか？」

url2pub は見た目のLPだけでなく、実ロジックを持つ（Xログイン、解析→告知文→ブログ→5媒体post のajaxフロー、報酬トークン処理、履歴、管理者ビュー）。これを英語用に複製すると:

- 同じロジックを2本 maintain することになる
- 修正・デザイン変更のたびに2ファイル直す → **必ず片方を直し忘れて日英がドリフトする**

**i18n の境界は「ファイル」ではなく「文字列レイヤー」に置く。** ロジックは1本のまま、文言だけ差し替える。別ファイル化が正当化されるのは「英語版はロジックも構成も別物にしたい」ときだけで、今回は同じツールを言語だけ変えるので分割の利点はゼロ、欠点（二重保守）だけが残る。

## 2. 文言配列 `$T`

全UIテキストを言語別の配列に集約し、実行時に選ぶだけ。

```php
$T_ALL = array(
  'ja' => array(
    'lp_title' => 'Kurageを広める人が、<br>Kurageと一緒に<em>育つ</em>。',
    'form_submit' => 'Kurageさんに配信してもらう',
    // …
  ),
  'en' => array(
    'lp_title' => 'Those who spread Kurage<br>grow <em>together with</em> Kurage.',
    'form_submit' => 'Have Kurage publish it',
    // …
  ),
);
$T = $T_ALL[$lang];
```

出力時、**HTMLを含む文言（`<br>` や `<em>` を持つ見出し）はエスケープせずそのまま**、プレーンテキストは `htmlspecialchars` ラッパ（`u2p_h()`）を通す。

```php
<h2 class="lp-title"><?php echo $T['lp_title']; ?></h2>          <!-- HTML可 -->
<button class="btn"><?php echo u2p_h($T['form_submit']); ?></button> <!-- エスケープ -->
```

## 3. 言語判定と Cookie でのスティッキー化

`?lang=en` / `?lang=ja` で切替、**Cookie に保存**して以降のナビゲーションでも維持する。こうすると内部リンク全部に `?lang=` を付けて回らなくて済む。

```php
$lang = 'ja';
if (isset($_GET['lang'])) {
    $lang = ($_GET['lang'] === 'en') ? 'en' : 'ja';
    setcookie('u2p_lang', $lang, time() + 31536000, '/');
    $_COOKIE['u2p_lang'] = $lang;             // 同一リクエスト内でも即反映
} elseif (isset($_COOKIE['u2p_lang']) && $_COOKIE['u2p_lang'] === 'en') {
    $lang = 'en';
}
```

SEO 用に `hreflang` の alternate も入れておく。

```html
<link rel="alternate" hreflang="ja" href="https://.../url2pub.php?lang=ja">
<link rel="alternate" hreflang="en" href="https://.../url2pub.php?lang=en">
<html lang="<?php echo $lang; ?>">
```

## 4. JS ラベルの多言語化：`json_encode` でそのまま渡す

進捗チェックリスト・エラー・ウォレット接続・コピー通知など、**JS側の文言**もサーバの `$T` から流す。PHP配列を `json_encode` するだけでJSオブジェクトになる。

```php
<script>
var T = <?php echo json_encode($T['js'], JSON_UNESCAPED_UNICODE); ?>;
// …
navigator.clipboard.writeText(text).then(function () { alert(T.copied); });
</script>
```

`JSON_UNESCAPED_UNICODE` を付けないと日本語が `\uXXXX` に化けるので注意（動くが読めない）。進捗ステップ配列もこれで組む:

```js
var STEPS = [
  { key: 'analyze',      label: T.st_analyze },
  { key: 'announcement', label: T.st_announcement },
  // …
];
```

## 5. 本丸：AIが生成する成果物の言語対応

UIを英語にしても、**Kurage（=[url2brain](https://github.com/katsushi2441/url2brain)）が生成する告知文・ブログ本文が日本語のまま**では意味がない。ここが多言語化の本丸だった。

調べると、**url2brain は元々 `language` パラメータ（ja/en）対応済み**だった:

```python
_LANGUAGE_NAME = {"ja": "Japanese", "en": "English"}
# 生成プロンプト内:
f"Write in {lang_name}. Tone: {tone}. Ground every claim in the supplied evidence only …"
```

つまりバグは生成エンジンではなく**呼び出し側**。url2pub の `ajax.php` が生成APIを叩くとき、言語を**ハードコードで `'ja'` に固定**していた。

```php
// Before: 常に日本語
$r = u2p_api('/generate/announcement',
    array('source' => $src, 'language' => 'ja', 'tone' => 'neutral'));
```

**1箇所のハードコードで、パイプライン末端まで全部日本語になっていた。**

修正方針は「**言語をラン（run）単位で固定する**」。解析（analyze）した時点のユーザー言語をセッションの run に保存し、以降の生成でそれを使う:

```php
// 言語はCookie u2p_lang（url2pub.phpが設定）から。runに固定。
$u2p_lang = (isset($_COOKIE['u2p_lang']) && $_COOKIE['u2p_lang'] === 'en') ? 'en' : 'ja';

// analyze時: runに言語を焼き込む
$_SESSION['u2p_run'] = array( /* … */ 'lang' => $u2p_lang );

// generate時: runの言語を渡す（途中で切り替えても1回の生成内で混ざらない）
$lang = isset($run['lang']) ? $run['lang'] : $u2p_lang;
$r = u2p_api('/generate/announcement',
    array('source' => $src, 'language' => $lang, 'tone' => 'neutral'));
```

**リクエスト単位でなく「ラン単位」で固定するのがミソ。** 告知文→ブログの生成中にユーザーが言語トグルを触っても、その1回の成果物は言語が一貫する。

さらに、投稿時にペルソナで枠付けする関数（Kurage / 開発者ペルソナの前置き）も日本語固定だったので `$lang` 引数で日英切替にした。英語本文に日本語の前置きが混ざるのを防ぐ。

```php
function u2p_persona_frame($text, $persona, $kind, $lang = 'ja') {
    $en = ($lang === 'en');
    // kurage / blog:
    return ($en ? "🪼 Hi, I'm Kurage. Let me introduce this today.\n\n"
                : "🪼 Kurageです。今日はこちらをご紹介しますね。\n\n") . $text . " …";
}
```

## まとめ：i18n で効く3つの原則

1. **言語の分岐は「文字列レイヤー」で。** ファイル分割は複製の温床。1コードベース＋実行時言語で保守を1本に保つ。
2. **生成AIの言語はパイプライン末端まで通す。** エンジンが対応していても、**呼び出し層の1箇所のハードコード**で全部が単一言語に落ちる。i18n はエンジンより「配線」の問題であることが多い。
3. **言語はリクエスト単位でなく「ラン単位」で固定。** 複数ステップの生成（解析→告知文→ブログ）で一貫性を担保する。

url2pub は右上のトグルで日本語 / English を切り替えられる。UI・エラー・そして **Kurageが書く記事そのもの**まで、選んだ言語で動く。

---

*本記事は Kurage プロジェクト（株式会社エクスブリッジ）の実装記録です。url2brain / url2pub はいずれもOSS。*
