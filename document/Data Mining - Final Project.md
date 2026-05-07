# 🚀 SIÊU ĐẶC TẢ HỆ THỐNG: POS INTELLIGENCE & SEMANTIC RAG

_(Tài liệu Kiến trúc & Thiết kế Thuật toán Khai phá Dữ liệu Lặp - Iterative Data Mining)_

> [!abstract] **Tầm nhìn Kiến trúc (Architectural Vision)**
> 
> - **Bài toán gốc:** Hệ thống POS hiện tại (viết bằng Google Apps Script) xử lý Transaction rất tốt nhờ cơ chế `LockService` và `CacheService`, nhưng lưu trữ dữ liệu hoàn toàn "phẳng". Cột ghi chú (`_ORDER_NOTE_SYSTEM_`) bị lãng phí.
>     
> - **Mục tiêu Khai phá:** Chuyển đổi từ dữ liệu phẳng sang **Tri thức đa chiều**. Thay vì dùng bộ dữ liệu Paysim (Credit Card Fraud) đã quá nhàm chán và nặng tính học thuật, dự án này dùng dữ liệu thực tế để giải quyết bài toán: **Rò rỉ dòng tiền (Cash Leakage) do áp lực vận hành.**
>     
> - **Quy trình Lặp (CRISP-DM):** > 1. Số liệu báo động (Isolation Forest / K-Means).
>     
>     2. Chữ nghĩa giải thích (PhoBERT).
>     
>     3. AI đưa ra quyết định (RAG / Gemini API).
>     

---

## 🎯 PHẦN I: GIẢI PHẪU 4 TRỤ CỘT ỨNG DỤNG (USE CASE ANATOMY)

### 1. Nhận diện Hành vi Thanh toán theo Ca (Shift-based Behavior Recognition)

- **Kỹ thuật:** Phân tích Thống kê mô tả (Descriptive Statistics) & `K-Means Clustering`.
    
- **Đầu vào (Vector $X$):** $X = [Shift\_Intensity, Cash\_Ratio, Is\_Morning]$ (Với `Is_Morning` lấy từ cột `Ca sáng?`).
    
- **Toán học cốt lõi:** K-Means sẽ gom cụm dữ liệu dựa trên khoảng cách Euclidean:
    
    $$J = \sum_{j=1}^{k} \sum_{i=1}^{n} ||x_i^{(j)} - c_j||^2$$
    
- **Logic Kinh doanh (Thực tế):** Quán có sự phân hóa rõ rệt giữa **Ca Sáng** và **Ca Chiều/Tối**. Thuật toán sẽ phân cụm để chứng minh sự khác biệt này bằng số liệu. Ví dụ: Cụm 0 (Đa phần là Ca Sáng: Tốc độ ra món nhanh, 85% thanh toán tiền mặt $\rightarrow$ Áp lực tiền lẻ), Cụm 1 (Đa phần là Ca Chiều: Doanh thu trung bình, 70% chuyển khoản $\rightarrow$ Áp lực kiểm tra bill).
    

### 2. Dò tìm Dị thường & Cảnh báo Rủi ro (Micro Risk Sentinel)

- **Kỹ thuật:** `Isolation Forest` (Cây cô lập).
    
- **Đầu vào:** $X = [Discrepancy\_Rate, Velocity, Manual\_Overhead]$
    
- **Toán học cốt lõi:** Thuật toán xây dựng các cây ngẫu nhiên (Random Trees) để **cô lập** các điểm dữ liệu. Điểm nào bị cô lập với số lần cắt (path length) ngắn nhất chính là điểm dị thường (Outlier).
    
- **Logic Kinh doanh:** Một ca làm việc bị lệch 50k không hẳn là ăn cắp, có thể do ca đó quá đông (`Velocity` cao) và khách đổi món nhiều (`Manual_Overhead` cao). Thuật toán sẽ tính toán xem mức độ lệch này có "chấp nhận được" trong bối cảnh của ca (Sáng hay Chiều) hay không.
    

### 3. Phân loại Ngữ nghĩa Ghi chú (Semantic Note Classification) 🌟

- **Kỹ thuật:** Fine-tuning / Zero-shot Classification với `vinai/phobert-base`.
    
- **Đầu vào:** Cột `Notes` đã được phục hồi từ History. (Vd: _"ít đường, thêm trân châu trắng anh Tuấn bàn 5"_).
    
- **Cơ chế hoạt động:** PhoBERT sẽ chuyển hóa câu Text thành Vector nhúng (Embeddings), sau đó phân loại vào 3 tập nhãn:
    
    - `Class 0`: Rác/Khác (Giao hàng, Hủy).
        
    - `Class 1`: Custom_Khẩu_Vị (Thay đổi công thức).
        
    - `Class 2`: Khách_VIP (Tên riêng, thẻ bàn tháng).
        
- **Đầu ra:** Biến chuỗi Text thành các biến định lượng mới: `VIP_Count` và `Custom_Count`.
    

### 4. Trợ lý Sinh văn bản có Truy xuất Context (Lightweight RAG) 🌟

- **Kỹ thuật:** `Gemini 1.5 Flash API` kết hợp với `Prompt Engineering`.
    
- **Cơ chế hoạt động (RAG Pipeline):**
    
    1. **Retrieval (Truy xuất):** Lấy thông số từ Vòng 1 (Lệch két ở Ca Sáng hay Ca Chiều) + Thống kê từ Vòng 2 (Số lượng Note VIP).
        
    2. **Augmentation (Làm giàu):** Bơm các số liệu này vào một Template Prompt chuẩn mực.
        
    3. **Generation (Sinh chữ):** Gemini nhận Prompt và trả về lời khuyên vận hành cho chủ quán.
        

---

## 🧬 PHẦN II: PIPELINE FEATURE ENGINEERING (ETL & TRANSFORMATION)

Chuyển từ dữ liệu `MainLog` (6 cột) sang ma trận đặc trưng cho Machine Learning.

### Bước 1: Khai thác Biến Thời gian & Cường độ (Time & Intensity)

- `Is_Morning`: Bê nguyên từ cột `Ca sáng?` (True/False) trong `MainLog`. Biến phân loại rạch ròi nhất của hệ thống.
    
- `Shift_Intensity` (Tốc độ dòng tiền):
    
    $$Shift\_Intensity = \frac{Gross\_Revenue}{Duration\_of\_Shift\_in\_Hours}$$
    

### Bước 2: Tính toán Biến Rủi ro & Thanh toán (Risk & Payment)

- `Cash_Ratio`: Khai phá thói quen thanh toán giữa các ca.
    
    $$Cash\_Ratio = \frac{Cash}{Cash + Transfer}$$
    
- `Discrepancy_Rate` (Biến mục tiêu cho Anomaly):
    
    $$Discrepancy\_Rate = \frac{Gross - (Cash + Transfer)}{Gross}$$
    

### Bước 3: Tính toán Biến Vận hành thủ công (Từ PhoBERT)

- `Manual_Overhead_Rate`: Tỷ lệ phần trăm đơn hàng có chứa ghi chú phải gõ tay (Sử dụng item ảo `_ORDER_NOTE_SYSTEM_`). Mức độ này càng cao, nhân viên càng dễ stress và tính nhầm tiền, đặc biệt là trong Ca Sáng vội vã.
    

---

## 🔄 PHẦN III: LUỒNG CHẢY CỦA VÒNG ĐỜI KHAI PHÁ (THE ITERATIVE DATA FLOW)

Đây là kịch bản chạy code (Flow of Execution) trên Streamlit App.

1. **Khởi tạo (Data Upload):** User upload `MainLog.csv` và `LiveOrders_History.csv`.
    
2. **Vòng 1 (Diagnostic):** Hàm `run_kmeans()` chạy để đối chiếu hành vi thanh toán giữa Ca Sáng và Ca Chiều. Sinh ra cột `Cluster_ID`. Hàm `run_isolation_forest()` chạy tiếp, sinh ra cột `Is_Anomaly` (True/False) để cảnh báo ca bị lệch tiền.
    
3. **Trigger Lặp (The Iteration Trigger):** Hệ thống kiểm tra: `if Is_Anomaly == True:` $\rightarrow$ Lọc ra khoảng thời gian (Timestamp) của ca bị lỗi này.
    
4. **Vòng 2 (Semantic Analysis):** Lấy tất cả các câu `Notes` trong khoảng thời gian vừa lọc, đẩy vào hàm `run_phobert_classification()`. Trả về số lượng `VIP_Count` và `Custom_Count`.
    
5. **Vòng 3 (RAG & Prescriptive):** Đưa toàn bộ `Is_Morning`, `Discrepancy_Rate`, `VIP_Count` vào Prompt, gọi hàm `call_gemini_api()`. In kết quả ra màn hình.
    
6. **Vòng 4 (Forecasting - Kế thừa):** Đưa `Is_Morning` cùng với dữ liệu lịch sử vào mô hình `RandomForestRegressor` để dự báo `Target = Cash_Amount` cho ca kế tiếp.
    

---

## 🛠️ PHẦN IV: CẤU TRÚC THƯ MỤC & TECH STACK (CHO DEVELOPER)

Bỏ qua FastAPI, hệ thống dùng **Streamlit Monolithic Architecture** để chạy siêu tốc.

### Tech Stack:

- **UI/Backend:** `streamlit` (v1.30+)
    
- **Data Processing:** `pandas`, `numpy`
    
- **Machine Learning:** `scikit-learn`
    
- **NLP:** `transformers` (HuggingFace), `torch` (Bản CPU)
    
- **LLM API:** `google-generativeai`
    
- **Visualization:** `plotly`
    

### Cấu trúc Project (Project Structure):

Plaintext

```
pos-iterative-miner/
├── .env                        # Chứa GEMINI_API_KEY
├── requirements.txt            # Danh sách thư viện
├── app.py                      # Main UI Streamlit
├── data/
│   ├── raw_mainlog.csv         # Dữ liệu xuất từ Google Sheets
│   └── notes_dataset_200.csv   # Dữ liệu 200 câu đã label tay (Bắt buộc có)
├── src/
│   ├── __init__.py
│   ├── data_processor.py       # Hàm tính toán Feature Engineering (Pandas)
│   ├── ml_engine.py            # Hàm K-Means, Isolation Forest, Random Forest
│   ├── nlp_engine.py           # Hàm load PhoBERT và phân loại text
│   └── rag_agent.py            # Hàm build Prompt và gọi Gemini API
└── notebooks/
    └── EDA_Training.ipynb      # File Jupyter dùng để train và test code
```

---

## 💻 PHẦN V: THIẾT KẾ CÁC ĐOẠN CODE LÕI (CORE SNIPPETS)

Đây là những đoạn code xương sống chứng minh bạn hiểu rõ hệ thống.

### 1. NLP Engine (PhoBERT Base Zero-shot)

Dùng Zero-shot Classification của HuggingFace là một "hack" cực mạnh:

Python

```
# src/nlp_engine.py
from transformers import pipeline

def analyze_notes_phobert(notes_list):
    # Ở đây dùng zero-shot để tiết kiệm thời gian training
    classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
    
    candidate_labels = ["Thay đổi khẩu vị món ăn", "Khách hàng VIP bàn tháng", "Phàn nàn dịch vụ", "Giao hàng"]
    
    results = {"Khẩu vị": 0, "VIP": 0, "Rác": 0}
    
    for note in notes_list:
        res = classifier(note, candidate_labels)
        top_label = res['labels'][0]
        score = res['scores'][0]
        
        if score > 0.6: # Confidence threshold
            if top_label == "Thay đổi khẩu vị món ăn": results["Khẩu vị"] += 1
            elif top_label == "Khách hàng VIP bàn tháng": results["VIP"] += 1
        else:
            results["Rác"] += 1
            
    return results
```

### 2. RAG Agent (Tích hợp Context và Gemini)

Python

```
# src/rag_agent.py
import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_advice(is_morning, discrepancy_amount, vip_count, custom_count, velocity):
    shift_name = "Ca Sáng" if is_morning else "Ca Chiều/Tối"
    
    prompt = f"""
    Đóng vai trò là một chuyên gia vận hành F&B. Hãy phân tích dữ liệu sau của một ca làm việc bị lệch tiền két:
    - Thời điểm: {shift_name}
    - Số tiền lệch: {discrepancy_amount} VNĐ.
    - Cường độ phục vụ: {velocity} đơn/giờ.
    - Số lượng khách VIP/Bàn tháng xuất hiện: {vip_count}.
    - Số lượng yêu cầu thay đổi khẩu vị (ít đường/đá): {custom_count}.
    
    Hãy giải thích tại sao lại xảy ra sự cố lệch tiền mặt này dựa trên áp lực thao tác ghi chú của nhân viên trong {shift_name}, và đề xuất 2 hành động cụ thể trên phần mềm POS để khắc phục. Phản hồi ngắn gọn, chuyên nghiệp bằng tiếng Việt.
    """
    response = model.generate_content(prompt)
    return response.text
```

---

## 📅 PHẦN VI: KẾ HOẠCH THỰC THI SPRINT 21 NGÀY (AGILE PLAN)

### 🔴 Tuần 1: Data Engineering & Ground Truth (Xây móng)

- **Ngày 1-2:** Trích xuất bảng `MainLog` và lấy lại khoảng 500 dòng `_ORDER_NOTE_SYSTEM_` từ History.
    
- **Ngày 3-4 (Nhiệm vụ sinh tử):** Mở file Excel chứa 500 dòng Note ra. Ngồi gõ tay cột `Label` (0, 1, 2) cho ít nhất 200 dòng. **Đây là tập Ground Truth để báo cáo với thầy.**
    
- **Ngày 5-7:** Khởi tạo Project. Code file `data_processor.py`. Hoàn thành giao diện Streamlit cơ bản.
    

### 🟡 Tuần 2: Machine Learning & NLP Core (Lắp Não)

- **Ngày 8-10:** Code file `ml_engine.py` (K-Means và Isolation Forest). Hiển thị Scatter Plot lên Streamlit.
    
- **Ngày 11-12:** Test thư viện `transformers`. Viết hàm nhận list câu Note và trả về số lượng đếm được.
    
- **Ngày 13-14:** Viết logic "Trigger": Chỉ lấy data của những dòng bị Isolation Forest báo đỏ $\rightarrow$ Gửi Text qua NLP Engine.
    

### 🟢 Tuần 3: LLM Integration & Polishing (Phép màu & Đóng gói)

- **Ngày 15-16:** Cắm Gemini API vào `rag_agent.py`. Truyền dữ liệu tĩnh vào test thử Prompt.
    
- **Ngày 17-18:** Nối toàn bộ quy trình lại (Upload CSV $\rightarrow$ Isolation Forest $\rightarrow$ Lọc Notes $\rightarrow$ PhoBERT $\rightarrow$ Gemini $\rightarrow$ UI).
    
- **Ngày 19-20 (Viết Báo Cáo):** Đưa Ma trận nhầm lẫn (Confusion Matrix) của 200 câu Notes vào báo cáo để chứng minh phần NLP.
    
- **Ngày 21:** Quay video màn hình hoạt động của Web. Nộp bài!
    

---

## 🎭 PHẦN VII: BÍ KÍP DEFENSE (BẢO VỆ ĐỒ ÁN TRƯỚC HỘI ĐỒNG)

1. **Thầy hỏi:** _"Em dùng PhoBERT hay DeBERTa Zero-shot? Nếu dùng Zero-shot thì em tự label 200 câu làm gì?"_
    
    - **Trả lời:** _"Dạ thưa thầy, trong môi trường Production thực tế với deadline 3 tuần, em sử dụng mô hình Zero-shot để triển khai Inference cho nhẹ máy và nhanh chóng. Tuy nhiên, tập 200 câu em tự Label không hề vô ích, nó đóng vai trò là tập **Validation Set**. Em dùng tập 200 câu này để đánh giá xem mô hình Zero-shot đạt độ chính xác (F1-Score) bao nhiêu phần trăm trên bộ từ vựng đặc thù của quán cà phê, từ đó tinh chỉnh Prompt của Zero-shot cho chuẩn xác nhất ạ."_
        
2. **Thầy hỏi:** _"Hệ thống RAG của em không có Vector Database (như Chroma/Pinecone)? Vậy sao gọi là RAG?"_
    
    - **Trả lời:** _"Dạ, RAG (Retrieval-Augmented Generation) bản chất là truy xuất thông tin để bổ sung ngữ cảnh cho LLM. Vì dữ liệu POS của em là Dữ liệu Có Cấu Trúc (Structured Data - dạng bảng) và tập Notes của từng ca khá nhỏ (vài chục dòng), việc thiết lập một Vector Database là **Over-engineering** và gây độ trễ. Em thực hiện quá trình 'Retrieval' bằng các câu lệnh truy vấn SQL/Pandas cơ bản để lấy đúng data của ca bị lỗi, sau đó 'Augment' trực tiếp vào Text Prompt. Phương pháp này gọi là **Lightweight RAG cho Tabular Data**, tối ưu tuyệt đối cho hệ thống máy tính cấu hình yếu ạ."_
        
3. **Thầy hỏi:** _"Đâu là điểm chứng minh sự 'Vòng đời' trong hệ thống này?"_
    
    - **Trả lời:** _"Dạ, điểm giao thoa nằm ở việc Mô hình Ngôn ngữ (NLP) **không chạy độc lập**. Mô hình NLP chỉ được đánh thức (Trigger) khi mô hình Toán học (Isolation Forest) chỉ ra điểm bất thường. Sự kết nối giữa **Phát hiện dị thường bằng Số liệu** và **Giải thích nguyên nhân bằng Chữ nghĩa** chính là vòng lặp khép kín của đồ án này ạ."_