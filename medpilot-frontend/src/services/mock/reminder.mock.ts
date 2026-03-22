import type { ReminderResponse } from "@/types";

export const MOCK_REMINDER_RESPONSE: ReminderResponse = {
  request_id: "req_reminder_demo_001",
  module: "clinical_reminder",
  missing_critical_info: [
    "Chưa xác nhận rõ cảm giác rát (burning) từ bệnh nhân",
    "Tiền sử dị ứng thuốc / mỹ phẩm chưa được khai thác đầy đủ",
  ],
  questions_to_ask: [
    "Bệnh nhân có dùng mỹ phẩm hoặc kem dưỡng da mới gần đây không?",
    "Có ai trong gia đình bị tình trạng da tương tự không?",
    "Bệnh nhân có dùng thuốc nào (kể cả kháng sinh, kháng histamine) trước khi phát bệnh không?",
    "Tên hoặc thành phần kem đã bôi ở tiệm thuốc là gì?",
  ],
  red_flags: [
    "Nếu tổn thương lan rộng nhanh hoặc kèm sốt → cần đánh giá sớm",
    "Nghi dị ứng thuốc nặng nếu xuất hiện sau khi uống thuốc mới",
  ],
  possible_considerations: [
    "Cân nhắc viêm da tiếp xúc kích ứng (do nước rửa chén)",
    "Cân nhắc eczema / chàm nếu tiền sử cơ địa liên quan",
    "Cân nhắc viêm da tiếp xúc dị ứng nếu có tiếp xúc chất lạ",
    "Loại trừ nhiễm nấm nếu có tổn thương hình vòng hoặc bờ rõ",
  ],
  suggested_next_checks: [
    "Hỏi thêm tiền sử dị ứng chi tiết",
    "Đánh giá phạm vi lan rộng của tổn thương thực thể",
    "Khai thác tên / thành phần thuốc bôi đã dùng",
  ],
  guideline_evidence: [
    "Theo guideline da liễu: viêm da tiếp xúc kích ứng thường liên quan tiếp xúc chất tẩy rửa, biểu hiện ở vùng tiếp xúc trực tiếp.",
    "Eczema tay có liên quan tiền sử viêm da cơ địa và yếu tố nghề nghiệp.",
  ],
  latency_ms: 0,
  model_version: "reminder_v1",
};
