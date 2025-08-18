#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de inicialização para a aplicação web Whisper.cpp

Este script configura o ambiente e inicia o servidor Flask.
"""

import os
import sys
import argparse
import logging
import json
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('whisper_app')

# Verificar se estamos no diretório correto
app_dir = Path(__file__).resolve().parent
os.chdir(app_dir)

# Verificar dependências
try:
    import flask
    import numpy
    import soundfile
    import ffmpeg
except ImportError as e:
    logger.error(f"Dependência não encontrada: {e}")
    logger.info("Instalando dependências necessárias...")
    
    # Instalar dependências
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    logger.info("Dependências instaladas com sucesso!")

# Verificar se o executável whisper.cpp existe
from config import WHISPER_EXECUTABLE, MODELS_DIR

if not os.path.exists(WHISPER_EXECUTABLE):
    logger.warning(f"Executável whisper.cpp não encontrado em: {WHISPER_EXECUTABLE}")
    logger.info("Por favor, compile o whisper.cpp e configure o caminho correto em config.py")
    logger.info("A aplicação será iniciada em modo de demonstração com funcionalidades limitadas.")
    demo_mode = True
else:
    demo_mode = False

# Verificar se o diretório de modelos existe
if not os.path.exists(MODELS_DIR):
    logger.info(f"Criando diretório de modelos: {MODELS_DIR}")
    os.makedirs(MODELS_DIR, exist_ok=True)

# Verificar se há pelo menos um modelo disponível
models = [f for f in os.listdir(MODELS_DIR) if f.endswith('.bin')]
if not models:
    logger.warning("Nenhum modelo encontrado no diretório de modelos.")
    logger.info("Você pode baixar modelos usando o script models/download.py")
    
    # Perguntar se o usuário deseja baixar um modelo agora
    response = input("Deseja baixar o modelo 'base' agora? (s/n): ")
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        try:
            from models.download import download_model
            download_model('base')
            logger.info("Modelo 'base' baixado com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao baixar o modelo: {e}")
            sys.exit(1)

# Criar diretórios necessários
os.makedirs('uploads', exist_ok=True)
os.makedirs('transcriptions', exist_ok=True)
os.makedirs('static/temp', exist_ok=True)

# Verificar se o arquivo MEMO.json existe
if not os.path.exists('MEMO.json'):
    logger.warning("Arquivo MEMO.json não encontrado. Criando arquivo padrão...")
    
    # Criar arquivo MEMO.json padrão
    memo_data = {
        "features": [
            "Implementação em C/C++ sem dependências",
            "Otimizado para Apple Silicon (ARM NEON, Accelerate framework)",
            "Suporte a AVX, AVX2, AVX512 em x86",
            "Suporte a VSX em PowerPC",
            "Precisão mista F16/F32",
            "Quantização de inteiros (4-bit, 5-bit, 8-bit)",
            "Zero alocações de memória em tempo de execução",
            "Suporte a Core ML para Apple Neural Engine",
            "Suporte a GPU via Vulkan, CUDA, OpenCL",
            "Suporte a OpenVINO para aceleração em Intel GPUs"
        ],
        "platforms": [
            "macOS", "Windows", "Linux", "iOS", "Android", "WebAssembly"
        ],
        "models": [
            {"name": "tiny", "size": "~75 MB", "memory": "~390 MB", "description": "Mais rápido, menos preciso"},
            {"name": "base", "size": "~142 MB", "memory": "~500 MB", "description": "Bom equilíbrio entre velocidade e precisão"},
            {"name": "small", "size": "~466 MB", "memory": "~1.0 GB", "description": "Mais preciso, velocidade moderada"},
            {"name": "medium", "size": "~1.5 GB", "memory": "~2.6 GB", "description": "Alta precisão, mais lento"},
            {"name": "large", "size": "~3.0 GB", "memory": "~4.7 GB", "description": "Máxima precisão, mais lento"}
        ]
    }
    
    with open('MEMO.json', 'w', encoding='utf-8') as f:
        json.dump(memo_data, f, ensure_ascii=False, indent=4)
    
    logger.info("Arquivo MEMO.json criado com sucesso!")

# Analisar argumentos da linha de comando
parser = argparse.ArgumentParser(description='Iniciar a aplicação web Whisper.cpp')
parser.add_argument('--host', default='127.0.0.1', help='Endereço IP para o servidor (padrão: 127.0.0.1)')
parser.add_argument('--port', type=int, default=5000, help='Porta para o servidor (padrão: 5000)')
parser.add_argument('--debug', action='store_true', help='Executar em modo de depuração')
args = parser.parse_args()

# Iniciar a aplicação Flask
from app import app

if __name__ == '__main__':
    logger.info(f"Iniciando servidor em http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)