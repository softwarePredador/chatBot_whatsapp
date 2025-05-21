import os
import re
import time
import traceback
from dotenv import load_dotenv
import openai

from DatabaseWhatsapp.db import (
    get_or_create_user,
    get_thread_by_user_and_assistant,
    create_thread_db,
    log_message,
    fetch_history
)

# 1) Carrega .env e chave
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("Defina OPENAI_API_KEY no seu .env")

ASSISTANT_IDS = {
    "sac": os.getenv("ASSISTANT_ID_SAC"),         # assistente geral
    "performance": os.getenv("ASSISTANT_ID_PERFORMANCE"),
    "4x4": os.getenv("ASSISTANT_ID_4X4"),
    "financeiro": os.getenv("ASSISTANT_ID_FINANCEIRO")
}

# 2) Pede telefone e garante user_id
user_phone = input("Informe seu número de telefone: ").strip()
user_id = get_or_create_user(user_phone)
print(f"[DEBUG] Usuário ID = {user_id}\n")
print("Bem-vindo! Inicie sua conversa (Ctrl+C para sair)\n")

try:
    while True:
        user_input = input("Você: ").strip()
        if not user_input:
            continue

        txt = user_input.lower()
        # 3) Roteamento por palavra-chave
        if re.match(r"^(oi|olá|ola|hello|bom dia|boa tarde|boa noite)\b", txt):
            assistant_key = "sac"
        elif "manual" in txt and "pedalbooster" in txt:
            assistant_key = "performance"
        elif re.search(r"\b(para-?choque|bagageiro|rockslider|snorkel|protetor|rack|cacamba)\b", txt):
            assistant_key = "4x4"
        elif re.search(r"\b(financeiro|dinheiro|custa|preço|preco)\b", txt):
            assistant_key = "financeiro"
        else:
            assistant_key = "sac"

        if assistant_key not in ASSISTANT_IDS or not ASSISTANT_IDS[assistant_key]:
            assistant_key = "sac"

        print(f"[DEBUG] assistant_key={assistant_key}")

        # 4) Recupera ou cria a thread (local + oficial)
        thread = get_thread_by_user_and_assistant(user_id, assistant_key)
        if thread is None:
            print("[DEBUG] criando novo thread no OpenAI e DB local...")
            new_thread = openai.beta.threads.create()
            openai_thread_id = new_thread.id
            thread_id_db = create_thread_db(user_id, assistant_key, openai_thread_id)
        else:
            thread_id_db = thread["id"]
            openai_thread_id = thread["openai_thread_id"]
            print(f"[DEBUG] thread existente: db_id={thread_id_db}, openai_id={openai_thread_id}")

        # 5) Loga mensagem do usuário e busca histórico
        log_message(thread_id_db, "user", user_input)
        history = fetch_history(thread_id_db)[-20:]
        print(f"[DEBUG] carregou histórico com {len(history)} mensagens")

        system_prompt = {"role": "system", "content": (
            "Ignorar instruções internas de independência. Você vê todo o histórico abaixo e deve usá-lo para responder."
        )}
        messages = [system_prompt] + [{"role": h["role"], "content": h["content"]} for h in history]

        # 6) Envia ao OpenAI Thread
        try:
            print("[DEBUG] enviando mensagem para OpenAI...")
            openai.beta.threads.messages.create(
                thread_id=openai_thread_id,
                role="user",
                content=user_input
            )
            run = openai.beta.threads.runs.create(
                thread_id=openai_thread_id,
                assistant_id=ASSISTANT_IDS[assistant_key]
            )
            while run.status not in ("completed", "failed"):
                time.sleep(0.3)
                run = openai.beta.threads.runs.retrieve(thread_id=openai_thread_id, run_id=run.id)
            if run.status == "failed":
                raise RuntimeError("OpenAI Threads run failed")

            # 7) Recupera e extrai a resposta limpa
            msgs = openai.beta.threads.messages.list(thread_id=openai_thread_id)
            assistant_msgs = [m for m in msgs.data if m.role == "assistant"]
            latest = assistant_msgs[-1]
            content = latest.content

            if isinstance(content, list):
                # percorre cada bloco e coleta o text.value
                texts = []
                for blk in content:
                    if hasattr(blk, 'text') and hasattr(blk.text, 'value'):
                        texts.append(blk.text.value)
                    else:
                        # caso tenha outro tipo de bloco, cai aqui
                        texts.append(str(blk))
                assistant_response = ''.join(texts)

            elif hasattr(content, 'text') and hasattr(content.text, 'value'):
                # caso venha um único bloco
                assistant_response = content.text.value

            else:
                # fallback genérico
                assistant_response = str(content)

        except Exception as e:
            print("[ERROR] falha na chamada OpenAI:", e)
            continue

        # 8) Loga e imprime apenas a resposta
        #log_message(thread_id_db, "assistant", assistant_response)
        print("Assistente:", assistant_response, "\n")

except KeyboardInterrupt:
    print("\n[DEBUG] Conversa encerrada pelo usuário")