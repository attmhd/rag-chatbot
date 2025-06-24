# Chatbot Transkrip Video dengan RAG & Memori

Chatbot ini memungkinkan Anda untuk mengajukan pertanyaan tentang konten dari sebuah file transkrip video. Dibangun dengan menggunakan model RAG (*Retrieval-Augmented Generation*), chatbot ini dapat memberikan jawaban yang relevan secara kontekstual berdasarkan informasi yang ada di dalam transkrip.

Untuk memberikan pengalaman pengguna yang lebih alami, chatbot ini dilengkapi dengan memori percakapan menggunakan **Redis**. Hal ini memungkinkan chatbot untuk mengingat interaksi sebelumnya dalam satu sesi, sehingga dapat menjawab pertanyaan lanjutan dengan lebih baik.

## Fitur Utama

- **Retrieval-Augmented Generation (RAG)**: Menggabungkan kekuatan model bahasa (Google Gemini Pro) dengan kemampuan pencarian semantik pada data lokal (transkrip video).
- **Pencarian Semantik**: Menggunakan `FAISS` dari Facebook AI untuk membuat dan menyimpan indeks vektor dari transkrip, memungkinkan pencarian cepat berdasarkan makna, bukan hanya kata kunci.
- **Model Embedding Lokal**: Mengandalkan model `sentence-transformers/all-MiniLM-L6-v2` dari Hugging Face untuk mengubah teks menjadi vektor embedding secara lokal, tanpa perlu API eksternal.
- **Memori Percakapan Persisten**: Terintegrasi dengan **Redis** untuk menyimpan riwayat obrolan, sehingga chatbot dapat mengingat konteks percakapan sebelumnya.
- **Konfigurasi Fleksibel**: Menggunakan file `.env` untuk mengelola kunci API dan konfigurasi lainnya dengan aman.

---

## Cara Kerja

1.  **Inisialisasi**: Skrip memuat kunci API Google dan URL Redis dari file `.env`.
2.  **Pemuatan Dokumen**: Transkrip dari file `transkrip.txt` dimuat dan dipecah menjadi beberapa bagian (chunks) yang lebih kecil.
3.  **Pembuatan Embedding & Indeks**: Setiap *chunk* diubah menjadi vektor numerik (embedding) menggunakan model Hugging Face. Vektor-vektor ini kemudian disimpan dalam sebuah indeks `FAISS` di direktori lokal (`vector_index/`). Jika indeks sudah ada, skrip akan memuatnya kembali untuk mempercepat proses.
4.  **Inisialisasi LLM & Memori**: Model `gemini-pro` dari Google AI diinisialisasi. Selain itu, koneksi ke Redis dibuat untuk mengelola memori percakapan melalui `RedisChatMessageHistory`.
5.  **Conversational Chain**: `ConversationalRetrievalChain` disiapkan. *Chain* ini bertugas:
    - Menerima pertanyaan dari pengguna.
    - Menggabungkan pertanyaan dengan riwayat percakapan dari Redis.
    - Mencari *chunk* transkrip yang paling relevan dari indeks FAISS.
    - Mengirimkan pertanyaan asli, riwayat obrolan, dan chunk yang relevan ke model Gemini Pro.
    - Menerima jawaban dari model dan menyimpannya kembali ke dalam riwayat di Redis.
6.  **Interaksi CLI**: Pengguna dapat berinteraksi dengan chatbot melalui antarmuka baris perintah (CLI).

---

## Prasyarat

- Python 3.8+
- Akses ke server Redis

## Instalasi

1.  **Kloning Repositori** (jika ada):
    ```bash
    git clone https://github.com/attmhd/rag-chatbot.git
    cd /rag-chatbot
    ```

2.  **Buat dan Aktifkan Lingkungan Virtual**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Di Windows, gunakan: venv\Scripts\activate
    ```

3.  **Instal Dependensi**:
    ```bash
    pip install -r requirements.txt
    ```

## Konfigurasi

1.  **Buat File `.env`**: Buat sebuah file bernama `.env` di dalam direktori `rag-chatbot`.

2.  **Tambahkan Kunci API & URL Redis**: Isi file `.env` dengan kredensial Anda. Ganti `<kunci-api-google-anda>` dengan kunci API Google Generative AI Anda.
    ```
    GOOGLE_API_KEY="<kunci-api-google-anda>"

    # (Opsional) Ganti jika Redis Anda berjalan di host atau port yang berbeda
    REDIS_URL="redis://localhost:6379/0"
    ```

3.  **Siapkan Transkrip**: Pastikan Anda memiliki file `transkrip.txt` di dalam direktori `rag-chatbot`.

## Menjalankan Chatbot

Setelah semua konfigurasi selesai, jalankan skrip chatbot:

```bash
python rag-chatbot/chatbot.py
```

Anda akan melihat pesan bahwa chatbot aktif dan siap menerima pertanyaan Anda melalui terminal.

```
📄 Memuat transkrip...
🧠 Memuat model embedding...
🔁 Memuat FAISS index yang sudah ada...
🧠 Menghubungkan ke Redis untuk chat memory (Session: user_session_01)...

💬 Chatbot Transkrip Video Aktif! (Ketik 'exit' untuk keluar)

🧑 Kamu: <ketik-pertanyaan-anda-di-sini>
```
