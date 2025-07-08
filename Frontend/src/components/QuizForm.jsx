import React, { useState } from 'react';
import { api } from '../services/api';

const QuizForm = ({ document, selectedHeadings, onQuizGenerated }) => {
  const [formData, setFormData] = useState({
    amount: 5,
    grade: 6,
    subject: 'english',
    note: '',
    questionTypes: {
      'multiple-choice': 2,
      'choose-many': 1,
      'fill-in': 1,
      'match-word': 1,
      'open': 0
    }
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleQuestionTypeChange = (type, value) => {
    const newValue = Math.max(0, parseInt(value) || 0);
    setFormData(prev => ({
      ...prev,
      questionTypes: {
        ...prev.questionTypes,
        [type]: newValue
      }
    }));
  };

  const getTotalQuestions = () => {
    return Object.values(formData.questionTypes).reduce((sum, count) => sum + count, 0);
  };

  const handleAutoBalance = () => {
    const total = formData.amount;
    const types = Object.keys(formData.questionTypes);
    const baseAmount = Math.floor(total / types.length);
    const remainder = total % types.length;
    
    const newTypes = {};
    types.forEach((type, index) => {
      newTypes[type] = baseAmount + (index < remainder ? 1 : 0);
    });
    
    setFormData(prev => ({
      ...prev,
      questionTypes: newTypes
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const totalQuestions = getTotalQuestions();
    if (totalQuestions !== formData.amount) {
      setError(`Tổng số câu hỏi (${totalQuestions}) phải bằng số lượng yêu cầu (${formData.amount})`);
      return;
    }

    if (selectedHeadings.length === 0) {
      setError('Vui lòng chọn ít nhất một chủ đề');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const payload = {
        amount: formData.amount,
        documentID: document.id,
        gptModel: 'gemini-1.5-flash',
        grade: formData.grade,
        note: formData.note,
        questionType: formData.questionTypes,
        subject: formData.subject,
        topic: selectedHeadings.map(h => h.text)
      };

      const result = await api.generateQuiz(payload);
      onQuizGenerated(result);
    } catch (err) {
      setError('Không thể tạo câu hỏi. Vui lòng thử lại.');
      console.error('Error generating quiz:', err);
    } finally {
      setLoading(false);
    }
  };

  const questionTypeLabels = {
    'multiple-choice': '🔘 Trắc nghiệm (1 đáp án)',
    'choose-many': '☑️ Chọn nhiều đáp án',
    'fill-in': '✏️ Điền từ vào chỗ trống',
    'match-word': '🔗 Ghép cặp từ/cụm từ',
    'open': '💭 Câu hỏi mở'
  };

  const subjectOptions = [
    { value: 'english', label: '🇬🇧 Tiếng Anh' },
    { value: 'math', label: '🔢 Toán học' },
    { value: 'science', label: '🔬 Khoa học' },
    { value: 'history', label: '📚 Lịch sử' },
    { value: 'geography', label: '🗺️ Địa lý' },
    { value: 'literature', label: '📖 Văn học' }
  ];

  return (
    <div className="quiz-form">
      <div className="section-header">
        <h2>✨ Tạo câu hỏi</h2>
        <p>Cấu hình chi tiết để tạo bộ câu hỏi phù hợp</p>
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="quiz-config-form">
        <div className="form-section">
          <h3>📊 Thông tin cơ bản</h3>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="amount">Tổng số câu hỏi:</label>
              <input
                type="number"
                id="amount"
                min="1"
                max="50"
                value={formData.amount}
                onChange={(e) => handleInputChange('amount', parseInt(e.target.value) || 1)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="grade">Lớp:</label>
              <select
                id="grade"
                value={formData.grade}
                onChange={(e) => handleInputChange('grade', parseInt(e.target.value))}
              >
                {[...Array(12)].map((_, i) => (
                  <option key={i + 1} value={i + 1}>Lớp {i + 1}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="subject">Môn học:</label>
              <select
                id="subject"
                value={formData.subject}
                onChange={(e) => handleInputChange('subject', e.target.value)}
              >
                {subjectOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="form-section">
          <div className="section-header-inline">
            <h3>📝 Phân bố loại câu hỏi</h3>
            <button 
              type="button" 
              className="auto-balance-btn"
              onClick={handleAutoBalance}
            >
              ⚖️ Tự động cân bằng
            </button>
          </div>
          
          <div className="question-types-grid">
            {Object.entries(formData.questionTypes).map(([type, count]) => (
              <div key={type} className="question-type-item">
                <label>{questionTypeLabels[type]}</label>
                <input
                  type="number"
                  min="0"
                  value={count}
                  onChange={(e) => handleQuestionTypeChange(type, e.target.value)}
                />
              </div>
            ))}
          </div>
          
          <div className="total-counter">
            <span className={`total-display ${getTotalQuestions() === formData.amount ? 'valid' : 'invalid'}`}>
              Tổng: {getTotalQuestions()}/{formData.amount} câu
              {getTotalQuestions() === formData.amount ? ' ✅' : ' ❌'}
            </span>
          </div>
        </div>

        <div className="form-section">
          <h3>📋 Chủ đề đã chọn</h3>
          <div className="selected-topics">
            {selectedHeadings.map(heading => (
              <span key={heading.id} className="topic-tag">
                <span className="topic-level">H{heading.level}</span>
                <span className="topic-text">{heading.text}</span>
              </span>
            ))}
          </div>
        </div>

        <div className="form-section">
          <h3>📌 Ghi chú (tùy chọn)</h3>
          <textarea
            placeholder="Thêm ghi chú hoặc yêu cầu đặc biệt cho việc tạo câu hỏi..."
            value={formData.note}
            onChange={(e) => handleInputChange('note', e.target.value)}
            rows="3"
          />
        </div>

        <div className="form-actions">
          <button 
            type="submit" 
            className="generate-btn"
            disabled={loading || getTotalQuestions() !== formData.amount}
          >
            {loading ? (
              <>
                <div className="btn-spinner"></div>
                Đang tạo câu hỏi...
              </>
            ) : (
              <>
                🎯 Tạo {formData.amount} câu hỏi
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default QuizForm;
