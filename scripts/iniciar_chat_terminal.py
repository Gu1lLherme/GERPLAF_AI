import os
import re
import json
from datetime import datetime
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import CTransformers
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

# Configuração
CAMINHO_INDICE = "C:\\Users\\gesbarreto\\Downloads\\REPOSITORIES\\GERPLAF_AI\\indice_json"
MODELO_EMBEDDING = "sentence-transformers/all-MiniLM-L6-v2"
LLM_PATH = "C:\\Users\\gesbarreto\\Downloads\\REPOSITORIES\\GERPLAF_AI\\modelos\\mistral-7b-instruct-v0.1.Q4_K_M.gguf"
CAMINHO_LOG = "C:\\Users\\gesbarreto\\Downloads\\REPOSITORIES\\GERPLAF_AI\\resultado\\log_chat.json"

os.makedirs(os.path.dirname(CAMINHO_LOG), exist_ok=True)

# Carregar embeddings e índice FAISS
print("🔄 Carregando modelo e índice vetorial...")
embeddings = HuggingFaceEmbeddings(model_name=MODELO_EMBEDDING)
vectorstore = FAISS.load_local(CAMINHO_INDICE, embeddings, allow_dangerous_deserialization=True)

llm = CTransformers(
    model=LLM_PATH,
    model_type="mistral",
    config={
        "max_new_tokens": 512,
        "temperature": 0.7,
        "context_length": 2048,
    }
)

# Prompt
template = """
Você é um assistente jurídico treinado para responder com base no Auto de Infração {numero_auto}.
Considere somente os documentos abaixo e não invente informações fora do contexto.

--------------------------
{context}
--------------------------
Pergunta: {question}
Resposta:
"""
prompt = PromptTemplate.from_template(template)
chain = create_stuff_documents_chain(llm, prompt)

# Extrair número do auto
def extrair_auto_infracao(pergunta):
    match = re.search(r'\b(2023\d{4})\b', pergunta)
    return match.group(1) if match else None

# Reduz o conteúdo dos documentos
def limitar_contexto(docs, limite=1000):
    return [
        Document(page_content=doc.page_content[:limite], metadata=doc.metadata)
        for doc in docs
    ]

# Tentar carregar log anterior
historico = []
if os.path.exists(CAMINHO_LOG) and os.path.getsize(CAMINHO_LOG) > 0:
    try:
        with open(CAMINHO_LOG, "r", encoding="utf-8") as f:
            historico = json.load(f)
    except json.JSONDecodeError:
        print("⚠️ Log existente está corrompido. Criando novo arquivo de log.")
        historico = []

# Loop do chat
print("\n🤖 IA pronta! Digite suas perguntas. Digite 'sair' para encerrar.\n")

while True:
    pergunta = input("❓ Você: ").strip()
    if pergunta.lower() in ["sair", "exit", "quit"]:
        print("👋 Encerrando o chat.")
        break

    numero_auto = extrair_auto_infracao(pergunta)

    if numero_auto:
        docs = vectorstore.similarity_search(pergunta, k=2, filter={"auto_infracao": numero_auto})
    else:
        docs = vectorstore.similarity_search(pergunta, k=2)

    if not docs:
        print("⚠️ Nenhum documento correspondente foi encontrado.\n")
        continue

    docs_limitados = limitar_contexto(docs)

    resposta = chain.invoke({
        "context": docs_limitados,
        "question": pergunta,
        "numero_auto": numero_auto or "desconhecido"
    })

    fontes = [doc.metadata.get("source", "desconhecido") for doc in docs]

    print(f"\n🧠 Resposta: {resposta.strip()}")
    print(f"📄 Fonte(s): {', '.join(fontes)}\n")

    historico.append({
        "pergunta": pergunta,
        "resposta": resposta.strip(),
        "data": datetime.now().isoformat(),
        "fontes": fontes
    })

    with open(CAMINHO_LOG, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=4)