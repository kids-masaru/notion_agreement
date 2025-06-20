import os
import csv
from notion_client import Client
from dotenv import load_dotenv
from datetime import datetime

# 環境変数読み込み
load_dotenv()
notion = Client(auth=os.getenv('NOTION_TOKEN'))
PARENT_PAGE_ID = os.getenv('PARENT_PAGE_ID')

def create_database(csv_path: str, db_name: str):
    """CSVからNotionデータベースを作成（プロパティタイプ修正版）"""
    # プロパティスキーマの定義
    properties = {
        "名前": {"title": {}},
        "作業順": {"multi_select": {}},
        "対応": {"select": {}},
        "担当": {"multi_select": {}},
        "説明": {"rich_text": {}}
    }
    
    # データベース作成
    new_db = notion.databases.create(
        parent={"page_id": PARENT_PAGE_ID, "type": "page_id"},
        title=[{"type": "text", "text": {"content": db_name}}],
        properties=properties
    )
    return new_db["id"]

def add_rows_to_db(db_id: str, csv_path: str):
    """CSVデータを行として追加（マルチセレクト対応）"""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # プロパティの変換
            properties = {
                "名前": {
                    "title": [{"text": {"content": row["名前"]}}]
                },
                "作業順": {
                    "multi_select": [{"name": row["作業順"].strip()}]
                },
                "対応": {
                    "select": {"name": row["対応"].strip()}
                },
                "担当": {
                    "multi_select": [{"name": tag.strip()} for tag in row["担当"].split(',')]
                },
                "説明": {
                    "rich_text": [{"text": {"content": row["説明"]}}]
                }
            }
            notion.pages.create(parent={"database_id": db_id}, properties=properties)

if __name__ == "__main__":
    CSV_PATH = "task.csv"
    DB_NAME = f"タスク管理DB - {datetime.now().strftime('%Y/%m/%d')}"
    
    db_id = create_database(CSV_PATH, DB_NAME)
    add_rows_to_db(db_id, CSV_PATH)
    print("✅ データベース作成とデータインポートが完了しました！")