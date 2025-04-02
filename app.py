from flask import Flask, request, render_template
import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime  # Importação adicionada

load_dotenv()

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
YOUR_SITE_URL = os.getenv("YOUR_SITE_URL")
YOUR_SITE_NAME = os.getenv("YOUR_SITE_NAME")

AIS = {
    "DeepSeek-R1": "deepseek/deepseek-r1:free",
    "DeepSeek Chat": "deepseek/deepseek-chat:free",
    "Google Gemma": "google/gemma-3-1b-it:free",
}

chat_history = []

# Filtro para formatar datas
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y %H:%M'):
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.strftime(format)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form.get("question")
        image_url = request.form.get("image_url")
        selected_ai = request.form.get("ai")

        if selected_ai not in AIS:
            return f"Erro: AI '{selected_ai}' não encontrada.", 400

        model = AIS[selected_ai]
        messages = [{"role": "user", "content": []}]

        if user_input:
            messages[0]["content"].append({"type": "text", "text": user_input})

        if image_url:
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })

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

        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"] if "choices" in result else "Erro: Resposta inválida"
        else:
            answer = f"Erro: {response.status_code} - {response.text}"

        chat_history.append({
            "ai": selected_ai,
            "question": user_input,
            "image_url": image_url,
            "answer": answer,
            "timestamp": datetime.now().isoformat()  # Agora funciona
        })

    return render_template("index.html", 
                         chat_history=list(reversed(chat_history)),
                         ais=AIS.keys())

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)