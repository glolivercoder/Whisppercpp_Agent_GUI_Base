@echo off
REM Script para iniciar o agente Whisper com testes e logs.

echo Iniciando o Agente Whisper...
echo.

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
CALL Whisper_Python\venv\Scripts\activate.bat
if errorlevel 1 (
    echo Erro ao ativar o ambiente virtual.
    pause
    exit /b 1
)
echo.

REM Executar testes
echo Executando testes...
REM -- Nenhum arquivo de teste foi encontrado. --
REM -- Adicione seu comando para rodar os testes aqui. Exemplo: python -m pytest Whisper_Python/tests/ --log-file=test_log.txt --
echo (Placeholder para comando deteste)
echo.

REM Iniciar a aplicacao com log
echo Iniciando a aplicacao e gerando log em app.log...
Whisper_Python\venv\Scripts\python.exe Whisper_Python\run.py > app.log 2>&1
echo.

echo O agente foi iniciado. Verifique o arquivo app.log para mais detalhes.
pause
