@echo off
REM Script para iniciar a aplicação Whisper.cpp Web App no Windows

cd /d "%~dp0"

echo Iniciando Whisper.cpp Web App...
echo.

REM Verificar se o ambiente virtual existe
if not exist venv (
    echo Criando ambiente virtual Python...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo Erro ao criar ambiente virtual. Verifique se o Python está instalado corretamente.
        pause
        exit /b 1
    )
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instalar dependências se necessário
if not exist venv\Lib\site-packages\flask (
    echo Instalando dependências...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo Erro ao instalar dependências.
        pause
        exit /b 1
    )
)

REM Verificar se há modelos disponíveis
if not exist models\*.bin (
    echo Nenhum modelo encontrado. Deseja baixar o modelo 'base'? (S/N)
    set /p download_model=
    if /i "%download_model%"=="S" (
        echo Baixando modelo 'base'...
        python models\download.py base
        if %ERRORLEVEL% neq 0 (
            echo Erro ao baixar o modelo.
            pause
            exit /b 1
        )
    )
)

REM Iniciar a aplicação
echo.
echo Iniciando servidor web...
echo Pressione Ctrl+C para encerrar o servidor.
echo.
python run.py

REM Desativar ambiente virtual ao sair
call venv\Scripts\deactivate.bat

pause