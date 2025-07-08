import React, { useState } from 'react';

const QuizResult = ({ quiz }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [showAnswers, setShowAnswers] = useState(false);
  const [expandedExplanations, setExpandedExplanations] = useState(new Set());

  if (!quiz || !quiz.questions || quiz.questions.length === 0) {
    return (
      <div className="quiz-result error">
        <h2>❌ Lỗi</h2>
        <p>Không có dữ liệu câu hỏi để hiển thị</p>
      </div>
    );
  }

  const toggleExplanation = (questionIndex) => {
    const newExpanded = new Set(expandedExplanations);
    if (newExpanded.has(questionIndex)) {
      newExpanded.delete(questionIndex);
    } else {
      newExpanded.add(questionIndex);
    }
    setExpandedExplanations(newExpanded);
  };

  const exportQuiz = () => {
    const dataStr = JSON.stringify(quiz, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `quiz_${quiz.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = () => {
    const textContent = quiz.questions.map((q, i) => {
      let text = `${i + 1}. ${q.question}\n`;
      text += `Loại: ${q.type}\n`;
      text += `Mức độ: ${q.level}\n`;
      text += `Đáp án đúng: ${q.correct_answers.join(', ')}\n`;
      if (q.incorrect_answers && q.incorrect_answers.length > 0) {
        text += `Đáp án sai: ${q.incorrect_answers.join(', ')}\n`;
      }
      text += `Giải thích: ${q.explanation}\n\n`;
      return text;
    }).join('');
    
    navigator.clipboard.writeText(textContent).then(() => {
      alert('Đã sao chép câu hỏi vào clipboard!');
    });
  };

  const getTypeIcon = (type) => {
    const icons = {
      'multiple-choice': '🔘',
      'choose-many': '☑️',
      'fill-in': '✏️',
      'match-word': '🔗',
      'open': '💭'
    };
    return icons[type] || '❓';
  };

  const getLevelColor = (level) => {
    const colors = {
      'easy': '#4caf50',
      'medium': '#ff9800',
      'hard': '#f44336'
    };
    return colors[level] || '#666';
  };

  const getTypeStats = () => {
    const stats = {};
    quiz.questions.forEach(q => {
      stats[q.type] = (stats[q.type] || 0) + 1;
    });
    return stats;
  };

  const getLevelStats = () => {
    const stats = {};
    quiz.questions.forEach(q => {
      stats[q.level] = (stats[q.level] || 0) + 1;
    });
    return stats;
  };

  return (
    <div className="quiz-result">
      <div className="result-header">
        <h2>🎉 Tạo câu hỏi thành công!</h2>
        <h3>{quiz.name}</h3>
        <p>Đã tạo <strong>{quiz.questions.length}</strong> câu hỏi</p>
      </div>

      <div className="quiz-stats">
        <div className="stats-section">
          <h4>📊 Thống kê theo loại:</h4>
          <div className="stats-grid">
            {Object.entries(getTypeStats()).map(([type, count]) => (
              <div key={type} className="stat-item">
                <span className="stat-icon">{getTypeIcon(type)}</span>
                <span className="stat-label">{type}</span>
                <span className="stat-value">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="stats-section">
          <h4>🎯 Thống kê theo mức độ:</h4>
          <div className="stats-grid">
            {Object.entries(getLevelStats()).map(([level, count]) => (
              <div key={level} className="stat-item">
                <span 
                  className="level-indicator"
                  style={{ backgroundColor: getLevelColor(level) }}
                ></span>
                <span className="stat-label">{level}</span>
                <span className="stat-value">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="quiz-controls">
        <div className="control-group">
          <button 
            className="control-btn primary"
            onClick={() => setShowAnswers(!showAnswers)}
          >
            {showAnswers ? '🙈 Ẩn đáp án' : '👁️ Hiện đáp án'}
          </button>
          
          <button 
            className="control-btn secondary"
            onClick={exportQuiz}
          >
            📥 Tải về JSON
          </button>
          
          <button 
            className="control-btn secondary"
            onClick={copyToClipboard}
          >
            📋 Sao chép
          </button>
        </div>

        <div className="question-navigation">
          <button 
            className="nav-btn"
            onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
            disabled={currentQuestion === 0}
          >
            ⬅️ Trước
          </button>
          
          <span className="question-counter">
            {currentQuestion + 1} / {quiz.questions.length}
          </span>
          
          <button 
            className="nav-btn"
            onClick={() => setCurrentQuestion(Math.min(quiz.questions.length - 1, currentQuestion + 1))}
            disabled={currentQuestion === quiz.questions.length - 1}
          >
            Sau ➡️
          </button>
        </div>
      </div>

      <div className="questions-container">
        {quiz.questions.map((question, index) => (
          <div 
            key={index} 
            className={`question-card ${index === currentQuestion ? 'active' : 'inactive'}`}
            style={{ display: index === currentQuestion ? 'block' : 'none' }}
          >
            <div className="question-header">
              <div className="question-meta">
                <span className="question-number">#{index + 1}</span>
                <span className="question-type">
                  {getTypeIcon(question.type)} {question.type}
                </span>
                <span 
                  className="question-level"
                  style={{ backgroundColor: getLevelColor(question.level) }}
                >
                  {question.level}
                </span>
              </div>
            </div>

            <div className="question-content">
              <h4 className="question-text">{question.question}</h4>

              {showAnswers && (
                <div className="answers-section">
                  <div className="correct-answers">
                    <h5>✅ Đáp án đúng:</h5>
                    <ul>
                      {question.correct_answers.map((answer, i) => (
                        <li key={i} className="correct-answer">{answer}</li>
                      ))}
                    </ul>
                  </div>

                  {question.incorrect_answers && question.incorrect_answers.length > 0 && (
                    <div className="incorrect-answers">
                      <h5>❌ Đáp án sai:</h5>
                      <ul>
                        {question.incorrect_answers.map((answer, i) => (
                          <li key={i} className="incorrect-answer">{answer}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="explanation-section">
                    <button 
                      className="explanation-toggle"
                      onClick={() => toggleExplanation(index)}
                    >
                      💡 {expandedExplanations.has(index) ? 'Ẩn giải thích' : 'Xem giải thích'}
                    </button>
                    
                    {expandedExplanations.has(index) && (
                      <div className="explanation-content">
                        <p>{question.explanation}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="questions-overview">
        <h4>📋 Tổng quan các câu hỏi:</h4>
        <div className="questions-grid">
          {quiz.questions.map((question, index) => (
            <div 
              key={index}
              className={`question-thumb ${index === currentQuestion ? 'active' : ''}`}
              onClick={() => setCurrentQuestion(index)}
            >
              <span className="thumb-number">#{index + 1}</span>
              <span className="thumb-type">{getTypeIcon(question.type)}</span>
              <span 
                className="thumb-level"
                style={{ backgroundColor: getLevelColor(question.level) }}
              ></span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default QuizResult;
