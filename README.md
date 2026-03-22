# MedAI — Trợ lý AI Phân loại & Chẩn đoán Da liễu

Hệ thống MedAI cung cấp trải nghiệm hoàn chỉnh từ tiếp nhận bệnh nhân đến tra cứu chuyên sâu cho lĩnh vực Da liễu. Dự án bao gồm 2 thành phần chính hoạt động song song.

1. **medpilot-core (Port 8000)**: Backend xử lý chính, cung cấp cơ sở tri thức da liễu (RAG Vector Database) và API giao tiếp với các mô hình LLM.
2. **medpilot-frontend (Port 3000)**: Giao diện Web trực diện dành cho bác sĩ/bệnh nhân, xây dựng trên nền tảng Next.js.

---

## 🚀 Hướng Dẫn Cài Đặt (Cho người dùng mới)

### Yêu cầu hệ thống
- Python 3.10 trở lên
- Node.js & npm (để chạy frontend)
- Lệnh Git cơ bản
- Mô hình LLM đang chạy (vLLM hoặc Ollama)

### Bước 1: Cài đặt cho medpilot-core (Backend)
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

#### Cấu hình Môi trường Backend (Environment Variables)
Sao chép file `.env.example` thành `.env` trong thư mục `medpilot-core` và cấu hình đường dẫn tới LLM của bạn:

```ini
# Sửa đường dẫn này trỏ tới server AI của bạn (Ollama hoặc vLLM)
# Ví dụ Ollama: http://localhost:11434/v1
# Ví dụ vLLM:   http://localhost:8001/v1
VLLM_BASE_URL=http://localhost:8001/v1
VLLM_MODEL_NAME=default
VLLM_TIMEOUT=180
```

### Bước 2: Cài đặt cho medpilot-frontend (Frontend Web GUI)
Mở một terminal MỚI và chạy lệnh sau:
```bash
cd medpilot-frontend

# Cài đặt các gói thư viện Node.js
npm install
```

#### Cấu hình Môi trường Frontend (Tùy chọn)
Nếu cần thay đổi API Backend theo mặc định (http://localhost:8000), bạn có thể tạo/chỉnh sửa biến môi trường trong `medpilot-frontend/.env.local`. 

---

## ▶️ Cách Chạy Hệ Thống

Dự án đã được trang bị script khởi chạy tự động cả hai hệ thống cùng lúc.

**Trên Windows:**
Chỉ cần bấm đúp chuột vào file `start_all.bat` nằm ở thư mục gốc, hoặc mở PowerShell và chạy lệnh `.\start_all.ps1`.

Scripts này sẽ tự động khởi động backend bằng Uvicorn và sử dụng thư viện Next.js để build/run code production cho frontend ở cổng 3000. 

**Chạy thủ công (nếu lỗi script hoặc để dev code):**
Mở 2 cửa sổ terminal:

*Terminal 1 (Backend):*
```bash
cd medpilot-core
.venv\Scripts\activate
uvicorn app.main:app --port 8000 --reload
```

*Terminal 2 (Frontend)*
```bash
cd medpilot-frontend
npm run dev
```
*(Lưu ý: Nếu sử dụng `start_all.bat`, dự án sẽ tự chạy tiến trình production: `npm run build && npm run start`)*

Sau khi chạy xong, trình duyệt sẽ tự mở trang web tại địa chỉ: `http://localhost:3000`. API Document của backend có thể xem tại: `http://localhost:8000/docs`.

---

## 📂 Nơi lưu trữ dữ liệu quan trọng

- **Lịch sử & Dữ liệu ghi nhớ:** Nằm trong thư mục `medpilot-core/data/` hoặc local db ở backend.
- **Dữ liệu RAG (Cơ sở tri thức):** Nằm trong thư mục `medpilot-core/chroma_db/`.

---

## 🤝 Lỗi phổ biến

1. **Lỗi Frontend báo thiếu file (ví dụ "SyntaxError: Unexpected token"):**
   - Đảm bảo bạn đã kích hoạt và tải các gói (thực hiện lệnh `npm install`) trước khi chạy dự án.

2. **Lỗi "Không có phản hồi" khi gửi chat tới AI:**
   - Nguyên nhân chính là do cấu hình API của LLM (Ollama/vLLM) trong hệ thống chưa bật, cấu hình cổng không khớp, hoặc mô hình LLM chưa được nạp lên bộ nhớ GPU/CPU.
