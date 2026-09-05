---
title: "Appsmithの公式イメージは初回起動を20秒中断すると永久に壊れる——画面は200を返すのにAPIが全部502になる罠を突き止め、データを消さずに直した"
emoji: "🧱"
type: "tech"
topics: ["appsmith", "docker", "mongodb", "oss", "運用"]
published: true
title_hatena: "画面は開くのにログインできない——Appsmithが初回起動の中断で壊れる仕組みと、データを消さない復旧"
title_blogger: "コンテナは動いているのに使えない。原因は起動時のたった20秒だった"
---

社内の管理画面を画面組み立てだけで作れるオープンソース **Appsmith** を検証環境に立てたところ、公式のとおりに起動したのに**ログインできない**状態になりました。

ブラウザで開くとログイン画面は出ます。コンテナ一覧にも名前があります。それでもメールアドレスとパスワードを入れると、何も起きません。

原因を最後まで追ったところ、**初回起動の最初の20秒を中断すると環境が恒久的に壊れる**という作りの問題でした。しかも壊れた状態は「動いているように見える」ため、気づくのが非常に難しい。

公式の案内はデータを消して作り直すことですが、**消さずに直せました**。手順と、その診断の道筋を残します。

## 症状

三つの事実が同時に成り立ちます。これが揃うのが特徴です。

**画面は正常に返る。**

```
$ curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/
200
```

**APIは全滅している。**

```
$ curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/api/v1/users/me
502
```

**コンテナは永久に unhealthy。**

```
$ docker ps --filter name=appsmith --format '{{.Status}}'
Up 25 minutes (unhealthy)
```

外形監視をトップページに向けていると、この障害は**永久に検知できません**。200が返り続けるからです。

## 追い方

### 1. 内部プロセスが再起動を繰り返している

Appsmith は単一のコンテナの中で複数のプロセスを動かしています。状態を見ると、あるプロセスの稼働時間だけが毎回0分台に戻っていました。

```
$ docker exec appsmith supervisorctl status
backend    RUNNING   pid 1508, uptime 0:21:14
editor     RUNNING   pid 1509, uptime 0:21:14
mongodb    RUNNING   pid 1505, uptime 0:21:14
mcp        RUNNING   pid 3761, uptime 0:00:11     ← ここ
```

ログには同じ行が延々と並んでいました。

```
Appsmith MCP failed to start: Server selection timed out after 30000 ms
Appsmith MCP failed to start: Server selection timed out after 30000 ms
```

30秒のタイムアウトで落ちて、また起動する。それを無限に繰り返しています。

### 2. なぜ諦めないのか

プロセスの管理設定を見ると、再試行の上限は3回でした。それなのに止まりません。

```
[program:mcp]
autorestart=true
startretries=3
# Require the process to stay up 5s to count as a successful start
```

コメントに答えが書いてありました。「5秒持てば起動成功と数える」。ところがこの不具合では、接続の待ち時間が30秒あるため、プロセスは**30秒生きてから落ちます**。5秒を超えているので毎回「起動成功」と判定され、再試行の回数が加算されません。永久に繰り返します。

### 3. 本当の原因はデータベース

サーバー側のログを見ると、より直接的な理由が出ていました。

```
com.mongodb.MongoQueryException: Command failed with error 13436
(NotPrimaryOrSecondary): 'node is not in primary or recovering state'
```

同梱のMongoDBに接続はできるものの、**読み書きを受け付けない状態**でした。確認すると理由がわかりました。

```
$ mongosh ... --eval "rs.status()"
NotYetInitialized
```

MongoDBは複製構成（レプリカセット）として起動していますが、**その初期化が一度も行われていません**。初期化されていない複製構成のノードは、主系でも副系でもない宙ぶらりんの状態になります。どのドライバも接続先を選べず、30秒待って諦めます。

サーバー側の起動時の移行処理もここで死んでいたため、APIが全部502になっていました。画面配信は別プロセスなので、200を返し続けます。

## なぜ初期化されなかったのか

起動スクリプトを読むと、初期化は確かに実装されていました。

```bash
if [[ $shouldPerformInitdb -gt 0 && $isUriLocal -eq 0 ]]; then
  mongod --fork --port 27017 --dbpath "$MONGO_DB_PATH" ...
  sleep 10
  # 利用者を作る
  mongod --shutdown
  mongod --fork ... --replSet mr1 --keyFile ...
  sleep 10
  mongosh "$APPSMITH_DB_URL" --eval 'rs.initiate()'    # ← 仕上げ
fi
```

問題は `shouldPerformInitdb` の決め方でした。

```bash
for path in "$MONGO_DB_PATH/local.0" "$MONGO_DB_PATH/storage.bson"; do
  if [ -e "$path" ]; then
    shouldPerformInitdb=0
    break
  fi
done
```

**データファイルが存在するかどうかだけで判断しています。**

そのデータファイルは、上の手順の1行目でMongoDBが起動した瞬間に作られます。仕上げの `rs.initiate()` まで、`sleep 10` が2回に加えて起動と停止があり、**20秒以上**あります。

この20秒の間にコンテナが止まると、次回以降は「データファイルがある＝初期化済み」と判断され、**仕上げが二度と実行されません**。

判定すべきは「初期化が完了したか」であって「データファイルがあるか」ではない、という典型的な取り違えです。

## 中断は簡単に起きる

意図的に止めなくても起きます。私の場合は、ポートを変えるために起動直後に `docker compose down` したのが原因でした。

他にも次のどれでも同じ状態になります。

- 設定を直そうとして起動直後に止めた
- ポートが衝突したので止めて直した
- サーバーが再起動した
- メモリ不足でコンテナが落ちた（小さなVPSでは十分あり得ます）
- `Ctrl-C` で止めた

つまり、**小さなサーバーに初めて入れる人ほど踏みやすい**罠です。

## 直す

データを消さずに直せます。未完了だった仕上げを、手で実行するだけです。

### 手順1. 状態を確認する

```bash
docker exec appsmith sh -c '. /appsmith-stacks/configuration/docker.env; \
  mongosh "$APPSMITH_DB_URL?authSource=appsmith&directConnection=true" --quiet \
  --eval "try{print(rs.status().myState)}catch(e){print(e.codeName)}"'
```

`NotYetInitialized` と出れば対象です。`1` と出たら原因は別にあります。

### 手順2. 初期化する

```bash
docker exec appsmith sh -c '. /appsmith-stacks/configuration/docker.env; \
  mongosh "$APPSMITH_DB_URL?authSource=appsmith&directConnection=true" --quiet \
  --eval "rs.initiate({_id:\"mr1\",members:[{_id:0,host:\"localhost:27017\"}]})"'
```

```
{ ok: 1 }
```

### 手順3. 主系になるのを待つ

30秒ほどで `1` になります。1が主系を意味します。

### 手順4. サーバー側を起動し直す

初期化前に落ちているので、起動し直す必要があります。

```bash
docker exec appsmith supervisorctl restart backend
```

### 結果

```
$ curl -s -o /dev/null -w 'API %{http_code}\n' http://127.0.0.1:8080/api/v1/users/me
API 200

$ docker ps --filter name=appsmith --format '{{.Status}}'
Up 5 minutes (healthy)
```

APIが復旧し、再起動を繰り返していたプロセスも安定しました。管理者アカウントを作ってログインでき、日本語の表示名もそのまま通りました。

## 効かなかった対処

再起動を繰り返すプロセスを止めようとして、無効化の変数を見つけました。

```yaml
APPSMITH_MCP_ENABLED: "false"
```

**効きませんでした。** プロセスの環境変数には確かに渡っています。

```
$ tr "\0" "\n" < /proc/<pid>/environ | grep MCP_ENABLED
APPSMITH_MCP_ENABLED=false
```

それでもプロセスは起動し、同じように失敗し続けます。起動する側がこの変数を見ていません。

そもそも、再起動を繰り返すプロセスは症状であって原因ではありません。直すべきはデータベースの側でした。

## 学び

**画面が200を返すことは、動いている証拠になりません。**

Appsmith に限らず、画面配信とサーバー処理が別プロセスになっている構成では、片方だけ生きている状態が普通に起こります。監視するなら、認証が要るAPIまで叩いてください。

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://<host>/api/v1/users/me
```

**200 か 401 なら正常。502 なら壊れています。** 401でよいのです。認証を要求できているのは、サーバーが生きている証拠だからです。

もうひとつ。**「一度きりの初期化」を、痕跡の有無で判断してはいけません。** 途中でできる痕跡と、完了の印は別物です。完了したときにだけ書く印を用意すべきでした。自分で似た仕組みを書くときの教訓にします。

## 日本語での利用について

ついでに測ったことも書いておきます。

Appsmith には**日本語表示がありません**。設定で切り替えられないだけでなく、翻訳の仕組み自体が存在しません。画面のHTMLは `lang="en"` に固定され、言語ファイルは1本もなく、文言1,397件が一つのプログラムファイルに直接書かれています。

一方で、**扱うデータが日本語であることには何の支障もありません**。日本語のテーブル名・列名はむしろ扱いやすく、引用符なしでそのまま使えます。

```sql
SELECT 会社名, 契約金額 FROM 取引先 WHERE 都道府県 = '愛知県'
```

対して英字で大文字が混ざる名前は引用符が要ります。PostgreSQLは引用符のない識別子を小文字に変換しますが、日本語には大文字小文字の区別がないためです。

```sql
SELECT CustomerName FROM MixedCase
-- ERROR: relation "mixedcase" does not exist
```

唯一の実務的な穴は**CSVの書き出し**でした。配信されている画面用プログラム216本を調べましたが、CSVにExcel向けの目印（BOM）を付けている箇所はありません。日本語版のExcelで開くと文字化けします。表の標準ボタンを隠して、自分でボタンを置くのが確実です。

```javascript
download("\uFEFF" + body, "取引先.csv", "text/csv");
```

## まとめ

| 症状 | 画面200・API502・永久にunhealthy |
| --- | --- |
| 原因 | 内部MongoDBの複製構成が未初期化 |
| 引き金 | 初回起動の最初の20秒での中断 |
| 根本 | 初期化済みかを「データファイルの有無」で判定している |
| 復旧 | `rs.initiate()` 一回 + backend再起動。データは消えない |
| 予防 | 初回起動は healthy になるまで中断しない |

Appsmith 自体は、社内の管理画面を短時間で作るには良い道具です。ただし最初の1分だけは、何もせず待ってください。

---

導入から復旧、日本語での運用までをまとめた手順書を[Kurage App Store](https://kappstore.exbridge.jp/)で配布しています。英語画面の読み替え表、Excelで化けないCSV書き出し、復旧を自動判定するスクリプトを同梱しています。
