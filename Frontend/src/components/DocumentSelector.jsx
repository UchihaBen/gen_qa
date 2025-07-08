import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

const DocumentSelector = ({ onDocumentSelect }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.getDocuments();
      setDocuments(response.documents || []);
    } catch (err) {
      setError('Không thể tải danh sách tài liệu. Vui lòng kiểm tra kết nối API.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>⏳ Đang tải danh sách tài liệu...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error">
        <div className="error-icon">❌</div>
        <p>{error}</p>
        <button onClick={loadDocuments} className="retry-btn">
          🔄 Thử lại
        </button>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📁</div>
        <h3>Không có tài liệu nào</h3>
        <p>Vui lòng thêm file .docx vào thư mục data của server</p>
        <button onClick={loadDocuments} className="retry-btn">
          🔄 Tải lại
        </button>
      </div>
    );
  }

  return (
    <div className="document-selector">
      <div className="section-header">
        <h2>📚 Chọn tài liệu</h2>
        <p>Chọn tài liệu bạn muốn tạo câu hỏi từ {documents.length} tài liệu có sẵn</p>
      </div>
      
      <div className="document-grid">
        {documents.map((doc) => (
          <div 
            key={doc.id} 
            className="document-card"
            onClick={() => onDocumentSelect(doc)}
          >
            <div className="document-icon">📄</div>
            <h3 className="document-name">{doc.name}</h3>
            <div className="document-info">
              <span className={`status ${doc.has_markdown ? 'ready' : 'pending'}`}>
                {doc.has_markdown ? '✅ Sẵn sàng' : '⏳ Đang xử lý'}
              </span>
              <span className="modified">
                📅 {new Date(doc.last_modified * 1000).toLocaleDateString('vi-VN')}
              </span>
            </div>
            <div className="card-hover-effect">
              <span>👆 Nhấp để chọn</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DocumentSelector;
