import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

const HeadingSelector = ({ document, onHeadingSelect }) => {
  const [headings, setHeadings] = useState([]);
  const [selectedHeadings, setSelectedHeadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedNodes, setExpandedNodes] = useState(new Set());

  useEffect(() => {
    loadHeadings();
  }, [document]);

  const loadHeadings = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.getHeadings(document.id);
      setHeadings(response.headings || []);
      
      // Mở rộng tất cả các node level 1 mặc định
      const level1Nodes = new Set();
      (response.headings || []).forEach(heading => {
        if (heading.level === 1) {
          level1Nodes.add(heading.id);
        }
      });
      setExpandedNodes(level1Nodes);
    } catch (err) {
      setError('Không thể tải danh sách chủ đề');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleExpansion = (headingId) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(headingId)) {
      newExpanded.delete(headingId);
    } else {
      newExpanded.add(headingId);
    }
    setExpandedNodes(newExpanded);
  };

  const toggleHeadingSelection = (heading) => {
    const isSelected = selectedHeadings.find(h => h.id === heading.id);
    if (isSelected) {
      setSelectedHeadings(selectedHeadings.filter(h => h.id !== heading.id));
    } else {
      setSelectedHeadings([...selectedHeadings, heading]);
    }
  };

  const selectAllChildren = (heading) => {
    const getAllChildren = (node) => {
      let children = [node];
      if (node.children) {
        node.children.forEach(child => {
          children = children.concat(getAllChildren(child));
        });
      }
      return children;
    };

    const allChildren = getAllChildren(heading);
    const newSelected = [...selectedHeadings];
    
    allChildren.forEach(child => {
      if (!newSelected.find(h => h.id === child.id)) {
        newSelected.push(child);
      }
    });
    
    setSelectedHeadings(newSelected);
  };

  const handleNext = () => {
    if (selectedHeadings.length > 0) {
      onHeadingSelect(selectedHeadings);
    }
  };

  const renderHeading = (heading, level = 0) => {
    const isSelected = selectedHeadings.find(h => h.id === heading.id);
    const hasChildren = heading.children && heading.children.length > 0;
    const isExpanded = expandedNodes.has(heading.id);
    
    return (
      <div key={heading.id} className={`heading-item level-${heading.level}`}>
        <div className="heading-row">
          {hasChildren && (
            <button 
              className={`expand-btn ${isExpanded ? 'expanded' : ''}`}
              onClick={() => toggleExpansion(heading.id)}
            >
              {isExpanded ? '▼' : '▶'}
            </button>
          )}
          
          <div 
            className={`heading-content ${isSelected ? 'selected' : ''}`}
            onClick={() => toggleHeadingSelection(heading)}
            style={{ marginLeft: hasChildren ? '0' : '24px' }}
          >
            <span className={`heading-level level-${heading.level}`}>
              H{heading.level}
            </span>
            <span className="heading-text">{heading.text}</span>
            {isSelected && <span className="selected-indicator">✅</span>}
          </div>

          {hasChildren && (
            <button 
              className="select-all-btn"
              onClick={() => selectAllChildren(heading)}
              title="Chọn tất cả con"
            >
              📋 Chọn tất cả
            </button>
          )}
        </div>
        
        {hasChildren && isExpanded && (
          <div className="children-container">
            {heading.children.map(child => renderHeading(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>⏳ Đang tải danh sách chủ đề...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error">
        <div className="error-icon">❌</div>
        <p>{error}</p>
        <button onClick={loadHeadings} className="retry-btn">
          🔄 Thử lại
        </button>
      </div>
    );
  }

  return (
    <div className="heading-selector">
      <div className="section-header">
        <h2>📖 Chọn chủ đề từ: {document.name}</h2>
        <p>Tổng cộng: <strong>{headings.length}</strong> chủ đề chính</p>
      </div>
      
      <div className="headings-container">
        <div className="headings-list">
          {headings.map(heading => renderHeading(heading))}
        </div>
      </div>

      <div className="selection-summary">
        <div className="summary-header">
          <h3>📝 Đã chọn ({selectedHeadings.length} chủ đề):</h3>
          {selectedHeadings.length > 0 && (
            <button 
              className="clear-all-btn"
              onClick={() => setSelectedHeadings([])}
            >
              🗑️ Xóa tất cả
            </button>
          )}
        </div>
        
        <div className="selected-tags">
          {selectedHeadings.length === 0 ? (
            <p className="no-selection">Chưa chọn chủ đề nào. Hãy nhấp vào các chủ đề bên trên để chọn.</p>
          ) : (
            selectedHeadings.map(heading => (
              <span key={heading.id} className="selected-tag">
                <span className="tag-level">H{heading.level}</span>
                <span className="tag-text">{heading.text}</span>
                <button 
                  className="remove-tag"
                  onClick={() => toggleHeadingSelection(heading)}
                >
                  ×
                </button>
              </span>
            ))
          )}
        </div>
      </div>

      <div className="actions">
        <button 
          className="next-btn"
          onClick={handleNext}
          disabled={selectedHeadings.length === 0}
        >
          ➡️ Tiếp tục với {selectedHeadings.length} chủ đề đã chọn
        </button>
      </div>
    </div>
  );
};

export default HeadingSelector;
