# Whisper.cpp Web App

Uma aplicação web para transcrição de áudio para texto usando o [whisper.cpp](https://github.com/ggerganov/whisper.cpp), uma implementação em C/C++ de alta performance do modelo Whisper da OpenAI para reconhecimento automático de fala (ASR).

## Características

- Interface web amigável usando Flask, HTML, CSS e JavaScript
- Gravação de áudio diretamente do microfone
- Upload de arquivos de áudio em diversos formatos
- Visualização de forma de onda do áudio
- Seleção de diferentes modelos do Whisper (tiny, base, small, medium, large)
- Suporte a múltiplos idiomas com detecção automática
- Opção de tradução para inglês
- Timestamps por palavra ou por segmento
- Histórico de transcrições

## Requisitos

- Python 3.8 ou superior
- whisper.cpp compilado (executável principal)
- FFmpeg instalado e disponível no PATH
- Navegador web moderno com suporte a MediaRecorder API

## Instalação

### 1. Clone o repositório whisper.cpp (se ainda não tiver)

```bash
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
```

### 2. Compile o whisper.cpp

**Windows:**
```bash
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

**Linux/macOS:**
```bash
make
```

### 3. Configure o ambiente Python

```bash
cd Whisper_Python
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 4. Baixe os modelos

```bash
python models/download.py base
```

Você pode substituir `base` por `tiny`, `small`, `medium` ou `large` dependendo das suas necessidades e recursos disponíveis.

### 5. Configure o caminho para o executável whisper.cpp

Edite o arquivo `config.py` e ajuste o caminho `WHISPER_CPP_PATH` para apontar para o executável whisper.cpp compilado.

## Uso

### Iniciar o servidor

```bash
python run.py
```

Por padrão, o servidor será iniciado em `http://127.0.0.1:5000`.

Opções adicionais:
- `--host`: Especificar o endereço IP (ex: `0.0.0.0` para acesso externo)
- `--port`: Especificar a porta (ex: `8080`)
- `--debug`: Executar em modo de depuração

Exemplo:
```bash
python run.py --host 0.0.0.0 --port 8080 --debug
```

### Usando a aplicação

1. Abra o navegador e acesse `http://127.0.0.1:5000` (ou o endereço configurado)
2. Escolha entre gravar áudio ou fazer upload de um arquivo
3. Selecione o modelo, idioma e outras opções de transcrição
4. Clique em "Transcrever" para iniciar o processo
5. Visualize o resultado da transcrição

## Estrutura do Projeto

```
Whisper_Python/
├── app.py                 # Aplicação Flask principal
├── config.py              # Configurações da aplicação
├── run.py                 # Script de inicialização
├── MEMO.json              # Documentação do whisper.cpp
├── requirements.txt       # Dependências Python
├── models/
│   ├── download.py        # Script para download de modelos
│   └── ...                # Modelos baixados (.bin)
├── static/
│   ├── css/
│   │   └── style.css      # Estilos CSS
│   ├── js/
│   │   └── app.js         # JavaScript da aplicação
│   └── temp/              # Arquivos temporários
├── templates/
│   ├── layout.html        # Template base
│   ├── index.html         # Página principal
│   └── about.html         # Página sobre
├── uploads/               # Arquivos de áudio enviados
├── transcriptions/        # Resultados de transcrições
└── utils/
    ├── __init__.py        # Inicialização do pacote
    ├── audio.py           # Processamento de áudio
    └── whisper_wrapper.py # Wrapper para whisper.cpp
```

## Otimizações

O whisper.cpp oferece várias otimizações que podem ser habilitadas durante a compilação:

- **BLAS**: Acelera operações de álgebra linear (`make WHISPER_CUBLAS=1`)
- **CUDA**: Suporte a GPUs NVIDIA (`make WHISPER_CUBLAS=1`)
- **Vulkan**: Suporte a GPUs diversas (`make WHISPER_VULKAN=1`)
- **OpenVINO**: Aceleração em Intel GPUs (`make WHISPER_OPENVINO=1`)
- **Core ML**: Aceleração no Apple Neural Engine (`make WHISPER_COREML=1`)

Consulte a [documentação do whisper.cpp](https://github.com/ggerganov/whisper.cpp) para mais detalhes sobre otimizações disponíveis.

## Licença

Este projeto segue a mesma licença do whisper.cpp (MIT).

## Agradecimentos

- [OpenAI](https://openai.com/) pelo modelo Whisper
- [Georgi Gerganov](https://github.com/ggerganov) pelo whisper.cpp