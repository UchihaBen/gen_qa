import json
import google.generativeai as genai

def generate_Multiple_Choice_Questions(prompt, api_key):
    try:
        # Cấu hình API key
        genai.configure(api_key=api_key)
        
        # Khởi tạo mô hình (sửa lỗi: bỏ .genai thừa)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt="""
        p
        
        """
        
        # Gửi yêu cầu tạo câu hỏi
        response = model.generate_content([prompt])
        
        # Trả về kết quả
        return response.text
        
    except Exception as e:
        return {"error": str(e)}

# Ví dụ sử dụng
if __name__ == "__main__":
    # Đường dẫn tới file DOCX hoặc PDF
    file_path = "ta6.docx"
    
    # Prompt yêu cầu của hệ thống
    prompt = """
    Hãy tạo 10 câu hỏi trắc nghiệm từ nội dung tài liệu này. 
    Mỗi câu hỏi có 4 đáp án A, B, C, D và chỉ rõ đáp án đúng.
    Format như sau:
    
    Câu 1: [nội dung câu hỏi]
    A. [đáp án A]
    B. [đáp án B] 
    C. [đáp án C]
    D. [đáp án D]
    Đáp án đúng: [A/B/C/D]
    """
    
    # API key của bạn từ Google GenAI
    api_key = "AIzaSyAqX5bkYluS_QKYSILRVCJHvY6KpSy2-ds"
    
    # Gọi hàm để tạo câu hỏi
    result = generate_Multiple_Choice_Questions( prompt, api_key)
    
    # In kết quả trả về
    if isinstance(result, dict) and "error" in result:
        print(f"Lỗi: {result['error']}")
    else:
        print("Câu hỏi trắc nghiệm được tạo:")
        print(result)