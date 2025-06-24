import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory

# 1. Load API Key dari .env
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY belum di-set di .env")

# 2. Konfigurasi Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
# Untuk aplikasi nyata, session_id harus unik per pengguna/percakapan
SESSION_ID = "user_session_01"

# 3. Load dan split dokumen
print("📄 Memuat transkrip...")
loader = TextLoader("./transkrip.txt", encoding='utf-8')
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

# 4. Load model embedding lokal
print("🧠 Memuat model embedding...")
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 5. Load atau buat FAISS vector index
INDEX_PATH = "vector_index"
if os.path.exists(INDEX_PATH):
    print("🔁 Memuat FAISS index yang sudah ada...")
    db = FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)
else:
    print("⚙️ Membuat FAISS index baru...")
    db = FAISS.from_documents(docs, embedding_model)
    db.save_local(INDEX_PATH)
    print("✅ Index disimpan ke folder:", INDEX_PATH)

# 6. Siapkan retriever (semantic search)
retriever = db.as_retriever(search_kwargs={"k": 3})

# 7. Siapkan LLM dari Google Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=0.3,
    google_api_key=GOOGLE_API_KEY
)

# 8. Siapkan memory dengan Redis
print(f"🧠 Menghubungkan ke Redis untuk chat memory (Session: {SESSION_ID})...")
try:
    redis_history = RedisChatMessageHistory(session_id=SESSION_ID, url=REDIS_URL)
except Exception as e:
    raise ConnectionError(f"❌ Gagal terhubung ke Redis di {REDIS_URL}. Pastikan Redis server berjalan. Error: {e}")

memory = ConversationBufferMemory(
    memory_key="chat_history",
    chat_memory=redis_history,
    return_messages=True,
    output_key='answer'
)

# 9. Buat ConversationalRetrievalChain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    return_source_documents=True,
    verbose=False
)

# 10. Jalankan chatbot CLI
print("\n💬 Chatbot Transkrip Video Aktif! (Ketik 'exit' untuk keluar)\n")

while True:
    query = input("🧑 Kamu: ")
    if query.lower() == "exit":
        print("👋 Sampai jumpa!")
        break
    if not query.strip():
        continue

    result = qa_chain.invoke({"question": query})

    print("\n🤖 Bot:", result["answer"])

    # (Opsional) tampilkan sumber dokumen
    if result.get("source_documents"):
        print("📚 Sumber (chunk):")
        for doc in result["source_documents"]:
            print(f"- {doc.page_content[:100].replace('\n', ' ')}...")
    print("\n" + "-" * 60)
