import os
import uuid
import json
import time
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import core modules
from core.file_processor import FileProcessor
from core.chunker import TextChunker
from core.embedder import Embedder
from core.vector_store import VectorStore
from llm.local_llm import LocalLLM
from llm.local_image_analyzer import LocalImageAnalyzer

app = Flask(__name__)
CORS(app)

# Global session dictionary
SESSIONS = {}

def get_session(session_id):
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "vector_store": VectorStore(),
            "files": [],
            "images": [],
            "embedder": Embedder(),
            "llm": LocalLLM(),
            "image_analyzer": LocalImageAnalyzer(),
            "last_active": time.time()
        }
    else:
        SESSIONS[session_id]["last_active"] = time.time()
    return SESSIONS[session_id]

# Clean up stale sessions (e.g., > 2 hours)
def cleanup_sessions():
    now = time.time()
    stale_keys = [k for k, v in SESSIONS.items() if now - v["last_active"] > 7200]
    for k in stale_keys:
        del SESSIONS[k]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/status", methods=["GET"])
def status():
    llm = LocalLLM()
    img_analyzer = LocalImageAnalyzer()
    return jsonify({
        "model_ready": llm.is_ready(),
        "model_name": "TinyLlama 1.1B (Local)",
        "ocr_ready": img_analyzer.is_ready(),
        "mode": "100% Offline - No API needed"
    })

@app.route("/upload", methods=["POST"])
def upload():
    cleanup_sessions()
    session_id = request.form.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        
    session_data = get_session(session_id)
    
    if "files[]" not in request.files:
        return jsonify({"success": False, "error": "No files provided"}), 400
        
    files = request.files.getlist("files[]")
    
    processor = FileProcessor()
    chunker = TextChunker()
    
    processed_files_info = []
    total_new_chunks = 0
    
    for file in files:
        filename = file.filename
        # Check if already processed
        if any(f["name"] == filename for f in session_data["files"]):
            continue
            
        try:
            text, images = processor.process(file)
            
            chunks = []
            if text:
                chunks = chunker.chunk(text)
                
            # Process images locally via OCR
            for i, img_dict in enumerate(images):
                b64 = img_dict.get("base64")
                if not b64:
                    continue
                
                desc = session_data["image_analyzer"].analyze(b64)
                combined_text = f"[Visual Content from {filename}]\n{desc}"
                chunks.append(combined_text)
                    
                session_data["images"].append(img_dict)

            # Embed and add to vector store
            if chunks:
                embeddings = session_data["embedder"].embed(chunks)
                session_data["vector_store"].add(chunks, embeddings)
                
            session_data["files"].append({
                "name": filename,
                "images": len(images),
                "chunks": len(chunks)
            })
            
            processed_files_info.append({
                "name": filename,
                "images": len(images),
                "status": "ready"
            })
            total_new_chunks += len(chunks)
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
    return jsonify({
        "success": True,
        "session_id": session_id,
        "files": processed_files_info,
        "total_chunks": total_new_chunks
    })

def handle_query_logic(session_id, query):
    session_data = get_session(session_id)
    vector_store = session_data["vector_store"]
    embedder = session_data["embedder"]
    
    relevant_chunks = []
    
    if not vector_store.is_empty():
        query_emb = embedder.embed_query(query)
        chunks, scores = vector_store.search(query_emb, top_k=5)
        for chunk, score in zip(chunks, scores):
            if score > 0.3:
                relevant_chunks.append(chunk)
                
    return relevant_chunks

@app.route("/chat", methods=["POST"])
def chat():
    cleanup_sessions()
    data = request.json
    query = data.get("message", "")
    session_id = data.get("session_id")
    mode = data.get("mode", "precise")
    
    if not session_id or not query:
        return jsonify({"error": "Missing session_id or message"}), 400
        
    relevant_chunks = handle_query_logic(session_id, query)
    
    session_data = get_session(session_id)
    llm = session_data["llm"]
    
    response_gen = llm.answer(query, relevant_chunks, mode)
    full_response = "".join(list(response_gen))
    
    return jsonify({
        "reply": full_response,
        "source": "document",
        "streaming": False
    })

@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    cleanup_sessions()
    data = request.json
    query = data.get("message", "")
    session_id = data.get("session_id")
    mode = data.get("mode", "precise")
    
    if not session_id or not query:
        return jsonify({"error": "Missing session_id or message"}), 400
        
    relevant_chunks = handle_query_logic(session_id, query)
    
    def generate():
        session_data = get_session(session_id)
        llm = session_data["llm"]
        for token in llm.answer(query, relevant_chunks, mode):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield f"data: {json.dumps({'done': True, 'source': 'document'})}\n\n"
        
    return Response(generate(), mimetype="text/event-stream")

@app.route("/generate-qa", methods=["POST"])
def generate_qa():
    cleanup_sessions()
    data = request.json
    session_id = data.get("session_id")
    
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400
        
    session_data = get_session(session_id)
    vector_store = session_data["vector_store"]
    
    # Get all chunks from the vector store
    # vector_store.chunks is the list of all uploaded text chunks
    all_chunks = vector_store.chunks
    
    if not all_chunks:
        return jsonify({"error": "No documents found to generate questions from"}), 400

    def generate():
        llm = session_data["llm"]
        for token in llm.generate_qa(all_chunks):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield f"data: {json.dumps({'done': True, 'source': 'auto-qa'})}\n\n"
        
    return Response(generate(), mimetype="text/event-stream")

@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    cleanup_sessions()
    data = request.json
    session_id = data.get("session_id")
    image_index = data.get("image_index", 0)
    
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400
        
    session_data = get_session(session_id)
    images = session_data.get("images", [])
    
    if image_index < 0 or image_index >= len(images):
        return jsonify({"error": "Invalid image index"}), 400
        
    b64 = images[image_index].get("base64")
    if not b64:
        return jsonify({"error": "Image data missing"}), 500
        
    img_analyzer = session_data["image_analyzer"]
    analysis = img_analyzer.analyze(b64)
    
    return jsonify({"analysis": analysis})

@app.route("/clear", methods=["DELETE"])
def clear():
    session_id = request.args.get("session_id")
    if session_id and session_id in SESSIONS:
        del SESSIONS[session_id]
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
