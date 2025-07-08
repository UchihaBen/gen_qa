import React, { useState } from 'react';
import { api } from '../services/api';

const ContentPreview = ({ document, headings, onContentPreview, onNext }) => {
  const [previewContent, setPreviewContent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [selectedHeadingForPreview, setSelectedHeadingForPreview] = useState(null);

  const handleCheckContent = async (heading = null) => {
    try {
      setLoading(true);
      
      // Sử dụng heading được chọn hoặc heading đầu tiên
      const targetHeading = heading || headings[0];
      setSelectedHeadingForPreview(targetHeading);
      
      const response = await api.getContent(
        document.id, 
        targetHeading.text, 
        true
      );
      
      setPreviewContent(response);
      setShowPreview(true);
      onContentPreview(response);
    } catch (err) {
      console.error('Lỗi khi lấy nội dung:', err);
      alert('Không thể tải nội dung. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  const formatContent = (content) => {
    if (!content) return '';
    
    // Chia nội dung thành các dòng và format
    const lines = content.split('\n');
    return lines.map((line, index) => {
      if (line.trim().startsWith('#')) {
        const level = (line.match(/^#+/) || [''])[0].length;
        return (
          <div key={index} className={`preview-heading preview-h${level}`}>
            {line.replace(/^#+\s*/, '')}
          </div>
        );
      }
      if (line.trim() === '') {
        return <div key={index} className="preview-space"></div>;
      }
      return (
        <div key={index} className="preview-paragraph">
          {line}
        </div>
      );
    });
  };

  return (
    <div className="content-preview">
      <div className="section-header">
        <h2>🔍 Kiểm tra nội dung</h2>
        <p>Xem trước nội dung sẽ được sử dụng để tạo câu hỏi</p>
      </div>
      
      <div className="selected-headings">
        <h3>📋 Các chủ đề đã chọn ({headings.length}):</h3>
        <div className="headings-grid">
          {headings.map(heading => (
            <div key={heading.id} className="heading-preview-card">
              <div className="heading-info">
                <span className={`level-badge level-${heading.level}`}>
                  H{heading.level}
                </span>
                <span className="heading-name">{heading.text}</span>
              </div>
              <button 
                className="preview-heading-btn"
                onClick={() => handleCheckContent(heading)}
                disabled={loading}
              >
                👁️ Xem
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="preview-actions">
        <button 
          className="check-content-btn primary"
          onClick={() => handleCheckContent()}
          disabled={loading}
        >
          {loading ? (
            <>
              <div className="btn-spinner"></div>
              Đang tải...
            </>
          ) : (
            <>
              👁️ Kiểm tra nội dung tổng hợp
            </>
          )}
        </button>
        
        <button 
          className="skip-btn secondary"
          onClick={onNext}
        >
          ⏭️ Bỏ qua & Sinh câu hỏi
        </button>
      </div>

      {showPreview && previewContent && (
        <div className="content-display">
          <div className="preview-header">
            <h3>📄 Nội dung từ: "{selectedHeadingForPreview?.text || 'Tổng hợp'}"</h3>
            <button 
              className="close-preview"
              onClick={() => setShowPreview(false)}
            >
              ✖️
            </button>
          </div>
          
          <div className="content-stats">
            <div className="stat-item">
              <span className="stat-icon">📊</span>
              <span className="stat-value">{previewContent.stats.words}</span>
              <span className="stat-label">từ</span>
            </div>
            <div className="stat-item">
              <span className="stat-icon">📝</span>
              <span className="stat-value">{previewContent.stats.lines}</span>
              <span className="stat-label">dòng</span>
            </div>
            <div className="stat-item">
              <span className="stat-icon">🔢</span>
              <span className="stat-value">{previewContent.stats.headings_included}</span>
              <span className="stat-label">tiêu đề</span>
            </div>
            <div className="stat-item">
              <span className="stat-icon">📄</span>
              <span className="stat-value">{previewContent.stats.characters}</span>
              <span className="stat-label">ký tự</span>
            </div>
          </div>

          <div className="content-preview-box">
            <div className="preview-toolbar">
              <span className="preview-title">📖 Nội dung chi tiết:</span>
              <div className="preview-controls">
                <button className="control-btn" title="Cuộn lên đầu">⬆️</button>
                <button className="control-btn" title="Cuộn xuống cuối">⬇️</button>
              </div>
            </div>
            <div className="formatted-content">
              {formatContent(previewContent.content)}
            </div>
          </div>

          <div className="preview-actions">
            <button 
              className="generate-quiz-btn"
              onClick={onNext}
            >
              ✨ Sinh câu hỏi từ nội dung này
            </button>
            <button 
              className="check-another-btn"
              onClick={() => setShowPreview(false)}
            >
              🔄 Xem nội dung khác
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentPreview;
