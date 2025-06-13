#!/usr/bin/env python
# blip_test.py
import os, time, json, requests

# ======== CONFIG (use as mesmas variáveis do .env) =========
CLIENT_ID     = os.getenv("BLIP_CLIENT_ID",     "9299951bf5c94a02a67262e34aa720e9")
CLIENT_SECRET = os.getenv("BLIP_CLIENT_SECRET", "sEc4M5g8RUWS3sV48ynuYQ==")
TENANT_ID     = os.getenv("BLIP_TENANT_ID",     "762e087d-ffac-4986-a488-df1fb16dc3d3")
APP_NAME      = os.getenv("BLIP_APP",           "CrewAI-Studio")
MODEL_NAME    = "gpt-4o-mini"          # pode trocar

# ======== END CONFIG =======================================

AUTH_URL = "https://secure-backend-api.stilingue.com.br/blip-ai-suite-auth/prod/token"
LLM_URL  = "https://secure-backend-api.stilingue.com.br/llm-server/prod/message-gen/generate"

def get_token():
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    r = requests.post(AUTH_URL, json=payload, timeout=15)
    r.raise_for_status()
    data = r.json()
    print("[TOKEN] ok, expira em", data["expires_in"], "s")
    return data["access_token"]

def call_llm(token, prompt:str):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }
    body = {
        "sender": {
            "app": APP_NAME,
            "tenant_id": TENANT_ID,
        },
        "prompt": {
            "messages": [
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user",   "content": prompt}
            ]
        },
        "request_config": {
            "request_params": {
                "temperature": 0.2,
                "max_tokens": 200
            },
            "api_version": "2024-02-01"
        },
        "resource_config": {
            "service": "auto_azure_open_ai",
            "params": {"model_name": MODEL_NAME}
        }
    }
    r = requests.post(LLM_URL, headers=headers, json=body, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["content"]

if __name__ == "__main__":
    tk = get_token()
    resposta = call_llm(tk, "Explique em uma frase quem foi Michael Jordan.")
    print("\n=== RESPOSTA DO LLM ===")
    print(resposta)