"""
MedPilot-Core API — Synced with Next.js Frontend
3 endpoints: POST /api/scribe, POST /api/reminder, POST /api/chat
Mode: MOCK DATA with QnA DEMO (trả về dữ liệu demo ngay lập tức)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
import uuid
from difflib import SequenceMatcher

from app.schemas import (
    ScribeRequest, ScribeResponse,
    ReminderRequest, ReminderResponse,
    ChatRequest, ChatResponse,
    PatientInfo, ClinicalInfo, StructuredSummary,
    PatientInput, DoctorApproveInput, APIResponse,
)
import app.db as db
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(level="INFO", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="MedPilot Core API",
    description="Backend cho frontend MedPilot — Scribe, Reminder, Chat (MOCK + QnA DEMO)",
    version="2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("✅ Backend ready! (MOCK + QnA DEMO MODE)")

# Khởi tạo Database cho Case Management
db.init_db()

# ═══════════════════════════════════════════════════════════════════════════════
# QnA DEMO DATA — from BỘ MẪU QnA DEMO CHO DỰ ÁN MEDPILOT.sty
# ═══════════════════════════════════════════════════════════════════════════════

# Chế độ Bệnh nhân — tất cả QnA pairs (Phần 1 + Phần 3)
PATIENT_QNA = [
    # ── Phần 1: 5 QnA hỏi đáp ──
    {
        "question": "Dạo gần đây da tay tôi bị ngứa và hơi đỏ, nguyên nhân có thể do đâu?",
        "keywords": ["ngứa", "đỏ", "da tay", "nguyên nhân"],
        "answer": "Ngứa và đỏ da tay có thể liên quan đến nhiều nguyên nhân khác nhau như kích ứng do xà phòng, nước rửa chén, viêm da tiếp xúc, da khô hoặc chàm. Một số trường hợp cũng có thể liên quan đến dị ứng hoặc các bệnh da liễu khác. Nếu tình trạng kéo dài, tái đi tái lại, lan rộng hoặc gây khó chịu nhiều, bạn nên đi khám bác sĩ da liễu để được đánh giá chính xác. Thông tin này chỉ mang tính tham khảo, không thay thế chẩn đoán của bác sĩ.",
        "safety_notice": "Thông tin chỉ mang tính tham khảo, không thay thế chẩn đoán của bác sĩ.",
        "possible_topics": ["Viêm da tiếp xúc", "Da khô", "Chàm", "Dị ứng da"],
        "when_to_seek_care": ["Tình trạng kéo dài, tái đi tái lại", "Lan rộng hoặc gây khó chịu nhiều"],
        "red_flag_advice": [],
        "confidence_level": "medium",
        "requires_emergency_care": False,
    },
    {
        "question": "Nếu tôi bị như vậy khoảng 2 tuần rồi thì có đáng lo không?",
        "keywords": ["2 tuần", "đáng lo", "kéo dài"],
        "answer": "Nếu triệu chứng kéo dài khoảng 2 tuần mà chưa cải thiện thì bạn nên theo dõi kỹ hơn. Trường hợp ngứa nhiều, ảnh hưởng sinh hoạt, vùng da tổn thương lan rộng hoặc không đỡ sau khi tự chăm sóc cơ bản thì nên đi khám bác sĩ da liễu. Nếu có thêm các dấu hiệu như sưng đau rõ, chảy dịch, nổi bóng nước nhiều, sốt hoặc mệt thì càng nên đi khám sớm. Việc đánh giá trực tiếp sẽ giúp xác định nguyên nhân rõ hơn.",
        "safety_notice": "Triệu chứng kéo dài 2 tuần nên được bác sĩ đánh giá.",
        "possible_topics": ["Theo dõi triệu chứng", "Khi nào cần khám"],
        "when_to_seek_care": ["Ngứa nhiều ảnh hưởng sinh hoạt", "Tổn thương lan rộng", "Sưng đau, chảy dịch, nổi bóng nước, sốt"],
        "red_flag_advice": [],
        "confidence_level": "medium",
        "requires_emergency_care": False,
    },
    {
        "question": "Tôi thấy mỗi lần rửa chén xong thì ngứa hơn, như vậy có liên quan không?",
        "keywords": ["rửa chén", "ngứa hơn", "liên quan", "nước rửa chén"],
        "answer": "Điều đó có thể có liên quan. Một số chất tẩy rửa hoặc việc tiếp xúc nước nhiều lần có thể làm da bị kích ứng hoặc làm nặng thêm tình trạng viêm da sẵn có. Nếu bạn thấy ngứa tăng rõ sau khi rửa chén hoặc tiếp xúc nước rửa chén thì đây là một yếu tố nên chú ý. Bạn có thể thử hạn chế tiếp xúc trực tiếp, dùng găng tay phù hợp, rửa tay nhẹ nhàng và dưỡng ẩm sau khi tiếp xúc. Tuy nhiên, để xác định nguyên nhân cụ thể vẫn cần bác sĩ đánh giá trực tiếp.",
        "safety_notice": "Tiếp xúc chất tẩy rửa có thể làm nặng thêm tình trạng da.",
        "possible_topics": ["Viêm da tiếp xúc kích ứng", "Chất tẩy rửa", "Bảo vệ da tay"],
        "when_to_seek_care": ["Ngứa tăng rõ sau tiếp xúc hóa chất", "Tình trạng không cải thiện sau tự chăm sóc"],
        "red_flag_advice": [],
        "confidence_level": "medium",
        "requires_emergency_care": False,
    },
    {
        "question": "Tôi có thể tự mua thuốc bôi ở tiệm thuốc được không?",
        "keywords": ["mua thuốc", "thuốc bôi", "tiệm thuốc", "tự mua"],
        "answer": "Bạn không nên tự dùng thuốc bôi kéo dài nếu chưa rõ nguyên nhân, đặc biệt là các thuốc có chứa corticoid vì nếu dùng không đúng có thể làm tình trạng da nặng hơn hoặc che lấp triệu chứng thật. Trong lúc chờ đi khám, bạn có thể chăm sóc cơ bản như tránh chất kích ứng, giữ da sạch nhẹ nhàng và dùng kem dưỡng ẩm phù hợp. Nếu tổn thương không cải thiện hoặc nặng hơn, bạn nên đi khám bác sĩ da liễu để được hướng dẫn đúng.",
        "safety_notice": "⚠️ KHÔNG nên tự mua thuốc bôi, đặc biệt corticoid, khi chưa có chẩn đoán.",
        "possible_topics": ["An toàn dùng thuốc", "Corticoid", "Chăm sóc da cơ bản"],
        "when_to_seek_care": ["Tổn thương không cải thiện hoặc nặng hơn sau tự chăm sóc"],
        "red_flag_advice": ["Không tự dùng thuốc corticoid kéo dài — có thể làm nặng hơn hoặc che lấp triệu chứng"],
        "confidence_level": "high",
        "requires_emergency_care": False,
    },
    {
        "question": "Khi nào thì tôi cần đi khám ngay?",
        "keywords": ["khi nào", "khám ngay", "đi khám", "cần khám"],
        "answer": "Bạn nên đi khám sớm nếu có một trong các dấu hiệu sau: tổn thương lan nhanh, đau nhiều, sưng nhiều, chảy dịch, chảy máu, nổi bóng nước nhiều, ngứa quá mức ảnh hưởng sinh hoạt, hoặc kèm sốt, mệt rõ. Nếu có khó thở, sưng môi hoặc lưỡi, choáng, hay phản ứng toàn thân thì cần đến cơ sở y tế ngay. Chatbot chỉ hỗ trợ thông tin tham khảo, không thay thế bác sĩ.",
        "safety_notice": "Nếu có triệu chứng nặng, hãy đến cơ sở y tế ngay.",
        "possible_topics": ["Dấu hiệu nguy hiểm", "Khi nào cần cấp cứu"],
        "when_to_seek_care": [
            "Tổn thương lan nhanh, đau nhiều, sưng nhiều",
            "Chảy dịch, chảy máu, nổi bóng nước nhiều",
            "Ngứa quá mức ảnh hưởng sinh hoạt, sốt, mệt",
        ],
        "red_flag_advice": [
            "Khó thở, sưng môi/lưỡi, choáng → đến cơ sở y tế NGAY",
        ],
        "confidence_level": "high",
        "requires_emergency_care": False,
    },

    # ── Phần 3: 5 lượt hội thoại tự nhiên bệnh nhân ──
    {
        "question": "Da tay tôi bị ngứa và đỏ khoảng 2 tuần nay, tôi nên nghĩ đến vấn đề gì?",
        "keywords": ["da tay", "ngứa", "đỏ", "2 tuần", "vấn đề gì"],
        "answer": "Ngứa và đỏ da tay kéo dài 2 tuần có thể liên quan đến kích ứng, viêm da tiếp xúc, da khô hoặc chàm. Nếu tình trạng không cải thiện, lan rộng hoặc tái phát nhiều lần thì bạn nên đi khám bác sĩ da liễu để được đánh giá chính xác. Đây chỉ là thông tin tham khảo.",
        "safety_notice": "Thông tin chỉ mang tính tham khảo.",
        "possible_topics": ["Kích ứng da", "Viêm da tiếp xúc", "Da khô", "Chàm"],
        "when_to_seek_care": ["Không cải thiện", "Lan rộng", "Tái phát nhiều lần"],
        "red_flag_advice": [],
        "confidence_level": "medium",
        "requires_emergency_care": False,
    },
    {
        "question": "Tôi thấy sau khi rửa chén xong thì ngứa hơn nhiều.",
        "keywords": ["rửa chén", "ngứa hơn nhiều"],
        "answer": "Điều đó có thể gợi ý da của bạn đang bị kích ứng bởi nước rửa chén hoặc việc tiếp xúc nước quá thường xuyên. Bạn nên hạn chế tiếp xúc trực tiếp, có thể dùng găng tay phù hợp và dưỡng ẩm sau đó. Tuy nhiên, để biết chính xác nguyên nhân vẫn cần bác sĩ đánh giá.",
        "safety_notice": "Hạn chế tiếp xúc trực tiếp với chất tẩy rửa.",
        "possible_topics": ["Kích ứng da do hóa chất", "Bảo vệ da tay"],
        "when_to_seek_care": ["Tình trạng không cải thiện sau khi hạn chế tiếp xúc"],
        "red_flag_advice": [],
        "confidence_level": "medium",
        "requires_emergency_care": False,
    },
    {
        "question": "Tôi có cần mua thuốc bôi không?",
        "keywords": ["mua thuốc bôi", "cần mua", "thuốc"],
        "answer": "Bạn không nên tự ý dùng thuốc bôi kéo dài nếu chưa rõ nguyên nhân, nhất là thuốc chứa corticoid. Bạn có thể chăm sóc cơ bản bằng cách tránh chất kích ứng và dưỡng ẩm. Nếu không đỡ, nên đi khám bác sĩ da liễu.",
        "safety_notice": "⚠️ KHÔNG tự ý dùng thuốc bôi kéo dài, đặc biệt corticoid.",
        "possible_topics": ["An toàn dùng thuốc", "Chăm sóc cơ bản"],
        "when_to_seek_care": ["Không đỡ sau chăm sóc cơ bản"],
        "red_flag_advice": ["Không tự dùng thuốc corticoid"],
        "confidence_level": "high",
        "requires_emergency_care": False,
    },
    {
        "question": "Nếu tôi chưa đi khám ngay thì cần theo dõi gì?",
        "keywords": ["chưa đi khám", "theo dõi", "cần theo dõi"],
        "answer": "Bạn nên theo dõi xem tổn thương có lan rộng hơn không, có chảy dịch, chảy máu, đau, nổi bóng nước hoặc ảnh hưởng sinh hoạt nhiều không. Nếu có các dấu hiệu đó thì nên đi khám sớm hơn.",
        "safety_notice": "Theo dõi các dấu hiệu diễn tiến nặng.",
        "possible_topics": ["Theo dõi triệu chứng", "Dấu hiệu cần khám"],
        "when_to_seek_care": ["Lan rộng", "Chảy dịch/máu", "Đau tăng", "Nổi bóng nước", "Ảnh hưởng sinh hoạt"],
        "red_flag_advice": [],
        "confidence_level": "medium",
        "requires_emergency_care": False,
    },
    {
        "question": "Khi nào là mức phải đi khám ngay?",
        "keywords": ["mức phải", "khám ngay", "khi nào"],
        "answer": "Bạn nên đi khám ngay nếu tổn thương lan nhanh, đau nhiều, sưng nhiều, chảy dịch, sốt, nổi bóng nước nhiều hoặc có biểu hiện toàn thân. Nếu có khó thở, sưng môi lưỡi hoặc phản ứng nặng thì cần đến cơ sở y tế ngay.",
        "safety_notice": "⚠️ Các triệu chứng nặng cần đến cơ sở y tế NGAY.",
        "possible_topics": ["Dấu hiệu nguy hiểm", "Cấp cứu da liễu"],
        "when_to_seek_care": ["Tổn thương lan nhanh", "Đau/sưng nhiều", "Chảy dịch, sốt", "Bóng nước nhiều"],
        "red_flag_advice": ["Khó thở, sưng môi lưỡi, phản ứng nặng → cơ sở y tế NGAY"],
        "confidence_level": "high",
        "requires_emergency_care": False,
    },
    
    # ── Bổ sung các câu hỏi gợi ý từ Frontend ──
    {
        "question": "Kem bôi da nào an toàn?",
        "keywords": ["kem bôi", "an toàn", "loại nào"],
        "answer": "Việc lựa chọn kem bôi da phụ thuộc vào tình trạng cụ thể của bạn (da khô, viêm da, nhiễm nấm, v.v.). Các loại kem dưỡng ẩm cơ bản, không mùi, không chứa cồn (như Vaseline, Cetaphil, Cerave) thường an toàn để sử dụng hàng ngày. Tuy nhiên, đối với các loại kem đặc trị chứa thành phần như Corticoid, kháng sinh hoặc thuốc chống nấm, bạn TUYỆT ĐỐI không nên tự ý sử dụng mà cần có sự kê đơn và hướng dẫn của bác sĩ da liễu để tránh các tác dụng phụ nghiêm trọng.",
        "safety_notice": "Không tự ý dùng thuốc bôi đặc trị khi chưa có chỉ định của bác sĩ.",
        "possible_topics": ["Chăm sóc da an toàn", "Kem dưỡng ẩm", "Tác dụng phụ của Corticoid"],
        "when_to_seek_care": ["Triệu chứng không cải thiện với kem dưỡng ẩm cơ bản"],
        "red_flag_advice": ["Tránh lạm dụng kem bôi không rõ nguồn gốc hoặc tự chế"],
        "confidence_level": "medium",
        "requires_emergency_care": False,
    },
    {
        "question": "Dấu hiệu nhiễm nấm da?",
        "keywords": ["dấu hiệu", "nấm da", "nhiễm nấm"],
        "answer": "Nhiễm nấm da thường có các dấu hiệu đặc trưng như: xuất hiện các mảng ban đỏ có hình tròn hoặc bầu dục, bong vảy ở rìa tổn thương, thường kèm theo ngứa nhiều (đặc biệt khi ra mồ hôi). Tổn thương thường thấy ở các vùng da ẩm ướt, có nếp gấp như bẹn, kẽ ngón chân, nách. Tuy nhiên, chẩn đoán chính xác nấm da cần có cái nhìn chuyên môn từ bác sĩ da liễu và đôi khi cần làm xét nghiệm soi nấm trực tiếp. Bạn không nên tự dùng thuốc trị nấm vì có thể làm bệnh khó chữa hơn.",
        "safety_notice": "Cần khám và xét nghiệm để chẩn đoán chính xác nấm da.",
        "possible_topics": ["Nhiễm nấm (Hắc lào, Lang ben)", "Vệ sinh da"],
        "when_to_seek_care": ["Nghi ngờ nhiễm nấm", "Ngứa nhiều, tổn thương lan rộng"],
        "red_flag_advice": [],
        "confidence_level": "medium",
        "requires_emergency_care": False,
    },
    {
        "question": "Viêm da tiếp xúc là gì?",
        "keywords": ["viêm da", "tiếp xúc", "là gì"],
        "answer": "Viêm da tiếp xúc là một tình trạng phát ban tấy đỏ, ngứa ngáy xảy ra khi da của bạn tiếp xúc trực tiếp với một chất gây kích ứng hoặc dị ứng. Có hai loại chính: Viêm da tiếp xúc kích ứng (do các chất như xà phòng mạnh, thuốc tẩy, acid...) tổn thương vùng da tiếp xúc; và Viêm da tiếp xúc dị ứng (do kim loại, mỹ phẩm, mủ cao su...) liên quan đến hệ miễn dịch. Bệnh không lây nhiễm nhưng gây khó chịu. Cách điều trị tốt nhất là xác định và tránh xa tác nhân gây bệnh.",
        "safety_notice": "Xác định đúng tác nhân gây bệnh là bước quan trọng nhất.",
        "possible_topics": ["Viêm da kích ứng", "Viêm da dị ứng", "Patch test"],
        "when_to_seek_care": ["Phát ban không cải thiện sau khi tránh tác nhân nghi ngờ", "Phát ban lan rộng lên mặt, sinh dục"],
        "red_flag_advice": [],
        "confidence_level": "high",
        "requires_emergency_care": False,
    },
]

# Câu trả lời mặc định khi không khớp câu hỏi nào
DEFAULT_PATIENT_ANSWER = {
    "answer": (
        "Xin chào! Tôi là trợ lý Da liễu AI. Dựa trên mô tả của bạn, tình trạng này "
        "**CÓ THỂ** liên quan đến một số vấn đề da liễu thường gặp.\n\n"
        "**Những gì bạn có thể làm:**\n"
        "- Giữ vùng da sạch sẽ và khô thoáng\n"
        "- Tránh gãi hoặc chà xát lên vùng da bị ảnh hưởng\n"
        "- Sử dụng kem dưỡng ẩm nhẹ, không mùi\n"
        "- Tránh tiếp xúc với xà phòng mạnh hoặc hóa chất\n\n"
        "⚠️ **QUAN TRỌNG:** Thông tin trên chỉ mang tính tham khảo. "
        "Vui lòng **đi khám bác sĩ da liễu** để được chẩn đoán và điều trị chính xác. "
        "**TUYỆT ĐỐI KHÔNG TỰ MUA THUỐC** mà chưa có đơn của bác sĩ!"
    ),
    "safety_notice": "Thông tin chỉ mang tính tham khảo, không thay thế chẩn đoán của bác sĩ.",
    "possible_topics": ["Viêm da", "Chàm", "Dị ứng da", "Nấm da"],
    "when_to_seek_care": [
        "Triệu chứng kéo dài hơn 2 tuần không cải thiện",
        "Xuất hiện mụn mủ hoặc dấu hiệu nhiễm trùng",
        "Tổn thương lan rộng nhanh",
    ],
    "red_flag_advice": [],
    "confidence_level": "medium",
    "requires_emergency_care": False,
}


def _find_best_match(question: str, qna_list: list, threshold: float = 0.55) -> dict | None:
    """Tìm câu hỏi khớp nhất bằng keyword matching + fuzzy similarity."""
    question_lower = question.lower().strip()
    best_score = 0.0
    best_match = None

    for qna in qna_list:
        # Fuzzy similarity score
        similarity = SequenceMatcher(None, question_lower, qna["question"].lower()).ratio()

        # Keyword bonus: mỗi keyword khớp +0.15
        keyword_bonus = sum(
            0.15 for kw in qna["keywords"] if kw.lower() in question_lower
        )

        total_score = similarity + keyword_bonus

        if total_score > best_score:
            best_score = total_score
            best_match = qna

    if best_score >= threshold and best_match:
        logger.info(f"[QnA Match] score={best_score:.2f} matched='{best_match['question'][:50]}...'")
        return best_match

    logger.info(f"[QnA Match] No match (best_score={best_score:.2f}), using default")
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# POST /api/scribe — Medical Scribe (MOCK)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/scribe", response_model=ScribeResponse, tags=["Scribe"])
async def scribe_endpoint(req: ScribeRequest):
    """Trích xuất thông tin lâm sàng từ transcript (dữ liệu demo)."""
    logger.info(f"[Scribe] MOCK request_id={req.request_id}")
    start = time.time()

    transcript = req.transcript or ""
    if not transcript.strip():
        logger.info("[Scribe] Nhận transcript trống, tự động gán Mock Audio Transcript.")
        transcript = "[AUDIO MOCK] Bệnh nhân than phiền nổi đỏ ngứa bong vảy hai bàn tay 2 tuần nay."

    response = ScribeResponse(
        request_id=req.request_id or f"req_scribe_{uuid.uuid4().hex[:8]}",
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
        latency_ms=round((time.time() - start) * 1000, 1),
        model_version="demo_v1",
    )

    logger.info(f"[Scribe] MOCK done in {response.latency_ms}ms")
    return response


# ═══════════════════════════════════════════════════════════════════════════════
# POST /api/reminder — Clinical Reminder (MOCK)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/reminder", response_model=ReminderResponse, tags=["Reminder"])
async def reminder_endpoint(req: ReminderRequest):
    """Phân tích hồ sơ lâm sàng và tạo nhắc nhở (dữ liệu demo)."""
    logger.info(f"[Reminder] MOCK request_id={req.request_id}")
    start = time.time()

    response = ReminderResponse(
        request_id=req.request_id or f"req_reminder_{uuid.uuid4().hex[:8]}",
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
        latency_ms=round((time.time() - start) * 1000, 1),
        model_version="demo_v1",
    )

    logger.info(f"[Reminder] MOCK done in {response.latency_ms}ms")
    return response


# ═══════════════════════════════════════════════════════════════════════════════
# POST /api/chat — Patient QnA Chatbot (QnA DEMO)
# ═══════════════════════════════════════════════════════════════════════════════

_EMERGENCY_KEYWORDS = ["khó thở", "sưng môi", "sưng lưỡi", "ngất", "sốc", "cấp cứu", "phản vệ"]

_EMERGENCY_RESPONSE = {
    "answer": (
        "🚨 **CẢNH BÁO KHẨN CẤP!**\n\n"
        "Dựa trên mô tả của bạn, tình trạng này CÓ THỂ cần được xử lý y tế ngay lập tức.\n\n"
        "**Hãy đến phòng cấp cứu NGAY nếu bạn có:**\n"
        "- Khó thở, sưng mặt/môi/lưỡi\n"
        "- Phát ban lan nhanh toàn thân\n"
        "- Sốt cao kèm phát ban\n"
        "- Chóng mặt, ngất xỉu\n\n"
        "📞 **Gọi 115 ngay** nếu có bất kỳ triệu chứng nào ở trên!"
    ),
    "safety_notice": "⚠️ Đây CÓ THỂ là tình huống khẩn cấp. Hãy đến bệnh viện NGAY.",
    "possible_topics": ["Dị ứng cấp tính", "Phản vệ", "Nhiễm trùng nặng"],
    "when_to_seek_care": ["NGAY LẬP TỨC — không nên chờ đợi"],
    "red_flag_advice": [
        "Khó thở hoặc sưng phù → gọi cấp cứu 115",
        "Sốt cao > 39°C kèm phát ban → đến bệnh viện ngay",
    ],
    "confidence_level": "high",
    "requires_emergency_care": True,
}


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(req: ChatRequest):
    """Hỏi đáp da liễu cho bệnh nhân — sử dụng bộ QnA DEMO."""
    logger.info(f"[Chat] QnA DEMO question='{req.question[:60]}...'")
    start = time.time()

    question_lower = req.question.lower()

    # 1. Check emergency keywords
    is_emergency = any(kw in question_lower for kw in _EMERGENCY_KEYWORDS)
    if is_emergency:
        data = _EMERGENCY_RESPONSE
        logger.info("[Chat] Emergency keywords detected")
    else:
        # 2. Find best matching QnA
        match = _find_best_match(req.question, PATIENT_QNA)
        data = match if match else DEFAULT_PATIENT_ANSWER

    response = ChatResponse(
        request_id=req.request_id or f"req_chat_{uuid.uuid4().hex[:8]}",
        question=req.question,
        answer=data["answer"],
        safety_notice=data.get("safety_notice", ""),
        possible_topics=data.get("possible_topics", []),
        when_to_seek_care=data.get("when_to_seek_care", []),
        red_flag_advice=data.get("red_flag_advice", []),
        source_evidence=data.get("source_evidence", ["Cơ sở dữ liệu DermNet Vietnamese"]),
        confidence_level=data.get("confidence_level", "medium"),
        requires_doctor_followup=True,
        requires_emergency_care=data.get("requires_emergency_care", False),
        latency_ms=round((time.time() - start) * 1000, 1),
        model_version="demo_v1",
    )

    logger.info(f"[Chat] Done in {response.latency_ms}ms")
    return response


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/health
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "ok", "mode": "demo_qna", "patient_qna_count": len(PATIENT_QNA)}


# ═══════════════════════════════════════════════════════════════════════════════
# Triage Endpoints (Consolidated into Core)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/cases/create", summary="Tạo ca bệnh mới", response_model=APIResponse, tags=["Cases"])
async def create_case_endpoint(patient: PatientInput):
    logger.info(f"Khởi tạo ca mới cho bác sĩ {patient.bac_si_id}")

    case_id = "CASE_" + str(uuid.uuid4())[:8].upper()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    db_record = {
        "Case_ID": case_id,
        "Ngày_giờ_khám": current_time,
        "Bác_sĩ_ID": patient.bac_si_id,
        "Họ_tên_BN": patient.ho_ten,
        "Tuổi": patient.tuoi,
        "Giới_tính": patient.gioi_tinh,
        "Triệu_chứng_Transcript": patient.trieu_chung_transcript,
        "Safety_Status": "created"
    }
    await db.save_case(db_record)

    return APIResponse(
        success=True,
        message="Ca bệnh đã được khởi tạo",
        data={"case_id": case_id, "created_at": current_time}
    )

@app.post("/api/v1/cases/{case_id}/doctor-approve", summary="Bác sĩ phê duyệt", response_model=APIResponse, tags=["Cases"])
async def doctor_approve_endpoint(case_id: str, payload: DoctorApproveInput):
    logger.info(f"Bác sĩ phê duyệt cho case {case_id}")

    start_time = time.time()
    update_data = {
        "Draft_Note": payload.draft_note,
        "Safety_Status": "approved_by_doctor",
        "SpO2_Final": payload.spo2,
        "HR_Final": payload.hr,
        "BP_Final": payload.bp,
        "Red_Flag": payload.red_flags,
        "Uncertainty_Score": payload.uncertainty_score,
    }
    await db.update_case(case_id, update_data)
    await db.log_ai_interaction(case_id, "/cases/doctor-approve", round(float(time.time() - start_time), 2), "None", "Approved")

    return APIResponse(
        success=True,
        message="Đã lưu hồ sơ bệnh án thành công vào Excel",
        data={"case_id": case_id}
    )