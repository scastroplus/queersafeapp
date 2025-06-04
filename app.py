# app.py

import streamlit as st
import google.generativeai as genai
import os # Embora não usemos para carregar a key localmente neste fluxo, é bom manter para referência futura.
import re
from datetime import datetime

# --- Configuração Inicial e Constantes ---
MODEL_ID = "gemini-1.5-flash-latest" 

# --- Funções do Notebook Adaptadas ---

def obter_relatorio_gemini_com_busca(destino, genero, api_key):
    """
    Usa um modelo Gemini com a ferramenta de busca para obter informações e gerar um relatório
    direto e conciso, com nuance baseada na pontuação e adaptado ao gênero do usuário,
    incluindo pontuação, justificativa e seções claras.
    """
    if not api_key: # Verifica se a api_key foi passada para a função
        return "ERRO: A chave da API Gemini não foi configurada. Verifique as configurações no Streamlit Cloud Secrets."

    try:
        genai.configure(api_key=api_key) 
        
        st.info(f"-> Usando Modelo '{MODEL_ID}' para analisar '{destino}' (Com Instrução de Gênero)...")

        model = genai.GenerativeModel(model_name=MODEL_ID)

        prompt_gender_instruction = f"""
        A pessoa que solicitou este relatório se identifica com o seguinte gênero: "{genero}".
        Ao gerar o conteúdo das seções do relatório (Justificativa da Nota, Resumo Geral da Situação, Alertas de Segurança, Dicas Locais LGBT+), **adapte a linguagem para se adequar a este gênero**:
        - Se o gênero fornecido for "homem", use pronomes e concordâncias gramaticais no masculino em português (ex: "o viajante", "seguro para ele", "bem recebido").
        - Se o gênero fornecido for "mulher", use pronomes e concordâncias gramaticais no feminino em português (ex: "a viajante", "segura para ela", "bem recebida").
        - **Para qualquer outro gênero** (incluindo "transgênero", "Não-binário", "Agênero", "Gênero fluido", ou se o termo fornecido for ambíguo, plural ou não listado), **utilize uma linguagem neutra em português**. Priorize frases e estruturas que evitem concordâncias de gênero explícitas sempre que possível (ex: "pessoa viajante", "seguro para essa pessoa", "bem recebide"). Se a linguagem neutra for difícil de manter em algumas frases, prefira o uso de termos mais gerais que não impliquem gênero. Evite pronomes específicos de gênero (ele/ela) e utilize alternativas neutras ou o nome da pessoa/gênero, se apropriado ao contexto.
        """

        prompt_text = f"""Você é um agente de IA especializado em segurança de viagens para pessoas LGBT+.
Sua tarefa é pesquisar na web (utilizando sua capacidade interna de acesso à informação, se aplicável, ou simulando com base no seu conhecimento atualizado)
informações sobre a situação atual (priorizando os **últimos 6-12 meses**) para pessoas LGBT+ em \"{destino}\".

Colete informações sobre os seguintes tópicos no destino \"{destino}\":
1. Leis e direitos LGBT+ RECENTES.
2. Nível de segurança para pessoas LGBT+, incluindo relatos RECENTES (últimos 6-12 meses) de violência, assédio ou discriminação.
3. Existência e atividades RECENTES (últimos 6-12 meses) de grupos extremistas (nazistas, neonazistas, fascistas, extrema direita, etc.) E se há relatos RECENTES (últimos 6-12 meses) de violência ou ameaças desses grupos contra minorias, incluindo a comunidade LGBT+.
4. Aceitação social e cultural RECENTE da comunidade LGBT+, incluindo atitudes gerais em relação a demonstrações públicas de afeto.
5. Informações sobre a comunidade LGBT+ local, espaços seguros (bares, clubes, ONGs, centros, eventos RECENTES).

Após coletar e analisar as informações encontradas (especialmente focando na RECÊNCIA), gere um relatório **DIRETO E CONCISO**.

**Crucialmente:** Ao descrever desafios ou problemas (como reações a demonstrações públicas de afeto), sempre **contextualize-os claramente dentro do panorama geral de segurança e aceitação no destino**.
- Se a **Pontuação de Segurança LGBT-Friendly** for alta (4.0 ou mais), minimize o foco em incidentes isolados ou desafios menores, enfatizando a segurança e aceitação geral. Mencione os desafios apenas como ressalvas menores dentro do contexto positivo.
- Se a pontuação for baixa, detalhe os riscos e desafios com mais ênfase, explicando por que a nota é baixa.

{prompt_gender_instruction}

O relatório DEVE conter as seguintes seções, usando os títulos exatos em negrito e duas estrelas `**`, e usando as informações coletadas:

**Pontuação de Segurança LGBT-Friendly:**
Avalie a segurança e o acolhimento em uma escala **numérica de 0.0 a 5.0**.
- 0.0: Extremamente perigoso, criminalizado com pena severa, alta hostilidade.
- 1.0: Muito arriscado, legalmente restritivo, forte discriminação.
- 2.0: Arriscado, poucas/nenhumas proteções, discriminação social presente.
- 3.0: Algumas preocupações, seguro com precauções; algumas proteções/aceitação.
- 4.0: Seguro e acolhedor na maior parte, boas proteções legais/aceitação.
- 5.0: Totalmente seguro, direitos plenos, sociedade acolhedora, cena vibrante.
**Escreva a pontuação numérica clara e destacada logo abaixo do título \"Pontuação de Segurança LGBT-Friendly:\", no formato: Pontuação: X.X/5.**

**Justificativa da Nota:**
Explique CLARAMENTE por que você deu essa pontuação, referenciando as informações encontradas (leis, segurança, grupos extremistas, aceitação, comunidade), **contextualizando desafios dentro da nota geral conforme instruído acima**. O impacto de leis que criminalizam atos LGBT+ (especialmente com pena severa) ou a presença de grupos extremistas com violência deve ser refletido na nota e justificado explicitamente.

**Resumo Geral da Situação:**
Um panorama CONCISO da situação legal, de segurança e social no destino, **mantendo a nuance e ponderação de acordo com a pontuação geral e adaptando a linguagem ao gênero do usuário**.

**Alertas de Segurança:**
Quaisquer cuidados específicos a serem tomados ou riscos a serem observados com base nas informações, listados de forma clara, **adaptando a linguagem ao gênero do usuário**.

**Dicas Locais LGBT+:**
Informações sobre bares, clubes, eventos, ONGs ou bairros conhecidos (se encontrados), listados de forma clara, **adaptando a linguagem ao gênero do usuário**.

Foque na clareza, precisão e na RECÊNCIA das informações ao gerar o relatório e a pontuação. Se a busca não retornar informações recentes relevantes para um tópico (especialmente sobre grupos extremistas e violência), mencione a falta de dados recentes para esse ponto.

Não use emojis de arco-íris no corpo principal do relatório gerado por você; apenas forneça a pontuação numérica, a justificativa clara e o conteúdo das seções no formato solicitado. A conversão para emojis será feita pelo meu código Python.
"""
        
        st.info("Enviando prompt para o modelo Gemini... Isso pode levar alguns instantes. ⏳")
        response = model.generate_content(prompt_text)

        if response and hasattr(response, 'text') and response.text:
            return response.text
        else:
            error_message = "Não foi possível gerar o relatório."
            if response and hasattr(response, 'candidates') and response.candidates:
                 if response.candidates[0].finish_reason:
                    error_message += f" Motivo da finalização: {response.candidates[0].finish_reason}."
                 if response.candidates[0].safety_ratings:
                    error_message += f" Classificações de segurança: {response.candidates[0].safety_ratings}." # Ajustado para pegar de candidates[0]
            elif response:
                 error_message += f" O modelo retornou uma resposta inesperada ou vazia para '{destino}'. Resposta: {response}"
            else:
                 error_message += " Resposta do modelo foi None."
            return error_message

    except Exception as e:
        st.error(f"ERRO CRÍTICO ao interagir com a API Gemini: {e}")
        return f"ERRO: Não foi possível gerar o relatório para '{destino}' devido a um problema na API Gemini: {e}"


def extrair_secao(texto, titulo_secao):
    """Extrai o texto de uma seção específica do relatório do modelo."""
    regex = rf'{re.escape(titulo_secao)}:?\s*(.*?)(?:(?=\n\*\*\w)|$)' # Regex da sua célula 5
    match = re.search(regex, texto, re.DOTALL | re.IGNORECASE) 
    if match:
        return match.group(1).strip()
    return ""


def exibir_relatorio_streamlit(texto_relatorio_do_modelo, destino):
    """Exibe o relatório formatado no Streamlit."""
    
    st.subheader(f"🔍 O que sabemos sobre {destino.capitalize()}")
    st.caption(f"Data da busca: {datetime.now().strftime('%Y-%m-%d')}")
    st.markdown("---")

    if not texto_relatorio_do_modelo or texto_relatorio_do_modelo.startswith("ERRO:"):
        st.error(f"Não foi possível exibir o relatório: {texto_relatorio_do_modelo}")
        return

    # --- Extração da Pontuação ---
    # Regex da sua célula 5 para pontuação
    pontuacao_str_match = re.search(r'Pontua(?:ção|cao)?:?\s*(\d(?:[.,]\d*)?)\s*/\s*5', texto_relatorio_do_modelo, re.IGNORECASE)
    pontuacao = None
    if pontuacao_str_match:
        try:
            pontuacao_val_str = pontuacao_str_match.group(1).replace(',', '.')
            pontuacao = float(pontuacao_val_str)
            pontuacao = max(0.0, min(pontuacao, 5.0)) 
        except ValueError:
            pontuacao = None
            st.warning("Não foi possível converter a pontuação para número.")
    else:
        st.warning("Formato da pontuação não encontrado na resposta do modelo. O modelo retornou:")
        st.code(texto_relatorio_do_modelo) # Mostra o que o modelo retornou para debug

    # --- Emojis da Pontuação (lógica da Célula 5) ---
    emojis = "🚫"  
    if pontuacao is not None:
        if pontuacao > 0.0:
            pontuacao_arredondada = round(pontuacao * 2) / 2.0
            num_arco_iris_completos = int(pontuacao_arredondada)
            tem_meio_emoji = abs(pontuacao_arredondada - num_arco_iris_completos - 0.5) < 1e-9
            emojis = "🌈" * num_arco_iris_completos
            if tem_meio_emoji:
                # Usei o caractere ½ que é mais simples, ou pode ser "½🌈"
                emojis += "½" 
        else: 
            emojis = "🚫"
    
    if pontuacao is not None:
        st.markdown(f"### **Pontuação LGBT+ Friendly: {pontuacao:.1f}/5 {emojis}**")
    else:
        st.markdown(f"### **Pontuação LGBT+ Friendly: Indisponível {emojis}**")
    st.markdown("---")

    # --- Extração e Exibição das Seções (títulos da Célula 5) ---
    # Ajustei os títulos na extração para corresponder EXATAMENTE ao que o prompt pede ao Gemini
    resumo_geral = extrair_secao(texto_relatorio_do_modelo, "**Resumo Geral da Situação:**")
    if resumo_geral:
        st.markdown("#### **Visão geral**") # Cabeçalho de exibição
        st.markdown(resumo_geral)
        st.markdown("---")
    else:
        st.markdown("*(Resumo geral não encontrado na resposta.)*")

    justificativa_nota = extrair_secao(texto_relatorio_do_modelo, "**Justificativa da Nota:**")
    if justificativa_nota:
        st.markdown("#### **Justificativa da nota**") # Cabeçalho de exibição
        st.markdown(justificativa_nota)
        st.markdown("---")
    else:
        st.markdown("*(Justificativa da nota não encontrada na resposta.)*")

    alertas_seguranca = extrair_secao(texto_relatorio_do_modelo, "**Alertas de Segurança:**")
    if alertas_seguranca:
        st.markdown("#### **Alertas de Segurança**") # Cabeçalho de exibição
        st.markdown(alertas_seguranca)
        st.markdown("---")
    else:
        st.markdown("*(Alertas de segurança não encontrados na resposta.)*")

    dicas_locais = extrair_secao(texto_relatorio_do_modelo, "**Dicas Locais LGBT+:**")
    if dicas_locais:
        st.markdown("#### **Dicas Locais LGBT+**") # Cabeçalho de exibição
        st.markdown(dicas_locais)
        st.markdown("---")
    else:
        st.markdown("*(Dicas locais LGBT+ não encontradas na resposta.)*")
    
    st.markdown("---")
    st.caption("DISCLAIMER: Este relatório foi gerado por um agente de IA utilizando um modelo Gemini e buscas na web com base em publicações dos últimos 6-12 meses. A precisão e completude dependem das informações encontradas pela ferramenta de busca e da capacidade do modelo em interpretá-las e sintetizá-las. A pontuação é baseada na interpretação do modelo e das informações encontradas. A situação em um destino pode mudar rapidamente. Sempre faça sua própria pesquisa adicional, consulte fontes oficiais de viagem e avalie os riscos com base nas suas circunstâncias pessoais antes de viajar.")


# --- Interface Principal do Aplicativo Streamlit ---
def main():
    st.set_page_config(page_title="Radar Queer Seguro", page_icon="🏳️‍🌈", layout="wide")
    
    # Carrega a API Key dos segredos do Streamlit
    # Esta é a maneira correta para apps no Streamlit Cloud
    google_api_key = st.secrets.get("GOOGLE_API_KEY")

    if not google_api_key:
        st.error("🔑 API Key do Google Gemini não configurada!")
        st.markdown("Para que o aplicativo funcione, a `GOOGLE_API_KEY` precisa ser configurada nos segredos do Streamlit Cloud. Vá em 'Settings' (ou 'Manage app' > '...' > 'Settings') > 'Secrets' e adicione sua chave.")
        st.markdown("Exemplo do formato no `Secrets`:")
        st.code("GOOGLE_API_KEY = \"SUA_CHAVE_AQUI\"")
        return # Interrompe a execução se não houver chave configurada nos Secrets

    # Interface do usuário (da Célula 6)
    st.title("SEJA BEM VIADE! 🏳️‍🌈") # Mantendo sua saudação personalizada
    st.header("Este é o RADAR QUEER SEGURO")
    st.subheader("Sua ferramenta de busca em IA e Google para encontrar locais seguros para viajar")
    st.markdown("---")

    genero = st.text_input("🗣️ Com qual gênero você se identifica?")
    destino = st.text_input("🌍 Digite qual cidade, estado ou país você quer conhecer:")

    if st.button("🔎 Gerar Relatório de Segurança"):
        if genero and destino:
            with st.spinner(f"Analisando {destino}... Por favor, aguarde. Isso pode levar um momento..."):
                # Passa a google_api_key para a função
                relatorio = obter_relatorio_gemini_com_busca(destino, genero, google_api_key) 
            
            if relatorio:
                exibir_relatorio_streamlit(relatorio, destino)
            else:
                st.error("Ocorreu um erro e não foi possível obter o relatório.")
        else:
            st.warning("Por favor, preencha seu gênero e o destino desejado.")

if __name__ == "__main__":
    main()