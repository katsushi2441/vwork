---
title: "Payload CMSを業務OSSカタログにした――Kurage Payload CMSのSEO・AEO・GEO設計"
emoji: "🪼"
type: "tech"
topics: [payloadcms, cms, seo, oss, nextjs]
published: true
---

企業で使えるOSSを調査しても、記事が増えるほど「用途、ライセンス、日本語対応、公式情報、デモ、導入手順書」が別々の場所へ散らばります。検索できる一覧がなければ、せっかく蓄積したOSS情報も再利用しにくくなります。

そこで、オープンソースの **Payload CMS** を管理基盤に使い、業務OSSを検索・比較できる **Kurage Payload CMS** を構築しました。

- 公開サイト: [Kurage Payload CMS・業務OSSカタログ](https://kurage.exbridge.jp/oss/)
- Payload CMS紹介ページ: [Payload CMSの技術・ライセンス・活用方法](https://kurage.exbridge.jp/oss/payload-cms/)
- OSSカスタマイズ: [Kurage バイブOSSカスタマイズ](https://kurage.exbridge.jp/vibe-oss.html?ref=vwork-payload)

現在は46件・17カテゴリのOSSを掲載しています。そのうち27件は、株式会社エクスブリッジがこれまで開発し、GitHubで公開してきた自作OSSです。

この記事では、Payload CMSを選んだ理由、共用レンタルサーバーへ静的公開する構成、SEO・AEO・GEOを同じデータから生成する方法、そしてOSS紹介を自社サービスへつなげる設計を解説します。

## Payload CMSとは

[Payload CMS](https://payloadcms.com/docs/getting-started/what-is-payload)は、Next.jsとTypeScriptを中心に構築されたオープンソースのフルスタックフレームワークです。設定したデータ構造から、管理画面、認証、アクセス制御、REST API、GraphQL APIなどを生成できます。

[公式GitHubリポジトリ](https://github.com/payloadcms/payload)はMITライセンスで公開され、2026年8月22日時点で約4.4万スターを集めています。

公式ドキュメントによると、データベースはアダプター方式で、MongoDB、PostgreSQL、SQLiteを正式にサポートしています。Kurage Payload CMSでは、公開情報を扱う小規模なカタログで、単一ファイルとして管理しやすいためSQLiteを選びました。

採用した主なバージョンは次のとおりです。

| 要素 | 採用構成 |
|---|---|
| Payload CMS | 3.88.0 |
| Next.js | 16.3.0 |
| React | 19.2.6 |
| データベース | SQLite + `@payloadcms/db-sqlite` |
| エディター | Lexical |
| 公開方式 | 静的HTML生成＋FTP同期 |

## OSS情報を一つのCollectionへ集約する

Kurage Payload CMSでは、`oss-projects` CollectionにOSS選定で必要になる情報を集約しました。

```ts
export const OSSProjects: CollectionConfig = {
  slug: 'oss-projects',
  access: { read: () => true },
  fields: [
    { name: 'name', type: 'text', required: true },
    { name: 'slug', type: 'text', required: true, unique: true, index: true },
    { name: 'category', type: 'select', required: true },
    { name: 'summary', type: 'textarea', required: true },
    { name: 'description', type: 'textarea', required: true },
    { name: 'license', type: 'text', required: true },
    { name: 'japaneseStatus', type: 'text', required: true },
    { name: 'officialUrl', type: 'text', required: true },
    { name: 'githubUrl', type: 'text' },
    { name: 'lpUrl', type: 'text' },
    { name: 'brainUrl', type: 'text' },
    { name: 'demoUrl', type: 'text' },
    { name: 'useCases', type: 'array', required: true },
    { name: 'keywords', type: 'array', required: true },
    { name: 'faqs', type: 'array', required: true },
  ],
}
```

OSS名と説明だけではなく、次の導線を同じレコードで管理することが重要です。

- 公式サイトとGitHub
- ライセンスと日本語対応状況
- Kurage側の製品・紹介LP
- 動作を確認できるデモ
- Brainで公開した構築手順書
- 検索キーワードとよくある質問

これにより、一覧、詳細ページ、検索、構造化データ、サイトマップ、サービス案内を別々に手修正する必要がなくなります。

## Payload CMSを公開サーバーで常時動かさない

公開先の `kurage.exbridge.jp` は共用レンタルサーバーです。Node.jsの常駐プロセスを前提にしたPayload CMS本体を、そのまま動かす構成にはしていません。

管理と公開を次のように分離しました。

```text
Payload CMS管理画面
  + SQLite
       |
       | seed / export
       v
静的HTML生成
  + OSS一覧
  + OSSごとの詳細ページ
  + catalog.json
  + sitemap.xml
  + feed.xml
  + llms.txt
       |
       | sync / FTP
       v
https://kurage.exbridge.jp/oss/
```

Payload CMSは、データ入力、スキーマ、型、管理画面を担当します。公開側は静的HTMLなので、PHPやNode.jsのAPIが停止してもOSS紹介ページを表示できます。

この構成には次の利点があります。

- HTML本文を検索エンジンが最初から取得できる
- JavaScriptが無効でも全OSSを閲覧できる
- ページ表示のたびにデータベースへ問い合わせない
- 共用サーバーでも公開できる
- CMSの管理画面をインターネットへ公開しなくてよい

一覧の検索とカテゴリ絞り込みにはJavaScriptを使いますが、カード本文自体は静的HTMLへ出力しています。JavaScriptは検索補助であり、コンテンツ表示の前提ではありません。

## SEOは一覧と詳細ページを分けて設計する

SEOでは、一覧ページだけで全OSSを狙わず、OSSごとの詳細URLを生成しました。

```text
/oss/                 OSS一覧
/oss/payload-cms/     Payload CMS
/oss/frappe-helpdesk/ Frappe Helpdesk
/oss/plane/           Plane
```

各ページには、次を出力しています。

- OSS名を含む固有の`title`と`description`
- 正規URLを示す`canonical`
- OGPとTwitter Card
- 用途、ライセンス、日本語対応、公式情報を含む本文
- 一覧へ戻るパンくず
- 関連OSSへの内部リンク
- 製品LP、デモ、Brain手順書へのリンク

構造化データは、一覧では`ItemList`、`Service`、`FAQPage`を使い、詳細ページでは`SoftwareApplication`、`Service`、`FAQPage`、`BreadcrumbList`を生成しています。

さらに、Google Analytics 4と独自の`simpletrack.php`を併用し、検索流入とページ単位の参照を確認できるようにしました。

## AEOは「質問の直後に答えを書く」

AEOでは、JSON-LDだけに回答を入れても不十分です。読者が見える本文にも、同じ問いと答えを表示する必要があります。

Kurage Payload CMSの一覧ページには、次の直接回答を置きました。

> OSSのバイブコーディング・カスタマイズとは、完成済みのオープンソースソフトウェアを土台に、AIエージェントと対話しながら、自社の業務に必要な変更を実装することです。

その後に、日本語化、画面、項目、権限、通知、外部連携、サーバー導入という具体例を続けています。

詳細ページでも、「このOSSは何か」「どのような用途に向くか」「日本語で使えるか」「自社向けにカスタマイズできるか」という質問へ、ページ内の情報だけで答えられる構成にしました。

## GEOは根拠と運営主体を機械可読にする

生成AIから参照されるためのGEOでは、キーワードを増やすだけでなく、情報の根拠と関係性を明確にします。

Kurage Payload CMSでは、次の情報を揃えました。

- 公式サイト、GitHub、ライセンスへの外部リンク
- 株式会社エクスブリッジが提供するサービスとの関係
- `SoftwareApplication`や`Service`による構造化
- AIクローラー向けの`llms.txt`
- 検索エンジン向けの`sitemap.xml`
- 更新を購読できる`feed.xml`
- 本文に表示するFAQと`FAQPage`の一致

`llms.txt`にはOSSカタログだけでなく、OSSカスタマイズサービスのURLと役割も記載しています。AIが個別OSSの説明を読むときに、「このサイトが何を提供し、誰が運営しているか」まで追える状態を目指しました。

## 生成後に決定論的な検査を行う

静的ページを生成できても、URLや構造化データが欠けていれば公開品質には届きません。そこで、生成後の検査をコードにしました。

```ts
if (!index.includes('ItemList') ||
    !index.includes('Service') ||
    !index.includes('FAQPage')) {
  throw new Error('Index SEO, AEO or GEO data is incomplete')
}

if (!html.includes('SoftwareApplication') ||
    !html.includes('BreadcrumbList')) {
  throw new Error(`${item.slug}: structured data is incomplete`)
}
```

検査対象には次も含めています。

- OSSスラッグの重複
- すべての詳細ページのcanonical
- Vibe OSSへのCTA
- Brain URLがある場合だけ表示される手順書リンク
- GA4とsimpletrack.php
- sitemap、feed、llms.txt

今回登録した自作OSSの公開LPについては、Playwrightで27件すべてを開き、OSSカタログとVibe OSSの2つの導線が表示されることも確認しました。

## OSS紹介を自社サービスへつなげる

OSSカタログの目的は、ページビューを増やすことだけではありません。

OSSを探している企業には、大きく二つのニーズがあります。

### 既存OSSを自社仕様へ変えたい

[Kurage バイブOSSカスタマイズ](https://kurage.exbridge.jp/vibe-oss.html?ref=vwork-payload)では、既存OSSを土台に、日本語化、項目、権限、通知、外部連携を変更し、サーバー導入と稼働確認まで行います。

OSS詳細ページから製品LPや標準デモを確認できるため、実物を見てから必要な変更を相談できます。

### OSSでは足りず、新しい仕組みを作りたい

既存OSSを選ぶ段階ではなく、独自業務から新しいシステムを設計したい場合は、[バイブプロトタイプ制作](https://kurage.exbridge.jp/vibe-prototype.html?ref=vwork-payload)へつなぎます。

Vibe OSSは「既存OSSが仕様と土台」、バイブプロトタイプは「設計書から新しいシステムの土台を作る」という違いがあります。この二つを分けることで、既存OSSで十分な企業へ不要な新規開発を勧めずに済みます。

また、[AIKnowledgeCMSのOSS紹介](https://aiknowledgecms.exbridge.jp/oss.php)で調査記事を読み、Kurage Payload CMSで比較し、製品LPやBrain手順書で導入方法を確認し、必要ならカスタマイズを相談する、という導線も作りました。

```text
OSS紹介記事
  -> Kurage Payload CMSで比較
  -> OSS詳細 / 製品LP / デモ / Brain手順書
  -> Vibe OSSでカスタマイズ・導入
  -> 独自開発が必要ならバイブプロトタイプ
```

## Payload CMSは「紹介して終わらない」カタログに向いている

Payload CMSを採用した価値は、きれいな一覧を作れたことだけではありません。

- Collectionを変えれば管理画面と型を同時に育てられる
- OSS情報とサービス導線を同じデータで管理できる
- Next.jsの管理基盤と静的HTML公開を分離できる
- SEO、AEO、GEO用の出力を一つの生成処理へ集約できる
- 自作OSSと外部OSSを同じ基準で比較できる

OSSを紹介するだけなら、Markdownや表計算でも始められます。しかし、数が増え、詳細ページ、ライセンス、デモ、手順書、サービス導線まで管理するなら、型を持つCMSが有効です。

Kurage Payload CMSは、これまで調査・開発してきたOSS資産を検索コンテンツへ変え、さらに企業の業務システム導入へつなげるための基盤になりました。

- [Kurage Payload CMSで業務OSSを探す](https://kurage.exbridge.jp/oss/)
- [Payload CMSの詳細を見る](https://kurage.exbridge.jp/oss/payload-cms/)
- [OSSをバイブコーディングで自社仕様へ変更する](https://kurage.exbridge.jp/vibe-oss.html?ref=vwork-payload)
- [独自システムのバイブプロトタイプを作る](https://kurage.exbridge.jp/vibe-prototype.html?ref=vwork-payload)
