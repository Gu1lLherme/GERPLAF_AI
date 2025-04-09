import pdfplumber
import re

def extrair_info_pdf(caminho_pdf):
    with pdfplumber.open(caminho_pdf) as pdf:
        texto = ''
        for pagina in pdf.pages:
            texto += pagina.extract_text() + '\n'

    # 1. Número do Auto de Infração
    match_auto = re.search(r"AUTO DE INFRAÇÃO Nº[:\s]*([0-9]+)", texto, re.IGNORECASE)
    numero_auto = match_auto.group(1) if match_auto else "Não encontrado"

    # 2. Julgamento do Auto de Infração
    match_julgamento = re.search(r"julgo\s+(NULO|IMPROCEDENTE|N[ÃA]O\s+IMPROCEDENTE)", texto, re.IGNORECASE)
    julgamento = match_julgamento.group(1).upper() if match_julgamento else "Não encontrado"

    # 3. Motivo do julgamento (busca próxima a "conclusão" ou trecho após "reanalise")
    motivo_match = re.search(
        r"reanalise.*?comprovando a quitação do débito.*?auto de infração",
        texto, re.IGNORECASE | re.DOTALL
    )
    motivo = "Quitação do débito comprovada" if motivo_match else "Motivo não encontrado"

    return {
        "Número do Auto de Infração": numero_auto,
        "Julgamento": julgamento,
        "Motivo do Julgamento": motivo
    }

# Exemplo de uso
resultado = extrair_info_pdf("2023009888.pdf")
for chave, valor in resultado.items():
    print(f"{chave}: {valor}")
