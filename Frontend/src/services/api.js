const API_BASE_URL = 'http://localhost:8000';

export const api = {
  // Lấy danh sách documents
  getDocuments: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/documents`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching documents:', error);
      throw error;
    }
  },

  // Lấy headings của document
  getHeadings: async (documentID) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/headings/${encodeURIComponent(documentID)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching headings:', error);
      throw error;
    }
  },

  // Lấy nội dung heading
  getContent: async (documentID, heading, includeChildren = true) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/content/${encodeURIComponent(documentID)}?heading=${encodeURIComponent(heading)}&include_children=${includeChildren}`
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching content:', error);
      throw error;
    }
  },

  // Sinh quiz
  generateQuiz: async (payload) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/generate-quiz`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error generating quiz:', error);
      throw error;
    }
  }
};
