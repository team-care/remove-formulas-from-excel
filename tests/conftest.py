import base64
import os
import pytest
import shutil


@pytest.fixture(scope="session", autouse=True)
def fixture_make_tmp_dir():
    """
    一時ディレクトリを作成するフィクスチャ
    テスト実行後、ディレクトリ内のフォルダとファイルを削除する。
    """
    tmp_dir = "/tmp"
    if os.path.exists(tmp_dir) is False:
        os.makedirs(tmp_dir)
    setup_file_list = os.listdir(tmp_dir)
    yield
    teardown_file_list = os.listdir(tmp_dir)
    for one_file in teardown_file_list:
        if one_file in setup_file_list:
            continue
        target_dir = os.path.join(tmp_dir, one_file)
        if os.path.isdir(target_dir):
            shutil.rmtree(target_dir)
        else:
            os.remove(target_dir)


@pytest.fixture(scope="function", autouse=True)
def get_test_xlsx():
    """
    テスト用のExcelのデータと各セルの値を返すフィクスチャ

    Yields
    ------
    xlsx_data, cell_value : tupple (str, dict)
        Excelのデータ, 各セルの値
    """
    tmp_xlsx_path = "./tests/test.xlsx"
    cell_value = {
        "A1": 2,
        "B1": 4,
        "C1": 6,
        "A2": 6,   # 実際は"=SUM(A1,B1)"
        "B2": 10,  # 実際は"=B1+C1"
        "C2": 8    # 実際は"=C1+A1"
    }
    with open(tmp_xlsx_path, "rb") as f:
        xlsx_data = base64.b64encode(f.read()).decode("utf8")
    yield xlsx_data, cell_value
