import asyncio
from app.db.excel_db import init_db, save_case, _flush_to_excel

async def main():
    init_db()
    await save_case({'Case_ID': 'TEST_1', 'Họ_tên_BN': 'Nguyen Van A', 'Draft_Note': 'This is draft note json only', 'Tuổi': 30})
    await _flush_to_excel()
    print("Success!")

if __name__ == "__main__":
    asyncio.run(main())
