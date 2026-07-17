import streamlit as st
from utils import (
    merge_documents, extract_pdf_pages, run_ocr,
    translate_text, text_to_speech, text_to_pdf, text_to_docx
)
from pypdf import PdfReader

st.set_page_config(page_title="AI Document Studio", layout="wide", page_icon="📄")

# Initialize shared across-module session variables
for key in ["merged", "extracted", "ocr_raw", "translated", "audio"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "ocr_raw" and key != "translated" else ""

LANG_MAP = {
    "English": "en", "Hindi": "hi", "Kannada": "kn", "Tamil": "ta", "Telugu": "te",
    "Malayalam": "ml", "Marathi": "mr", "Gujarati": "gu", "Bengali": "bn",
    "French": "fr", "German": "de", "Spanish": "es", "Japanese": "ja", "Arabic": "ar"
}

st.sidebar.title("Studio Workspace")
module = st.sidebar.radio("Navigate Modules:", [
    "1 & 2: Upload & Merge", "3: Page Extractor", "4: OCR Engine", "5: AI Translator", "6: Speech Studio", "7: Export Hub"
])

# MODULE 1 & 2: UPLOAD & MERGE
if module == "1 & 2: Upload & Merge":
    st.header("Upload & Merge Documents")
    uploaded_files = st.file_uploader("Drop assets here:", accept_multiple_files=True, type=["pdf","docx","jpg","jpeg","png","bmp","tiff"])
    if uploaded_files:
        ordered_files = []
        for i, f in enumerate(uploaded_files):
            col1, col2 = st.columns(2)
            col1.write(f.name)
            pos = col2.number_input(f"Order Index for {f.name[:15]}...", min_value=1, max_value=len(uploaded_files), value=i+1, key=f"ord_{i}")
            ordered_files.append((pos, f))
        ordered_files.sort(key=lambda x: x[0])
        final_list = [item[1] for item in ordered_files]
        
        add_cover = st.checkbox("Attach cover page?")
        if st.button("Merge Documents"):
            st.session_state.merged = merge_documents(final_list, add_cover)
            st.success("Documents successfully merged!")

# MODULE 3: PAGE EXTRACTOR
elif module == "3: Page Extractor":
    st.header("Extract PDF Pages")
    pdf_file = st.file_uploader("Upload Target PDF:", type=["pdf"])
    if pdf_file:
        reader = PdfReader(pdf_file)
        total = len(reader.pages)
        st.write(f"Total pages detected: {total}")
        page_input = st.text_input("Enter comma-separated pages to extract (e.g., 1,3,5):", value="1")
        if st.button("Extract Pages"):
            pages = [int(p.strip()) for p in page_input.split(",") if p.strip().isdigit() and 0 < int(p.strip()) <= total]
            if pages:
                pdf_file.seek(0)
                st.session_state.extracted = extract_pdf_pages(pdf_file.read(), pages)
                st.success(f"Extracted {len(pages)} pages successfully!")

# MODULE 4: OCR ENGINE
elif module == "4: OCR Engine":
    st.header("OCR Text Extraction")
    ocr_file = st.file_uploader("Upload Image or PDF:", type=["pdf","png","jpg","jpeg","bmp","tiff"])
    if ocr_file and st.button("Extract Text"):
        st.session_state.ocr_raw = run_ocr(ocr_file)
    if st.session_state.ocr_raw:
        st.text_area("Extracted Plain Text Output:", value=st.session_state.ocr_raw, height=300)

# MODULE 5: AI TRANSLATOR
elif module == "5: AI Translator":
    st.header("AI Multi-Language Translator")
    text_input = st.text_area("Source Text to Translate:", value=st.session_state.ocr_raw, height=200)
    target_lang = st.selectbox("Select Target Language:", list(LANG_MAP.keys()))
    if st.button("Translate Now"):
        st.session_state.translated = translate_text(text_input, LANG_MAP[target_lang])
    if st.session_state.translated:
        st.text_area("Translated Output:", value=st.session_state.translated, height=200)

# MODULE 6: SPEECH STUDIO
elif module == "6: Speech Studio":
    st.header("Text to Speech Synthesizer")
    speech_text = st.text_area("Input Text for Audio Generation:", value=st.session_state.translated if st.session_state.translated else st.session_state.ocr_raw, height=200)
    speech_lang = st.selectbox("Select Speech Language Track:", list(LANG_MAP.keys()))
    if st.button("Generate Audio Engine"):
        st.session_state.audio = text_to_speech(speech_text, LANG_MAP[speech_lang])
    if st.session_state.audio:
        st.audio(st.session_state.audio, format="audio/mp3")

# MODULE 7: EXPORT HUB
elif module == "7: Export Hub":
    st.header("Centralized Export Hub")
    c1, c2 = st.columns(2)
    with c1:
        if st.session_state.merged:
            st.download_button("Download Merged Document Master (PDF)", st.session_state.merged, "merged_master.pdf", "application/pdf")
        if st.session_state.extracted:
            st.download_button("Download Extracted Segment (PDF)", st.session_state.extracted, "extracted_pages.pdf", "application/pdf")
    with c2:
        if st.session_state.ocr_raw:
            st.download_button("Download Raw OCR Data (TXT)", st.session_state.ocr_raw, "ocr_data.txt", "text/plain")
            st.download_button("Download Raw OCR Data (DOCX)", text_to_docx(st.session_state.ocr_raw), "ocr_data.docx", "application/vnd.openxmlformats")
        if st.session_state.translated:
            st.download_button("Download Translation Document (PDF)", text_to_pdf(st.session_state.translated), "translated_output.pdf", "application/pdf")
        if st.session_state.audio:
            st.download_button("Download Audio Presentation (MP3)", st.session_state.audio, "synthesized_voice.mp3", "audio/mp3")
