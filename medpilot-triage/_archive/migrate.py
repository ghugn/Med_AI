import asyncio
import os
import pandas as pd
from app.db.sqlite_db import init_db, DB_FILENAME, save_case
from app.core.config import settings
from app.core.logging import logger

async def migrate_data():
    await init_db()
    
    excel_file = settings.DB_FILE
    if not os.path.exists(excel_file):
        print(f"File {excel_file} không tồn tại. Bỏ qua migrate.")
        return
        
    print(f"Đang đọc dữ liệu từ {excel_file}...")
    try:
        df = pd.read_excel(excel_file, engine='openpyxl')
        count = 0
        for _, row in df.iterrows():
            if "Case_ID" in row and pd.notna(row["Case_ID"]):
                clean_row = {k: v for k, v in row.to_dict().items() if pd.notna(v)}
                await save_case(clean_row)
                count += 1
                
        print(f"Migrate thành công {count} records sang SQLite ({DB_FILENAME}).")
    except Exception as e:
        print(f"Lỗi khi migrate: {e}")

if __name__ == "__main__":
    asyncio.run(migrate_data())
