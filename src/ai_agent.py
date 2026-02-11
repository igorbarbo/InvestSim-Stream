from google import genai
from google.genai import types
import streamlit as st

def ask_ai(question, df):
    api_key = st.secrets["GEMINI_API_KEY"]
    
    # Novo cliente da SDK google-genai (Padrão 2026)
    client = genai.Client(api_key=api_key)
    
    # Preparando o contexto da sua carteira para a IA
    contexto_carteira = df[['Ativo', 'QTD', 'Preço Atual', 'Patrimônio', 'Valorização %', 'Prioridade']].to_string()
    
    prompt_config = (
        f"Você é o Guru Financeiro do Igor. Analise os dados da carteira dele abaixo e responda de forma objetiva.\n\n"
        f"DADOS DA CARTEIRA:\n{contexto_carteira}\n\n"
        f"PERGUNTA DO IGOR: {question}"
    )

    try:
        # Nova forma de gerar conteúdo com Grounding (Busca no Google)
        response = client.models.generate_content(
            model="gemini-2.0-flash", # Usando o modelo mais atual
            contents=prompt_config,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())], # Novo padrão de busca
                system_instruction="Seja direto, use um tom profissional e foque em gestão de risco."
            )
        )
        return response.text
    except Exception as e:
        return f"🚨 Erro na Migração V5: {str(e)}"
        
