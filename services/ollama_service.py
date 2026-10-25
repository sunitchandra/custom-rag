import ollama
from config.settings import OLLAMA_HOST, DEFAULT_CHAT_MODEL, DEFAULT_EMBEDDING_MODEL

def get_client():
    return ollama.Client(host=OLLAMA_HOST)

def list_models():
    client = get_client()
    result = client.list()
    models = result.get("models", []) if isinstance(result, dict) else getattr(result, "models", [])
    names = []
    for model in models:
        name = model.get("name") if isinstance(model, dict) else getattr(model, "model", None)
        if name:
            names.append(name)
    return names

def embed_texts(texts, model=None):
    client = get_client()
    response = client.embed(model=model or DEFAULT_EMBEDDING_MODEL, input=texts)
    return response["embeddings"] if isinstance(response, dict) else response.embeddings

def answer_chat(messages, model=None, temperature=0.1):
    client = get_client()
    response = client.chat(
        model=model or DEFAULT_CHAT_MODEL,
        messages=messages,
        options={"temperature": float(temperature)},
        stream=False,
    )
    return response["message"]["content"] if isinstance(response, dict) else response.message.content
