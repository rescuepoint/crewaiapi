import os, sys, json, requests, time, pathlib
sys.path.append('app')
from llms import create_llm

# Ensure environment variables are set (fallback to .env)
from dotenv import load_dotenv
load_dotenv()

required = ['BLIP_CLIENT_ID','BLIP_CLIENT_SECRET','BLIP_TENANT_ID']
missing=[v for v in required if not os.getenv(v)]
if missing:
    print('Variáveis faltando:', missing)
    exit(1)

llm = create_llm('Blip: gpt-4o-mini', temperature=0.1)
print('Tipo do objeto LLM:', type(llm))
try:
    resposta = llm('Teste rápido: diga Olá.')
    print('Resposta da Blip:', resposta)
except Exception as e:
    print('Erro ao chamar a Blip:', e)
