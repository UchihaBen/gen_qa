from docx import Document


input_file = "data/Tiếng Anh 6 - tập 2 - SGV .docx"
output_file = "data/Tiếng Anh 6 - tập 2 - SGV .md"
# Đọc file DOCX
doc = Document(input_file)

# Tạo danh sách lưu trữ các phần trong Markdown
markdown_content = []

# Duyệt qua tất cả các đoạn văn trong file DOCX
for para in doc.paragraphs:
    # Kiểm tra kiểu của từng đoạn
    if para.style.name == "Heading 1":
        markdown_content.append(f"# {para.text}\n")  # Heading 1: # tiêu đề cấp 1
    elif para.style.name == "Heading 2":
        markdown_content.append(f"## {para.text}\n")  # Heading 2: ## tiêu đề cấp 2
    elif para.style.name == "Heading 3":
        markdown_content.append(f"### {para.text}\n")  # Heading 3: ### tiêu đề cấp 3
    elif para.style.name == "Heading 4":
        markdown_content.append(f"#### {para.text}\n")  # Heading 4: #### tiêu đề cấp 4
    else:
        # Đoạn văn bình thường (không phải tiêu đề)
        markdown_content.append(f"{para.text}\n")

# Lưu kết quả vào file Markdown (.md)
with open(output_file, "w", encoding="utf-8") as md_file:
    md_file.write("\n".join(markdown_content))

print("Tái cấu trúc thành công và lưu vào file Markdown:", output_file)
