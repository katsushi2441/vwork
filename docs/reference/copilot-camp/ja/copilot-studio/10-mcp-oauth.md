---
search:
  exclude: true
---
# ラボ MCS10 - OAuth 2.0 で MCP サーバーを利用する

このラボでは、Microsoft Copilot Studio で作成したエージェントから、OAuth 2.0 認証を使用して MCP (Model Context Protocol) サーバーを利用します。ここでは、認証なしで HR MCP サーバーを操作した [ラボ MCS6 - MCP サーバーの利用](../06-mcp){target=_blank} で紹介した概念を基に、同じ HR MCP サーバーに OAuth 2.0 の Authorization Code Flow を構成し、HR 候補者管理ツールへの安全なアクセスを実現します。

<div class="lab-intro-video">
    <div style="flex: 1; min-width: 0;">
        <!-- <iframe  src="//www.youtube.com/embed/VIDEO_ID" frameborder="0" allowfullscreen style="width: 100%; aspect-ratio: 16/9;">          
        </iframe>
          <div>Get a quick overview of the lab in this video.</div> -->
    </div>
    <div style="flex: 1; min-width: 0;">
   ---8<--- "ja/mcs-labs-prelude.md"
    </div>
</div>

!!! note
    このラボは [ラボ MCS6 - MCP サーバーの利用](../06-mcp){target=_blank} の内容を拡張したものです。ラボ MCS6 を先に完了していなくても構いませんが、MCP の概念と Copilot Studio でのエージェント作成に慣れていると理解が深まります。

!!! tip "OAuth 2.0 について学ぶ"
    OAuth 2.0 Authorization Code Flow は、安全な委任アクセスを実現する業界標準の方式です。アプリケーションが資格情報を公開することなくユーザーに代わるトークンを取得できます。詳細は [Microsoft identity platform and OAuth 2.0 authorization code flow](https://learn.microsoft.com/ja-jp/entra/identity-platform/v2-oauth2-auth-code-flow){target=_blank} を参照してください。

このラボで学ぶ内容:

- OAuth 2.0 認証を用いた MCP サーバーの構成方法
- 安全な API アクセスのための Microsoft Entra ID アプリケーション登録方法
- Copilot Studio での OAuth 2.0 Authorization Code Flow の設定方法
- Copilot Studio エージェントからセキュアな MCP ツールを利用する方法

## 演習 1 : セキュアな MCP サーバーのセットアップ

この演習では、OAuth 2.0 で保護された HR 候補者管理機能を提供する、事前構築済みの MCP サーバーをセットアップします。サーバーは Microsoft .NET ベースで、JWT トークン検証を組み込み、認証されたユーザーのみが HR ツールへアクセスできるようにします。

### 手順 1: セキュアな MCP サーバーと前提条件の理解

セキュアな HR MCP サーバーは、[ラボ MCS6](../06-mcp){target=_blank} で使用したサーバーの強化版です。同じツールを提供します:

- **list_candidates**: 候補者の一覧を取得
- **search_candidates**: 名前、メール、スキル、役職で候補者を検索
- **add_candidate**: 新しい候補者を追加
- **update_candidate**: メールアドレスで既存候補者を更新
- **remove_candidate**: メールアドレスで候補者を削除

大きな違いは、このバージョンではすべてのリクエストに対し Authorization ヘッダー内の有効な OAuth 2.0 アクセストークンが必須である点です。サーバーは Microsoft Entra ID テナントに対して JWT トークンを検証し、安全なアクセスを保証します。

開始前に以下を用意してください:

- [.NET 10.0 SDK](https://dotnet.microsoft.com/download/dotnet/10.0){target=_blank}
- [Visual Studio Code](https://code.visualstudio.com/){target=_blank}
- [Node.js v.22 以上](https://nodejs.org/en){target=_blank}
- [Dev tunnel](https://learn.microsoft.com/ja-jp/azure/developer/dev-tunnels/get-started){target=_blank}
- アプリケーション登録用の [Microsoft Entra 管理センター](https://entra.microsoft.com){target=_blank} へのアクセス

<cc-end-step lab="mcs10" exercise="1" step="1" />

### 手順 2: セキュアな MCP サーバーのダウンロードと確認

このラボでは、事前構築されたセキュア HR MCP サーバーを使用します。サーバーファイルを [こちら](https://download-directory.github.io/?url=https://github.com/microsoft/copilot-camp/tree/main/src/make/copilot-studio/path-m-lab-mcs10-mcp-oauth/hr-mcp-server-secured&filename=hr-mcp-server){target=_blank} からダウンロードしてください。

ZIP を展開し、対象フォルダーを Visual Studio Code で開きます。サーバーはすでに OAuth 2.0 セキュリティを実装済みで、設定を行うだけで利用できます。

![The outline of the Secured HR MCP Server project in Visual Studio Code showing the server files including authentication middleware.](../../../assets/images/make/copilot-studio-10/mcp-server-secured-01.png)

プロジェクト構成の主な要素は次のとおりです。

- `Configuration`: `HRMCPServerConfiguration.cs` が含まれ、OAuth 設定を含む MCP サーバーの構成を定義するフォルダー
- `Data`: 候補者リストを保持する `candidates.json` を含むフォルダー
- `Services`: `ICandidateService.cs` と `IAuthorizationService.cs` のインターフェイス、および候補者リストの管理とセキュリティ処理を行う `CandidateService.cs` と `AuthorizationService.cs` の実装
- `Tools`: MCP ツールを定義する `HRTools.cs` とツールで使用するデータモデルを定義する `Models.cs`
- `appsettings.json.sample`: Entra ID 設定を行う際のサンプル構成ファイル
- `Program.cs`: メインエントリーポイント。ここで MCP サーバーが JWT 認証付きで初期化されます。

!!! info
    セキュア MCP サーバーには、Microsoft Entra ID テナントに対して受信トークンを検証する JWT ベアラートークン認証ミドルウェアが含まれています。これにより、有効なトークンを持つ認証済みユーザーのみが HR ツールにアクセスできます。

<cc-end-step lab="mcs10" exercise="1" step="2" />

### 手順 3: OAuth 2.0 Authorization Code Flow の理解

アプリケーションを構成する前に、このシナリオでの OAuth 2.0 Authorization Code Flow の流れを理解しましょう。

1. **ユーザー認証**: ユーザーが Copilot Studio エージェントを操作して MCP ツールを起動すると、Microsoft Entra ID での認証を求められます。  
2. **認可コードの発行**: ログインが成功すると、Microsoft Entra ID はリダイレクト URI 経由で Copilot Studio に認可コードを送信します。  
3. **トークン交換**: Copilot Studio は認可コード (およびクライアント資格情報) を使用してアクセストークンを取得します。  
4. **API へのアクセス**: Copilot Studio はアクセストークンを MCP サーバーへのリクエストに含め、サーバーはトークンを検証してからリクエストを処理します。

このフローにより、以下が保証されます。

- ユーザーの資格情報が MCP サーバーに公開されない  
- アクセストークンには有効期限とスコープが設定される  
- MCP サーバーはユーザーの ID とアクセス許可を検証できる  

<cc-end-step lab="mcs10" exercise="1" step="3" />

## 演習 2 : Microsoft Entra ID アプリケーションの構成

この演習では、HR MCP サーバー (バックエンド) 用と Copilot Studio クライアント (フロントエンド) 用の 2 つの Microsoft Entra ID アプリケーションを登録します。

### 手順 1: HR MCP サーバー アプリケーション (バックエンド) の登録

ブラウザーで [https://entra.microsoft.com](https://entra.microsoft.com){target=_blank} を開き、職場アカウントでサインインします。

左ナビゲーションで 1️⃣ **App registrations** → 2️⃣ **+ New registration** を選択します。

![The Microsoft Entra admin center showing the App registrations page with the New registration button highlighted.](../../../assets/images/make/copilot-studio-10/entra-app-registration-01.png)

次の設定でアプリケーションを作成します。

- **Name**: 

```text
HR MCP Server
```

- **Supported account types**: **Accounts in this organizational directory only** を選択

- **Redirect URI**: ここでは空欄のまま (必要に応じて後で設定)

**Register** を選択してアプリケーションを作成します。

![The Register an application page with the HR MCP Server name and single tenant option selected.](../../../assets/images/make/copilot-studio-10/entra-app-registration-02.png)

<cc-end-step lab="mcs10" exercise="2" step="1" />

### 手順 2: HR MCP サーバー アプリケーションの構成

アプリ登録後、クライアント アプリがアクセスできる API を公開するよう設定します。

#### Expose an API 設定

1. **HR MCP Server** アプリで **Expose an API** を選択  
2. **Application ID URI** の横にある **Add** をクリック  
3. デフォルト値 (形式 `api://<client-id>`) をそのまま使用  
4. **Save** を選択  

![The Expose an API page showing the Application ID URI configuration.](../../../assets/images/make/copilot-studio-10/entra-expose-api-01.png)

#### スコープの追加

1. **Scopes defined by this API** で **+ Add a scope** を選択  
2. 次の設定でスコープを作成:

- **Scope name**: 

```text
HR.Manage
```

- **Who can consent?**: **Admins and users**

- **Admin consent display name**: 

```text
Manage HR Data
```

- **Admin consent description**: 

```text
Allows managing HR data as an Admin
```

- **User consent display name**: 

```text
Manage HR Data
```

- **User consent description**: 

```text
Allows managing HR data as a user
```

- **State**: **Enabled**

3. **Add scope** を選択  

![The Add a scope dialog with all fields configured for the access_as_user scope.](../../../assets/images/make/copilot-studio-10/entra-add-scope-01.png)

#### 重要な値の記録

**Overview** ページで以下の値を控えておきます (後ほど使用)。

- **Application (client) ID**  
- **Directory (tenant) ID**

<cc-end-step lab="mcs10" exercise="2" step="2" />

### 手順 3: Copilot Studio クライアント アプリケーションの登録

次に、HR MCP サーバーを消費する Copilot Studio クライアントを表すアプリを作成します。

前の手順と同様に Microsoft Entra 管理センターで **Applications** → **App registrations** → **+ New registration** を選択し、次を設定します。

- **Name**: 

```text
HR MCP Consumer
```

- **Supported account types**: **Accounts in this organizational directory only**

- **Redirect URI**: 空欄のまま (Copilot Studio が後で提供)

**Register** を選択して作成します。

<cc-end-step lab="mcs10" exercise="2" step="3" />

### 手順 4: Copilot Studio クライアント アプリケーションの構成

登録後、必要なアクセス許可と資格情報を設定します。

#### クライアント シークレットの作成

1. **HR MCP Consumer** アプリで **Certificates & secrets** を選択  
2. **+ New client secret** をクリック  
3. 次を設定:

- **Description**: 

```text
ClientSecret
```

- **Expires**: 適切な期間 (例: 12 か月)

4. **Add** を選択  

**重要**: **Value** はこの時だけ表示されるため、必ず安全な場所に保存してください。

#### API Permissions の設定

1. 左メニューで **API permissions** を選択  
2. **+ Add a permission** をクリック  
3. **APIs my organization uses** タブを選択  
4. **HR MCP Server** を検索して選択  

    ![The Request API permissions dialog showing the "APIs my organization uses" tab with HR MCP Server selected.](../../../assets/images/make/copilot-studio-10/entra-api-permissions-01.png)

6. 1️⃣ **Delegated permissions** を選択  
7. 2️⃣ **HR.Manage** をチェック  
8. 3️⃣ **Add permissions** を選択  

    ![The permission selection dialog with access_as_user selected.](../../../assets/images/make/copilot-studio-10/entra-api-permissions-02.png)

9. さらに Microsoft Graph の権限を追加します。**+ Add a permission** → **Microsoft Graph** → **Delegated permissions** を選択  
10. 次の権限をチェック:

    - **email**
    - **openid**
    - **profile**
    - **User.Read**

11. **Add permissions** を再度選択  

#### 管理者の同意を付与

1. **API permissions** 一覧で **Grant admin consent for [Your Tenant]** をクリック  
2. **Yes** を選択して確定  

![The API permissions page showing all permissions with admin consent granted.](../../../assets/images/make/copilot-studio-10/entra-admin-consent-01.png)

#### 重要な値の記録

クライアント アプリ **Overview** ページで以下を控えます。

- **Application (client) ID**  
- **Client Secret Value** (前ステップで保存済み)

<cc-end-step lab="mcs10" exercise="2" step="4" />

### 手順 5: MCP サーバーの構成と起動

Entra ID の設定を MCP サーバーに反映します。

`appsettings.json.sample` を `appsettings.json` としてコピーし、`AzureAd` セクションを更新します。

```json
{
  "AzureAd": {
    "Instance": "https://login.microsoftonline.com/",
    "TenantId": "[YOUR_TENANT_ID]",
    "ClientId": "[YOUR_HR_MCP_SERVER_CLIENT_ID]",
    "Audience": "[YOUR_HR_MCP_SERVER_CLIENT_ID]",
    "Scopes": "[YOUR_APPLICATION_ID_URI]/HR.Manage"
  }
}
```

プレースホルダーを置き換えます。

- `[YOUR_TENANT_ID]`: HR MCP Server アプリ登録の Directory (tenant) ID  
- `[YOUR_HR_MCP_SERVER_CLIENT_ID]`: HR MCP Server アプリの Application (client) ID  
- `[YOUR_APPLICATION_ID_URI]`: HR MCP Server アプリの Application ID URI (例: `api://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

ファイルを保存し、MCP サーバーを実行します。

```console
dotnet run
```

サーバーが起動しリクエスト待機状態になります。以降、有効なアクセストークンのないリクエストは 401 Unauthorized になります。

<cc-end-step lab="mcs10" exercise="2" step="5" />

### 手順 6: Dev tunnel の構成

dev tunnel を使用して MCP サーバーを公開 URL で公開します。未インストールの場合は [こちらの手順](https://learn.microsoft.com/ja-jp/azure/developer/dev-tunnels/get-started){target=_blank} を参照してください。

dev tunnel へログイン:

```console
devtunnel user login
```

dev tunnel をホスト:

!!! important
    以下の `hr-mcp-secured` は一意なトンネル名に変更してください。例: 名前が Alex の場合 `hr-mcp-secured-alex` など。

```console
devtunnel create hr-mcp-secured -a --host-header unchanged
devtunnel port create hr-mcp-secured -p 47002
devtunnel host hr-mcp-secured
```

「Connect via browser」の URL をコピーして保存します。Copilot Studio の MCP ツール設定および **HR MCP Consumer** アプリの更新で使用します。

![The dev tunnel running showing the connection URLs.](../../../assets/images/make/copilot-studio-10/devtunnel-hosting-01.png)

!!! tip
    このラボ全体で MCP サーバーと dev tunnel を起動したままにしてください。再起動が必要な場合は、サーバーに対して `dotnet run`、トンネルに対して `devtunnel host hr-mcp-secured` を実行します。

<cc-end-step lab="mcs10" exercise="2" step="6" />

### 手順 7: Application ID URI と構成の更新

dev tunnel URL が取得できたら、Microsoft Entra ID の **HR MCP Server** アプリで Application ID URI をデフォルトの `api://<guid>` から dev tunnel URL に更新します。

#### Entra ID で Application ID URI を更新

1. [Microsoft Entra 管理センター](https://entra.microsoft.com){target=_blank} に移動  
2. **Applications** → **App registrations** へ  
3. **HR MCP Server** アプリを選択  
4. **Expose an API** を選択  
5. **Application ID URI** の横で **Edit** をクリック  
6. 値を dev tunnel URL に置き換え (例: `https://hr-mcp-secured.devtunnels.ms`)  
7. **Save** を選択  

!!! warning "URL の形式"
    末尾にスラッシュを付けず、`https://your-tunnel-name.devtunnels.ms` の形式にしてください。

#### appsettings.json の更新

`appsettings.json` の `Scopes` プロパティを dev tunnel URL に合わせて更新します。

```json
{
  "AzureAd": {
    "Instance": "https://login.microsoftonline.com/",
    "TenantId": "[YOUR_TENANT_ID]",
    "ClientId": "[YOUR_HR_MCP_SERVER_CLIENT_ID]",
    "Audience": "[YOUR_HR_MCP_SERVER_CLIENT_ID]",
    "Scopes": "[YOUR_DEVTUNNEL_URL]/HR.Manage"
  }
}
```

`[YOUR_DEVTUNNEL_URL]` を先ほど設定した dev tunnel URL (例: `https://hr-mcp-secured.devtunnels.ms`) に置き換えます。

最終的な構成例:

```json
{
  "AzureAd": {
    "Instance": "https://login.microsoftonline.com/",
    "TenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "ClientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "Audience": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "Scopes": "https://hr-mcp-secured.devtunnels.ms/HR.Manage"
  }
}
```

#### MCP サーバーの再起動

`appsettings.json` を保存後、サーバーを再起動します。

1. 実行中のサーバーを `Ctrl+C` で停止  
2. 再度起動:

```console
dotnet run
```

これでサーバーは、Entra ID で設定した dev tunnel URL を使用してトークンを検証します。

<cc-end-step lab="mcs10" exercise="2" step="7" />

## 演習 3 : Copilot Studio でのエージェント作成

この演習では、セキュア MCP サーバーを利用する新しい Copilot Studio エージェントを作成します。

### 手順 1: HR エージェントの作成

ブラウザーで [https://copilotstudio.microsoft.com](https://copilotstudio.microsoft.com){target=_blank} を開き、職場アカウントでサインインします。

以前のラボで作成した `Copilot Dev Camp` 環境を選択し、**Create an agent** を選択して新しいエージェントを作成します。

**Details** セクションの **Edit** を選択し、次を設定します。

- **Name**: 

```text
HR Candidate Management (Secured)
```

- **Description**: 

```text
An AI assistant that helps manage HR candidates using a secured MCP server 
with OAuth 2.0 authentication for enterprise-grade security
```

**Save** をクリックして保存します。  
次に **Instructions** セクションの **Edit** を選択し、以下を設定します。

```text
You are a helpful HR assistant that specializes in secure candidate management. You can help users 
search for candidates, check their availability, get detailed candidate information, and add new 
candidates to the system. 

All operations require user authentication through OAuth 2.0 to ensure data security and compliance 
with enterprise policies.

Always provide clear and helpful information about candidates, including their skills, experience, 
contact details, and availability status.
```

**Save** をクリックして保存します。

**Agent's Model** を **GPT-5 Chat** に変更します。

![The agent Overview page with name, description, model, and instructions configured for the secured HR agent.](../../../assets/images/make/copilot-studio-10/create-agent-01.png)

<cc-end-step lab="mcs10" exercise="3" step="1" />

### 手順 2: エージェント設定の構成

最適なパフォーマンスのため、エージェントのナレッジ設定を構成します。

右上の **Settings** をクリックし、**Knowledge** セクションで以下を設定:

- **Use general knowledge**: off  
- **Use information from the web**: off

**Save** を選択して確定します。

<cc-end-step lab="mcs10" exercise="3" step="2" />

### 手順 3: 会話スターターの設定

**Overview** ページの **Suggested prompts** セクションに次を追加します。

1. Title: `List all candidates` - Prompt: `Show me all candidates in the HR system`  
2. Title: `Search candidates` - Prompt: `Search for candidates with skills in [SKILL]`  
3. Title: `Add new candidate` - Prompt: `Add a new candidate with firstname [FIRSTNAME], lastname [LASTNAME], email [EMAIL], role [ROLE], languages [LANGUAGES], and skills [SKILLS]`

![The Suggested prompts section configured with sample prompts.](../../../assets/images/make/copilot-studio-10/conversation-starters-01.png)

**Save** を選択して変更を保存します。

<cc-end-step lab="mcs10" exercise="3" step="3" />

## 演習 4 : OAuth 2.0 付き MCP ツールの登録

この演習では、セキュア MCP サーバーを Copilot Studio エージェントのツールとして OAuth 2.0 認証付きで構成します。

### 手順 1: MCP サーバー ツールの追加

エージェントで 1️⃣ **Tools** セクションに移動し、2️⃣ **+ Add a tool** をクリックします。

![The Tools section with the Add a tool command highlighted.](../../../assets/images/make/copilot-studio-10/add-tool-01.png)

1️⃣ **Create new** セクションで 2️⃣ **Model Context Protocol** を選択します。

![The Add tool panel with Model Context Protocol selected and New tool highlighted.](../../../assets/images/make/copilot-studio-10/add-tool-02.png)

<cc-end-step lab="mcs10" exercise="4" step="1" />

### 手順 2: OAuth 2.0 認証の構成

次の設定で MCP サーバー接続と OAuth 2.0 を構成します。

【基本設定】

- **Server name**: 

```text
HR MCP Server Secured
```

- **Server description**: 

```text
Securely manages HR candidates with OAuth 2.0 authentication for enterprise compliance
```

- **URL**: 先ほど保存した dev tunnel URL (「Connect via browser」の URL)

【認証設定】

**Authentication method** として **OAuth 2.0** を選択し、**Manual** を選びます。

![The MCP server configuration dialog showing OAuth 2.0 Manual selected as authentication method.](../../../assets/images/make/copilot-studio-10/oauth-config-01.png)

OAuth 2.0 の各項目を入力します。

- **Client ID**: **HR MCP Client - Copilot Studio** アプリの Application (client) ID  
- **Client secret**: 保存しておいたクライアント シークレット  
- **Authorization URL template**: 

```text
https://login.microsoftonline.com/[YOUR_TENANT_ID]/oauth2/v2.0/authorize
```

- **Token URL template**: 

```text
https://login.microsoftonline.com/[YOUR_TENANT_ID]/oauth2/v2.0/token
```

- **Refresh URL template**: 

```text
https://login.microsoftonline.com/[YOUR_TENANT_ID]/oauth2/v2.0/token
```

- **Scopes**: スペース区切りで入力

```text
openid profile email
```

!!! important
    ここで入力するスコープは一時的なものです。後でセキュア HR MCP サーバーに必要な実際のスコープに置き換えます。

![The OAuth 2.0 configuration section with all fields filled in.](../../../assets/images/make/copilot-studio-10/oauth-config-02.png)

**Create** を選択して MCP サーバー設定を保存します。

<cc-end-step lab="mcs10" exercise="4" step="2" />

### 手順 3: Entra ID での Redirect URI 設定

MCP ツール作成後、Copilot Studio が **Redirect URL** を生成します。この URL を **HR MCP Consumer** アプリに設定します。

1. Copilot Studio で表示された Redirect URL をコピー  

![The MCP tool configuration showing the Redirect URL that needs to be configured in Entra ID.](../../../assets/images/make/copilot-studio-10/redirect-url-01.png)

2. [Microsoft Entra 管理センター](https://entra.microsoft.com){target=_blank} へ移動  
3. **Applications** → **App registrations**  
4. **HR MCP Consumer** アプリを選択  
5. **Authentication** を選択  
6. **+ Add Redirect URI** → **Web** を選択  
7. コピーした Redirect URI を貼り付け  
8. **Configure** を選択  

![The Authentication page showing the Redirect URI configured.](../../../assets/images/make/copilot-studio-10/entra-redirect-uri-01.png)

<cc-end-step lab="mcs10" exercise="4" step="3" />

Copilot Studio に戻り、ツール設定を続行します。**Next** を選択すると接続を求めるダイアログが表示されますが、接続は保留にして次の手順 4 へ進みます。

### 手順 4: Power Apps コネクタの構成 (オプション)

!!! info
    環境によっては、この手順が必要になる場合があります。Copilot Studio で作成した MCP コネクタは Power Apps にも登録され、追加設定が必要なケースがあります。

1. [https://make.powerautomate.com](https://make.powerautomate.com){target=_blank} にアクセス  
2. 右上の環境ピッカーで `Copilot Dev Camp` を選択  
3. **More** → **Discover all** → **Custom connectors** を選択  
4. **HR MCP Server Secured** という名前のコネクタを探し、鉛筆アイコンで **Edit**  

![The Power Platform connectors page with the connector for the MCP server highlighted and the pencil to edit highligthed.](../../../assets/images/make/copilot-studio-10/power-connector-01.png)

6. **Security** タブを開き **Edit** を選択  

![The Power Platform connectors page with the connector for the MCP server highlighted and the pencil to edit highligthed.](../../../assets/images/make/copilot-studio-10/power-connector-02.png)

8. **Client Secret** に **HR MCP Consumer** アプリで取得したシークレット値を入力  
9. **Resource URL** に Application ID URI、つまり `[YOUR_DEVTUNNEL_URL]` (例: `https://hr-mcp-secured.devtunnels.ms`) を入力  
10. **Scope** にカスタム スコープ名 **HR.Manage** を入力  
11. 画面上部の **Update connector** をクリック  

![The Power Platform connector security configuration page with updated settings.](../../../assets/images/make/copilot-studio-10/power-connector-03.png)

<cc-end-step lab="mcs10" exercise="4" step="4" />

### 手順 5: MCP ツール構成の完了

Copilot Studio に戻り、MCP ツール構成と接続を完了します。

1. MCP ツール設定ダイアログで **Connection** が **Not connected** と表示されます  
2. **Not connected** をクリックして接続オプションを開き、**Create new connection** を選択  

![The MCP tool configuration dialog showing the Not connected status and the option to create a new connection.](../../../assets/images/make/copilot-studio-10/complete-connection-01.png)

4. 表示されたダイアログで **Create** を選択し、接続作成を開始  
5. Copilot Studio が Microsoft Entra ID での認証を促します  
6. 有効なユーザー アカウントを選択または資格情報を入力  
7. アプリが HR MCP サーバーへアクセスする許可を求められた場合は承認  

![The authentication dialog prompting for user credentials to establish the connection.](../../../assets/images/make/copilot-studio-10/complete-connection-02.png)

8. 認証に成功すると接続が確立され、緑のチェックマークが表示されます  
9. **Add and configure** を選択して MCP ツールをエージェントに追加  

![The MCP tool configuration dialog showing the connection established and the Add and configure button.](../../../assets/images/make/copilot-studio-10/complete-connection-03.png)

MCP サーバーの設定ページが表示され、利用可能なツールが一覧表示されます。

- list_candidates  
- search_candidates  
- add_candidate  
- update_candidate  
- remove_candidate  

![The MCP server details page showing all available tools.](../../../assets/images/make/copilot-studio-10/tool-details-01.png)

セキュア MCP サーバーの構成が完了しました。テストを行いましょう。

<cc-end-step lab="mcs10" exercise="4" step="5" />

## 演習 5 : エージェントのテスト

この演習では、エージェントをテストして OAuth 2.0 認証が正しく機能することを確認します。

### 手順 1: エージェントの発行

テスト前にエージェントを発行します。

1. Copilot Studio 右上の **Publish** を選択  
2. 発行が完了するまで待機  

<cc-end-step lab="mcs10" exercise="5" step="1" />

### 手順 2: 認証フローのテスト

Copilot Studio のテスト パネルを開き、次のプロンプトを入力します。

```text
List all candidates
```

初回のセキュア MCP サーバー利用時には、エージェントがユーザーの資格情報を使用して外部サービスへアクセスする **Allow** の確認が表示されます。**Allow** をクリックしてください。

![The message asking to "Allow" using user's credentials to access the external service.](../../../assets/images/make/copilot-studio-10/allow-secure-connection-01.png)

接続されていない、またはトークンが期限切れの場合は **Open connection manager** が表示されます。その際は以下を実施します。

1. **Open connection manager** を選択  
2. 新しいタブで接続ページが開くので **Connect** をクリック  
3. 職場アカウントでサインイン  
4. 必要に応じて HR MCP サーバーへのアクセスを許可  
5. 認証成功後、接続ステータスが **Connected** になります  

![The message asking to "Allow" using user's credentials to access the external service.](../../../assets/images/make/copilot-studio-10/connection-01.png)

<cc-end-step lab="mcs10" exercise="5" step="2" />

### 手順 3: MCP ツールのテスト

認証後、プロンプトが処理されます。処理されない場合は再度入力してください。

```text
List all candidates
```

エージェントはセキュア MCP サーバーへ正常にアクセスし、候補者リストを返すはずです。

![The test panel showing successful retrieval of candidates after authentication.](../../../assets/images/make/copilot-studio-10/test-success-01.png)


!!! tip "トークン キャッシュ"
    初回認証後、アクセストークンは一定期間キャッシュされます。トークンが期限切れまたは失効しない限り、毎回認証を求められることはありません。

他のツールもテストしてみましょう。

**候補者を検索:**
```text
Search for candidates with Training skills
```

**特定の候補者を取得:**
```text
Get candidate with email bob.brown@example.com
```

!!! info "MCP サーバーのアクティビティ監視"
    Copilot Studio から MCP サーバーを呼び出すと、.NET アプリケーションである MCP サーバーがターミナルにログを出力します。各ツール メソッドの呼び出しや、リクエストヘッダーに含まれる `Authorization: Bearer` JWT アクセストークンを確認できます。認証が正しく機能しているかのデバッグに役立ちます。

    ![The terminal window showing MCP server logs with tool method calls and OAuth bearer token evidence.](../../../assets/images/make/copilot-studio-10/dotnet-terminal-mcp-call-secured.png)

<cc-end-step lab="mcs10" exercise="5" step="4" />

---8<--- "ja/mcs-congratulations.md"

このラボ MCS10 - OAuth 2.0 で MCP サーバーを利用する を完了しました！

このラボでは、次の内容を学習しました。

- OAuth 2.0 の JWT トークン検証を使用した MCP サーバーの構成  
- セキュアな API アクセスのための Microsoft Entra ID アプリケーション (バックエンド / クライアント) の登録  
- Copilot Studio での OAuth 2.0 Authorization Code Flow の設定  
- 企業レベルの認証で保護された MCP ツールの利用  

OAuth 2.0 認証を導入することで、HR 候補者管理システムを業界標準のセキュリティで保護できました。これは、データ セキュリティとユーザー認証が重要な本番環境で不可欠なアプローチです。

<!-- <cc-next />  -->

<img src="https://m365-visitor-stats.azurewebsites.net/copilot-camp/make/copilot-studio/10-mcp-oauth--ja" />