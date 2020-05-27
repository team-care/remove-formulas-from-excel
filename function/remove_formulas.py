import base64
import json
import os
import pathlib
from logging.config import fileConfig
from logging import getLogger
from openpyxl import load_workbook


class LambdaRuntimeException(Exception):
    """
    Lambda実行中に発生するException

    Attributes
    ----------
    _code : int
        ステータスコード
    _messages : str
        エラーメッセージ
    _content_type : str
        応答のコンテントタイプ
    """

    def __init__(self, code, messages, content_type="application/json"):
        self._code = code
        self._messages = messages
        self._content_type = content_type

    def __str__(self):
        """
        オブジェクトの文字列表現を定義する。
        API Gatewayで処理できるようにエラーの詳細をdictで返す。

        Returns
        -------
        response : dict
            エラーの詳細
        """
        response = {
            "statusCode": self._code,
            "headers": {
                "Content-Type": self._content_type
            },
            "body": {
                "message": self._messages
            }
        }
        return json.dumps(response)


def handler(event, context):
    """
    AWS Lambdaが起動したときに最初に呼び出される処理。

    Parameters
    ----------
    event : dict
        API Gatewayから受け取る入力パラメータ
    context : dict
        contextは使用しないので、特に考える必要はない。
        以下が公式のドキュメント。
        https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/python-context.html

    Raises
    -------
    LambdaRuntimeException
        処理中にエラーが発生した場合にAPI Gatewayに返すException

    Returns
    -------
    dict
        httpレスポンス
    """
    try:
        # loggerの設定
        logger = getLogger(__name__)
        directory = str(pathlib.Path(__file__).parent)
        fileConfig(f"{directory}/logging.conf", disable_existing_loggers=False)

        # Excelの情報を定義
        xlsx_path = "/tmp/tmp.xlsx"
        xlsx_content_type = \
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        # Lambdaのイベント入力を取り出す
        event = json.loads(event) if isinstance(event, str) else event
        input_file = event["body"]
        headers = event["headers"]
        content_type = headers.get("Content-Type")
        content_type = headers["content-type"] if headers.get(
            "content-type") else content_type

        # Content-Typeの確認
        if content_type is None or content_type != xlsx_content_type:
            message = f"Content-Type is not {xlsx_content_type}"
            logger.warning(message)
            raise LambdaRuntimeException(400, message)

        # 入力Excelを一時的に保存
        with open(xlsx_path, "wb") as f:
            f.write(base64.b64decode(input_file.encode("utf8")))

        # Excelファイルの数式を除去して上書きする
        book = load_workbook(
            filename=xlsx_path,
            data_only=True)
        book.save(xlsx_path)

        # Excelファイルのバイナリを取得
        with open(xlsx_path, "rb") as f:
            output_file = f.read()

        # 保存されているExcelファイルの削除
        os.remove(xlsx_path)

        return {
            "statusCode": 200,
            "headers": {
                "content-type": content_type
            },
            "isBase64Encoded": True,
            "body": base64.b64encode(output_file)
        }
    except LambdaRuntimeException as e:
        # 想定内エラーをraise
        raise e
    except Exception:
        # 予期しないエラーをraise
        message = "Unexpected Error"
        logger.exception(message)
        raise LambdaRuntimeException(503, message)
