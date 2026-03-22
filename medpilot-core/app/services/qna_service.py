"""
QnA Service — Service xử lý logic tải file dữ liệu QnA JSON và tìm kiếm câu trả lời dựa trên matching.
"""
import json
import logging
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class QnAService:
    _instance = None

    def __init__(self, data_path: str = None):
        if not data_path:
            # Default to the data directory in medpilot-core
            base_dir = Path(__file__).parent.parent.parent
            data_path = str(base_dir / "data" / "qna_demo.json")

        self.data_path = data_path
        self.patient_qna: List[Dict] = []
        self.default_answer: Dict = {}
        self.is_loaded = False

    @classmethod
    def get_instance(cls, data_path: str = None):
        if cls._instance is None:
            cls._instance = cls(data_path)
        return cls._instance

    def load_data(self):
        """Tải dữ liệu QnA từ file json."""
        if self.is_loaded:
            return

        json_path = Path(self.data_path)
        if not json_path.exists():
            logger.error(f"[QnAService] Không tìm thấy file dữ liệu QnA tại {json_path}")
            return

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.patient_qna = data.get("patient_qna", [])
            self.default_answer = data.get("default_patient_answer", {})
            self.is_loaded = True
            logger.info(f"[QnAService] Đã tải {len(self.patient_qna)} câu hỏi QnA từ {json_path}")
        except Exception as e:
            logger.error(f"[QnAService] Lỗi tải dữ liệu QnA: {e}")

    def find_best_match(self, question: str, threshold: float = 0.55) -> Dict:
        """Tìm câu hỏi khớp nhất bằng keyword matching + fuzzy similarity."""
        if not self.is_loaded:
            self.load_data()

        if not self.patient_qna:
            return self.default_answer

        question_lower = question.lower().strip()
        best_score = 0.0
        best_match = None

        for qna in self.patient_qna:
            # Fuzzy similarity score
            similarity = SequenceMatcher(None, question_lower, qna.get("question", "").lower()).ratio()

            # Keyword bonus: mỗi keyword khớp +0.15
            keywords = qna.get("keywords", [])
            keyword_bonus = sum(
                0.15 for kw in keywords if kw.lower() in question_lower
            )

            total_score = similarity + keyword_bonus

            if total_score > best_score:
                best_score = total_score
                best_match = qna

        if best_score >= threshold and best_match:
            logger.info(f"[QnA Match] score={best_score:.2f} matched='{best_match.get('question', '')[:50]}...'")
            return best_match

        logger.info(f"[QnA Match] No match (best_score={best_score:.2f}), using default")
        return self.default_answer

def get_qna_service() -> QnAService:
    return QnAService.get_instance()
