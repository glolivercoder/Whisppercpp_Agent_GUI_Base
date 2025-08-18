#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import requests
from tqdm import tqdm
import hashlib

# Adicionar o diretório pai ao path para importar config.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# URLs e hashes dos modelos
MODEL_URLS = {
    'tiny.en': {
        'url': 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.en.bin',
        'md5': '99de7cb4b4f3452b1129c60cb8dab833',
        'size_mb': 75
    },
    'tiny': {
        'url': 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin',
        'md5': 'be07e048e1e599ad46341c8d2a135930',
        'size_mb': 75
    },
    'base.en': {
        'url': 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin',
        'md5': '137c40403d78fd54d454da0f9bd998f7',
        'size_mb': 142
    },
    'base': {
        'url': 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin',
        'md5': '465707469ff3a37a2b9b8d8f89f2f99d',
        'size_mb': 142
    },
    'small.en': {
        'url': 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin',
        'md5': '55356645c8fc6c9ae5d39c2b56e84f81',
        'size_mb': 466
    },
    'small': {
        'url': 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin',
        'md5': '55356645c8fc6c9ae5d39c2b56e84f81',
        'size_mb': 466
    },
    'medium.en': {
        'url': 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.en.bin',
        'md5': '8c30f0e44ce9ab2b0b7374e66e7edc2f',
        'size_mb': 1500
    },
    'medium': {
        'url': 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin',
        'md5': '8c30f0e44ce9ab2b0b7374e66e7edc2f',
        'size_mb': 1500
    },
    'large-v1': {
        'url': 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v1.bin',
        'md5': 'b1caaf735c4cc1429223d5a74f0f4d0a',
        'size_mb': 2950
    },
    'large-v2': {
        'url': 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v2.bin',
        'md5': '9c9e5a8a0a385c6a2a2c9acc84782f15',
        'size_mb': 2950
    },
    'large-v3': {
        'url': 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin',
        'md5': '196f17d05a26e09098c12e6dc3197a3f',
        'size_mb': 2950
    },
    'large': {
        'url': 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large.bin',
        'md5': '196f17d05a26e09098c12e6dc3197a3f',  # Same as large-v3
        'size_mb': 2950
    },
}

# Função para calcular o hash MD5 de um arquivo
def md5sum(filename):
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()

# Função para baixar um arquivo com barra de progresso
def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        
        with open(local_filename, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=local_filename) as pbar:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

# Função para verificar se o modelo já existe e está correto
def check_model(model_name, models_dir):
    if model_name not in MODEL_URLS:
        print(f"Erro: Modelo '{model_name}' não encontrado.")
        return False
    
    model_path = os.path.join(models_dir, f"ggml-{model_name}.bin")
    
    # Verificar se o arquivo existe
    if not os.path.exists(model_path):
        return False
    
    # Verificar o tamanho do arquivo
    expected_size = MODEL_URLS[model_name]['size_mb'] * 1024 * 1024
    actual_size = os.path.getsize(model_path)
    
    if abs(actual_size - expected_size) > 1024 * 1024:  # Tolerância de 1MB
        print(f"Aviso: Tamanho do arquivo {model_path} é {actual_size} bytes, esperado ~{expected_size} bytes.")
        return False
    
    # Verificar o hash MD5
    expected_md5 = MODEL_URLS[model_name]['md5']
    actual_md5 = md5sum(model_path)
    
    if actual_md5 != expected_md5:
        print(f"Aviso: Hash MD5 do arquivo {model_path} é {actual_md5}, esperado {expected_md5}.")
        return False
    
    return True

# Função para baixar um modelo
def download_model(model_name, models_dir):
    if model_name not in MODEL_URLS:
        print(f"Erro: Modelo '{model_name}' não encontrado.")
        return False
    
    # Criar diretório de modelos se não existir
    os.makedirs(models_dir, exist_ok=True)
    
    model_info = MODEL_URLS[model_name]
    model_url = model_info['url']
    model_path = os.path.join(models_dir, os.path.basename(model_url))
    
    # Verificar se o modelo já existe e está correto
    if check_model(model_name, models_dir):
        print(f"Modelo '{model_name}' já existe e está correto.")
        return True
    
    # Baixar o modelo
    print(f"Baixando modelo '{model_name}' ({model_info['size_mb']} MB)...")
    try:
        download_file(model_url, model_path)
    except Exception as e:
        print(f"Erro ao baixar modelo: {e}")
        return False
    
    # Verificar o hash MD5
    expected_md5 = model_info['md5']
    actual_md5 = md5sum(model_path)
    
    if actual_md5 != expected_md5:
        print(f"Aviso: Hash MD5 do arquivo {model_path} é {actual_md5}, esperado {expected_md5}.")
        print("O arquivo pode estar corrompido ou incompleto.")
        return False
    
    print(f"Modelo '{model_name}' baixado com sucesso.")
    return True

# Função para listar modelos disponíveis
def list_models():
    print("Modelos disponíveis:")
    print("{:<10} {:<10} {:<10}".format("Modelo", "Tamanho", "Descrição"))
    print("-" * 50)
    
    for model_name, model_info in config.AVAILABLE_MODELS.items():
        print("{:<10} {:<10} {:<10}".format(
            model_name,
            model_info['size'],
            model_info['description']
        ))

# Função principal
def main():
    parser = argparse.ArgumentParser(description='Download de modelos para whisper.cpp')
    parser.add_argument('--list', action='store_true', help='Listar modelos disponíveis')
    parser.add_argument('--model', type=str, help='Nome do modelo para baixar')
    parser.add_argument('--all', action='store_true', help='Baixar todos os modelos')
    parser.add_argument('--dir', type=str, default=config.MODELS_DIR, help='Diretório para salvar os modelos')
    
    args = parser.parse_args()
    
    if args.list:
        list_models()
        return
    
    if args.all:
        print("Baixando todos os modelos...")
        for model_name in MODEL_URLS.keys():
            download_model(model_name, args.dir)
        return
    
    if args.model:
        download_model(args.model, args.dir)
        return
    
    # Se nenhuma opção for especificada, mostrar ajuda
    parser.print_help()

if __name__ == '__main__':
    main()