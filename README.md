# MedAI — Trợ lý AI Phân loại & Chẩn đoán Da liễu

Hệ thống MedAI bao gồm 3 thành phần hoạt động song song để cung cấp trải nghiệm hoàn chỉnh từ tiếp nhận bệnh nhân (Triage) đến tra cứu chuyên sâu (RAG).

1. **medpilot-core (Port 8000)**: Hệ thống chính. Cung cấp cơ sở tri thức da liễu (RAG Vector Database) và xử lý ngôn ngữ AI.
2. **medpilot-triage (Port 8080)**: Hệ thống phân luồng (Triage Workflow API). Nơi tiếp nhận thông tin, phân tích ban đầu, xin ý kiến bác sĩ, và lưu trữ dữ liệu vào Excel.
3. **medpilot-frontend (Port 3000)**: Giao diện Web trực diện dành cho bác sĩ/bệnh nhân.

---

## 🚀 Hướng Dẫn Cài Đặt (Cho người dùng mới)

### Yêu cầu hệ thống
- Python 3.10 trở lên
- Git
- Mô hình LLM đang chạy (vLLM hoặc Ollama)

### Bước 1: Cài đặt cho medpilot-core (Hệ thống chính)
Mở terminal và chạy lệnh sau:
```bash
cd medpilot-core
python -m venv .venv

# Kích hoạt môi trường ảo
# Trên Windows:
.venv\Scripts\activate
# Trên Mac/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

### Bước 2: Cài đặt cho medpilot-triage (Hệ thống Triage/Frontend)
Mở một terminal MỚI và chạy lệnh sau:
```bash
cd medpilot-triage
python -m venv .venv

# Kích hoạt môi trường ảo
# Trên Windows:
.venv\Scripts\activate
# Trên Mac/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

### Bước 3: Cấu hình Môi trường (Environment Variables)
Trong thư mục `medpilot-triage`, đã có sẵn file `.env` mẫu. Bạn mở file `medpilot-triage/.env` ra và cấu hình đường dẫn tới LLM của bạn:

```ini
BACKEND_PORT=8080

# Sửa đường dẫn này trỏ tới server AI của bạn (Ollama hoặc vLLM)
# Ví dụ Ollama: http://localhost:11434/v1
# Ví dụ vLLM:   http://localhost:8001/v1
VLLM_BASE_URL=http://localhost:8001/v1
VLLM_MODEL_NAME=default
VLLM_TIMEOUT=180

# Đường dẫn gọi sang medpilot-core (Mặc định không cần sửa)
MEDPILOT_API_URL=http://localhost:8000/api/v1
```

---

## ▶️ Cách Chạy Hệ Thống

Dự án đã được trang bị script khởi chạy tự động cả hai hệ thống cùng lúc.

**Trên Windows:**
Chỉ cần bấm đúp chuột vào file `start_all.bat` nằm ở thư mục gốc (hoặc chuột phải > Run with PowerShell vào file `start_all.ps1`).

**Chạy thủ công (nếu lỗi script):**
Mở 2 cửa sổ terminal:

*Terminal 1:*
```bash
cd medpilot-core
.venv\Scripts\activate
uvicorn app.main:app --port 8000
```

*Terminal 2:*
```bash
cd medpilot-triage
.venv\Scripts\activate
python main.py
```

Sau khi chạy xong, trình duyệt sẽ tự động mở trang web giao diện tại địa chỉ: `http://localhost:3000`.

---

## 📂 Nơi lưu trữ dữ liệu quan trọng

- **Mã nguồn giao diện:** Nằm hoàn toàn trong thư mục `medpilot-frontend/`. Bạn có thể chỉnh sửa `index.html` ở đây, không cần khởi động lại backend.
- **Danh sách bệnh nhân:** Được tự động lưu vào file Excel tại `medpilot-triage/database.xlsx` sau khi bác sĩ ấn "Phê duyệt & Lưu".
- **Lịch sử truy xuất chi tiết:** Nằm trong thư mục `medpilot-triage/data/cases/`.
- **Dữ liệu RAG (Cơ sở tri thức):** Nằm trong thư mục `medpilot-core/chroma_db/`.

---

## 🤝 Góp ý đóng góp & Lỗi phổ biến

1. **Màn hình thông báo "RAG: offline" ở góc phải:**
   - Nghĩa là `medpilot-core` chưa chạy ở port 8000. Bạn cần kiểm tra xem terminal chạy uvicorn có báo lỗi gì không.

2. **Lỗi "Không có phản hồi" khi chat hoặc Triage quay mãi không dừng:**
   - Nguyên nhân chính là do cấu hình API của LLM (Ollama/vLLM) trong file `medpilot-triage/.env` chưa đúng, hoặc model LLM chưa được load lên bộ nhớ.
