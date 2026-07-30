---
title: "OpenAlice-JPを公開：AIトレーディングOSSを日本語既定・Docker・HTTPSで安全にセルフホストする"
emoji: "🇯🇵"
type: "tech"
topics: [openalice, aiagent, docker, nginx, fintech]
published: true
---

AIに市場調査やポートフォリオ分析を頼めるOSSは増えています。しかし、日本の利用者が実際にセルフホストしようとすると、英語UI、AIの応答言語、Node.jsのバージョン、認証、HTTPS、そして「誤って実注文を出さないか」という運用上の壁にぶつかります。

そこで、AIトレーディングワークスペースOpenAliceを日本語既定で起動できる **[OpenAlice-JP](https://github.com/katsushi2441/OpenAlice-JP)** を公開しました。

- GitHub: [katsushi2441/OpenAlice-JP](https://github.com/katsushi2441/OpenAlice-JP)
- 稼働デモ: [https://exbridge.ddns.net:18348/](https://exbridge.ddns.net:18348/)
- Upstream: [TraderAlice/OpenAlice](https://github.com/TraderAlice/OpenAlice)

公開デモは管理者トークンで保護されています。ソースコード、Docker構成、日本語対応の差分はGitHubで確認できます。

## OpenAliceは何をするOSSか

OpenAliceは、単体のチャットボットではありません。Claude Code、Codex、OpenCode、PiなどのネイティブなコーディングエージェントCLIを、マーケットデータ、ワークスペース、調査記録、ポートフォリオ、取引承認フローへ接続するローカル環境です。

構成上の重要な特徴は、画面とエージェント実行を担当するAliceと、ブローカー口座・注文・ポジションを担当するUTAが分離されていることです。

```text
ブラウザ
   │ HTTPS
   ▼
nginx :18348
   │ Docker内部HTTP
   ▼
OpenAlice
   ├─ 日本語Web UI
   ├─ Workspace / Session
   ├─ Claude Code / Codex / OpenCode / Pi
   ├─ 市場データ・調査ツール
   └─ UTAクライアント
             │
             ▼
       UTA（口座・注文境界）
```

LLMが直接ブローカーSDKを操作するのではなく、取引状態と書き込み境界を別プロセスへ置く設計です。とはいえ、AIと金融口座を接続する以上、セルフホスト側でも公開範囲と取引モードを明示的に制限する必要があります。

## 「日本語化」ではなく「日本語版として成立させる」

調査したOpenAlice `v0.87.0-beta`には、すでに型付きの日本語辞書 `ui/src/i18n/locales/ja.ts` が含まれていました。したがってOpenAlice-JPでは、既存の成果を無視して全文を再翻訳するのではなく、次の不足を埋めています。

1. UIの初期言語を英語から日本語へ変更
2. ブラウザタイトルと主要ブランド表示を`OpenAlice-JP`へ統一
3. AIの通常回答・分析・確認事項を日本語で返す既定ペルソナを追加
4. 銘柄コード、JSONキー、CLIコマンドなど機械処理する文字列は翻訳しない方針を追加
5. 約定・一部約定・未約定、データ源、取得時刻を日本語回答でも明示する方針を追加

言語の初期値はZustandの永続ストアで変更しています。

```ts
export const useLocaleStore = create<LocaleStore>()(
  persist(
    (set) => ({
      locale: 'ja',
      setLocale: (locale) => set({ locale }),
    }),
    {
      name: 'openalice.locale.v1',
      version: 1,
    },
  ),
)
```

単に翻訳ファイルを追加するだけでは、初回アクセス時は英語のままです。OpenAlice-JPでは未設定時の初期値を`ja`にし、利用者が設定画面で別の言語を選んだ後は、その選択を優先します。

さらに、日本語を既定に変更すると、英語ラベルを固定で期待していた既存UIテストが失敗します。そこで、英語表示を検証するテストは明示的に`i18n.changeLanguage('en')`を実行し、別途「保存済み設定がない場合は日本語で起動する」回帰テストを追加しました。既定言語の変更と、各言語のテスト条件を混同しないためです。

## AIの回答も日本語にする

UIが日本語でも、ワークスペースへ渡す指示が英語だけなら、LLMの回答は安定して日本語になりません。OpenAlice-JPでは既定ペルソナへ、次の運用方針を追加しました。

- 通常の説明、分析、確認事項、最終回答は自然で簡潔な日本語
- API名、注文アクション、JSONキー、CLIコマンドは原文を維持
- 市場データを説明するときはデータ源と取得時刻を明示
- 注文状態は未約定・一部約定・約定を区別

ここで注意したいのは、OpenAlice-JP自体がGemma 4専用ではないことです。DockerイメージにはClaude Code、Codex、OpenCode、Piを固定バージョンで導入していますが、実際に利用するLLMはワークスペースで選択したエージェントとAIプロバイダーで決まります。

Gemma 4を使う場合は、Ollamaなどでモデルを起動し、OpenAI互換APIとしてOpenCodeまたはPiから利用する構成にできます。LLMを製品名へ固定せず、ローカルモデルとクラウドモデルを用途ごとに切り替えられるのがOpenAliceの強みです。

## Node.js 22をDocker内に固定する

OpenAliceの現在の実行要件はNode.js 22系です。ホスト側のNode.jsが古い環境で無理に更新すると、同じサーバーで動いている別サービスへ影響する可能性があります。

OpenAlice-JPではホストのNode.jsを変更せず、Dockerのビルド・実行環境をNode.js 22へ固定しました。イメージのビルド時にはUIのTypeScriptビルド、モノレポの各パッケージ、エージェントCLIの`--version`確認まで実行されます。

```bash
cd /home/kojima/work/OpenAlice-JP
docker compose up -d --build
docker compose ps
```

状態が`healthy`になれば、アプリケーションとHTTPSプロキシの準備が完了です。認証情報、ワークスペース、設定は名前付きDockerボリュームに保存されるため、コンテナを再作成しても維持されます。

## HTTPS以外からOpenAlice本体へ入れない

最初の構成では、OpenAliceのHTTPポートをホストへ直接公開していました。しかし、管理者トークンやワークスペース内容を扱うサービスを、暗号化されていないHTTPで外部公開すべきではありません。

現在のOpenAlice-JPは、次の二つのコンテナに分けています。

```text
Internet
  │ TLS 1.2 / 1.3
  ▼
openalice-jp-https (nginx:18348)
  │ Docker network
  ▼
openalice-jp (HTTP:47331)
```

ホストへ公開するのはnginxの18348番だけです。OpenAlice本体の47331番、MCPゲートウェイ、UTA、コネクターはDocker内部へ限定しています。nginxでは通常のHTTPプロキシだけでなく、WebSocketの`Upgrade`と長時間接続も転送します。

```nginx
location / {
    proxy_pass http://openalice-jp:47331;
    proxy_http_version 1.1;
    proxy_set_header X-Forwarded-Proto https;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;
    proxy_buffering off;
    proxy_read_timeout 3600s;
}
```

証明書はホストのLet's Encrypt証明書を読み取り専用でマウントします。また、Certbotによる更新後の証明書を取り込めるよう、nginxを定期的にreloadする構成にしました。

## まずは`readonly`で起動する

OpenAlice-JPのDocker環境では、取引モードを次のように固定しています。

```yaml
environment:
  OPENALICE_TRADING_MODE: readonly
```

`readonly`ではポートフォリオ分析や市場データの参照はできますが、ブローカー側を変更する注文書き込みを拒否します。AIによる自動発注も既定では無効です。

これは「安全なAIトレードが完成した」という意味ではありません。LLMの判断品質、価格データの遅延、ブローカーAPIの権限、ペーパー口座と実口座の取り違えなど、運用上のリスクは残ります。最初はMockまたはペーパー口座だけで検証し、実口座へ接続する場合も人間の承認と最小権限を維持すべきです。

## テストと実ブラウザで確認したこと

OpenAlice-JPでは、次の確認を実施しました。

- Docker本番イメージのビルド
- 3,000件を超えるモノレポのテスト
- UIとルートプロジェクトのTypeScript検査
- 日本語が初期言語になる回帰テスト
- Docker構成の契約テスト
- nginx設定の構文検査
- Let's Encrypt証明書を検証した公開HTTPSアクセス
- 実ブラウザで日本語ログイン画面とログイン後ダッシュボードを確認
- OpenAlice本体とHTTPSプロキシのヘルスチェック

公開デモは[https://exbridge.ddns.net:18348/](https://exbridge.ddns.net:18348/)で稼働していますが、管理者トークンは公開していません。自分の環境で試す場合は、GitHubからクローンして自分専用のトークンとワークスペースを作成してください。

## OpenAlice-JPを公開した理由

OpenAliceには、日本語辞書、取引境界、複数エージェントCLI、Dockerイメージなど、多くの実装がすでにあります。一方で、日本語利用者が「クローンして、起動して、安全に試す」ところまでには、複数の設定をつなぐ必要があります。

OpenAlice-JPは本家から切り離された別物を目指すのではなく、日本語利用者向けの実行可能なリファレンス環境として公開しました。差分がGitHubで確認できるため、既存のOpenAliceへ日本語既定、HTTPS、読み取り専用運用だけを取り込む際の参考にもできます。

- [OpenAlice-JP GitHubリポジトリ](https://github.com/katsushi2441/OpenAlice-JP)
- [OpenAlice-JP HTTPSデモ](https://exbridge.ddns.net:18348/)

AGPL-3.0のプロジェクトなので、ネットワークサービスとして改変版を提供する場合は、利用者への対応ソース提供条件も確認してください。

## 関連書籍

AI・OSS・生成AIを使った開発をさらに学びたい方は、こちらの書籍も参考にしてください。

[Amazon.co.jpで書籍を見る](https://www.amazon.co.jp/dp/B0HC27BLHG)
