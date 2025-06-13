# Prompts sugeridos para cada etapa do pipeline

PROMPT_ANALISE = '''\
Você é um especialista em Databricks e BlipForge. Analise o notebook legado abaixo, identifique padrões, dependências, pontos de melhoria e possíveis problemas de compatibilidade. Responda de forma estruturada, destacando cada ponto encontrado.

Notebook legado:
{notebook}
'''

PROMPT_TRANSFORMACAO = '''\
Utilize as regras do BlipForge (consulte a documentação se necessário) para transformar e otimizar o notebook legado abaixo. O resultado deve ser um notebook pronto para uso no novo sistema, seguindo as melhores práticas e padrões do BlipForge.

Notebook legado:
{notebook}
'''

PROMPT_EXPLICACAO = '''\
Liste as principais mudanças e otimizações realizadas na transformação do notebook legado para o novo formato BlipForge. Explique de forma clara e objetiva cada alteração.

Notebook legado:
{notebook}
Notebook transformado:
{notebook_novo}
'''
