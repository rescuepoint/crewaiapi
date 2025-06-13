# Página isolada, sem importações de outros módulos do app exceto o necessário
import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'notebook_transform'))

class PageNotebookTransform:
    def __init__(self):
        self.name = "Notebook Transform"
    def draw(self):
        from notebook_transform.page_transform import run_notebook_transform_page
        run_notebook_transform_page()
