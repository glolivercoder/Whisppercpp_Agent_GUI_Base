@echo off
REM Script para iniciar o agente Whisper com ambiente virtual no Windows

cd /d "%~dp0"

echo Iniciando agente Whisper...
echo.

REM Verificar se o ambiente virtual existe
if not exist venv (
    echo Criando ambiente virtual Python...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo Erro ao criar ambiente virtual. Verifique se o Python esta instalado corretamente.
        pause
        exit /b 1
    )
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo Erro ao ativar ambiente virtual.
    pause
    exit /b 1
)

REM Instalar/atualizar dependencias
echo Verificando e instalando dependencias...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Erro ao instalar dependencias.
    pause
    exit /b 1
)

REM Verificar se ha modelos disponiveis
if not exist models\*.bin (
    echo Nenhum modelo encontrado.
    echo Deseja baixar o modelo 'base'? (S/N)
    set /p download_model=
    if /i "%download_model%"=="S" (
        echo Baixando modelo 'base'...
        python -c "from models.download import download_model; download_model('base')"
        if %ERRORLEVEL% neq 0 (
            echo Erro ao baixar o modelo.
            pause
            exit /b 1
        )
    )
)

REM Iniciar a aplicacao
echo.
echo Iniciando servidor web...
echo Pressione Ctrl+C para encerrar o servidor.
echo.
python run.py

REM Desativar ambiente virtual ao sair
call venv\Scripts\deactivate.bat

pause