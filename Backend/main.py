from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json
import re
import os
import google.generativeai as genai
from dotenv import load_dotenv
import aiofiles
from docx import Document
from pathlib import Path

# Load environment variables
load_dotenv()

# Cấu hình Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Khởi tạo FastAPI
app = FastAPI(title="Quiz Generator API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class QuestionTypeModel(BaseModel):
    choose_many: int = Field(0, alias="choose-many")
    fill_in: int = Field(0, alias="fill-in")
    match_word: int = Field(0, alias="match-word")
    multiple_choice: int = Field(0, alias="multiple-choice")
    open: int = 0

class Payload(BaseModel):
    amount: int = 0
    documentID: str = "string"
    gptModel: str = "string"
    grade: int = 0
    note: Optional[str] = "string"
    questionType: QuestionTypeModel = QuestionTypeModel()
    subject: str = "math"
    topic: List[str] = ["string"]

class QuizQuestion(BaseModel):
    correct_answers: List[str]
    explanation: Optional[str] = "No explanation provided"
    incorrect_answers: List[str]
    level: str
    question: str
    type: str

class QuizResponse(BaseModel):
    name: str
    questions: List[QuizQuestion]

# Utility Functions
def convert_docx_to_md(input_file: str, output_file: str) -> bool:
    """
    Chuyển đổi file DOCX sang Markdown
    """
    try:
        # Đọc file DOCX
        doc = Document(input_file)
        
        # Tạo danh sách lưu trữ các phần trong Markdown
        markdown_content = []
        
        # Duyệt qua tất cả các đoạn văn trong file DOCX
        for para in doc.paragraphs:
            # Bỏ qua các đoạn trống
            if not para.text.strip():
                markdown_content.append("")
                continue
                
            # Kiểm tra kiểu của từng đoạn
            if para.style.name == "Heading 1":
                markdown_content.append(f"# {para.text}")
            elif para.style.name == "Heading 2":
                markdown_content.append(f"## {para.text}")
            elif para.style.name == "Heading 3":
                markdown_content.append(f"### {para.text}")
            elif para.style.name == "Heading 4":
                markdown_content.append(f"#### {para.text}")
            elif para.style.name == "Heading 5":
                markdown_content.append(f"##### {para.text}")
            elif para.style.name == "Heading 6":
                markdown_content.append(f"###### {para.text}")
            else:
                # Đoạn văn bình thường (không phải tiêu đề)
                markdown_content.append(para.text)
        
        # Lưu kết quả vào file Markdown (.md)
        with open(output_file, "w", encoding="utf-8") as md_file:
            md_file.write("\n".join(markdown_content))
        
        print(f"Tái cấu trúc thành công và lưu vào file Markdown: {output_file}")
        return True
        
    except Exception as e:
        print(f"Lỗi khi chuyển đổi DOCX sang MD: {str(e)}")
        return False

def extract_all_headings(markdown_content: str) -> List[dict]:
    """
    Trích xuất tất cả headings từ markdown content
    """
    headings = []
    lines = markdown_content.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('#'):
            # Đếm số lượng # để xác định level
            level = 0
            for char in line:
                if char == '#':
                    level += 1
                else:
                    break
            
            # Lấy text của heading (bỏ các dấu #)
            heading_text = line[level:].strip()
            
            if heading_text:  # Chỉ thêm nếu có text
                headings.append({
                    "level": level,
                    "text": heading_text,
                    "line_number": i + 1,
                    "id": f"heading_{i}_{level}"
                })
    
    return headings

def extract_content_by_specific_heading(markdown_content: str, target_heading: str) -> str:
    """
    Trích xuất nội dung của một heading cụ thể (chỉ heading đó, không bao gồm sub-headings)
    """
    lines = markdown_content.split('\n')
    content_lines = []
    found_target = False
    target_level = 0
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Nếu là heading
        if line_stripped.startswith('#'):
            level = 0
            for char in line_stripped:
                if char == '#':
                    level += 1
                else:
                    break
            
            heading_text = line_stripped[level:].strip().lower()
            target_lower = target_heading.lower().strip()
            
            # Nếu tìm thấy heading mục tiêu
            if target_lower in heading_text:
                found_target = True
                target_level = level
                content_lines.append(line)
                continue
            
            # Nếu đã tìm thấy target và gặp heading cùng cấp hoặc cao hơn thì dừng
            elif found_target and level <= target_level:
                break
        
        # Nếu đã tìm thấy target heading, thêm tất cả content sau đó
        if found_target:
            content_lines.append(line)
    
    result = '\n'.join(content_lines).strip()
    return result

def extract_content_by_heading_with_children(markdown_content: str, target_heading: str) -> str:
    """
    Trích xuất nội dung của một heading và TẤT CẢ sub-headings bên trong
    Ví dụ: Chọn "Unit 7" sẽ lấy cả "A CLOSER LOOK 1", "A CLOSER LOOK 2", etc.
    """
    lines = markdown_content.split('\n')
    content_lines = []
    found_target = False
    target_level = 0
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Nếu là heading
        if line_stripped.startswith('#'):
            level = 0
            for char in line_stripped:
                if char == '#':
                    level += 1
                else:
                    break
            
            heading_text = line_stripped[level:].strip().lower()
            target_lower = target_heading.lower().strip()
            
            # Nếu tìm thấy heading mục tiêu
            if target_lower in heading_text:
                found_target = True
                target_level = level
                content_lines.append(line)
                print(f"Tìm thấy heading target: '{heading_text}' (level {level})")
                continue
            
            # Nếu đã tìm thấy target và gặp heading CÙNG LEVEL hoặc CAO HƠN thì dừng
            # (không dừng với sub-headings có level thấp hơn)
            elif found_target and level <= target_level:
                print(f"Dừng tại heading: '{heading_text}' (level {level})")
                break
        
        # Nếu đã tìm thấy target heading, thêm tất cả content sau đó (bao gồm sub-headings)
        if found_target:
            content_lines.append(line)
    
    result = '\n'.join(content_lines).strip()
    
    if result:
        # Đếm số sub-headings được bao gồm
        sub_headings = [line for line in content_lines if line.strip().startswith('#')]
        print(f"Đã lấy nội dung với {len(sub_headings)} headings (bao gồm heading chính)")
    
    return result

def extract_content_by_topics(markdown_content: str, topics: List[str], include_children: bool = True) -> str:
    """
    Trích xuất nội dung dựa trên các topic (headings)
    
    Args:
        markdown_content: Nội dung markdown
        topics: Danh sách các heading cần tìm
        include_children: Có lấy cả sub-headings hay không
    """
    if not topics or not markdown_content:
        return markdown_content
    
    all_matched_content = []
    
    for topic in topics:
        if include_children:
            # Lấy heading và tất cả sub-headings bên trong
            specific_content = extract_content_by_heading_with_children(markdown_content, topic)
        else:
            # Chỉ lấy nội dung của heading cụ thể đó (như cũ)
            specific_content = extract_content_by_specific_heading(markdown_content, topic)
        
        if specific_content and specific_content != markdown_content:
            all_matched_content.append(specific_content)
            if include_children:
                print(f"Tìm thấy nội dung cho heading '{topic}' (bao gồm sub-headings)")
            else:
                print(f"Tìm thấy nội dung cụ thể cho heading '{topic}'")
    
    if all_matched_content:
        # Loại bỏ trùng lặp và ghép nội dung
        unique_content = list(dict.fromkeys(all_matched_content))
        result = "\n\n".join(unique_content)
        print(f"Tổng cộng tìm thấy {len(unique_content)} sections phù hợp")
    else:
        # Fallback: thử tìm theo keyword matching
        print(f"Không tìm thấy heading chính xác, thử tìm theo keyword...")
        sections = re.split(r'\n(?=#{1,6}\s)', markdown_content)
        matched_sections = []
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            lines = section.split('\n')
            if not lines:
                continue
            
            header = lines[0].lower()
            for topic in topics:
                if topic.lower().strip() in header:
                    matched_sections.append(section)
                    print(f"Tìm thấy section chứa keyword: '{topic}'")
                    break
        
        if matched_sections:
            result = "\n\n".join(matched_sections)
        else:
            result = markdown_content
            print(f"Không tìm thấy nội dung phù hợp. Sử dụng toàn bộ document.")
    
    return result

def validate_and_clean_quiz_response(quiz_data: dict, payload: Payload) -> dict:
    """
    Validate và clean up response từ AI
    """
    if not isinstance(quiz_data, dict):
        raise ValueError("Response không phải là dict")
    
    if 'questions' not in quiz_data:
        raise ValueError("Response thiếu field 'questions'")
    
    if 'name' not in quiz_data:
        quiz_data['name'] = f"Quiz on {', '.join(payload.topic)} - Grade {payload.grade}"
    
    # Validate và clean up từng câu hỏi
    required_fields = ['question', 'type', 'correct_answers', 'incorrect_answers', 'level']
    
    for i, question in enumerate(quiz_data['questions']):
        # Kiểm tra các field bắt buộc
        for field in required_fields:
            if field not in question:
                raise ValueError(f"Question {i+1} thiếu field '{field}'")
        
        # Đảm bảo có explanation
        if 'explanation' not in question or not question['explanation']:
            question['explanation'] = f"This is the correct answer for this {question['type']} question."
        
        # Đảm bảo correct_answers và incorrect_answers là lists
        if not isinstance(question['correct_answers'], list):
            question['correct_answers'] = [str(question['correct_answers'])]
        
        if not isinstance(question['incorrect_answers'], list):
            question['incorrect_answers'] = [str(question['incorrect_answers'])]
    
    return quiz_data

async def generate_quiz_with_gemini(payload: Payload, content: str) -> dict:
    """
    Gọi Gemini API để sinh câu hỏi
    """
    # Tạo system prompt chi tiết
    system_prompt = f"""
Bạn là một nhà thiết kế bài kiểm tra chuyên nghiệp. Tạo một bài quiz cho học sinh lớp {payload.grade}, môn {payload.subject}.

**YÊU CẦU NGHIÊM NGẶT:**

Tổng số câu hỏi: {payload.amount}
Phân bố CHÍNH XÁC các loại câu hỏi:
- Multiple Choice: {payload.questionType.multiple_choice} câu (1 đáp án đúng, 3 đáp án sai)
- Choose Many: {payload.questionType.choose_many} câu (2-4 đáp án đúng)
- Fill In: {payload.questionType.fill_in} câu (điền từ vào chỗ trống)
- Match Word: {payload.questionType.match_word} câu (ghép cặp từ/cụm từ)
- Open: {payload.questionType.open} câu (câu hỏi mở)

**HƯỚNG DẪN CHI TIẾT:**

1. **Multiple Choice**: 
   - correct_answers: ["đáp án đúng duy nhất"]
   - incorrect_answers: ["sai 1", "sai 2", "sai 3"]

2. **Choose Many**: 
   - correct_answers: ["đúng 1", "đúng 2", "đúng 3"]
   - incorrect_answers: ["sai 1", "sai 2"]

3. **Fill In**: 
   - question: "Câu hỏi có chỗ trống _____"
   - correct_answers: ["từ/cụm từ cần điền"]
   - incorrect_answers: ["các từ khác có thể điền sai"]

4. **Match Word**: 
   - question: "Match the following: A) word1, B) word2, C) word3 with 1) meaning1, 2) meaning2, 3) meaning3"
   - correct_answers: ["A-1", "B-2", "C-3"]
   - incorrect_answers: ["A-2", "B-1", "C-1"]

5. **Open**: 
   - correct_answers: ["mẫu câu trả lời đúng"]
   - incorrect_answers: ["các câu trả lời thường gặp nhưng sai"]

**Mức độ**: Phân bố easy (40%), medium (40%), hard (20%)

**Nội dung dựa trên:**
{content}

**Chủ đề:** {', '.join(payload.topic)}
{f"**Ghi chú:** {payload.note}" if payload.note else ""}

**QUAN TRỌNG**: 
- Chỉ trả về JSON thuần túy, không có markdown hay text khác
- MỖI câu hỏi PHẢI có field "explanation" để giải thích đáp án đúng
- Explanation phải bằng tiếng Anh, ngắn gọn và dễ hiểu cho học sinh lớp {payload.grade}

{{
  "name": "Quiz on {', '.join(payload.topic)} - Grade {payload.grade}",
  "questions": [
    {{
      "question": "Nội dung câu hỏi",
      "type": "multiple-choice/choose-many/fill-in/match-word/open",
      "correct_answers": ["đáp án đúng"],
      "incorrect_answers": ["đáp án sai"],
      "level": "easy/medium/hard",
      "explanation": "Brief explanation in English why this answer is correct"
    }}
  ]
}}
"""

    try:
        # Khởi tạo Gemini model
        model_name = payload.gptModel if payload.gptModel.startswith('gemini') else 'gemini-1.5-flash'
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )

        # Gọi Gemini API
        response = model.generate_content(system_prompt)
        
        # Xử lý response
        quiz_content = response.text.strip()
        
        # Clean up formatting
        if quiz_content.startswith('```json'):
            quiz_content = quiz_content.replace('```json', '').replace('```', '').strip()
        elif quiz_content.startswith('```'):
            quiz_content = quiz_content.replace('```', '').strip()
        
        # Parse JSON
        try:
            quiz_data = json.loads(quiz_content)
        except json.JSONDecodeError:
            # Thử tìm JSON block trong response
            json_match = re.search(r'\{.*\}', quiz_content, re.DOTALL)
            if json_match:
                quiz_data = json.loads(json_match.group())
            else:
                raise ValueError("Không thể parse JSON từ response của Gemini")
        
        # Đảm bảo mỗi câu hỏi có explanation
        if 'questions' in quiz_data:
            for i, question in enumerate(quiz_data['questions']):
                if 'explanation' not in question or not question['explanation']:
                    question['explanation'] = f"This is the correct answer based on the content from {', '.join(payload.topic)}."
        
        # Validate và clean up response
        quiz_data = validate_and_clean_quiz_response(quiz_data, payload)
        
        return quiz_data
        
    except Exception as e:
        raise Exception(f"Lỗi khi gọi Gemini API: {str(e)}")

# API Endpoints
@app.post("/api/generate-quiz", response_model=QuizResponse)
async def generate_quiz(payload: Payload):
    """
    API chính để tạo quiz từ document
    """
    try:
        # Validate input
        if payload.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount phải lớn hơn 0")
        
        total_questions = (
            payload.questionType.choose_many +
            payload.questionType.fill_in +
            payload.questionType.match_word +
            payload.questionType.multiple_choice +
            payload.questionType.open
        )
        
        if total_questions != payload.amount:
            raise HTTPException(
                status_code=400, 
                detail=f"Tổng số câu hỏi ({total_questions}) không khớp với amount ({payload.amount})"
            )
        
        # Đường dẫn file
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        docx_path = data_dir / f"{payload.documentID}.docx"
        md_path = data_dir / f"{payload.documentID}.md"
        
        # Kiểm tra file DOCX
        if not docx_path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Không tìm thấy file {payload.documentID}.docx trong thư mục data"
            )
        
        # Chuyển đổi DOCX sang MD nếu cần
        if not md_path.exists() or docx_path.stat().st_mtime > md_path.stat().st_mtime:
            print(f"Đang chuyển đổi {docx_path} sang {md_path}...")
            success = convert_docx_to_md(str(docx_path), str(md_path))
            if not success:
                raise HTTPException(status_code=500, detail="Lỗi khi chuyển đổi DOCX sang Markdown")
        
        # Đọc file markdown
        async with aiofiles.open(md_path, "r", encoding="utf-8") as f:
            markdown_content = await f.read()
        
        # Trích xuất nội dung theo topics (mặc định lấy cả sub-headings)
        extracted_content = extract_content_by_topics(
            markdown_content, 
            payload.topic, 
            include_children=True
        )
        
        if not extracted_content.strip():
            raise HTTPException(
                status_code=400, 
                detail=f"Không tìm thấy nội dung phù hợp với topics: {', '.join(payload.topic)}"
            )
        
        # Gọi Gemini để tạo quiz
        quiz_data = await generate_quiz_with_gemini(payload, extracted_content)
        
        # Validate response structure
        if not isinstance(quiz_data, dict) or 'questions' not in quiz_data:
            raise HTTPException(status_code=500, detail="Cấu trúc response từ AI không hợp lệ")
        
        if len(quiz_data['questions']) != payload.amount:
            print(f"Cảnh báo: AI tạo {len(quiz_data['questions'])} câu hỏi thay vì {payload.amount}")
        
        return quiz_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

@app.get("/api/health")
async def health_check():
    """
    Kiểm tra trạng thái service
    """
    return {"status": "ok", "message": "Quiz Generator Service is running"}

@app.get("/api/headings/{documentID}")
async def get_document_headings(documentID: str):
    """
    Lấy tất cả headings trong document để người dùng chọn
    """
    try:
        # Đường dẫn file
        data_dir = Path("data")
        docx_path = data_dir / f"{documentID}.docx"
        md_path = data_dir / f"{documentID}.md"
        
        # Kiểm tra file DOCX
        if not docx_path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Không tìm thấy file {documentID}.docx trong thư mục data"
            )
        
        # Chuyển đổi DOCX sang MD nếu cần
        if not md_path.exists() or docx_path.stat().st_mtime > md_path.stat().st_mtime:
            print(f"Đang chuyển đổi {docx_path} sang {md_path}...")
            success = convert_docx_to_md(str(docx_path), str(md_path))
            if not success:
                raise HTTPException(status_code=500, detail="Lỗi khi chuyển đổi DOCX sang Markdown")
        
        # Đọc file markdown
        async with aiofiles.open(md_path, "r", encoding="utf-8") as f:
            markdown_content = await f.read()
        
        # Trích xuất tất cả headings
        headings = extract_all_headings(markdown_content)
        
        # Tổ chức headings theo cấu trúc tree
        organized_headings = organize_headings_tree(headings)
        
        return {
            "documentID": documentID,
            "total_headings": len(headings),
            "headings": organized_headings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy headings: {str(e)}")

def organize_headings_tree(headings: List[dict]) -> List[dict]:
    """
    Tổ chức headings thành cấu trúc tree với children
    """
    if not headings:
        return []
    
    tree = []
    stack = []
    
    for heading in headings:
        # Pop các headings có level cao hơn hoặc bằng current heading
        while stack and stack[-1]['level'] >= heading['level']:
            stack.pop()
        
        # Tạo node mới với cấu trúc đúng
        node = {
            "level": heading['level'],
            "text": heading['text'],
            "id": heading['id'],
            "children": []
        }
        
        # Nếu có parent trong stack, thêm vào children của parent
        if stack:
            stack[-1]['children'].append(node)
        else:
            # Nếu không có parent, thêm vào root level
            tree.append(node)
        
        # Push node hiện tại vào stack để làm parent cho các node tiếp theo
        stack.append(node)
    
    return tree

@app.get("/api/content/{documentID}")
async def get_heading_content(documentID: str, heading: str, include_children: bool = True):
    """
    Xem trước nội dung của một heading 
    - include_children=True: Lấy cả sub-headings (mặc định)
    - include_children=False: Chỉ lấy nội dung của heading đó
    """
    try:
        # Đường dẫn file
        data_dir = Path("data")
        md_path = data_dir / f"{documentID}.md"
        
        if not md_path.exists():
            raise HTTPException(status_code=404, detail="File markdown không tồn tại")
        
        # Đọc file markdown
        async with aiofiles.open(md_path, "r", encoding="utf-8") as f:
            markdown_content = await f.read()
        
        # Trích xuất nội dung
        if include_children:
            content = extract_content_by_heading_with_children(markdown_content, heading)
            extraction_type = "with sub-headings"
        else:
            content = extract_content_by_specific_heading(markdown_content, heading)
            extraction_type = "specific heading only"
        
        if not content or content == markdown_content:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy nội dung cho heading: {heading}")
        
        # Tính toán thống kê
        lines = content.split('\n')
        word_count = len(' '.join(lines).split())
        
        # Đếm số headings trong content
        heading_count = len([line for line in lines if line.strip().startswith('#')])
        
        return {
            "documentID": documentID,
            "heading": heading,
            "extraction_type": extraction_type,
            "include_children": include_children,
            "content": content,
            "preview": content[:500] + "..." if len(content) > 500 else content,
            "stats": {
                "lines": len(lines),
                "characters": len(content),
                "words": word_count,
                "headings_included": heading_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy nội dung: {str(e)}")

@app.get("/api/documents")
async def list_documents():
    """
    Liệt kê tất cả documents có sẵn
    """
    try:
        data_dir = Path("data")
        if not data_dir.exists():
            return {"documents": []}
        
        documents = []
        for file_path in data_dir.glob("*.docx"):
            md_path = data_dir / f"{file_path.stem}.md"
            documents.append({
                "id": file_path.stem,
                "name": file_path.name,
                "has_markdown": md_path.exists(),
                "last_modified": file_path.stat().st_mtime
            })
        
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi liệt kê documents: {str(e)}")

# Chạy ứng dụng
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)