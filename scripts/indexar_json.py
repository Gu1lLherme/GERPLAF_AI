"""
Este script realiza a indexação de arquivos JSON em um banco de dados vetorial utilizando a biblioteca Langchain. 
Ele é projetado para processar arquivos JSON localizados em um diretório específico, extrair informações relevantes, 
e armazenar os dados indexados em um formato que pode ser consultado posteriormente.

### Funcionalidades principais:
1. **Leitura de arquivos JSON**:
   - O script percorre um diretório contendo arquivos JSON (`PASTA_JSON`).
   - Para cada arquivo JSON, ele extrai o conteúdo principal e metadados específicos.

2. **Preparação de documentos**:
   - Cada arquivo JSON é transformado em um objeto `Document` da biblioteca Langchain, contendo:
     - O conteúdo principal do documento.
     - Metadados como auto de infração, status de julgamento, relatório, fundamentação, conclusão e o nome do arquivo de origem.

3. **Criação de embeddings**:
   - Utiliza o modelo de embeddings `sentence-transformers/all-MiniLM-L6-v2` para gerar representações vetoriais dos documentos.

4. **Armazenamento em um banco de dados vetorial**:
   - Os documentos processados são armazenados em um banco de dados vetorial utilizando a implementação FAISS da biblioteca Langchain.
   - O índice vetorial é salvo localmente no diretório especificado (`CAMINHO_INDICE`).

5. **Mensagens de status**:
   - O script exibe mensagens no console indicando o progresso da indexação, como o número de documentos processados e a conclusão da tarefa.

### Variáveis principais:
- `PASTA_JSON`: Caminho para o diretório contendo os arquivos JSON a serem indexados.
- `CAMINHO_INDICE`: Caminho para o diretório onde o índice vetorial será salvo.
- `EMBEDDING_MODEL_NAME`: Nome do modelo de embeddings utilizado para gerar representações vetoriais.

### Dependências:
- `os`: Para manipulação de diretórios e arquivos.
- `json`: Para leitura e manipulação de arquivos JSON.
- `langchain_community.vectorstores.FAISS`: Para criação e manipulação do banco de dados vetorial.
- `langchain_community.embeddings.HuggingFaceEmbeddings`: Para geração de embeddings utilizando modelos Hugging Face.
- `langchain.docstore.document.Document`: Para representar documentos com conteúdo e metadados.

### Como usar:
1. Certifique-se de que os arquivos JSON estejam no diretório especificado em `PASTA_JSON`.
2. Execute o script. Ele processará os arquivos, criará o índice vetorial e salvará no diretório especificado em `CAMINHO_INDICE`.
3. Após a execução, o índice vetorial estará pronto para consultas.

### Observações:
- Certifique-se de que o modelo de embeddings especificado em `EMBEDDING_MODEL_NAME` esteja disponível e configurado corretamente.
- O script ignora arquivos que não possuem a extensão `.json`.
"""

import os
import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

PASTA_JSON = "C:\\Users\\gesbarreto\\Downloads\\REPOSITORIES\\GERPLAF_AI\\dados_json"
CAMINHO_INDICE = "C:\\Users\\gesbarreto\\Downloads\\REPOSITORIES\\GERPLAF_AI\\indice_json"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

docs = []

for arquivo in os.listdir(PASTA_JSON):
    if not arquivo.endswith(".json"):
        continue

    with open(os.path.join(PASTA_JSON, arquivo), "r", encoding="utf-8") as f:
        dados = json.load(f)

    conteudo = dados.get("conteudo", "")
    metadados = {
        "auto_infracao": dados.get("auto_infracao", ""),
        "status_julgamento": dados.get("status_julgamento", ""),
        "relatorio": dados.get("relatorio", ""),
        "fundamentacao": dados.get("fundamentacao", ""),
        "conclusao": dados.get("conclusao", ""),
        "source": arquivo
    }

    docs.append(Document(page_content=conteudo, metadata=metadados))

print(f"📄 {len(docs)} documentos preparados para indexação")

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
vectorstore = FAISS.from_documents(docs, embeddings)
vectorstore.save_local(CAMINHO_INDICE)

print("✅ Indexação concluída com sucesso!")
