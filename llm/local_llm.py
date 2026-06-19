from llama_cpp import Llama
import os

class LocalLLM:
    def __init__(self):
        model_path = os.getenv("MODEL_PATH", "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
        if not os.path.exists(model_path):
            self.llm = None
        else:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=4096,
                n_threads=4,
                n_gpu_layers=0,
                verbose=False
            )
            
        self.system_prompt = """You are BUZZ AI, a helpful document assistant. Rules:
1. Answer ONLY what the user asked. Be direct and concise.
2. Use ONLY the document context provided to answer.
3. Never mention chunks, vectors, or internal processing.
4. Precise mode: give a short direct answer, 1-4 sentences.
5. Summary mode: give clean bullet points of key information.
6. If answer not in documents: say exactly 'I could not find that in your documents.'
7. Write naturally like a helpful human assistant."""

    def answer(self, query: str, chunks: list[str], mode: str = "precise"):
        if not self.llm:
            yield "Error: Local model not found. Please download TinyLlama into the models/ folder."
            return
            
        context = "\n\n".join(chunks[:5])
        prompt = f"""<|system|>
{self.system_prompt}</s>
<|user|>
Document content:
{context}

Question: {query}
Mode: {mode}</s>
<|assistant|>"""

        try:
            response = self.llm(
                prompt,
                max_tokens=512,
                temperature=0.2,
                top_p=0.95,
                repeat_penalty=1.1,
                stream=True,
                stop=["</s>", "<|user|>", "<|system|>"]
            )
            for token in response:
                text = token["choices"][0]["text"]
                if text:
                    yield text
        except Exception as e:
            yield f"Error generating response: {e}"

    def generate_qa(self, chunks: list[str]):
        if not self.llm:
            yield "Error: Local model not found. Please download TinyLlama into the models/ folder."
            return
            
        # Limit to first 10 chunks to avoid massive processing times on the CPU
        context = "\n\n".join(chunks[:10])
        prompt = f"""<|system|>
You are a helpful teacher. Based strictly on the provided document content, generate a list of 5-10 important questions and their detailed answers.
Format your output exactly like this for each pair:
Q: [Question]
A: [Answer]
</s>
<|user|>
Document content:
{context}

Please generate the questions and answers.</s>
<|assistant|>"""

        try:
            response = self.llm(
                prompt,
                max_tokens=1024,
                temperature=0.3,
                top_p=0.95,
                repeat_penalty=1.1,
                stream=True,
                stop=["</s>", "<|user|>", "<|system|>"]
            )
            for token in response:
                text = token["choices"][0]["text"]
                if text:
                    yield text
        except Exception as e:
            yield f"Error generating Q&A: {e}"

    def is_ready(self) -> bool:
        model_path = os.getenv("MODEL_PATH", "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
        return os.path.exists(model_path)
