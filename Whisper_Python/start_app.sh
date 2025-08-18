#!/bin/bash
# Script para iniciar a aplicação Whisper.cpp Web App em Linux/macOS

echo "Iniciando Whisper.cpp Web App..."
echo

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual Python..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Erro ao criar ambiente virtual. Verifique se o Python está instalado corretamente."
        read -p "Pressione Enter para continuar..."
        exit 1
    fi
fi

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências se necessário
if [ ! -d "venv/lib/python*/site-packages/flask" ]; then
    echo "Instalando dependências..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Erro ao instalar dependências."
        read -p "Pressione Enter para continuar..."
        exit 1
    fi
fi

# Verificar se há modelos disponíveis
if [ ! -f "models"/*.bin ]; then
    echo "Nenhum modelo encontrado. Deseja baixar o modelo 'base'? (S/N)"
    read download_model
    if [[ "$download_model" =~ ^[Ss]$ ]]; then
        echo "Baixando modelo 'base'..."
        python models/download.py base
        if [ $? -ne 0 ]; then
            echo "Erro ao baixar o modelo."
            read -p "Pressione Enter para continuar..."
            exit 1
        fi
    fi
fi

# Iniciar a aplicação
echo
echo "Iniciando servidor web..."
echo "Pressione Ctrl+C para encerrar o servidor."
echo
python run.py

# Desativar ambiente virtual ao sair
deactivate

read -p "Pressione Enter para continuar..."