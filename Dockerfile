# Imagem base com Python
FROM python:3.10-slim
# Define o diretório de trabalho
WORKDIR /app
# Copia os arquivos para o container
COPY . .
# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt
# Expõe a porta 8080 exigida pelo Cloud Run
EXPOSE 8080
# Comando de execução do bot
CMD ["python", "main.py"]
