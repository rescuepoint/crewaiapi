# Script para criar agente e tarefas para transformação de notebooks Databricks
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.db_utils import save_agent, save_task, save_crew
from app.my_agent import MyAgent
from app.my_task import MyTask
from app.my_crew import MyCrew

# 1. Criação do agente
agent = MyAgent(
    role="Transformador de Notebooks Databricks",
    backstory="Especialista em migração e otimização de notebooks Databricks, com domínio das regras do BlipForge.",
    goal="Transformar notebooks legados em versões otimizadas e compatíveis com o novo sistema.",
    llm_provider_model="Blip: gpt-4o-mini",
    temperature=0.1,
    verbose=True,
    allow_delegation=False,
    cache=True,
    max_iter=10,
    tools=[],
)
save_agent(agent)

# 2. Criação das tarefas
# Task 1: Receber notebook legado
input_task = MyTask(
    description="Receba o notebook Databricks legado fornecido pelo usuário.",
    expected_output="Notebook legado em formato texto.",
    agent=agent
)
save_task(input_task)

# Task 2: Analisar notebook
analyze_task = MyTask(
    description="Analise o notebook legado, identifique padrões, dependências e pontos de melhoria.",
    expected_output="Relatório de análise do notebook.",
    agent=agent
)
save_task(analyze_task)

# Task 3: Aplicar regras do BlipForge
transform_task = MyTask(
    description="Aplique as regras do BlipForge para transformar e otimizar o notebook legado.",
    expected_output="Novo notebook transformado, pronto para uso no sistema novo.",
    agent=agent
)
save_task(transform_task)

# Task 4: Explicar mudanças
explain_task = MyTask(
    description="Liste as principais mudanças e otimizações realizadas na transformação.",
    expected_output="Relatório de mudanças.",
    agent=agent
)
save_task(explain_task)

# 3. Criação da crew
crew = MyCrew(
    name="Transformação de Notebooks Databricks",
    agents=[agent],
    tasks=[input_task, analyze_task, transform_task, explain_task],
    process="sequential",
    verbose=True,
    cache=True,
    max_rpm=1000,
)
save_crew(crew)

print("Agente, tarefas e crew criados com sucesso!")
