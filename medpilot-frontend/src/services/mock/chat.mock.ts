import type { ChatResponse } from "@/types";

export function buildMockChatResponse(question: string): ChatResponse {
  return {
    request_id: `req_chat_${Date.now()}`,
    module: "patient_derma_qna",
    schema_version: "1.0",
    user_role: "patient",
    question,
    answer:
      "Dựa trên mô tả của bạn, tình trạng này có thể liên quan đến viêm da tiếp xúc hoặc eczema. Viêm da tiếp xúc thường xuất hiện ở vùng da tiếp xúc trực tiếp với chất kích ứng như xà phòng, chất tẩy rửa. Tuy nhiên, để có đánh giá chính xác và điều trị phù hợp, bạn nên đến gặp bác sĩ da liễu để được khám trực tiếp.",
    safety_notice: "Thông tin chỉ mang tính tham khảo, không thay thế chẩn đoán của bác sĩ.",
    possible_topics: ["Viêm da tiếp xúc", "Eczema / Chàm", "Dị ứng da"],
    when_to_seek_care: [
      "Tổn thương lan rộng nhanh trong vài giờ",
      "Kèm theo sốt hoặc mệt mỏi bất thường",
      "Có dấu hiệu nhiễm trùng: chảy dịch vàng, sưng đỏ nóng",
      "Không cải thiện sau 1 tuần tự chăm sóc",
    ],
    red_flag_advice: [],
    source_evidence: [],
    confidence_level: "medium",
    requires_doctor_followup: true,
    requires_emergency_care: false,
    latency_ms: 0,
    model_version: "patient_qna_v1",
  };
}

export function buildMockEmergencyResponse(question: string): ChatResponse {
  return {
    ...buildMockChatResponse(question),
    answer:
      "Dựa trên các triệu chứng bạn mô tả, đây có thể là dấu hiệu phản ứng dị ứng nghiêm trọng. Bạn cần được đánh giá y tế ngay.",
    red_flag_advice: [
      "Có dấu hiệu cần được đánh giá y tế sớm.",
      "Nếu khó thở, phù môi/lưỡi hoặc tổn thương lan nhanh, nên đến cơ sở y tế ngay.",
    ],
    requires_doctor_followup: true,
    requires_emergency_care: true,
    confidence_level: "high",
  };
}
