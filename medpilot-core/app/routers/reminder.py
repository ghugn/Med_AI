from fastapi import APIRouter
import time
import uuid
import logging

from app.schemas import ReminderRequest, ReminderResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Reminder"])

@router.post("/api/reminder", response_model=ReminderResponse)
async def reminder_endpoint(req: ReminderRequest):
    """Phân tích hồ sơ lâm sàng và tạo nhắc nhở (dữ liệu demo)."""
    logger.info(f"[Reminder] MOCK request_id={req.request_id}")
    start = time.time()

    # 3. Handle UUID to avoid Pyre string slice lint
    new_id = str(uuid.uuid4()).split("-")[0]

    response = ReminderResponse(
        request_id=req.request_id or f"req_reminder_{new_id}",
        missing_critical_info=[
            "Chưa rõ cảm giác rát (burning) có hay không",
            "Chưa rõ tiền sử dị ứng cá nhân hoặc gia đình",
            "Chưa biết tên kem đã bôi trước đó",
            "Chưa khai thác có dùng găng tay khi rửa chén hay không",
        ],
        questions_to_ask=[
            "Thời điểm bắt đầu rửa chén nhiều hơn có trùng với lúc khởi phát tổn thương không?",
            "Bệnh nhân có dùng găng tay không, nếu có thì là loại nào?",
            "Ngoài nước rửa chén còn tiếp xúc với mỹ phẩm, chất tẩy khác, kim loại hoặc chất mới nào không?",
            "Có tiền sử hen, viêm mũi dị ứng, chàm hoặc cơ địa dị ứng không?",
            "Loại kem đã bôi trước đó là gì, có còn vỏ thuốc hoặc nhớ thành phần nào không?",
            "Có cảm giác rát, châm chích, nóng da hoặc nứt da không?",
            "Mức độ ảnh hưởng sinh hoạt hằng ngày như thế nào?",
        ],
        red_flags=[
            "Hiện chưa có red flags rõ rệt (không sốt, không đau, không chảy dịch, không triệu chứng toàn thân)",
            "Cần khám trực tiếp để đánh giá nguy cơ bội nhiễm và mức độ viêm thực tế",
        ],
        possible_considerations=[
            "Viêm da tiếp xúc kích ứng — tổn thương ở bàn tay, triệu chứng tăng khi tiếp xúc nước rửa chén",
            "Viêm da tiếp xúc dị ứng — cần loại trừ nếu có yếu tố tiếp xúc dị ứng nguyên cụ thể",
            "Đợt bùng phát viêm da cơ địa — có tiền sử viêm da cơ địa 2 năm trước",
        ],
        suggested_next_checks=[
            "Khám trực tiếp hình thái tổn thương — đánh giá nứt, dày da, lichen hóa",
            "Patch test (thử nghiệm áp da) nếu nghi viêm da tiếp xúc dị ứng",
            "Khai thác thêm tiền sử cơ địa dị ứng để hỗ trợ phân biệt",
        ],
        guideline_evidence=[
            "Hướng dẫn BAD (British Association of Dermatologists) về viêm da tiếp xúc",
            "Khuyến cáo AAD về quản lý viêm da cơ địa ở người lớn",
        ],
        latency_ms=round((time.time() - start) * 1000),
        model_version="demo_v1",
    )

    logger.info(f"[Reminder] MOCK done in {response.latency_ms}ms")
    return response
