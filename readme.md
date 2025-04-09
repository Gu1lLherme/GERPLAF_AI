# GERPLAF AI 

Gerente de Documento com IA, capas de receber arquivos em pdf e analisa-lo para que o usuario
possa fazer perguntas sobre esse arquivo e ter as informações que ele busca como: 
 
 - Qual foi a conclusão do julgamento?
 - Qual a fundamentação?
 - Qual a fundamentação?

## Do que ele é CAPAZ ?

Sistema com IA capaz de:

📄 Receber arquivos PDF (manualmente ou por upload)

🔁 Converter automaticamente para JSON estruturado

🤖 Analisar o conteúdo e responder perguntas como:

Qual foi a conclusão do julgamento?

Qual foi o motivo?

Qual a fundamentação?

💬 Fornecer respostas precisas, rápidas e claras

🖥️ Ter uma interface amigável (tipo chat + upload de PDFs)


🕰️ Linha do tempo do projeto Gerente de Documentos com IA
Etapa	| Sucesso |	Descrição
✅ Inicial	🧠	Estrutura básica com extração de PDFs e respostas via terminal
✅ RAG v1	🔎	Implementação de busca vetorial com FAISS + LangChain
✅ Modelo Local	🧠	LLM funcionando com CTransformers e modelo Mistral 7B
✅ Resposta direta	💬	Ajuste para mostrar a resposta no terminal imediatamente
✅ Fontes na resposta	📄	Exibir os nomes dos PDFs de onde veio a resposta
✅ Persistência FAISS	💾	Reutilização de índice para não reprocessar sempre
🔜 Conversão para JSON	🚀	Agora vamos organizar tudo em um novo formato estruturado