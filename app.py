from flask import Flask, request, render_template
import requests
import json
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Obter variáveis de ambiente
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
YOUR_SITE_URL = os.getenv("YOUR_SITE_URL")
YOUR_SITE_NAME = os.getenv("YOUR_SITE_NAME")

# Lista de AIs disponíveis
AIS = {
    "DeepSeek": "deepseek/deepseek-r1-zero:free",
    "DeepSeek Chat": "deepseek/deepseek-chat:free",  # Nova AI
    "Google Gemma": "google/gemma-3-1b-it:free",
}

# Histórico de chats
chat_history = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Obter a pergunta, a AI selecionada e a URL da imagem (se houver) do formulário
        user_input = request.form.get("question")
        image_url = request.form.get("image_url")
        selected_ai = request.form.get("ai")

        # Verificar se a AI selecionada existe
        if selected_ai not in AIS:
            return f"Erro: AI '{selected_ai}' não encontrada.", 400

        # Obter o modelo da AI selecionada
        model = AIS[selected_ai]

        # Preparar a mensagem para a API
        messages = [{"role": "user", "content": []}]

        # Adicionar texto à mensagem, se fornecido
        if user_input:
            messages[0]["content"].append({"type": "text", "text": user_input})

        # Adicionar imagem à mensagem, se a URL for fornecida
        if image_url:
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })

        # Fazer a requisição para a API do OpenRouter
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": YOUR_SITE_URL,
                "X-Title": YOUR_SITE_NAME,
            },
            data=json.dumps({
                "model": model,
                "messages": messages,
            })
        )

        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            result = response.json()
            # Verificar se a resposta contém o campo "choices"
            if "choices" in result and len(result["choices"]) > 0:
                answer = result["choices"][0]["message"]["content"]
            else:
                answer = "Erro: Resposta da API não contém dados válidos."
        else:
            answer = f"Erro: {response.status_code} - {response.text}"

        # Adicionar a pergunta, URL da imagem (se houver) e resposta ao histórico
        chat_history.append({
            "ai": selected_ai,
            "question": user_input,
            "image_url": image_url,
            "answer": answer,
        })

    # Renderizar o template com o histórico de conversas e a lista de AIs
    return render_template("index.html", chat_history=chat_history, ais=AIS.keys())

if __name__ == "__main__":
    app.run(debug=True)