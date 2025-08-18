import os
import sys
import json
import subprocess
import logging
from typing import Dict, List, Optional, Union, Tuple

# Adicionar o diretório pai ao path para importar config.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WhisperWrapper:
    """Wrapper para o whisper.cpp"""
    
    def __init__(self, executable_path: str = None, models_dir: str = None):
        """Inicializa o wrapper para o whisper.cpp
        
        Args:
            executable_path: Caminho para o executável whisper.cpp
            models_dir: Diretório onde os modelos estão armazenados
        """
        self.executable_path = executable_path or config.WHISPER_EXECUTABLE
        self.models_dir = models_dir or config.MODELS_DIR
        
        # Verificar se o executável existe
        if not os.path.exists(self.executable_path):
            logger.warning(f"Executável whisper.cpp não encontrado em: {self.executable_path}")
        
        # Verificar se o diretório de modelos existe
        if not os.path.exists(self.models_dir):
            logger.warning(f"Diretório de modelos não encontrado: {self.models_dir}")
            os.makedirs(self.models_dir, exist_ok=True)
    
    def check_executable(self) -> bool:
        """Verifica se o executável whisper.cpp está disponível
        
        Returns:
            bool: True se o executável existe, False caso contrário
        """
        return os.path.exists(self.executable_path)
    
    def list_models(self) -> List[Dict[str, str]]:
        """Lista os modelos disponíveis no diretório de modelos
        
        Returns:
            List[Dict[str, str]]: Lista de modelos disponíveis com informações
        """
        models = []
        
        if not os.path.exists(self.models_dir):
            logger.warning(f"Diretório de modelos não encontrado: {self.models_dir}")
            return models
        
        # Verificar quais modelos estão disponíveis
        for model_name, model_info in config.AVAILABLE_MODELS.items():
            model_path = os.path.join(self.models_dir, model_info['file'])
            
            if os.path.exists(model_path):
                models.append({
                    'name': model_name,
                    'file': model_info['file'],
                    'size': model_info['size'],
                    'memory': model_info['memory'],
                    'description': model_info['description'],
                    'path': model_path
                })
        
        return models
    
    def get_model_path(self, model_name: str) -> Optional[str]:
        """Obtém o caminho para um modelo específico
        
        Args:
            model_name: Nome do modelo (tiny, base, small, medium, large)
            
        Returns:
            Optional[str]: Caminho para o modelo ou None se não encontrado
        """
        if model_name not in config.AVAILABLE_MODELS:
            logger.error(f"Modelo não reconhecido: {model_name}")
            return None
        
        model_file = config.AVAILABLE_MODELS[model_name]['file']
        model_path = os.path.join(self.models_dir, model_file)
        
        if not os.path.exists(model_path):
            logger.error(f"Arquivo de modelo não encontrado: {model_path}")
            return None
        
        return model_path
    
    def transcribe(self, 
                  audio_path: str, 
                  model_name: str = 'base', 
                  language: Optional[str] = None,
                  translate: bool = False,
                  output_format: str = 'text',
                  word_timestamps: bool = False,
                  **kwargs) -> Dict[str, Union[str, List, Dict]]:
        """Transcreve um arquivo de áudio usando whisper.cpp
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            model_name: Nome do modelo a ser usado (tiny, base, small, medium, large)
            language: Código do idioma (opcional, auto-detecção se None)
            translate: Se True, traduz para inglês
            output_format: Formato de saída (text, vtt, srt, json)
            word_timestamps: Se True, inclui timestamps por palavra
            **kwargs: Argumentos adicionais para o whisper.cpp
            
        Returns:
            Dict: Resultado da transcrição com texto, segmentos, etc.
        """
        # Verificar se o arquivo de áudio existe
        if not os.path.exists(audio_path):
            logger.error(f"Arquivo de áudio não encontrado: {audio_path}")
            return {"error": "Arquivo de áudio não encontrado"}
        
        # Obter caminho do modelo
        model_path = self.get_model_path(model_name)
        if not model_path:
            return {"error": f"Modelo '{model_name}' não encontrado ou não disponível"}
        
        # Construir comando base
        cmd = [self.executable_path, '-m', model_path, '-f', audio_path]
        
        # Adicionar opções com base nos argumentos
        if language:
            cmd.extend(['-l', language])
        
        if translate:
            cmd.append('--translate')
        
        if output_format != 'text':
            cmd.extend(['--output-format', output_format])
        
        if word_timestamps:
            cmd.append('--word-timestamps')
        
        # Adicionar argumentos adicionais
        for key, value in kwargs.items():
            if isinstance(value, bool):
                if value:
                    cmd.append(f'--{key.replace("_", "-")}')
            else:
                cmd.extend([f'--{key.replace("_", "-")}', str(value)])
        
        logger.info(f"Executando comando: {' '.join(cmd)}")
        
        try:
            # Executar whisper.cpp
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Erro ao executar whisper.cpp: {stderr}")
                return {"error": "Erro ao processar áudio", "details": stderr}
            
            # Processar saída com base no formato
            if output_format == 'json':
                try:
                    result = json.loads(stdout)
                    return {
                        "text": result.get("text", ""),
                        "segments": result.get("segments", []),
                        "language": result.get("language", language or "auto"),
                        "raw": result
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao decodificar JSON: {e}")
                    return {"error": "Erro ao decodificar saída JSON", "details": str(e)}
            else:
                return {
                    "text": stdout,
                    "format": output_format,
                    "language": language or "auto"
                }
                
        except Exception as e:
            logger.error(f"Erro ao executar whisper.cpp: {e}")
            return {"error": "Erro inesperado", "details": str(e)}
    
    def transcribe_realtime(self, 
                           audio_chunk_path: str, 
                           model_name: str = 'tiny', 
                           language: Optional[str] = None,
                           callback = None) -> Dict[str, Union[str, List, Dict]]:
        """Transcreve um chunk de áudio em tempo real
        
        Args:
            audio_chunk_path: Caminho para o chunk de áudio
            model_name: Nome do modelo a ser usado (tiny, base, small, medium, large)
            language: Código do idioma (opcional, auto-detecção se None)
            callback: Função de callback para receber resultados parciais
            
        Returns:
            Dict: Resultado da transcrição
        """
        # Usar modelo tiny por padrão para transcrição em tempo real (mais rápido)
        return self.transcribe(
            audio_path=audio_chunk_path,
            model_name=model_name,
            language=language,
            output_format='json',
            print_realtime=True,
            print_progress=False,
            no_timestamps=True
        )
    
    def get_version(self) -> str:
        """Obtém a versão do whisper.cpp
        
        Returns:
            str: Versão do whisper.cpp
        """
        if not self.check_executable():
            return "Executável não encontrado"
        
        try:
            result = subprocess.run(
                [self.executable_path, '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao obter versão: {e}")
            return f"Erro: {e.stderr}"
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return f"Erro: {str(e)}"

# Função para criar uma instância do wrapper
def get_whisper_wrapper() -> WhisperWrapper:
    """Cria e retorna uma instância do WhisperWrapper
    
    Returns:
        WhisperWrapper: Instância do wrapper para whisper.cpp
    """
    return WhisperWrapper()

# Exemplo de uso
if __name__ == '__main__':
    # Criar wrapper
    whisper = get_whisper_wrapper()
    
    # Verificar se o executável existe
    if not whisper.check_executable():
        print(f"Executável whisper.cpp não encontrado em: {whisper.executable_path}")
        sys.exit(1)
    
    # Listar modelos disponíveis
    models = whisper.list_models()
    print(f"Modelos disponíveis: {len(models)}")
    for model in models:
        print(f"  - {model['name']} ({model['size']})")
    
    # Verificar versão
    version = whisper.get_version()
    print(f"Versão do whisper.cpp: {version}")