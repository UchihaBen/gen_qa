# Quiz Generator Frontend

```bash
# Cài đặt dependencies
npm install

# Chạy development server
npm start


Backend cần cung cấp các endpoints:

- `GET /api/documents` - Danh sách tài liệu
- `GET /api/headings/{documentID}` - Headings của tài liệu
- `GET /api/content/{documentID}` - Nội dung theo heading
- `POST /api/generate-quiz` - Tạo câu hỏi
