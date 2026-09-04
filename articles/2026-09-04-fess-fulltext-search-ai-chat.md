---
title: "NamazuからFessへ——日本発の全文検索OSS「Fess」をdockerで立てて45本のPDFを索引し、ローカルLLMで「聞けば答える」を10問で実測（検索10/10・回答9/10）"
emoji: "🔎"
type: "tech"
topics: ["fess", "namazu", "全文検索", "rag", "oss"]
published: true
title_hatena: "ベクトルDB無しで社内PDFに答えるAI——全文検索OSS Fess＋ローカルLLMを10問で実測した記録"
title_blogger: "Namazuの後継にFessを立てて、AIチャットに接いでみた"
---

数万件の技術資料PDFを Namazu で全文検索し、AIチャットが答える仕組みを当社は実用化しています（[開発実績の記事](https://katsushi2441.github.io/vwork/blog/2026-09-04-namazu-ai-chat-knowledge.html)）。Namazu は枯れていて安定していますが、これから新しく立てる会社には「後継は何か」と聞かれます。答えは **Fess** です。日本発（CodeLibs）、Apache-2.0、OpenSearch を土台にした全文検索サーバーで、管理画面・ドキュメントとも日本語があります。

この記事では、Fess を docker で立て、当社の技術記事45本をPDFにして索引し、ローカルLLM（gemma4）を回答役にして「聞けば答える」を10問で実測しました。結論を先に書きます。

- **索引**: 45本のPDF（16MB）を約40秒で索引。検索は 7〜31ms
- **AI回答**: 10問中、正解のPDFが上位5件に入ったのは **10/10**、答えに正解の数値や語が含まれたのは **9/10**
- 最初は 4/10 でした。改善したのは LLM でも検索でもなく、**「検索で当てたファイルの本文から該当箇所を切り出して渡す」**という Namazu 方式の作り込みです
- 立てる途中で3つの罠を踏みました（管理APIの作成が PUT でなく POST、ファイルクロールの含めるパスにディレクトリが要る、権限を入れないと検索に出ない）。後述します

## 構成

- Fess 15.8.0 ＋ OpenSearch（公式 docker-fess の compose を1本にまとめ、ポートを変更、検索対象の `docs/` を読み取り専用でマウント）
- 検索対象: 当社の技術記事45本を Chrome のヘッドレスでPDF化（日本語本文のあるPDF＝Namazu の案件と同じ条件）
- 回答役: ローカルの Ollama（gemma4 12B、`think: false`）
- 接続: 質問 → LLM が検索語を3パターン生成 → Fess の検索API → 上位5件 → **各PDFの本文から検索語の周辺を切り出し**（pdftotext）→ LLM が出典番号つきで回答。根拠が無ければ「資料に記載がありません」と答える

## 立て方（docker）

OpenSearch のために、ホスト側で先に1つ設定が要ります。

```bash
sudo sysctl -w vm.max_map_count=262144
```

compose は公式の `compose.yaml` と `compose-opensearch3.yaml` をそのまま使えます。当社は2本を1本にまとめ、`fess01` のポートを `127.0.0.1:18371:8080` に、`./docs:/opt/fess/docs:ro` を足しました。`docker compose up -d` で、両コンテナが healthy になるまで約2分でした。

管理画面は `/login/`（初期は admin / admin）。管理APIを使うには、管理画面の「システム → アクセストークン」で `{role}admin-api` の権限を持つトークンを作ります。

## 踏んだ罠3つ

**1. 管理APIの「作成」は POST**。公式の解説記事（13系）では `PUT /api/admin/fileconfig/setting` で作成していますが、15.8 では PUT が更新で、作成は POST です。PUT で作ろうとすると「ID is required. Version No is required.」が返ります。ジョブの即時実行は `PUT /api/admin/scheduler/{id}/start` でした。

**2. ファイルクロールの「含めるパス」にディレクトリも入れる**。`.*\.pdf$` だけにすると、出発点のディレクトリ自体が除外されて中を辿れず、クロールは「完了」するのに索引が0件になります。`file:/opt/fess/docs/.*` のように配下全部を含めて解決しました。

**3. 権限を入れないと検索に出ない**。管理APIで作ったクロール設定は「権限」が空になり、索引された文書に役割が付かず、匿名の検索では1件も出ません（管理画面の一覧には30件見えるのに）。設定の権限に `{role}guest` を入れて再クロールすると出るようになりました。管理画面から作れば既定で入る項目なので、APIで作るときだけ踏む罠です。

もう1つ、検索APIの場所も変わっていました。15.8 では `/json/` と `/api/v1/documents` は無く、**`/api/v2/search?q=`** です。

## 実測1: 索引と検索

| 項目 | 実測 |
|---|---|
| 索引対象 | PDF 45本（16MB・日本語の技術記事） |
| クロール〜索引完了 | 約40秒（2スレッド） |
| 検索の応答（`/api/v2/search`） | 7〜31ms |
| 「Vikunja」「Zammad Weblate」「商圏 到達圏」など9語の検索 | 9語すべてで正しい記事が1位 |

Namazu と同じく、専門用語や製品名のような固有の語はキーワード検索で確実に当たります。

## 実測2: AIに10問聞く

記事に答えが書いてある質問を10問用意し、「正解のPDFが上位5件に入ったか」「答えに正解の数値・語が含まれたか」を分けて数えました。

| 構成 | 正解PDFが上位5件 | 答えが正解 |
|---|---|---|
| Fess のスニペット（検索結果の要約文）だけを LLM に渡す | 8/10 | **4/10** |
| ヒットしたPDFの本文から検索語の周辺を切り出して渡す | 7/10 | 5/10 |
| 切り出しを「一致語の多い区間」順に並べ、LLMの検索語で0件なら固有名詞1語で再検索 | **10/10** | **9/10** |

1回目の 4/10 は、検索は当たっているのに LLM が「資料に記載がありません」と答えるケースが大半でした。Fess が返すスニペットは200文字程度の要約で、数値や条件が入っている段落まで届かないためです。Namazu の案件で当社が最初にやったのと同じ「検索でファイルを特定し、本文の該当箇所だけを渡す」を Fess でも入れると 9/10 になりました。最後に残った1問は、答えが記事の別の段落にあってプルリクエスト番号が切り出しに入らなかったもので、LLM は正直に「記載がありません」と答えています。

回答までの時間は1問あたり3〜5秒（検索語の生成と回答の2回、gemma4 12B）でした。

## Namazu と Fess、どちらを選ぶか

- 既に Namazu の索引と運用があるなら、そのままで困りません。AIチャットの検索役としても十分です
- 新しく立てる、Webサイトやファイルサーバーもまとめて検索したい、管理画面で運用したい、日本語の形態素解析が欲しい、という場合は Fess です
- どちらでも、AI側の作りは同じです。**検索役は枯れた全文検索、AIは読んで答える役に限定し、根拠の箇所を本文から渡す**。ベクトルDBもGPU（回答用のLLMを除く）も要りません

## まとめ

- Fess は docker 2コンテナで立ち、45本のPDFを40秒で索引、検索は数十ms。日本語UIとドキュメントがあり、Namazu の後継として現実的です
- AIに答えさせる精度は、検索エンジンより「根拠の渡し方」で決まりました。スニペットだけだと 4/10、本文の該当箇所を渡すと 9/10
- 管理APIで組むときの罠は3つ（作成はPOST、含めるパスにディレクトリ、権限に `{role}guest`）

当社は、この構成の回答役に買い切りの [Kurage Light ChatBot（税込55,000円）](https://kappstore.exbridge.jp/app.php?id=224e141f77bd07a8&ref=vwork-fess) を使い、Namazu でも Fess でも接続します。全文検索のオープンソースを実測つきで比較した一覧は [全文検索システムのオープンソース一覧・比較](https://exbridge.jp/ai-system/c/search/?ref=vwork-fess)、Fess と Namazu それぞれの解説は [Fess の紹介ページ](https://kurage.exbridge.jp/oss/fess/)・[Namazu の紹介ページ](https://kurage.exbridge.jp/oss/namazu/) にあります。

## 参考

- Fess: https://github.com/codelibs/fess （Apache-2.0）／ドキュメント: https://fess.codelibs.org/ja/
- docker-fess: https://github.com/codelibs/docker-fess
- 実測に使った compose・スクリプト（管理APIでのクロール設定、検索×LLMの最小実装、評価セット）: 当社の fess 検証フォルダ `scripts/`（crawl_docs.py・ask.py・eval.json）
- 関連記事: [Namazu全文検索×買い切りチャットボット×AIの開発実績](https://katsushi2441.github.io/vwork/blog/2026-09-04-namazu-ai-chat-knowledge.html)／[whisper.cppの日本語文字起こし実測](2026-09-04-whisper-cpp-japanese-transcription.html)
