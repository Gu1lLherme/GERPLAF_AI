import os
import json
import csv
import pdfplumber
from datetime import datetime
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain_community.llms import LlamaCpp
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# -----------------------
# CONFIGURAÇÕES
# -----------------------
PASTA_PDFS = "./pdfs"
CAMINHO_INDICE = "indice_documentos"
LLM_PATH = "./modelos/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
RESULTADO_JSON = "./Resultado/resultados_respostas.json"
RESULTADO_CSV = "./Resultado/resultados_respostas.csv"


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
    docs = carregar_documentos(PASTA_PDFS)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(CAMINHO_INDICE)
    print("✅ Indexação concluída!")


def responder_perguntas(perguntas):
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectorstore = FAISS.load_local(
        CAMINHO_INDICE, embeddings, allow_dangerous_deserialization=True
    )

    llm = LlamaCpp(
        model_path=LLM_PATH, temperature=0.7, max_tokens=512, n_ctx=2048, verbose=True
    )

    chain = load_qa_chain(llm, chain_type="stuff")

    resultados = []
    for pergunta in perguntas:
        docs = vectorstore.similarity_search(pergunta, k=5)
        resposta = chain.run(input_documents=docs, question=pergunta)
        print(f"\n🔹 Pergunta: {pergunta}\n🧠 Resposta: {resposta}")
        resultados.append(
            {
                "pergunta": pergunta,
                "resposta": resposta,
                "data": datetime.now().isoformat(),
                "fontes": [doc.metadata["source"] for doc in docs],
            }
        )

    return resultados


def salvar_resultados(resultados):
    # Salvar em JSON
    with open(RESULTADO_JSON, "w", encoding="utf-8") as fjson:
        json.dump(resultados, fjson, indent=4, ensure_ascii=False)

    # Salvar em CSV
    with open(RESULTADO_CSV, "w", newline="", encoding="utf-8") as fcsv:
        writer = csv.DictWriter(
            fcsv, fieldnames=["pergunta", "resposta", "data", "fontes"]
        )
        writer.writeheader()
        for linha in resultados:
            writer.writerow(linha)

    print(f"\n📂 Resultados salvos em:\n - {RESULTADO_JSON}\n - {RESULTADO_CSV}")


"""# -----------------------
# FLUXO PRINCIPAL
# -----------------------
if __name__ == "__main__":
    if not os.path.exists(CAMINHO_INDICE):
        indexar_documentos()

    print("\n📥 Digite suas perguntas (digite 'sair' para encerrar):")
    resultados = []
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectorstore = FAISS.load_local(
        CAMINHO_INDICE, embeddings, allow_dangerous_deserialization=True
    )
    llm = LlamaCpp(
        model_path=LLM_PATH, temperature=0.7, max_tokens=512, n_ctx=2048, verbose=True
    )
    chain = load_qa_chain(llm, chain_type="stuff")

    while True:
        pergunta = input("❓ Pergunta: ")
        if pergunta.lower() in ["sair", "exit", "quit"]:
            break

        docs = vectorstore.similarity_search(pergunta, k=5)
        resposta = chain.run(input_documents=docs, question=pergunta)
        print(f"\n🔹 Pergunta: {pergunta}\n🧠 Resposta: {resposta}")

        resultados.append({
            "pergunta": pergunta,
            "resposta": resposta,
            "data": datetime.now().isoformat(),
            "fontes": [doc.metadata["source"] for doc in docs],
        })

    if resultados:
        salvar_resultados(resultados)
    else:
        print("⚠️ Nenhuma pergunta foi feita.")
"""

# -----------------------
# FLUXO PRINCIPAL
# -----------------------

if __name__ == "__main__":
    if not os.path.exists(CAMINHO_INDICE):
        indexar_documentos()

    print("\n📥 Digite suas perguntas (digite 'sair' para encerrar):")
    perguntas = []
    while True:
        p = input("❓ Pergunta: ")
        if p.lower() in ["sair", "exit", "quit"]:
            break
        perguntas.append(p)

    if perguntas:
        # 1️⃣ Primeiro responde e mostra no terminal
        respostas = responder_perguntas(perguntas)

        # 2️⃣ Depois salva as respostas
        salvar_resultados(respostas)
    else:
        print("⚠️ Nenhuma pergunta foi feita.")
