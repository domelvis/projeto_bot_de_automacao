# Imagem base leve com Python 3.11
FROM python:3.11-slim

# Criar diretório da aplicação
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para aproveitar cache
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar toda a aplicação, incluindo assets
COPY . .

# Garantir que a pasta assets está presente
RUN mkdir -p /app/assets

# Expor porta da API
EXPOSE 8000

# Rodar a aplicação com uvicorn para produção
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
