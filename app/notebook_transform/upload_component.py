import streamlit as st

def notebook_upload_component():
    st.markdown("## Upload do Notebook Legado")
    uploaded_file = st.file_uploader("Faça upload do notebook Databricks (.py ou .ipynb)", type=["py", "ipynb"])
    notebook_text = ""
    if uploaded_file is not None:
        notebook_text = uploaded_file.read().decode("utf-8")
        st.text_area("Conteúdo do notebook carregado:", value=notebook_text, height=300)
    else:
        notebook_text = st.text_area("Ou cole o conteúdo do notebook aqui:", value="", height=300)
    return notebook_text
