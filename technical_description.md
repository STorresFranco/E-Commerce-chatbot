## 🧠 Conversational Route

If the user prompt is classified as **conversational**, the chatbot will generate a friendly, direct response and invite the user to either ask a **FAQ** or make a **product inquiry**.

- A **Few-Shot Prompt** is used to instruct the **Groq API** for chat completion.
- This route is focused on **natural, free-form interactions** without retrieving external data.

### 🗂️ Process Overview

```
[User Prompt]
     ↓
[Semantic Router → Conversational Route]
     ↓
[Chat Completion using Few-Shot Prompt (Groq)]
     ↓
[Friendly Response + Suggestion to explore FAQ/Product]
```

---

## ❓ FAQ Route

**Resources**: A Chroma database containing **10 frequently asked questions**, chunked for efficient similarity search.

If the prompt is classified as an **FAQ**, the system performs a **two-stage process**:

1. **Retrieval**  
   The top two most relevant chunks are selected from the FAQ database using **similarity-based retrieval**.

2. **Response Generation**  
   A **RAG (Retrieval-Augmented Generation)** strategy is used to answer the question, leveraging the retrieved content for accuracy and relevance.

### 📌 Process Overview

```
[User Prompt]
     ↓
[Semantic Router → FAQ Route]
     ↓
[Retrieve top 2 similar chunks (Chroma DB)]
     ↓
[RAG Response using Groq Completion API]
```

---

## 🛒 Product Route

**Resources**: An **SQLite database** containing **903 shoes**, with attributes including:

- `product_link` – Product URL  
- `title` – Product title or classification  
- `brand` – Brand name  
- `discount` – Discount percentage  
- `avg_rating` – Average user rating  
- `total_ratings` – Total number of reviews  

When the prompt is classified as a **product-related inquiry**, the application follows a **three-stage pipeline**:

1. **SQL Translation**  
   The natural language prompt is converted to a valid **SQL query** using the **Groq framework**.

2. **Query Execution**  
   The SQL query is run on the in-memory DataFrame loaded from the SQLite database.

3. **UX-Oriented Response**  
   The result is passed to Groq again to generate a **user-friendly response** that simulates a natural assistant.

### 🛠️ Process Overview

```
[User Prompt]
     ↓
[Semantic Router → Product Route]
     ↓
[Translate prompt → SQL query (Groq)]
     ↓
[Run query on DataFrame (SQLite → Pandas)]
     ↓
[Generate UI-style response (Groq)]
```

---

## 🧩 Unknown Route

If the prompt doesn't match any of the defined categories (Conversational, FAQ, or Product), the system falls into the **Unknown Route**.

- In this case, the chatbot asks the user to choose a valid route explicitly.
- The conversation then redirects back to the **semantic router** for reevaluation.

### 🔄 Process Overview

```
[User Prompt]
     ↓
[Semantic Router → Unknown Route]
     ↓
[Ask user to select a valid route]
     ↓
[Return to Semantic Router]
```
