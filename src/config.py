"""
Módulo de configuração para o Pipeline de Engenharia de Dados Netflix.

Este módulo centraliza todas as configurações incluindo:
- Parâmetros de conexão com banco de dados
- Configurações de API e endpoints
- Caminhos de arquivos e diretórios
- Parâmetros de execução do pipeline
- Configuração de logging

Todas as informações sensíveis devem ser armazenadas em variáveis de ambiente.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Carrega variáveis de ambiente
load_dotenv()

# Caminhos do projeto
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

# Cria diretórios se não existirem
for directory in [DATA_DIR, OUTPUT_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Parâmetros de conexão com banco de dados
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "netflix_pipeline")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configuração da fonte de dados
NETFLIX_CSV_PATH = PROJECT_ROOT.parent / "netflix_titles.csv"
TABLE_NAME = "netflix_titles"

# Configuração da API (para uso futuro)
API_URL = os.getenv("API_URL", "https://api.example.com/data")
API_KEY = os.getenv("API_KEY", "sua_chave_api_aqui")

# Configurações do pipeline
TIMEOUT = 30  # Tempo limite para requisições da API em segundos
RETRY_COUNT = 3  # Número de tentativas para requisições da API
CHUNK_SIZE = 1000  # Tamanho do lote para operações de banco de dados

# Configuração de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"

# Configurações de visualização
FIGURE_SIZE = (12, 8)
DPI = 300
COLOR_PALETTE = "viridis"