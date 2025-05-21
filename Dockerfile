# Use a imagem oficial do Python 3.13
FROM python:3.13-slim

# Instale dependências do sistema
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Defina diretório de trabalho
WORKDIR /app

# Copie arquivos do projeto
COPY pyproject.toml uv.lock ./
COPY src ./src

# Instale o gerenciador de pacotes UV
RUN pip install --no-cache-dir uv

# Instale as dependências do projeto usando UV
RUN uv pip compile pyproject.toml --no-emit-index-url -o requirements.txt
RUN uv pip install --system -r requirements.txt

# Exponha a porta usada pelo FastAPI/Uvicorn
EXPOSE 8000

# Comando para iniciar o servidor FastAPI com Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
