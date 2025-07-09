
Hướng dẫn đóng gói và chạy Quiz Generator Backend bằng Docker.

- Docker và Docker Compose đã được cài đặt
- File `.env` chứa `GEMINI_API_KEY`

**Build Docker image:**
```bash
docker build -t quiz-generator-backend .
```

**Chạy với Docker Compose (khuyến nghị):**
```bash
docker-compose up -d
```

**Xem logs:**
```bash
docker-compose logs -f quiz-generator-backend
```

**Dừng container:**
```bash
docker-compose down
```

**Khởi động lại:**
```bash
docker-compose restart
```

**Xem trạng thái:**
```bash
docker-compose ps
```

## Endpoints

Sau khi chạy thành công:

- **API Base URL:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health



Tạo file `.env` với nội dung:
```
GEMINI_API_KEY=your_gemini_api_key_here
```


**4. Port 8000 đã được sử dụng:**
- Thay đổi port trong `docker-compose.yml`: `"8001:8000"`

