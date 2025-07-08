import React, { useState } from 'react';
import DocumentSelector from './components/DocumentSelector';
import HeadingSelector from './components/HeadingSelector';
import ContentPreview from './components/ContentPreview';
import QuizForm from './components/QuizForm';
import QuizResult from './components/QuizResult';
import './App.css';

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [selectedHeadings, setSelectedHeadings] = useState([]);
  const [contentPreview, setContentPreview] = useState(null);
  const [quizResult, setQuizResult] = useState(null);

  const handleDocumentSelect = (document) => {
    setSelectedDocument(document);
    setSelectedHeadings([]);
    setContentPreview(null);
    setQuizResult(null);
    setCurrentStep(2);
  };

  const handleHeadingSelect = (headings) => {
    setSelectedHeadings(headings);
    setCurrentStep(3);
  };

  const handleContentPreview = (content) => {
    setContentPreview(content);
  };

  const handleQuizGenerated = (quiz) => {
    setQuizResult(quiz);
    setCurrentStep(5);
  };

  const resetToStart = () => {
    setCurrentStep(1);
    setSelectedDocument(null);
    setSelectedHeadings([]);
    setContentPreview(null);
    setQuizResult(null);
  };

  const goToStep = (step) => {
    if (step <= currentStep) {
      setCurrentStep(step);
    }
  };

  const steps = [
    { number: 1, title: 'Chọn tài liệu', icon: '📚' },
    { number: 2, title: 'Chọn chủ đề', icon: '📖' },
    { number: 3, title: 'Kiểm tra nội dung', icon: '🔍' },
    { number: 4, title: 'Cấu hình câu hỏi', icon: '⚙️' },
    { number: 5, title: 'Kết quả', icon: '🎯' }
  ];

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>🎯 Quiz Generator</h1>
          <p>Công cụ tạo câu hỏi tự động từ tài liệu</p>
        </div>
        
        <div className="progress-container">
          <div className="progress-bar">
            {steps.map((step) => (
              <div 
                key={step.number}
                className={`step ${currentStep >= step.number ? 'active' : ''} ${currentStep === step.number ? 'current' : ''}`}
                onClick={() => goToStep(step.number)}
              >
                <div className="step-icon">{step.icon}</div>
                <div className="step-content">
                  <div className="step-number">{step.number}</div>
                  <div className="step-title">{step.title}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="header-actions">
          <button className="reset-btn" onClick={resetToStart}>
            🔄 Bắt đầu lại
          </button>
        </div>
      </header>

      <main className="app-main">
        <div className="main-content">
          {currentStep === 1 && (
            <DocumentSelector onDocumentSelect={handleDocumentSelect} />
          )}

          {currentStep === 2 && selectedDocument && (
            <HeadingSelector 
              document={selectedDocument}
              onHeadingSelect={handleHeadingSelect}
            />
          )}

          {currentStep === 3 && selectedDocument && selectedHeadings.length > 0 && (
            <ContentPreview
              document={selectedDocument}
              headings={selectedHeadings}
              onContentPreview={handleContentPreview}
              onNext={() => setCurrentStep(4)}
            />
          )}

          {currentStep === 4 && selectedDocument && selectedHeadings.length > 0 && (
            <QuizForm
              document={selectedDocument}
              selectedHeadings={selectedHeadings}
              onQuizGenerated={handleQuizGenerated}
            />
          )}

          {currentStep === 5 && quizResult && (
            <QuizResult quiz={quizResult} />
          )}
        </div>
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <p>© 2025 Quiz Generator - Tạo câu hỏi thông minh</p>
          <div className="footer-info">
            {selectedDocument && (
              <span>📄 {selectedDocument.name}</span>
            )}
            {selectedHeadings.length > 0 && (
              <span>📖 {selectedHeadings.length} chủ đề</span>
            )}
            {quizResult && (
              <span>🎯 {quizResult.questions.length} câu hỏi</span>
            )}
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
