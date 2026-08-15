---
title: "OpenKB——ベクトルDB不要のRAG「PageIndex」でナレッジチャットAIを作る（ローカルLLM/DeepSeek実測つき）"
emoji: "📚"
type: "tech"
topics: ["openkb", "rag", "llm", "ollama", "deepseek"]
published: true
---

社内文書やFAQを読ませて答えるチャットAI（RAG）を作るとき、最初の面倒はベクトルDBの選定と運用です。[OpenKB](https://github.com/VectifyAI/OpenKB)（Apache-2.0）は、そこを丸ごと省略できる設計のOSSです。当社（エクスブリッジ）で商品カタログ・代理店制度文書を使って実際に検証したので、セットアップのハマりどころと、実測で分かった得意・不得意まで含めて紹介します。

## OpenKBとは——「wikiにコンパイルする」RAG

OpenKBはVectifyAIが公開しているナレッジベースエンジンで、コンセプトはAndrej Karpathyの「ドキュメントをwikiに編纂して読む」構想に近いものです。仕組みは2段階です。

1. **コンパイル**: `openkb add` で投入したMarkdown/テキストを、LLMが **summaries / concepts / entities** の3層のwikiページ群に再編纂する
2. **検索（PageIndex）**: 質問が来ると、embeddingの類似検索ではなく、**LLMがwikiの目次ツリーを推論で辿って**該当ページを読みに行く

つまり**ベクトルDBもembeddingモデルも不要**。導入物が減り、「なぜこの文書が引っかかったのか」がwikiページ単位で追えるのが利点です。CLIは `openkb add sources/`、`openkb status`、質問はquery/chatだけの最小構成です。

## セットアップ——ローカルLLM（Ollama）で動かすときの3つの罠

LLM接続はLiteLLM経由なので、OpenAI/Anthropic/DeepSeek/Ollamaを設定だけで切り替えられます。ローカルのOllama（gemmaクラスの12Bモデル）で動かす場合、実際に必要だったのは次の3点でした。

```yaml
# config.yaml
litellm:
  drop_params: true   # Ollamaが parallel_tool_calls 非対応のため必須
```

```bash
export OLLAMA_API_BASE=http://<ollamaホスト>:11434
echo 'LLM_API_KEY=ollama' >> .env   # ダミーでよい（未設定だと警告）
```

`drop_params: true` を入れないと、OpenKBが投げる `parallel_tool_calls` パラメータをOllamaが受け付けずに落ちます。ここが一番詰まりやすいポイントです。

また、**コンパイルはローカル12Bには重い**処理です。実測では小さな文書1本で2〜3分、商品カタログ一式は10分でも終わりませんでした。KB構築だけ高速なAPIモデルで行い、質問応答をローカルにする使い分けが現実的です。

## 実測で分かった得意・不得意

商品カタログ（価格・URL入り）と代理店制度文書を入れて検証した結果です。

**✅ 得意: 概念理解と選定推論**。「サロンの予約管理を探している客に何を勧める？」に対し、カタログから正しい商品を選んで理由付きで答えました。制度の仕組み（手数料率の構造など）の説明も正確です。

**❌ 不得意: 一字一句の事実**。wikiコンパイルは文書を概念的な文章へ要約するため、その過程で**価格（55,000円）・URL・手数料率のような「正確さが命の値」がsummary/entityページから抜け落ちます**。生テキストは内部に残っているのですが、queryエージェントはそこまで掘らず「詳細は記載なし」と答えました。FAQボットや営業支援のように「値段と誘導先URL」が主役の用途では、これは致命傷になり得ます。

## 実務の落とし所——KBサイズで方式を使い分ける

この検証から、当社では次の指針に落ち着きました。

- **KBが小さいうち（〜数百KB）**: OpenKBを使わず、**生Markdownをそのままコンテキストに渡す**のが最も単純で正確。安価なDeepSeek APIで実測したところ、全カタログ＋制度文書を読ませた状態で**1回答あたり約$0.01（約1.5円）**。価格・URLの事実も落とさず、応答速度はローカル12B比で約2.7倍でした
- **KBが育ったら（数MB〜）**: 全文をコンテキストに入れられなくなった時点でPageIndex型の出番。ベクトルDBなしで運用を軽く保てるOpenKBの設計が効いてきます
- どちらもLiteLLM系の構成ならモデル差し替えは設定1行なので、**「普段は安価なAPI・機密文書だけローカルLLM」**という売り分けも同じコードでできます

## この構成でチャットAIを作るノウハウ（実例）

当社はこの検証結果をもとに、FAQ対応・AI接客・社内ChatGPT型のナレッジチャットAIを構築しています（自社サイトのAI相談チャットも同系統の構成で実運用中です）。SaaSの月額相場との費用比較や、「作業の8割は文書整備」という実感値を含めた構築ノウハウは、noteにまとめました。

**→ [チャットボットSaaSを契約する前に。AIに作らせたら「1回答1.5円」だった話（note）](https://note.com/tokoname/n/ne3a3786c0956)**

費用相場の全体像と買い切り開発という選択肢は、[解説ページ（AIチャットボット開発の費用相場と「買い切り11万円」という選択肢）](https://kurage.exbridge.jp/ai-chatbot-kaikiri.php?ref=oss-openkb)にもまとめています。

## まとめ

- OpenKBは**ベクトルDB不要のRAG**を最小構成で実現するOSS。概念理解・選定推論は実力あり
- ただし**wiki要約の過程で正確な事実（価格・URL）が落ちる**設計上の癖があり、事実回答が主役の用途は生ソース直渡しとの併用が必要
- Ollamaで動かすなら `drop_params: true`・`OLLAMA_API_BASE`・ダミーAPIキーの3点セット
- 小さいKBは直渡し＋安価API（DeepSeekで1回答約1.5円）、大きくなったらPageIndex——この使い分けが2026年時点の現実解
