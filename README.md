# remove-formulas-from-excel
[![codecov](https://codecov.io/gh/team-care/remove-formulas-from-excel/branch/master/graph/badge.svg)](https://codecov.io/gh/team-care/remove-formulas-from-excel)

Excelファイルから数式を除去する。


## 1 デプロイ手順

### 1.1 環境構築

- AWS CLI
    - credentialの設定が必要
- npm/serverless
    ```
    npm install -g serverless
    ```
- docker
    - serverless-python-requirementsで使用

### 1.2 デプロイ

1. 以下のコマンドでnpmパッケージをインストール
    ```
    npm ci
    ```

2. 以下のコマンドでデプロイ
    ```
    sls deploy -v --stage {ステージ名}
    ```
    ※ステージ名は任意に設定する。<br>
    　作成されるリソースが全て{ステージ名}-hogehogeになる。

## 2 動作確認手順

1. LambdaコンソールのAPI GatewayトリガーからエンドポイントとAPIキーを下記のコマンドに記入して実行する。
    ```
    curl -X POST -H 'Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' -H 'x-api-key: {APIキー}' --data-binary @{Excelファイルのパス} {エンドポイント} | base64 -di > {保存するファイルのパス}
    ```

2. 保存されたExcelファイルから数式が除去されていることを確認する。

## 3 設計

### 3.1 リクエストヘッダー

| キー | 項目名 | 必須 | 属性 |
| -- | -- | -- | -- |
| x-api-key | APIキー | 必須 | 半角英数字 |
| Content-Type | コンテントタイプ | 必須 | 半角英字 |

### 3.2 リクエストボディ

| 項目名 | 必須 | 属性 |
| -- | -- | -- |
| 入力ファイル | 必須 | ファイル |

### 3.3 レスポンスヘッダー

| キー | 項目名 | 属性 |
| -- | -- | -- |
| Content-Type | MIME タイプ | 半角英字 |

### 3.4 レスポンスボディ

| 項目名 | 属性 |
| -- | -- |
| 出力ファイル | ファイル |

### 3.5 ステータスコード

| コード | ステータス |
| -- | -- |
| 200 | 成功 |
| 400 | 無効なリクエスト |
| 408 | タイムアウト |
| 503 | 変換失敗 |
