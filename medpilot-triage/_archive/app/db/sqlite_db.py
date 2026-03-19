import os
import json
import asyncio
import aiosqlite
from datetime import datetime
from app.core.config import settings
from app.core.logging import logger

CASE_DATA_DIR = os.path.join("data", "cases")

JSON_FIELDS = [
    "Triệu_chứng_Transcript", "Extracted_Entities",
    "Chẩn_đoán_sơ_bộ", "Hướng_giải_quyết", "Draft_Note", "Problem_List",
    "Missing_Info"
]

# Thư mục DB
# Sửa cài đặt từ config, do hiện config đang trỏ tới .xlsx
DB_FILENAME = settings.DB_FILE.replace(".xlsx", ".db")

def _save_case_details_sync(case_id: str, record: dict) -> None:
    try:
        json_data = {k: record.get(k) for k in JSON_FIELDS if k in record}
        file_path = os.path.join(CASE_DATA_DIR, f"{case_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Lỗi ghi json details cho case {case_id}: {e}")

def _load_case_details_sync(case_id: str) -> dict:
    try:
        file_path = os.path.join(CASE_DATA_DIR, f"{case_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Lỗi đọc json details cho case {case_id}: {e}")
    return {}

async def init_db() -> None:
    """Khởi tạo database.db và thư mục JSON nếu chưa tồn tại"""
    os.makedirs(CASE_DATA_DIR, exist_ok=True)
    
    # Tạo bảng if not exists
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS cases (
        Case_ID TEXT PRIMARY KEY,
        Ngày_giờ_khám TEXT,
        Bác_sĩ_ID TEXT,
        Họ_tên_BN TEXT,
        Tuổi TEXT,
        Giới_tính TEXT,
        Red_Flag TEXT,
        Uncertainty_Score REAL,
        Safety_Status TEXT,
        SpO2_Final TEXT,
        HR_Final TEXT,
        BP_Final TEXT
    );
    """
    try:
        async with aiosqlite.connect(DB_FILENAME) as db:
            await db.execute(create_table_query)
            await db.commit()
            logger.info(f"Đã khởi tạo bảng cases trong {DB_FILENAME} thành công.")
    except Exception as e:
        logger.error(f"Lỗi khởi tạo DB SQLite {DB_FILENAME}: {e}")

async def save_case(data_dict: dict) -> None:
    """Thêm mới một dòng (ca bệnh) trực tiếp vào sqlite async"""
    case_id = data_dict.get("Case_ID", data_dict.get("case_id"))
    if not case_id:
        return
        
    # Chuẩn hóa string
    processed = data_dict.copy()
    for k, v in processed.items():
        if isinstance(v, list) or isinstance(v, dict):
            processed[k] = str(v)
            
    # Tách dữ liệu JSON
    await asyncio.to_thread(_save_case_details_sync, case_id, processed)
    
    # Lấy các trường thuộc bảng sqlite
    db_keys = [
        "Case_ID", "Ngày_giờ_khám", "Bác_sĩ_ID", "Họ_tên_BN", "Tuổi", "Giới_tính",
        "Red_Flag", "Uncertainty_Score", "Safety_Status",
        "SpO2_Final", "HR_Final", "BP_Final"
    ]
    
    db_record = {k: processed.get(k) for k in db_keys}
    
    columns = ", ".join(db_record.keys())
    placeholders = ", ".join(["?"] * len(db_record))
    values = tuple(db_record.values())
    
    query = f"INSERT OR REPLACE INTO cases ({columns}) VALUES ({placeholders})"
    
    try:
        async with aiosqlite.connect(DB_FILENAME) as db:
            await db.execute(query, values)
            await db.commit()
    except Exception as e:
        logger.error(f"Lỗi ghi sqlite ({query}): {e}")

async def update_case(case_id: str, update_dict: dict) -> None:
    """Cập nhật thông tin record case trong sqlite"""
    if not case_id:
        return
        
    # Luôn phải fetch state hiện tại vì JSON có thể cần update nối (không thay thế hoàn toàn)
    current_case = await get_case(case_id)
    if not current_case:
        logger.warning(f"Không tìm thấy Case_ID '{case_id}' để cập nhật vào DB.")
        # Hoặc tự log tạo mới tùy usecase, tạm bỏ qua theo đúng logic cũ
        return
        
    processed_updates = update_dict.copy()
    for k, v in processed_updates.items():
        if isinstance(v, list) or isinstance(v, dict):
            processed_updates[k] = str(v)
            
    # Gộp state cũ và mới
    current_case.update(processed_updates)
    
    # Trích tách JSON save
    await asyncio.to_thread(_save_case_details_sync, case_id, current_case)
    
    # Lấy các field SQL để update
    db_keys = [
        "Ngày_giờ_khám", "Bác_sĩ_ID", "Họ_tên_BN", "Tuổi", "Giới_tính",
        "Red_Flag", "Uncertainty_Score", "Safety_Status",
        "SpO2_Final", "HR_Final", "BP_Final"
    ]
    
    update_fields = {}
    for k in db_keys:
        if k in processed_updates:
            update_fields[k] = processed_updates[k]
            
    if update_fields:
        set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
        values = tuple(update_fields.values()) + (case_id,)
        
        query = f"UPDATE cases SET {set_clause} WHERE Case_ID = ?"
        
        try:
            async with aiosqlite.connect(DB_FILENAME) as db:
                await db.execute(query, values)
                await db.commit()
        except Exception as e:
            logger.error(f"Lỗi cập nhật sqlite ({query}): {e}")

async def get_case(case_id: str) -> dict | None:
    """Lấy thông tin một ca bệnh từ sqlite + nối với JSON"""
    if not case_id:
        return None
        
    query = "SELECT * FROM cases WHERE Case_ID = ?"
    
    try:
        async with aiosqlite.connect(DB_FILENAME) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, (case_id,)) as cursor:
                row = await cursor.fetchone()
                
        if row:
            case_data = dict(row)
            json_data = await asyncio.to_thread(_load_case_details_sync, case_id)
            case_data.update(json_data)
            return case_data
            
    except Exception as e:
        logger.error(f"Lỗi select sqlite cho case {case_id}: {e}")
        
    return None

def _log_ai_interaction_sync(case_id: str, endpoint: str, latency: float, error_msg: str, ai_output: str) -> None:
    try:
        log_data = {
            "Case_ID": case_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "endpoint": endpoint,
            "latency": latency,
            "error": error_msg,
            "output": ai_output
        }
        with open("ai_logs.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
        logger.info(f"Đã ghi log API {endpoint} mất {latency}s cho Case {case_id} vào ai_logs.jsonl")
    except Exception as e:
        logger.error(f"Lỗi ghi nhận log: {e}")

async def log_ai_interaction(case_id: str, endpoint: str, latency: float, error_msg: str, ai_output: str) -> None:
    """Ghi log tương tác AI vào ai_logs.jsonl (async)"""
    await asyncio.to_thread(_log_ai_interaction_sync, case_id, endpoint, latency, error_msg, ai_output)
