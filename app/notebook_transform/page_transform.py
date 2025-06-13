import streamlit as st
from .upload_component import notebook_upload_component
from .prompts import PROMPT_ANALISE, PROMPT_TRANSFORMACAO, PROMPT_EXPLICACAO
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from llms import create_llm

def run_notebook_transform_page():
    st.title("Transformação de Notebooks Databricks com BlipForge")
    st.markdown("""
    Faça upload de um notebook Databricks legado (.py ou .ipynb) ou cole o conteúdo abaixo. O sistema irá analisar, transformar e explicar as mudanças usando as regras do BlipForge.
    """)
    notebook_text = notebook_upload_component()
    if not notebook_text.strip():
        st.info("Faça upload ou cole o notebook para começar.")
        return
    llm = create_llm("Blip: gpt-4o-mini", temperature=0.1)
    if st.button("Analisar e Transformar"):
        with st.spinner("Analisando notebook..."):
            analise = llm(PROMPT_ANALISE.format(notebook=notebook_text))
        st.subheader("Análise do Notebook Legado")
        st.write(analise)
        with st.spinner("Transformando notebook..."):
            notebook_novo = llm(PROMPT_TRANSFORMACAO.format(notebook=notebook_text))
        st.subheader("Notebook Transformado (BlipForge)")
        st.code(notebook_novo, language="python")
        with st.spinner("Explicando mudanças..."):
            explicacao = llm(PROMPT_EXPLICACAO.format(notebook=notebook_text, notebook_novo=notebook_novo))
        st.subheader("Principais Mudanças e Otimizações")
        st.write(explicacao)
