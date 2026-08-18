---
title: "スター2.3万のオープンソースCRM「Krayin」に日本語がなかったので、2,066キー全部訳して本家にPRを送った——導入ガイドつき"
emoji: "🗾"
type: "tech"
topics: ["crm", "laravel", "oss", "krayin", "翻訳"]
published: true
---

Salesforceの代替を探していて、オープンソースCRMを調べたら [Krayin](https://github.com/krayin/laravel-crm)（Laravel製・MIT・GitHubスター23,000超）に行き着きました。リード管理のかんばん、顧客台帳、活動記録、見積、ワークフロー自動化——中小企業の営業管理に必要な芯が揃っています。

ひとつだけ問題がありました。**同梱ロケールは英語・スペイン語・ポルトガル語・トルコ語・ペルシャ語・アラビア語・ベトナム語などで、日本語がない。**

ないなら作ればいい、ということで、当社（名古屋のAIシステム開発会社・エクスブリッジ）で言語ファイル一式（4パッケージ・**2,066キー**）を日本語化し、本家にプルリクエストを送りました。この記事はその翻訳の当て方と、Krayinを日本語で動かすまでの導入ガイドです。

- 本家PR: [krayin/laravel-crm#2638 — feat: add Japanese (ja) locale](https://github.com/krayin/laravel-crm/pull/2638)
- マージ前でも使えます（後述の方法で当てられます）

![Krayin リードかんばん（日本語UI）](https://katsushi2441.github.io/vwork/articles/krayin-ja-leads.png)
*日本語化したKrayinのリードかんばん。メニュー・ボタン・空状態まで日本語になる*

## Krayinとは——「顧客台帳・商談・活動・集計」の芯が揃ったCRM

Krayinはインドの[Webkul](https://webkul.com/)社が主導するオープンソースCRMです（ECのBagistoと同じ系譜）。主な機能：

- **リード管理**: パイプライン×ステージのかんばん。停滞日数（Rotten Days）の追跡つき
- **連絡先**: 個人・組織の台帳。カスタム属性を画面から追加できる
- **活動**: 電話・会議・メモ・ファイル・メールをリードや個人に紐づけて時系列表示
- **見積**: 明細・税・値引き・PDF出力
- **自動化**: ワークフロー（条件→アクション）、Webフォーム、Webhook、メールテンプレート
- **ダッシュボード**: 受注/失注金額、ソース別売上など

ライセンスは**MIT**。商用利用・改変・再配布が自由です。技術スタックはLaravel 12 + Vue + MySQL。

## 翻訳で作ったもの

言語ファイルはLaravel標準の配列形式で、4パッケージに分かれています。

| パッケージ | キー数 | 中身 |
|---|---|---|
| Admin | 1,832 | 管理画面の全UI（メニュー・かんばん・見積・設定・エラーページまで） |
| Installer | 223 | インストールウィザード＋初期データ（パイプラインのステージ名など） |
| WebForm / GoogleContact | 11 | Webフォーム・Google連絡先連携 |

翻訳では次を守っています。

- CRMの定番用語で統一（Lead=リード、Quote=見積、Pipeline=パイプライン、Activity=活動、Won/Lost=受注/失注、Rotten=停滞）
- プレースホルダ（`:attribute` `:symbol` `%s` など）とHTML断片はそのまま保持
- 英語版とのキー完全一致（2,066キー・欠落0・余剰0）を検証スクリプトで機械チェック

## 導入手順（PHP 8.3 + MySQL）

実際にやった手順そのままです。今回はDockerで検証しました。

```bash
# 1. 取得（本家マージ後は本家でOK。それまではPRブランチ）
git clone -b feat/japanese-locale https://github.com/katsushi2441/laravel-crm.git krayin
cd krayin

# 2. 依存インストール
composer install

# 3. 環境設定（.envにDB接続とAPP_URLを書く）
cp .env.example .env
php artisan key:generate

# 4. インストール（対話式。ロケールで ja=日本語 を選べる）
php artisan krayin-crm:install
```

Webサーバー（nginx+php-fpmやapache）を`public/`に向ければ完了。開発なら`php artisan serve`でも動きます。

**既存のKrayinに日本語だけ足す場合**は、PRの差分（`packages/Webkul/*/src/Resources/lang/ja/` の4ファイルと`config/app.php`の1行）をコピーするだけです。ビルドは不要で、置けば即反映されます。

## 日本語への切り替え

管理画面にログイン → **環境設定 → 一般 → 言語設定** で「日本語」を選んで保存。メニューからダッシュボード、かんばんの空状態メッセージ、エラーページまで日本語になります。

![Krayin 環境設定の言語選択](https://katsushi2441.github.io/vwork/articles/krayin-ja-config.png)
*環境設定の言語ドロップダウンに「日本語」が追加される*

## ハマりどころ（正直に）

- **初期データの言語はインストール時に決まる。** パイプラインのステージ名（New/Won/Lost…）は言語ファイルではなくDBにシードされるため、英語でインストールした後に日本語へ切り替えても英語のまま残ります（手で直せます）。最初から日本語で使うなら、インストーラーの言語選択で日本語を選ぶのが正解
- **MySQL必須。** SQLiteでは動きません。軽く試すならDockerでMySQLを立てるのが早い
- **PHP 8.3以上。** レンタルサーバーだと満たせない場合があります。VPS向きです
- 本家マージまでは当社フォークのブランチ参照になります。マージされ次第、本家だけで完結します

## 用語対訳（抜粋）

| 英語 | 日本語訳 |
|---|---|
| Lead / Lead Value | リード / リードの見込み金額 |
| Pipeline / Stage | パイプライン / ステージ |
| Won / Lost / Rotten | 受注 / 失注 / 停滞 |
| Quote / Grand Total | 見積 / 総合計 |
| Activity / Participants | 活動 / 参加者 |
| Person / Organization | 個人 / 組織 |
| Sales Owner | 営業担当者 |

## さいごに——どこまでKrayinで、どこから別の道か

Krayinは「Salesforceは過剰、でもCRMは欲しい」という会社に良い選択肢です。一方で、LaravelとMySQLの運用が要るので、**サーバーの面倒を見る人がいない小さな会社には重い**のも事実です。

当社は「顧客台帳・商談メモ・活動履歴・簡単な集計」だけに絞った、レンタルサーバーに置くだけの買い切り業務アプリも作って販売しています。道具選びの相談は無料の窓口（[名古屋AI経営勉強会](https://kurage.exbridge.jp/nagoya-ai-study.php?ref=ossjp)／[Kurage.AIチャット](https://kurage.exbridge.jp/chat.php?ref=ossjp)）へどうぞ。業務システムの選び方の全体像は[業務システムの種類一覧](https://kurage.exbridge.jp/gyomu-system-ichiran.php?ref=ossjp)にまとめてあります。

日本語版Krayinへの質問・翻訳の改善提案は、[PR #2638](https://github.com/krayin/laravel-crm/pull/2638)のコメントか勉強会でお気軽に。
