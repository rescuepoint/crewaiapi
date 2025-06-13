import os
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from crewai import LLM
from langchain_openai.chat_models.base import BaseChatOpenAI
from litellm import completion
import time
import requests

def load_secrets_fron_env():
    load_dotenv(override=True)
    if "env_vars" not in st.session_state:
        st.session_state.env_vars = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "OPENAI_API_BASE": os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1/"),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
            "LMSTUDIO_API_BASE": os.getenv("LMSTUDIO_API_BASE"),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            "OLLAMA_HOST": os.getenv("OLLAMA_HOST"),
            "XAI_API_KEY": os.getenv("XAI_API_KEY"),
            "BLIP_CLIENT_ID": os.getenv("BLIP_CLIENT_ID"),
            "BLIP_CLIENT_SECRET": os.getenv("BLIP_CLIENT_SECRET"),
            "BLIP_TENANT_ID": os.getenv("BLIP_TENANT_ID"),
        }
    else:
        st.session_state.env_vars = st.session_state.env_vars

def switch_environment(new_env_vars):
    for key, value in new_env_vars.items():
        if value not in (None, ""):
            os.environ[key] = value
            st.session_state.env_vars[key] = value

def restore_environment():
    """Restaura o ambiente com os valores armazenados em session_state.

    Se um valor for ``None`` removemos a variável de ambiente caso exista. Isso
    evita que chaves desnecessárias (por exemplo `OPENAI_API_KEY`) permaneçam
    definidas e causem rotas de fallback inesperadas dentro do LiteLLM / OpenAI
    quando estamos usando outro provedor como a Blip.
    """
    for key, value in st.session_state.env_vars.items():
        if value not in (None, ""):
            # Restaura o valor original
            os.environ[key] = value
        else:
            # Remove variável se estiver presente
            os.environ.pop(key, None)

def safe_pop_env_var(key):
    os.environ.pop(key, None)

def create_openai_llm(model, temperature):
    switch_environment({
        "OPENAI_API_KEY": st.session_state.env_vars["OPENAI_API_KEY"],
        "OPENAI_API_BASE": st.session_state.env_vars["OPENAI_API_BASE"],
    })
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")

    if api_key:
        return LLM(model=model, temperature=temperature, base_url=api_base)
    else:
        raise ValueError("OpenAI API key not set in .env file")

def create_anthropic_llm(model, temperature):
    switch_environment({
        "ANTHROPIC_API_KEY": st.session_state.env_vars["ANTHROPIC_API_KEY"],
    })
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if api_key:
        return ChatAnthropic(
            anthropic_api_key=api_key,
            model_name=model,
            temperature=temperature,
            max_tokens=4095,
        )
    else:
        raise ValueError("Anthropic API key not set in .env file")

def create_groq_llm(model, temperature):
    switch_environment({
        "GROQ_API_KEY": st.session_state.env_vars["GROQ_API_KEY"],
    })
    api_key = os.getenv("GROQ_API_KEY")

    if api_key:
        return ChatGroq(groq_api_key=api_key, model_name=model, temperature=temperature, max_tokens=4095)
    else:
        raise ValueError("Groq API key not set in .env file")

def create_ollama_llm(model, temperature):
    host = st.session_state.env_vars["OLLAMA_HOST"]
    if host:
        switch_environment({
            "OPENAI_API_KEY": "ollama",  # Nastaví OpenAI API klíč na "ollama"
            "OPENAI_API_BASE": host,    # Nastaví OpenAI API Base na hodnotu OLLAMA_HOST
        })
        return LLM(model=model, temperature=temperature, base_url=host)
    else:
        raise ValueError("Ollama Host is not set in .env file")


def create_xai_llm(model, temperature):
    host = "https://api.x.ai/v1"
    api_key = st.session_state.env_vars.get("XAI_API_KEY")

    if not api_key:
        raise ValueError("XAI_API_KEY must be set in .env file")

    switch_environment({
        "OPENAI_API_KEY": api_key,
        "OPENAI_API_BASE": host,
    })

    return LLM(
        model=model,
        temperature=temperature,
        api_key=api_key,
        base_url=host
    )

def create_lmstudio_llm(model, temperature):
    switch_environment({
        "OPENAI_API_KEY": "lm-studio",
        "OPENAI_API_BASE": st.session_state.env_vars["LMSTUDIO_API_BASE"],
    })
    api_base = os.getenv("OPENAI_API_BASE")

    if api_base:
        return ChatOpenAI(
            openai_api_key="lm-studio",
            openai_api_base=api_base,
            temperature=temperature,
            max_tokens=4095,
        )
    else:
        raise ValueError("LM Studio API base not set in .env file")

class BlipLLMWrapper:
    def __init__(self, model_name="gpt-4o-mini", temperature=0.5, max_tokens=800):
        self.client_id = os.getenv("BLIP_CLIENT_ID")
        self.client_secret = os.getenv("BLIP_CLIENT_SECRET")
        self.app = os.getenv("BLIP_APP", "CrewAI-Studio")
        self.tenant_id = os.getenv("BLIP_TENANT_ID")
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.token_info = None
        if not all([self.client_id, self.client_secret, self.tenant_id]):
            raise ValueError("Variáveis de ambiente BLIP_CLIENT_ID, BLIP_CLIENT_SECRET e BLIP_TENANT_ID precisam estar definidas.")

    def _get_token(self):
        url = "https://secure-backend-api.stilingue.com.br/blip-ai-suite-auth/prod/token"
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            self.token_info = response.json()
            return self.token_info["access_token"]
        else:
            raise Exception(f"Erro ao obter token: {response.status_code} - {response.text}")

    def _get_valid_token(self):
        if not self.token_info or self.token_info.get("expires_on", 0) - 10 < int(time.time()):
            return self._get_token()
        return self.token_info["access_token"]

    def call(self, prompt: str, **kwargs) -> str:
        token = self._get_valid_token()
        url = "https://secure-backend-api.stilingue.com.br/llm-server/prod/message-gen/generate"
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        payload = {
            "sender": {
                "app": self.app,
                "tenant_id": self.tenant_id,
                "subs_id": os.getenv("BLIP_SUBS_ID"),
                "subs_name": self.app,
            },
            "prompt": {
                "messages": [
                    {"role": "system", "content": "Você é um assistente útil e preciso."},
                    {"role": "user", "content": str(prompt)}
                ]
            },
            "request_config": {
                "request_params": {
                    "temperature": kwargs.get("temperature", self.temperature),
                    "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                },
                "api_version": "2024-02-01"
            },
            "resource_config": {
                "service": "auto_azure_open_ai",
                "params": {"model_name": self.model_name}
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Erro ao chamar o LLM Server: {response.status_code} - {response.text}")
        return response.json()["choices"][0]["content"]

    # compatibilidade com CrewAI: objeto pode ser chamado diretamente
    def __call__(self, prompt: str, **kwargs):
        return self.call(prompt, **kwargs)


def create_blip_llm(model="gpt-4o-mini", temperature=0.5):
    return BlipLLMWrapper(model_name=model, temperature=temperature)

LLM_CONFIG = {
    "OpenAI": {
        "models": os.getenv("OPENAI_PROXY_MODELS", "").split(",") if os.getenv("OPENAI_PROXY_MODELS") else ["gpt-4.1-mini","gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "gpt-4-turbo"],
        "create_llm": create_openai_llm,
    },
    "Groq": {
        "models": ["groq/llama3-8b-8192", "groq/llama3-70b-8192", "groq/mixtral-8x7b-32768"],
        "create_llm": create_groq_llm,
    },
    "Ollama": {
        "models": os.getenv("OLLAMA_MODELS", "").split(",") if os.getenv("OLLAMA_MODELS") else [],
        "create_llm": create_ollama_llm,
    },
    "Anthropic": {
        "models": ["claude-3-5-sonnet-20240620","claude-3-7-sonnet-20250219"],
        "create_llm": create_anthropic_llm,
    },
    "LM Studio": {
        "models": ["lms-default"],
        "create_llm": create_lmstudio_llm,
    },
     "Xai": {
        "models": ["xai/grok-2-1212", "xai/grok-beta"],
        "create_llm": create_xai_llm,
    },
    "Blip": {
        "models": ["gpt-4o-mini"],
        "create_llm": create_blip_llm,
    },
}

def llm_providers_and_models():
    return [f"{provider}: {model}" for provider in LLM_CONFIG.keys() for model in LLM_CONFIG[provider]["models"]]

def create_llm(provider_and_model, temperature=0.15):
    provider, model = provider_and_model.split(": ")
    create_llm_func = LLM_CONFIG.get(provider, {}).get("create_llm")

    if create_llm_func:
        llm = create_llm_func(model, temperature)
        restore_environment()  # Obnoví původní prostředí po vytvoření LLM
        return llm
    else:
        raise ValueError(f"LLM provider {provider} is not recognized or not supported")
