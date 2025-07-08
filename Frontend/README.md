# Quiz Generator Frontend

Giao diện React cho hệ thống tạo câu hỏi tự động từ tài liệu.

## Tính năng

- 📚 **Chọn tài liệu**: Lựa chọn từ danh sách tài liệu có sẵn
- 📖 **Chọn chủ đề**: Chọn các heading từ cấu trúc tree
- 🔍 **Kiểm tra nội dung**: Xem trước nội dung sẽ được sử dụng
- ⚙️ **Cấu hình câu hỏi**: Thiết lập loại câu hỏi, số lượng, mức độ
- 🎯 **Xem kết quả**: Hiển thị và xuất câu hỏi đã tạo

## Cài đặt

```bash
# Cài đặt dependencies
npm install

# Chạy development server
npm start

# Build cho production
npm run build
```

## Cấu hình API

Sửa URL API trong `src/services/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## Cấu trúc dự án

```
src/
├── components/          # React components
│   ├── DocumentSelector.jsx
│   ├── HeadingSelector.jsx
│   ├── ContentPreview.jsx
│   ├── QuizForm.jsx
│   └── QuizResult.jsx
├── services/           # API services
│   └── api.js
├── App.js             # Main app component
├── App.css           # Styles
└── index.js          # Entry point
```

## Tương thích

- React 18+
- Browsers hiện đại (Chrome, Firefox, Safari, Edge)
- Responsive design cho mobile và desktop

## API Requirements

Backend cần cung cấp các endpoints:

- `GET /api/documents` - Danh sách tài liệu
- `GET /api/headings/{documentID}` - Headings của tài liệu
- `GET /api/content/{documentID}` - Nội dung theo heading
- `POST /api/generate-quiz` - Tạo câu hỏi
