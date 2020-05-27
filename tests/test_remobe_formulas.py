import json
import base64
import pytest
from function.remove_formulas import handler
from openpyxl import load_workbook


@pytest.mark.parametrize(
    ("is_exists_content_type", "is_exists_body"),
    [(True, True), (False, True), (True, False)]
)
def test_handler(is_exists_content_type, is_exists_body,
                 fixture_make_tmp_dir, get_test_xlsx):
    """
    remove_formulasのhandlerを以下の観点でテストする。

    - 正常系
      - 返却されるExcelから数式が除去されている。

    - 異常系（リクエストパラメータに不備がある）
      - エラーとして正しいコード、メッセージが返る。

    Parameters
    ----------
    is_exists_content_type : bool
        リクエストにContent-Typeが存在するかを制御するフラグ
    is_exists_body : bool
        リクエストにbodyが存在するかを制御するフラグ
    fixture_make_tmp_dir : NoneType
        一時ディレクトリを作成するフィクスチャ
    get_test_xlsx : list
        テスト用のExcelのデータと各セルの値を返すフィクスチャ
    """

    # 一時フォルダ作成
    fixture_make_tmp_dir

    # 入力パラメータを作成
    xlsx_data, cell_value = get_test_xlsx
    xlsx_path = "/tmp/tmp.xlsx"
    event = {
        "body": None,
        "headers": {
            "content-type": None
        }
    }
    context = {}
    if is_exists_content_type:
        event["headers"]["content-type"] = \
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if is_exists_body:
        event["body"] = xlsx_data

    # 正常系のテストを実施
    if is_exists_content_type and is_exists_body:
        response = handler(event, context)
        with open(xlsx_path, "wb") as f:
            f.write(base64.b64decode(response["body"]))
        book = load_workbook(xlsx_path)
        sheet = book.active
        for cell in cell_value:
            assert sheet[cell].value == cell_value[cell]
    # 異常系のテストを実施
    elif not is_exists_content_type and is_exists_body:
        try:
            handler(event, context)
        except Exception as e:
            e = json.loads(str(e))
            assert e["statusCode"] == 400
            assert e["headers"]["Content-Type"] == "application/json"
            assert e["body"]["message"].startswith("Content-Type is not")
    # 異常系のテストを実施
    elif is_exists_content_type and not is_exists_body:
        try:
            handler(event, context)
        except Exception as e:
            e = json.loads(str(e))
            assert e["statusCode"] == 503
            assert e["headers"]["Content-Type"] == "application/json"
            assert e["body"]["message"] == "Unexpected Error"
