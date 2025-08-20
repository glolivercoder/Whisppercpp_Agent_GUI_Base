@echo off
ECHO "Iniciando ambiente virtual..."
CALL venv\Scripts\activate.bat

ECHO "Iniciando aplicacao TempoReal_Karaoke..."
cd TempoReal_Karaoke

ECHO "Gravando logs em TEMPOREAL_KARAOKE.log"
python app.py > TEMPOREAL_KARAOKE.log 2>&1