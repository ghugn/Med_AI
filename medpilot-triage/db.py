"""
Database Layer — MedPilot PoC
Excel-based DB with in-memory cache and JSON sidecar files.
"""
import os
import pandas as pd
from datetime import datetime
import json
import asyncio
import logging

logger = logging.getLogger("medpilot")

# ─── Config ──────────────────────────────────────────────────────────────────

DB_FILE = "database.xlsx"

DB_HEADERS = [
    "Case_ID", "Ngày_giờ_khám", "Bác_sĩ_ID", "Họ_tên_BN", "Tuổi", "Giới_tính",
    "Red_Flag", "Uncertainty_Score", "Safety_Status",
    "SpO2_Final", "HR_Final", "BP_Final"
]

JSON_FIELDS = [
    "Triệu_chứng_Transcript", "Extracted_Entities",
    "Chẩn_đoán_sơ_bộ", "Hướng_giải_quyết", "Draft_Note", "Problem_List",
    "Missing_Info"
]

CASE_DATA_DIR = os.path.join("data", "cases")

# ─── In-memory cache ─────────────────────────────────────────────────────────

_case_cache = {}
_dirty_cases = set()
_db_lock = asyncio.Lock()


# ─── JSON sidecar helpers ────────────────────────────────────────────────────

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


# ─── Init ────────────────────────────────────────────────────────────────────

def init_db() -> None:
    """Khởi tạo database.xlsx và thư mục JSON nếu chưa tồn tại, nạp cache"""
    os.makedirs(CASE_DATA_DIR, exist_ok=True)
    if not os.path.exists(DB_FILE):
        logger.info(f"Đang khởi tạo file giả lập: {DB_FILE}...")
        df = pd.DataFrame(columns=DB_HEADERS)
        df.to_excel(DB_FILE, index=False, engine='openpyxl')
        logger.info(f"Đã tạo file {DB_FILE} thành công")
    else:
        logger.info(f"File {DB_FILE} đã tồn tại. Đang nạp bộ đệm (cache)...")
        try:
            df = pd.read_excel(DB_FILE, engine='openpyxl')
            for _, row in df.iterrows():
                if "Case_ID" in row and pd.notna(row["Case_ID"]):
                    clean_row = {k: v for k, v in row.to_dict().items() if pd.notna(v)}
                    case_id = clean_row["Case_ID"]
                    json_data = _load_case_details_sync(case_id)
                    clean_row.update(json_data)
                    _case_cache[case_id] = clean_row
            logger.info("Nạp bộ đệm thành công.")
        except Exception as e:
            logger.error(f"Lỗi nạp bộ đệm: {e}")


# ─── Flush dirty cases to Excel ──────────────────────────────────────────────

def _flush_dirty_cases_sync(cases_to_flush: dict) -> None:
    try:
        if not cases_to_flush:
            return
        if os.path.exists(DB_FILE):
            df = pd.read_excel(DB_FILE, engine='openpyxl')
        else:
            df = pd.DataFrame(columns=DB_HEADERS)
        for case_id, record in cases_to_flush.items():
            _save_case_details_sync(case_id, record)
            excel_record = {k: v for k, v in record.items() if k not in JSON_FIELDS}
            mask = df['Case_ID'] == case_id
            if mask.any():
                for k, v in excel_record.items():
                    if k not in df.columns:
                        df[k] = None
                    df.loc[mask, k] = v
            else:
                df_new = pd.DataFrame([excel_record])
                if not df_new.empty:
                    df = pd.concat([df, df_new], ignore_index=True)
        missing_cols = set(DB_HEADERS) - set(df.columns)
        for col in missing_cols:
            df[col] = None
        cols = [c for c in DB_HEADERS if c in df.columns] + [c for c in df.columns if c not in DB_HEADERS and c not in JSON_FIELDS]
        for col in JSON_FIELDS:
            if col in df.columns:
                df.drop(columns=[col], inplace=True)
        df = df[cols]
        df.to_excel(DB_FILE, index=False, engine='openpyxl')
    except Exception as e:
        logger.error(f"Lỗi đồng bộ file excel: {e}")

async def _flush_to_excel():
    async with _db_lock:
        if not _dirty_cases:
            return
        dirty = list(_dirty_cases)
        _dirty_cases.clear()
        cases_to_flush = {cid: _case_cache[cid] for cid in dirty if cid in _case_cache}
        await asyncio.to_thread(_flush_dirty_cases_sync, cases_to_flush)


# ─── CRUD ────────────────────────────────────────────────────────────────────

async def save_case(data_dict: dict) -> None:
    """Thêm mới một dòng (ca bệnh) vào bộ đệm và ghi file ngầm"""
    case_id = data_dict.get("Case_ID", data_dict.get("case_id"))
    if not case_id:
        return
    processed = data_dict.copy()
    for k, v in processed.items():
        if isinstance(v, list) or isinstance(v, dict):
            processed[k] = str(v)
    _case_cache[case_id] = processed
    _dirty_cases.add(case_id)
    asyncio.create_task(_flush_to_excel())

async def update_case(case_id: str, update_dict: dict) -> None:
    """Cập nhật thông tin trong bộ đệm và ghi file ngầm"""
    if case_id in _case_cache:
        processed = update_dict.copy()
        for k, v in processed.items():
            if isinstance(v, list) or isinstance(v, dict):
                processed[k] = str(v)
        _case_cache[case_id].update(processed)
        _dirty_cases.add(case_id)
        asyncio.create_task(_flush_to_excel())
    else:
        logger.warning(f"Không tìm thấy Case_ID '{case_id}' để cập nhật vào DB.")

async def get_case(case_id: str) -> dict | None:
    """Lấy thông tin một ca bệnh từ bộ đệm"""
    return _case_cache.get(case_id)


# ─── AI Logging ──────────────────────────────────────────────────────────────

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
