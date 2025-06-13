import os, json, time, base64, requests
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv("BLIP_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLIP_CLIENT_SECRET")

auth_url = "https://secure-backend-api.stilingue.com.br/blip-ai-suite-auth/prod/token"
payload = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
}
print(f"[+] Solicitando token para client_id {CLIENT_ID[:6]}…")
resp = requests.post(auth_url, json=payload, timeout=15)
resp.raise_for_status()
data = resp.json()
access_token = data["access_token"]
print("[+] Token recebido. Expires_in:", data["expires_in"], "s")

# Decode JWT payload (segunda parte)
parts = access_token.split('.')
if len(parts) < 2:
    raise SystemExit("Formato JWT inesperado")

payload_b64 = parts[1] + '=='  # fix padding
payload_json = json.loads(base64.urlsafe_b64decode(payload_b64))
print("\n[ Decoded payload ]\n", json.dumps(payload_json, indent=2, ensure_ascii=False))

print("\nCopie os valores:")
print("BLIP_TENANT_ID=", payload_json.get("tid"))
print("BLIP_APP=", payload_json.get("subName"), "(ou o valor que você preferir)")
