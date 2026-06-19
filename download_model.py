"""
download_model.py
Downloads the TinyLlama GGUF model from HuggingFace at startup if it's not
already present. Called once before the Flask/Gunicorn workers spin up.
"""
import os
import sys

MODEL_REPO = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
MODEL_FILENAME = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MODEL_DIR = os.getenv("MODEL_DIR", "models")
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)


def download_if_missing():
    if os.path.exists(MODEL_PATH):
        print(f"[model] Found existing model at {MODEL_PATH} — skipping download.")
        return

    print(f"[model] Model not found. Downloading {MODEL_FILENAME} from HuggingFace...")
    print(f"[model] Destination: {MODEL_PATH}  (~700 MB, please wait...)")

    os.makedirs(MODEL_DIR, exist_ok=True)

    try:
        from huggingface_hub import hf_hub_download
        downloaded_path = hf_hub_download(
            repo_id=MODEL_REPO,
            filename=MODEL_FILENAME,
            local_dir=MODEL_DIR,
            local_dir_use_symlinks=False,
        )
        print(f"[model] Download complete: {downloaded_path}")
    except Exception as e:
        print(f"[model] ERROR: Failed to download model — {e}", file=sys.stderr)
        print("[model] The app will start, but AI responses will be unavailable.", file=sys.stderr)


if __name__ == "__main__":
    download_if_missing()
