from fastapi import APIRouter
import time
import uuid
import logging

from app.schemas import ScribeRequest, ScribeResponse, ClinicalInfo, StructuredSummary

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Scribe"])

@router.post("/api/scribe", response_model=ScribeResponse)
async def scribe_endpoint(req: ScribeRequest):
    """Trích xuất thông tin lâm sàng từ transcript (dữ liệu demo)."""
    logger.info(f"[Scribe] MOCK request_id={req.request_id}")
    start = time.time()

    transcript = req.transcript or ""
    if not transcript.strip():
        logger.info("[Scribe] Nhận transcript trống, tự động gán Mock Audio Transcript.")
        transcript = "[AUDIO MOCK] Bệnh nhân than phiền nổi đỏ ngứa bong vảy hai bàn tay 2 tuần nay."

    # 3. Handle UUID to avoid Pyre string slice lint
    new_id = str(uuid.uuid4()).split("-")[0]

    response = ScribeResponse(
        request_id=req.request_id or f"req_scribe_{new_id}",
        schema_version=req.schema_version,
        patient_info=req.patient_info,
        clinical_info=ClinicalInfo(
            chief_complaint="Nổi đỏ, ngứa nhiều, bong vảy nhẹ ở hai bàn tay",
            symptoms=["Nổi đỏ", "Ngứa nhiều", "Bong vảy nhẹ"],
            duration="Khoảng 2 tuần",
            onset="Ban đầu hơi đỏ ở mu bàn tay, sau vài ngày ngứa nhiều hơn và lan ra cổ tay",
            lesion_location=["Hai bàn tay", "Cổ tay"],
            lesion_distribution="Hai bên, tay phải nặng hơn",
            itching=True,
            pain=False,
            burning=None,
            scaling=True,
            blister=False,
            discharge=False,
            bleeding=False,
            spreading_pattern="Lan từ mu bàn tay ra cổ tay",
            trigger_factors=["Rửa chén nhiều", "Tiếp xúc nước rửa chén"],
            previous_treatment=["Bôi kem không rõ tên, cải thiện ít"],
            history_update=["Từng bị viêm da cơ địa khoảng 2 năm trước"],
            allergy_update=[],
            medication_update=[],
            current_notes="Bệnh nhân cho biết triệu chứng nặng hơn khi tiếp xúc nước rửa chén.",
        ),
        structured_summary=StructuredSummary(
            one_liner="Nổi đỏ, ngứa nhiều, bong vảy nhẹ hai bàn tay 2 tuần, tay phải nặng hơn, tiền sử viêm da cơ địa",
            important_findings=[
                "Tổn thương hai bên, tay phải nặng hơn",
                "Triệu chứng tăng khi tiếp xúc nước rửa chén",
                "Tiền sử viêm da cơ địa 2 năm trước",
                "Bong vảy nhẹ kèm ngứa nhiều",
            ],
            negative_findings=[
                "Không sốt, không mệt",
                "Không chảy dịch, không chảy máu",
                "Không đau",
                "Không mụn nước",
            ],
            missing_required_fields=["burning", "allergy_update", "previous_treatment (tên thuốc cụ thể)"],
        ),
        draft_note=(
            "Bệnh nhân đến khám vì nổi đỏ, ngứa nhiều, bong vảy nhẹ ở hai bàn tay kéo dài khoảng 2 tuần. "
            "Khởi phát ban đầu hơi đỏ ở mu bàn tay, sau vài ngày ngứa nhiều hơn và lan ra cổ tay. "
            "Tổn thương hai bên, tay phải nặng hơn. Bệnh nhân có ngứa nhiều, bong vảy nhẹ, không đau. "
            "Yếu tố khởi phát: rửa chén nhiều, tiếp xúc nước rửa chén. "
            "Tiền sử: từng bị viêm da cơ địa khoảng 2 năm trước. "
            "Đã bôi kem không rõ tên, cải thiện ít. "
            "Không sốt, không mệt, không chảy dịch, không chảy máu, không mụn nước. "
            "Chưa rõ cảm giác rát, chưa rõ tiền sử dị ứng."
        ),
        missing_required_fields=["burning", "allergy_update", "previous_treatment (tên thuốc cụ thể)"],
        uncertain_fields=["burning", "allergy_update", "previous_treatment"],
        requires_doctor_approval=True,
        field_confidence={
            "chief_complaint": 0.95,
            "symptoms": 0.92,
            "duration": 0.88,
            "onset": 0.85,
            "lesion_location": 0.90,
            "trigger_factors": 0.85,
            "history_update": 0.80,
        },
        latency_ms=round((time.time() - start) * 1000),
        model_version="demo_v1",
    )

    logger.info(f"[Scribe] MOCK done in {response.latency_ms}ms")
    return response
