"""
Este script converte arquivos PDF em arquivos JSON, extraindo informações específicas de documentos legais.
Ele é projetado para processar arquivos PDF localizados em um diretório específico, extrair texto e campos relevantes,
e salvar os dados em formato JSON para facilitar a análise e consulta posterior.

### Funcionalidades principais:
1. **Leitura de arquivos PDF**:
   - O script percorre um diretório contendo arquivos PDF (`PASTA_PDFS`).
   - Para cada arquivo PDF, ele extrai o texto completo utilizando a biblioteca `pdfplumber`.

2. **Extração de campos relevantes**:
   - A partir do texto extraído, o script identifica e organiza informações específicas, como:
     - Número do auto de infração.
     - Relatório.
     - Fundamentação.
     - Conclusão.
     - Status do julgamento.
     - Conteúdo completo do texto.

3. **Conversão para JSON**:
   - Os dados extraídos de cada PDF são salvos em arquivos JSON no diretório especificado (`PASTA_JSON`).

4. **Mensagens de status**:
   - O script exibe mensagens no console indicando o progresso da conversão e a conclusão da tarefa.

### Variáveis principais:
- `PASTA_PDFS`: Caminho para o diretório contendo os arquivos PDF a serem convertidos.
- `PASTA_JSON`: Caminho para o diretório onde os arquivos JSON serão salvos.

### Dependências:
- `os`: Para manipulação de diretórios e arquivos.
- `pdfplumber`: Para extração de texto de arquivos PDF.
- `json`: Para salvar os dados extraídos em formato JSON.
- `re`: Para realizar buscas e extrações de padrões específicos no texto.

### Como usar:
1. Certifique-se de que os arquivos PDF estejam no diretório especificado em `PASTA_PDFS`.
2. Execute o script. Ele processará os arquivos PDF, extrairá os dados e salvará os arquivos JSON no diretório especificado em `PASTA_JSON`.
3. Após a execução, os arquivos JSON estarão prontos para uso.

### Observações:
- O script ignora arquivos que não possuem a extensão `.pdf`.
- Certifique-se de que o diretório especificado em `PASTA_JSON` tenha permissões de escrita.
"""

import os
import pdfplumber
import json
import re

PASTA_PDFS = "C:\\Users\\gesbarreto\\Downloads\\REPOSITORIES\\GERPLAF_AI\\pdfs"
PASTA_JSON = "C:\\Users\\gesbarreto\\Downloads\\REPOSITORIES\\GERPLAF_AI\\dados_json"

os.makedirs(PASTA_JSON, exist_ok=True)

def extrair_texto_pdf(path):
    with pdfplumber.open(path) as pdf:
        return "\n".join([page.extract_text() or "" for page in pdf.pages])

def extrair_campos(texto, nome_arquivo):
    resultado = {
        "auto_infracao": nome_arquivo.replace(".pdf", ""),
        "relatorio": "",
        "fundamentacao": "",
        "conclusao": "",
        "status_julgamento": "",
        "conteudo": texto,
    }

    # Seções principais
    relatorio_match = re.search(r"Relat[oó]rio\n(.*?)\nFundamenta[cç][aã]o", texto, re.DOTALL | re.IGNORECASE)
    if relatorio_match:
        resultado["relatorio"] = relatorio_match.group(1).strip()

    fundamentacao_match = re.search(r"Fundamenta[cç][aã]o\n(.*?)\nConclus[aã]o", texto, re.DOTALL | re.IGNORECASE)
    if fundamentacao_match:
        resultado["fundamentacao"] = fundamentacao_match.group(1).strip()

    conclusao_match = re.search(r"Conclus[aã]o\n(.*?)(?:\nAssinatura|\Z)", texto, re.DOTALL | re.IGNORECASE)
    if conclusao_match:
        resultado["conclusao"] = conclusao_match.group(1).strip()

        # Extrair status diretamente da conclusão
        status = re.search(
            r"julg[oa]\s+(Nulo|Improcedente|N[aã]o improcedente)",
            resultado["conclusao"],
            re.IGNORECASE
        )
        if status:
            resultado["status_julgamento"] = status.group(1).capitalize()
        else:
            # Tentativa alternativa com palavras-chave
            conclusao_upper = resultado["conclusao"].upper()
            if "NULO" in conclusao_upper:
                resultado["status_julgamento"] = "Nulo"
            elif "IMPROCEDENTE" in conclusao_upper:
                resultado["status_julgamento"] = "Improcedente"
            elif "NÃO IMPROCEDENTE" in conclusao_upper or "NÃO-PROCEDENTE" in conclusao_upper:
                resultado["status_julgamento"] = "Não improcedente"

    return resultado

# Processamento de PDFs
for arquivo in os.listdir(PASTA_PDFS):
    if not arquivo.endswith(".pdf"):
        continue

    caminho_pdf = os.path.join(PASTA_PDFS, arquivo)
    texto = extrair_texto_pdf(caminho_pdf)
    dados = extrair_campos(texto, arquivo)

    caminho_json = os.path.join(PASTA_JSON, arquivo.replace(".pdf", ".json"))
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

print("✅ Conversão concluída com sucesso!")