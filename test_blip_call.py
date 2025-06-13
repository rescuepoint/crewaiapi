# test_blip_call.py
import os, json, requests, base64
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID  = os.environ["BLIP_CLIENT_ID"]
CLIENT_SEC = os.environ["BLIP_CLIENT_SECRET"]

TENANT_ID  = os.environ["BLIP_TENANT_ID"]
APP_NAME   = os.environ["BLIP_APP"]
SUBS_ID    = os.environ["BLIP_SUBS_ID"]      # 5095
SUBS_NAME  = APP_NAME                        # normalmente o mesmo nome

AUTH_URL = "https://secure-backend-api.stilingue.com.br/blip-ai-suite-auth/prod/token"
LLM_URL  = "https://secure-backend-api.stilingue.com.br/llm-server/prod/message-gen/generate"

# --- token ---
tok = requests.post(AUTH_URL, json={
    "grant_type": "client_credentials",
    "client_id":  CLIENT_ID,
    "client_secret": CLIENT_SEC,
}, timeout=15).json()["access_token"]

# --- chamada ---
body = {
    "sender": {
        "app": APP_NAME,
        "tenant_id": TENANT_ID,
        "subs_id": SUBS_ID,
        "subs_name": SUBS_NAME
    },
    "prompt": {
        "messages": [
            {"role": "user", "content": "Explique em uma frase quem foi Michael Jordan."}
        ]
    },
    "request_config": {
        "request_params": {"temperature": 0.2, "max_tokens": 120},
        "api_version": "2024-02-01"
    },
    "resource_config": {
        "service": "auto_azure_open_ai",
        "params": {"model_name": "gpt-4o-mini"}
    }
}
r = requests.post(LLM_URL,
                  headers={"Authorization": tok,
                           "Content-Type": "application/json"},
                  json=body, timeout=30)

print("Status:", r.status_code)
print("Body:", r.text)

print("Headers enviados:", json.dumps(headers, indent=2))
print("Body enviado:", json.dumps(body, indent=2, ensure_ascii=False))