# app.py - RADAR QUEER SEGURO - Versão para Streamlit

import streamlit as st
# Imports necessários para a API Gemini e para o Streamlit
from google import genai
from google.genai import types 
import os 
import re
from datetime import datetime
import math # Para o arredondamento da pontuação

# --- Configuração Inicial e Constantes ---
# ID do Modelo (Usamos o que você definiu no Colab)
MODEL_ID = "gemini-2.5-flash" 

# CONFIGURAÇÃO DE BUSCA: Define a ferramenta de busca (Google Search)
SEARCH_TOOL = [
    types.Tool(
        google_search=types.GoogleSearch()
    )
]

# --- Funções do Aplicativo ---

def obter_relatorio_gemini_com_busca(destino, genero, api_key):
    """
    Usa um modelo Gemini com a ferramenta de busca para obter informações e gerar um relatório
    direto e conciso. (Com correção de sintaxe)
    """
    if not api_key: 
        return "ERRO: A chave da API Gemini não foi configurada. Verifique as configurações no Streamlit Cloud Secrets."

    # A partir daqui, toda a lógica está dentro do bloco try-except 
    try:
        # Configura o cliente da API
        client = genai.Client()

        # O PROMPT GIGANTE DO SEU CÓDIGO (mantido para garantir a lógica)
        prompt_gender_instruction = f"""
        A pessoa que solicitou este relatório se identifica com o seguinte gênero: "{genero}".
        Ao gerar o conteúdo das seções do relatório (Justificativa da Nota, Resumo Geral da Situação, Alertas de Segurança, Dicas Locais LGBT+), **adapte a linguagem para se adequar a este gênero**:
        - Se o gênero fornecido for "homem", use pronomes e concordâncias gramaticais no masculino em português (ex: "o viajante", "seguro para ele", "bem recebido").
        - Se o gênero fornecido for "mulher", use pronomes e concordâncias gramaticais no feminino em português (ex: "a viajante", "segura para ela", "bem recebida").
        - **Para qualquer outro gênero** (incluindo "transgênero", "Não-binário", "Agênero", "Gênero fluido", ou se o termo fornecido for ambíguo, plural ou não listado), **utilize uma linguagem neutra em português**. Priorize frases e estruturas que evitem concordâncias de gênero explícitas sempre que possível (ex: "pessoa viajante", "seguro para essa pessoa", "bem recebide"). Se a linguagem neutra for difícil de manter em algumas frases, prefira o uso
