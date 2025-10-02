import os
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

# Carrega variáveis de ambiente
load_dotenv()
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) 

app = Flask(__name__)

def process_email_with_ai(email_text):
    """
    Função principal que interage com a API da OpenAI.
    Utiliza um prompt estruturado para classificação e geração de resposta.
    """
    
    # 1. Definição do Prompt (Ações)
    # Define as categorias e o formato de saída esperado.
    system_prompt = (
        "Você é um classificador de e-mails de uma grande empresa financeira e um gerador de respostas automáticas. "
        "Seu objetivo é classificar o e-mail em uma das categorias: 'Produtivo' ou 'Improdutivo'.\n\n"
        "- **Produtivo**: Requer ação ou resposta específica (suporte técnico, status, dúvida).\n"
        "- **Improdutivo**: Não requer ação imediata (felicitações, agradecimentos, mensagens não relevantes).\n\n"
        "Após a classificação, gere uma resposta automática adequada ao tom do e-mail. Para e-mails Produtivos, a resposta deve ser formal e indicar o próximo passo. Para e-mails Improdutivos, a resposta deve ser breve e de agradecimento."
    )

    # 2. Definição do Formato de Saída (JSON)
    # Garante que a saída seja um JSON estruturado para fácil processamento.
    response_schema = {
        "type": "object",
        "properties": {
            "classificacao": {
                "type": "string",
                "enum": ["Produtivo", "Improdutivo"],
                "description": "A categoria do email: Produtivo ou Improdutivo."
            },
            "resposta_sugerida": {
                "type": "string",
                "description": "A resposta automática e completa, adequada ao tom e classificação do email."
            }
        },
        "required": ["classificacao", "resposta_sugerida"]
    }

    try:
        # 3. Chamada da API
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Modelo rápido e ideal para classificação e JSON
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"E-mail a classificar:\n\n---\n{email_text}\n---"}
            ],
            response_model=response_schema, # Força o output em JSON
        )
        
        # A API retorna um objeto que se ajusta ao schema
        return response.model_dump()
        
    except Exception as e:
        print(f"Erro na comunicação com a API OpenAI: {e}")
        return {"error": "Falha ao processar o e-mail pela IA.", "details": str(e)}

# -------------------------- ROTAS DO FLASK --------------------------

@app.route('/', methods=['GET'])
def index():
    """Rota para exibir o formulário inicial."""
    return render_template('index.html')

@app.route('/processar_email', methods=['POST'])
def processar_email():
    """Rota para receber o email e retornar a classificação/resposta."""
    
    email_text = request.form.get('email_content')
    
    if not email_text:
        return jsonify({"error": "O campo de texto do e-mail é obrigatório."}), 400

    # Processa o email
    ai_result = process_email_with_ai(email_text)

    if "error" in ai_result:
        return jsonify(ai_result), 500

    # Retorna o resultado da IA
    return jsonify(ai_result)

if __name__ == '__main__':
    # Rodar com thread single para ser compativel com alguns hosts gratuitos
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))