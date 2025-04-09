import os
import json
import csv
import pdfplumber
from datetime import datetime
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import CTransformers
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate

# -----------------------
# CONFIGURAÇÕES
# -----------------------
PASTA_PDFS = "./pdfs"
CAMINHO_INDICE = "indice_json"
LLM_PATH = "./modelos/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
RESULTADO_JSON = "./resultado/resultados_respostas.json"
RESULTADO_CSV = "./resultado/resultados_respostas.csv"

# -----------------------
# FUNÇÕES
# -----------------------

def extrair_texto_pdf(path):
    with pdfplumber.open(path) as pdf:
        return "\n".join([page.extract_text() or "" for page in pdf.pages])

def carregar_documentos(pasta):
    documentos = []
    for nome in os.listdir(pasta):
        if nome.endswith(".pdf"):
            caminho_completo = os.path.join(pasta, nome)
            texto = extrair_texto_pdf(caminho_completo)
            documentos.append(Document(page_content=texto, metadata={"source": nome}))
    return documentos

def indexar_documentos():
    print("📚 Indexando PDFs...")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    if os.path.exists(CAMINHO_INDICE):
        vectorstore = FAISS.load_local(
            CAMINHO_INDICE, embeddings, allow_dangerous_deserialization=True
        )
    else:
        vectorstore = None

    novos_docs = carregar_documentos(PASTA_PDFS)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(novos_docs)

    if vectorstore:
        vectorstore.add_documents(chunks)
    else:
        vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(CAMINHO_INDICE)
    print("✅ Indexação concluída.")

def salvar_resultados(resultados):
    with open(RESULTADO_JSON, "w", encoding="utf-8") as fjson:
        json.dump(resultados, fjson, indent=4, ensure_ascii=False)

    with open(RESULTADO_CSV, "w", newline="", encoding="utf-8") as fcsv:
        writer = csv.DictWriter(
            fcsv, fieldnames=["pergunta", "resposta", "data", "fontes"]
        )
        writer.writeheader()
        for linha in resultados:
            writer.writerow(linha)

    print(f"\n📂 Resultados salvos em:\n - {RESULTADO_JSON}\n - {RESULTADO_CSV}")

def iniciar_chat(vectorstore, chain):
    print("\n🤖 IA pronta! Digite suas perguntas. Digite 'sair' para encerrar.\n")
    historico = []

    while True:
        pergunta = input("❓ Você: ")

        if pergunta.lower() in ["sair", "exit", "quit"]:
            print("👋 Encerrando o chat.")
            break

        docs = vectorstore.similarity_search(pergunta, k=2)
        resposta = chain.invoke({"context": docs, "question": pergunta})
        fontes = [doc.metadata.get("source", "Desconhecida") for doc in docs]

        print(f"\n🤖 IA: {resposta}")
        print(f"📄 Fonte(s): {', '.join(fontes)}\n")

        historico.append({
            "pergunta": pergunta,
            "resposta": resposta,
            "data": datetime.now().isoformat(),
            "fontes": fontes,
        })

    salvar_resultados(historico)

# -----------------------
# FLUXO PRINCIPAL
# -----------------------

if __name__ == "__main__":
    if not os.path.exists(CAMINHO_INDICE):
        indexar_documentos()

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectorstore = FAISS.load_local(
        CAMINHO_INDICE, embeddings, allow_dangerous_deserialization=True
    )

    llm = CTransformers(
        model=LLM_PATH,
        model_type="mistral",
        config={
            "max_new_tokens": 512,
            "temperature": 0.7,
            "context_length": 2048
        }
    )

    template = """
    Responda à pergunta com base nos documentos abaixo. Seja objetivo e claro.
    -----------------
    {context}
    -----------------
    Pergunta: {question}
    Resposta:
    """
    prompt = PromptTemplate.from_template(template)
    chain = create_stuff_documents_chain(llm, prompt)

    iniciar_chat(vectorstore, chain)
