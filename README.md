# ChatBot WhatsApp

Este é um projeto de chatbot em Python que se conecta à API do OpenAI para interpretar intenções e responder a usuários via terminal ou WhatsApp.

## 📋 Pré-requisitos

* Python 3.8+ instalado
* Git instalado
* Acesso à sua chave SSH configurada no GitHub
* `pip` para instalar dependências

## 📝 Clonar o repositório

```bash
# via SSH (recomendado)
git clone git@github.com:softwarePredador/chatBot_whatsapp.git
cd chatBot_whatsapp
```

## 🛠️ Configurar ambiente virtual

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 📦 Instalar dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Dica**: sempre que adicionar uma nova biblioteca, rode `pip freeze > requirements.txt` para manter o arquivo atualizado.

## 🔒 Configurar variáveis de ambiente (.env)

1. Na raiz do projeto, crie um arquivo chamado `.env`.
2. Adicione as chaves necessárias (exemplo abaixo):

   ```dotenv
   OPENAI_API_KEY=sk_************************
   ASSISTANT_ID_SAC=asst_***************
   ASSISTANT_ID_PERFORMANCE=asst_******
   ASSISTANT_ID_4X4=asst_***************
   # ... outras chaves que você use
   ```
3. Salve o arquivo.

O projeto usa a biblioteca `python-dotenv` para carregar automaticamente essas variáveis sempre que você rodar o script.

## 🚀 Executar o chatbot

```bash
# Certifique-se de que o .venv está ativado
env # deve mostrar algo como (.venv)
python chatbot_terminal.py
```

Digite sua mensagem e aguarde a resposta do assistente!

## 📝 Estrutura básica

```
├─ .env                # Variáveis de ambiente (não versionado)
├─ .gitignore          # Arquivos ignorados pelo Git
├─ chatbot_terminal.py # Código principal do chatbot
├─ requirements.txt    # Dependências do Python
└─ README.md           # Este arquivo de documentação
```

---

### 🎯 Próximos passos

* 🎨 **Personalizar**: ajuste o fluxo de mensagens, helpers e intents.
* 🔀 **Branching**: crie branches por feature (`feature/nova-intent`).
* ✅ **Tests**: adicione testes unitários para captura de erros de API e parsing.
* ⚙️ **CI/CD**: configure GitHub Actions para rodar testes a cada push.

Bom codar e bons testes! 🚀
