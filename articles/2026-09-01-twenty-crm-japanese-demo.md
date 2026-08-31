---
title: "スター5.5万のSalesforce代替CRM「Twenty」は日本語で使えるか——構築して分かった日本語検索の穴と、触れるデモ"
emoji: "🔍"
type: "tech"
topics: ["crm", "twenty", "oss", "postgresql", "selfhosted"]
published: true
---

Salesforce代替のオープンソースCRMとして今いちばん勢いがあるのが [Twenty](https://github.com/twentyhq/twenty)（TypeScript製・AGPL-3.0・GitHubスター55,000超・Y Combinator S23）です。「日本語で使えるのか」を確かめるために実際に構築したところ、**翻訳は本家が100%完了済みで、立てるだけで日本語UIになりました**。一方で、**日本語の検索には設定では直らない穴がある**ことも実測で分かりました。

この記事は、名古屋のAIシステム開発会社（エクスブリッジ）が実際に構築・計測した記録です。触って確かめられるデモも公開しています。

## 結論から

- **UIの日本語化は不要。** `ja-JP.po` は front / server / emails の3ファイル合計6,160キーが全訳済み（2026-09-01時点・未訳0）。翻訳はCrowdinで管理されており、有志の翻訳PRは受け付けられない体制なので、「日本語化して本家に送る」余地はもう無い
- **docker composeで立てるだけで、ようこそ画面からCRM本体まで日本語で出る**（ブラウザの言語設定がjaなら自動）
- **日本語のグローバル検索には穴がある。** 部分語で会社名を引くと、条件次第でヒットしない（後述・実測）

## 触れるデモ

構築済みのものを公開しています。ログインしてそのまま触れます。

- **https://proto.exbridge.jp/twenty/**
- ログイン: `demo@exbridge.jp` / パスワード: `KurageDemo2026`
- サンプルの会社データと、日本語の会社「株式会社エクスブリッジ」を入れてあります。**後述の検索の穴を自分で再現できます**
- データは毎朝5:20にリセットされます。自由に触ってください

## 構築手順（VPS前提・15分）

Twentyは server / worker / PostgreSQL 16 / Redis の4コンテナ構成です。共有レンタルサーバーでは動きません。メモリは2GB以上を見てください。

```bash
mkdir twenty && cd twenty
curl -sLO https://raw.githubusercontent.com/twentyhq/twenty/main/packages/twenty-docker/docker-compose.yml
curl -sL https://raw.githubusercontent.com/twentyhq/twenty/main/packages/twenty-docker/.env.example -o .env
```

`.env` の要点は4つだけです。

```bash
SERVER_URL=https://あなたの公開URL     # フロントのAPI接続先になる
PG_DATABASE_PASSWORD=強いパスワード
ENCRYPTION_KEY=$(openssl rand -base64 32)
STORAGE_TYPE=local
```

```bash
docker compose up -d
```

初回アクセスで「ワークスペースへようこそ」（日本語）が出れば成功です。メールアドレスとパスワードを登録し、ワークスペースを作ると、サンプルデータ入りのCRMが開きます。

補足を2つ。

- **サブパス配置はできません。** SPAのアセットと画面遷移が全部ドメイン直下の絶対パス（`/assets/...` `/objects/...`）です。`https://example.com/twenty/` のような置き方をするなら、リバースプロキシ側で「実在しないパスを全部Twentyへ回す」構成が要ります（当社のデモはこの方式です）
- **第三者の勝手なサインアップは入りません。** 既存ワークスペースがある状態で他人がメール登録すると `User does not have access to this workspace` で拒否されることを実測で確認しています

## 日本語検索の穴（実測）

ここがこの記事の本題です。

PostgreSQLの全文検索（`to_tsvector('simple', …)`）は、空白で区切られていない日本語をひとかたまりの語彙として扱います。「株式会社エクスブリッジ」はまるごと1語彙になるので、前方一致以外の部分語では引けません。

Twenty本家はこの問題を把握していて、2026年2月に対策を入れています（[PR #18030](https://github.com/twentyhq/twenty/pull/18030)）。**tsvector検索が0件のときだけ、ILIKE（部分一致）で再検索するフォールバック**です。

当社のデモ環境で実測しました。会社「株式会社エクスブリッジ」と、社員「デモ エクスブリッジ」（姓がエクスブリッジ）が入っている状態です。

| 検索語 | 会社がヒットするか |
|---|---|
| 株式会社エクスブリッジ（完全一致） | ○ |
| ブリッジ（途中の語） | ○ フォールバックが効く |
| 会社エクス（途中の語） | ○ 同上 |
| **エクスブリッジ** | **× 出ない** |

なぜ「ブリッジ」で出るのに、より長い「エクスブリッジ」で出ないのか。

**フォールバックは「tsvectorが0件のとき」しか発火しないからです。**「デモ エクスブリッジ」は空白区切りなので「エクスブリッジ」が独立した語彙になっており、tsvector検索が社員1件を返します。1件でも返るとILIKE再検索は走らず、会社は表示されません。

現実の業務データで言うと、こうなります。

> 社員に田中さんがいる会社で「田中」を検索すると、**田中さんは出るが「田中商事」（取引先）は出ない**

姓・名が空白区切りで入る人物データと、空白なしの会社名が混ざるほど起きやすくなります。日本語だけの問題ではなくCJK共通ですが、実務での遭遇率は日本の会社名データが高いはずです。

### 対処

設定では直りません。選択肢は3つです。

1. **運用で回避する**——会社名の完全一致か、短い部分語（「ブリッジ」型）で引く。デモで挙動を体感しておくのが一番早い
2. **PGroongaやpg_bigmを入れて検索列を差し替える**——`searchVector` は `GENERATED ALWAYS ... STORED` の生成列なので、マイグレーションを自前で書く改造になります。アップデートとの衝突を管理する覚悟が要ります
3. **本家へ報告する**——「tsvectorが部分ヒットしたときもILIKEを併走させる」提案。パフォーマンス影響の議論になるはずです（フォールバックが0件時限定なのは速度のため、とコードコメントに明記されています）

当社は1で運用しつつ、この記事の実測を添えて本家に報告する予定です。

## EspoCRM・Krayinとどう選ぶか

当社は同じ用途で [EspoCRM](https://proto.exbridge.jp/espocrm/) と [Krayin](https://proto.exbridge.jp/krayin/admin/login) のデモも公開しています（どちらも `demo` / `demo2026` 系で触れます）。

| | Twenty | EspoCRM | Krayin |
|---|---|---|---|
| GitHubスター | 55,000+ | 4,600+ | 23,000+ |
| 技術 | TypeScript + PostgreSQL + Redis | PHP + MySQL | Laravel + MySQL |
| 動く場所 | VPS必須 | 共有レンタルサーバー可 | 共有レンタルサーバー可 |
| 日本語UI | 本家100%訳済み | 公式収録 | 当社が2,066キー全訳し本家へ提出 |
| 画面の性格 | Notion的・モダン | 業務システム的・機能豊富 | かんばん中心・シンプル |

**月数百円で始めたいならEspoCRMかKrayin、VPSがありモダンなUIとAPI・カスタムオブジェクトが欲しいならTwenty**です。

## まとめ

- Twentyの日本語UIは本家が100%完了。立てるだけで日本語になる
- 日本語検索にはフォールバック抑止の穴がある。「田中」で田中商事が出ない形で実務に出る
- [デモ](https://proto.exbridge.jp/twenty/)で両方確かめられます
- 構築一式（compose・リバースプロキシ・日次リセット）は [twenty-jp](https://github.com/katsushi2441/twenty-jp) に公開しています

自社の業務に合わせた画面・項目・権限のカスタマイズや、既存データの移行を含めた導入は、[バイブOSSカスタマイズ（税込110,000円〜）](https://kurage.exbridge.jp/vibe-oss.html?ref=article-twenty)で承っています。どのCRMを土台にすべきかの相談だけでも構いません。
