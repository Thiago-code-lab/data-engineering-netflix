"""
Funções utilitárias para o Pipeline de Engenharia de Dados Netflix.

Este módulo fornece utilitários comuns incluindo:
- Configuração e gerenciamento de logging
- Funções de validação de dados
- Utilitários de tratamento de erros
- Operações de arquivo e diretório
- Relatórios de qualidade de dados
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger
from config import LOGS_DIR, LOG_LEVEL, LOG_FORMAT

# Configura o logger
logger.remove()  # Remove handler padrão
logger.add(
    LOGS_DIR / "pipeline.log",
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    rotation="10 MB",
    retention="30 days"
)
logger.add(
    lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
    level=LOG_LEVEL
)

def registrar_mensagem(message: str) -> None:
    """Registra uma mensagem de informação."""
    logger.info(message)

def tratar_erro(error: str) -> None:
    """Trata erros registrando-os."""
    logger.error(error)

def registrar_sucesso(message: str) -> None:
    """Registra uma mensagem de sucesso."""
    logger.success(message)

def validar_dados(data: pd.DataFrame) -> bool:
    """Valida o formato e estrutura dos dados."""
    if data is None:
        tratar_erro("Dados são None")
        return False
    
    if data.empty:
        tratar_erro("Dados estão vazios")
        return False
    
    registrar_mensagem(f"Validação de dados passou: {len(data)} linhas, {len(data.columns)} colunas")
    return True

def validar_dados_netflix(df: pd.DataFrame) -> bool:
    """Valida a estrutura do conjunto de dados do Netflix."""
    colunas_obrigatórias = [
        'show_id', 'type', 'title', 'director', 'cast', 'country',
        'date_added', 'release_year', 'rating', 'duration', 'listed_in', 'description'
    ]
    
    colunas_ausentes = [col for col in colunas_obrigatórias if col not in df.columns]
    if colunas_ausentes:
        tratar_erro(f"Colunas obrigatórias ausentes: {colunas_ausentes}")
        return False
    
    registrar_sucesso("Validação da estrutura dos dados do Netflix passou")
    return True

def get_relatorio_qualidade_dados(df: pd.DataFrame) -> Dict[str, Any]:
    """Gera um relatório abrangente de qualidade de dados."""
    relatorio = {
        'total_linhas': len(df),
        'total_colunas': len(df.columns),
        'valores_ausentes': df.isnull().sum().to_dict(),
        'linhas_duplicadas': df.duplicated().sum(),
        'tipos_de_dados': df.dtypes.to_dict(),
        'uso_de_memoria': df.memory_usage(deep=True).sum(),
        'colunas_numericas': df.select_dtypes(include=[np.number]).columns.tolist(),
        'colunas_categoricas': df.select_dtypes(include=['object']).columns.tolist()
    }
    
    registrar_mensagem(f"Relatório de qualidade de dados gerado para {relatorio['total_linhas']} linhas")
    return relatorio

def salvar_arquivo(data: str, filename: Path) -> None:
    """Salva dados em um arquivo especificado."""
    try:
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(data)
        registrar_sucesso(f"Arquivo salvo com sucesso: {filename}")
    except Exception as e:
        tratar_erro(f"Erro ao salvar arquivo {filename}", e)

def criar_diretorio(path: Path) -> None:
    """Cria um diretório se ele não existir."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        registrar_mensagem(f"Diretório criado/verificado: {path}")
    except Exception as e:
        tratar_erro(f"Erro ao criar diretório {path}", e)

# Aliases para compatibilidade com código existente
log_message = registrar_mensagem
handle_error = tratar_erro
log_success = registrar_sucesso
validate_data = validar_dados
validate_dataframe = validar_dados
validate_netflix_data = validar_dados_netflix
get_data_quality_report = get_relatorio_qualidade_dados
save_to_file = salvar_arquivo
create_directory = criar_diretorio