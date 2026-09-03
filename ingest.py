"""
ingest.py
=========
سكربت بناء فهرس FAISS المحلي من مستندات الجامعة الخام.

يُنتج بالضبط الصيغة التي يتوقعها src/tools/rag_tool.py:
  - data/processed/faiss_index/index.faiss          (فهرس FAISS خام)
  - data/processed/faiss_index/index_metadata.json   (قائمة قواميس
    بالشكل: [{"text": "...", "source": "...", "chunk_id": ...}, ...])

يقرأ الملفات من:
  - data/raw/pdf/*.pdf
  - data/raw/docx/*.docx
  - data/raw/docx/*.pdf   (بعض ملفات PDF وُجدت داخل مجلد docx أيضًا،
    السكربت يبحث عن *.pdf و *.docx في كلا المجلدين بلا تمييز).

نموذج التضمين مطابق تمامًا لما هو مُستخدم في rag_tool.py:
  BAAI/bge-small-en-v1.5  مع normalize_embeddings=True
  → لذلك استخدمنا faiss.IndexFlatL2 (متوافق مع L2 distance المستخدمة
    في similarity_search_with_score() ومع عتبة score_threshold=0.65
    في retrieval_agent.py — كلما كانت القيمة أصغر كانت الصلة أقوى).

تشغيل:
    python ingest.py
"""

import os
import json
import glob
import faiss
import numpy as np

from langchain_huggingface import HuggingFaceEmbeddings

# ==========================================
# الإعدادات — مطابقة لِـ rag_tool.py
# ==========================================
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
RAW_DIRS = ["data/raw/pdf", "data/raw/docx", "data/raw"]
OUTPUT_DIR = "data/processed/faiss_index"
CHUNK_SIZE = 800      # عدد الأحرف تقريبًا لكل مقطع (chunk)
CHUNK_OVERLAP = 150   # تداخل بين المقاطع لتفادي فقدان السياق عند الحدود


# ==========================================
# استخراج النص
# ==========================================
def extract_text_from_pdf(path: str) -> str:
    from pypdf import PdfReader
    reader = PdfReader(path)
    pages_text = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages_text.append(text)
    return "\n".join(pages_text)


def extract_text_from_docx(path: str) -> str:
    import docx
    doc = docx.Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def collect_source_files() -> list:
    """يجمع كل ملفات pdf/docx من مجلدات data/raw بلا تكرار."""
    found = set()
    for d in RAW_DIRS:
        if not os.path.isdir(d):
            continue
        for ext in ("*.pdf", "*.docx"):
            for f in glob.glob(os.path.join(d, ext)):
                found.add(os.path.abspath(f))
    return sorted(found)


# ==========================================
# التقسيم إلى مقاطع (Chunking)
# ==========================================
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:
    text = " ".join(text.split())  # توحيد المسافات
    if not text:
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == text_len:
            break
        start = end - overlap  # تراجع للتداخل

    return chunks


# ==========================================
# البناء الرئيسي
# ==========================================
def main():
    source_files = collect_source_files()

    if not source_files:
        print("[ERROR] لا توجد ملفات PDF أو DOCX في data/raw/. تأكد من المسار.")
        return

    print(f"[1/4] تم العثور على {len(source_files)} ملف مصدر:")
    for f in source_files:
        print(f"   - {f}")

    all_chunks = []   # نصوص المقاطع فقط (للتضمين)
    all_metadata = []  # القواميس الكاملة (تُحفظ في index_metadata.json)

    print("\n[2/4] استخراج النصوص وتقسيمها إلى مقاطع...")
    for filepath in source_files:
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filepath)[1].lower()

        try:
            if ext == ".pdf":
                raw_text = extract_text_from_pdf(filepath)
            elif ext == ".docx":
                raw_text = extract_text_from_docx(filepath)
            else:
                continue
        except Exception as e:
            print(f"   [WARN] فشل استخراج النص من {filename}: {e}")
            continue

        chunks = chunk_text(raw_text)
        print(f"   - {filename}: {len(chunks)} مقطع")

        for idx, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadata.append({
                "text": chunk,
                "source": filename,
                "chunk_id": idx,
            })

    if not all_chunks:
        print("[ERROR] لم يُستخرج أي نص قابل للاستخدام من الملفات. تأكد أن الملفات ليست ممسوحة ضوئيًا (صور) بدون OCR.")
        return

    print(f"\n[3/4] توليد التضمينات (Embeddings) باستخدام {EMBEDDING_MODEL_NAME} ...")
    embeddings_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vectors = embeddings_model.embed_documents(all_chunks)
    vectors_np = np.array(vectors, dtype="float32")
    dimension = vectors_np.shape[1]
    print(f"   - عدد المتجهات: {vectors_np.shape[0]} | البعد: {dimension}")

    print("\n[4/4] بناء فهرس FAISS وحفظه...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    index = faiss.IndexFlatL2(dimension)
    index.add(vectors_np)

    faiss_path = os.path.join(OUTPUT_DIR, "index.faiss")
    metadata_path = os.path.join(OUTPUT_DIR, "index_metadata.json")

    faiss.write_index(index, faiss_path)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(all_metadata, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCESS] تم حفظ الفهرس في:")
    print(f"   - {faiss_path}  ({index.ntotal} متجه)")
    print(f"   - {metadata_path}  ({len(all_metadata)} سجل)")
    print("\nيمكنك الآن تشغيل: streamlit run app.py")


if __name__ == "__main__":
    main()
