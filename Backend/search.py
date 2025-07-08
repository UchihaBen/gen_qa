# import chromadb
# from transformers import AutoTokenizer, AutoModel
# import torch
# import numpy as np
# import re

# # 1. Đọc file .md và phân tách thành các chunk
# def load_md_file(file_path):
#     with open(file_path, 'r', encoding='utf-8') as f:
#         content = f.read()
    
#     # Tách các unit và bài theo Heading 1 và Heading 2
#     units = re.split(r'\n# ', content)  # Phân tách theo unit (Heading 1)
#     units = [unit.strip() for unit in units if unit.strip()]
    
#     # Phân tách mỗi unit thành các bài (Heading 2)
#     unit_chunks = {}
#     for unit in units:
#         unit_name = unit.split("\n")[0].strip()  # Tên của unit
#         unit_content = "\n".join(unit.split("\n")[1:]).strip()
#         lessons = re.split(r'\n## ', unit_content)  # Phân tách theo bài học (Heading 2)
#         lessons = [lesson.strip() for lesson in lessons if lesson.strip()]
#         unit_chunks[unit_name] = lessons
    
#     return unit_chunks

# # 2. Chuyển các bài học thành embedding
# class EmbeddingModel:
#     def __init__(self, model_name="intfloat/multilingual-e5-base"):
#         self.tokenizer = AutoTokenizer.from_pretrained(model_name)
#         self.model = AutoModel.from_pretrained(model_name)
    
#     def encode(self, text):
#         inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
#         with torch.no_grad():
#             embeddings = self.model(**inputs).last_hidden_state.mean(dim=1)  # Mean pooling
#         return embeddings.squeeze().cpu().numpy()

# # 3. Lưu embedding vào ChromaDB và tìm kiếm
# def generate_and_store_embeddings(unit_chunks):
#     model = EmbeddingModel()
#     client = chromadb.Client()  # Khởi tạo ChromaDB client
#     collection = client.create_collection("unit_lessons")  # Tạo collection mới trong ChromaDB
    
#     # Tạo embedding cho các bài học và lưu vào ChromaDB
#     texts = []
#     embeddings = []
#     metadata = []  # Metadata để lưu thông tin về Heading 1 và Heading 2
    
#     chunk_counter = 1  # Biến đếm số chunk
    
#     for unit_name, lessons in unit_chunks.items():
#         for lesson_name in lessons:
#             # Kết hợp tiêu đề và nội dung bài học thành một chunk duy nhất
#             full_text = f"Chunk {chunk_counter}: {unit_name} - {lesson_name}"  # Kết hợp cả Unit và bài học
#             embedding = model.encode(full_text)
#             texts.append(full_text)
#             embeddings.append(embedding)
#             # Lưu metadata chỉ với tiêu đề Heading 1 và Heading 2
#             metadata.append({"heading_1": unit_name, "heading_2": lesson_name})  # Lưu Heading 1 và Heading 2
#             chunk_counter += 1  # Tăng số chunk
    
#     # Lưu embedding vào ChromaDB
#     collection.add(
#         documents=texts,
#         embeddings=np.array(embeddings),
#         metadatas=metadata,
#         ids=[str(i) for i in range(len(texts))]
#     )
    
#     return collection

# # 4. Tìm kiếm bài học theo câu hỏi của người dùng
# def search_in_chromadb(query, collection, model):
#     # Tạo embedding cho câu hỏi
#     query_embedding = model.encode(query)
    
#     # Tìm kiếm trong ChromaDB
#     results = collection.query(
#         query_embeddings=np.array([query_embedding]),
#         n_results=3  # Trả về 3 kết quả gần nhất
#     )
    
#     return results["documents"], results["metadatas"], results["distances"]  # In thêm độ tương đồng (score)

# # 5. Main function
# if __name__ == "__main__":
#     file_path = 'output.md'  # Đường dẫn đến file Markdown
#     unit_chunks = load_md_file(file_path)
    
#     # Lưu embedding vào ChromaDB
#     collection = generate_and_store_embeddings(unit_chunks)
    
#     # Tìm kiếm ví dụ với câu hỏi
#     query = "Unit 7 Activity 3"  # Câu hỏi của người dùng
#     documents, metadatas, distances = search_in_chromadb(query, collection, EmbeddingModel())
    
#     print("Top 3 relevant lessons based on your query:")
#     for idx, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances), start=1):
#         # Đảm bảo metadata là một danh sách các từ điển
#         if isinstance(metadata, list):  # Kiểm tra nếu metadata là danh sách
#             metadata = metadata[0]  # Lấy phần tử đầu tiên trong danh sách nếu metadata là một list
        
#         # In ra các thông tin về Unit và Lesson
#         print(f"Chunk {idx}:")
#         print(f"Heading 1: {metadata.get('heading_1', 'N/A')}, Heading 2: {metadata.get('heading_2', 'N/A')}")
#         print(f"Content: {doc}")
#         print(f"Score (distance): {distance}\n")





import chromadb
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import re

# 1. Đọc file .md và phân tách thành các chunk
def load_md_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tách các unit và bài theo Heading 1 và Heading 2
    units = re.split(r'\n# ', content)  # Phân tách theo unit (Heading 1)
    units = [unit.strip() for unit in units if unit.strip()]
    
    # Phân tách mỗi unit thành các bài (Heading 2)
    unit_chunks = {}
    for unit in units:
        unit_name = unit.split("\n")[0].strip()  # Tên của unit
        unit_content = "\n".join(unit.split("\n")[1:]).strip()
        lessons = re.split(r'\n## ', unit_content)  # Phân tách theo bài học (Heading 2)
        lessons = [lesson.strip() for lesson in lessons if lesson.strip()]
        unit_chunks[unit_name] = lessons
    
    return unit_chunks

# 2. Chuyển các bài học thành embedding
class EmbeddingModel:
    def __init__(self, model_name="intfloat/multilingual-e5-base"):
        # Tải mô hình và tokenizer một lần duy nhất
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
    
    def encode(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            embeddings = self.model(**inputs).last_hidden_state.mean(dim=1)  # Mean pooling
        return embeddings.squeeze().cpu().numpy()

# 3. Lưu embedding vào ChromaDB và tìm kiếm
def generate_and_store_embeddings(unit_chunks, model):
    client = chromadb.Client()  # Khởi tạo ChromaDB client
    collection = client.create_collection("unit_lessons")  # Tạo collection mới trong ChromaDB
    
    # Tạo embedding cho các bài học và lưu vào ChromaDB
    texts = []
    embeddings = []
    metadata = []  # Metadata để lưu thông tin về Heading 1 và Heading 2
    
    chunk_counter = 1  # Biến đếm số chunk
    
    for unit_name, lessons in unit_chunks.items():
        for lesson_name in lessons:
            # Kết hợp tiêu đề và nội dung bài học thành một chunk duy nhất
            full_text = f"Chunk {chunk_counter}: {unit_name} - {lesson_name}"  # Kết hợp cả Unit và bài học
            embedding = model.encode(full_text)
            texts.append(full_text)
            embeddings.append(embedding)
            # Lưu metadata chỉ với tiêu đề Heading 1 và Heading 2
            metadata.append({"heading_1": unit_name, "heading_2": lesson_name})  # Lưu Heading 1 và Heading 2
            chunk_counter += 1  # Tăng số chunk
    
    # Lưu embedding vào ChromaDB
    collection.add(
        documents=texts,
        embeddings=np.array(embeddings),
        metadatas=metadata,
        ids=[str(i) for i in range(len(texts))]
    )
    
    return collection

# 4. Tìm kiếm bài học theo câu hỏi của người dùng
def search_in_chromadb(query, collection, model):
    # Tạo embedding cho câu hỏi
    query_embedding = model.encode(query)
    
    # Tìm kiếm trong ChromaDB
    results = collection.query(
        query_embeddings=np.array([query_embedding]),
        n_results=3  # Trả về 3 kết quả gần nhất
    )
    
    return results["documents"], results["metadatas"], results["distances"]  # In thêm độ tương đồng (score)

# 5. Main function
if __name__ == "__main__":
    file_path = 'output.md'  # Đường dẫn đến file Markdown
    unit_chunks = load_md_file(file_path)
    
    # Tải mô hình và tokenizer một lần
    model = EmbeddingModel()
    
    # Lưu embedding vào ChromaDB
    collection = generate_and_store_embeddings(unit_chunks, model)
    
    # Tìm kiếm ví dụ với câu hỏi
    query = "Unit 7 Activity 3"  # Câu hỏi của người dùng
    documents, metadatas, distances = search_in_chromadb(query, collection, model)
    
    print("Top 3 relevant lessons based on your query:")
    for idx, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances), start=1):
        # Đảm bảo metadata là một danh sách các từ điển
        # if isinstance(metadata, list):  # Kiểm tra nếu metadata là danh sách
        #     metadata = metadata[0]  # Lấy phần tử đầu tiên trong danh sách nếu metadata là một list
        
        # In ra các thông tin về Unit và Lesson
        print(f"Chunk {idx}:")
        print(f"Heading 1: {metadata[0].get('heading_1', 'N/A')}, Heading 2: {metadata[0].get('heading_2', 'N/A')}")

        print(f"Chunk {idx}:")
        print(f"Heading 2: {metadata[1].get('heading_1', 'N/A')}, Heading 2: {metadata[1].get('heading_2', 'N/A')}")

        print(f"Chunk {idx}:")
        print(f"Heading 3: {metadata[2].get('heading_1', 'N/A')}, Heading 2: {metadata[2].get('heading_2', 'N/A')}")
        
        # print(f"Content: {doc}")
        # print(f"Score (distance): {distance}\n")
