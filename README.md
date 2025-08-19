# PerfectPay QR Code PIX Generator

Ferramenta automatizada para gerar códigos PIX através do sistema Perfect Pay, incluindo captura e salvamento das imagens dos QR Codes.

## 🚀 Instalação

### 1. Instalar uv

Primeiro, instale o `uv` seguindo a [documentação oficial](https://docs.astral.sh/uv/getting-started/installation/):

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Instalar dependências

```bash
uv sync
```

### 3. Configurar variáveis de ambiente

```bash
copy env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
PERFECTPAY_CHECKOUT_URL=https://checkout.perfectpay.com.br/pay/{id}
```

## 📋 Como Usar

### Execução Básica

```bash
uv run app.py
```

### Parâmetros da Função

A função `generate_pix()` requer os seguintes parâmetros:

```python
qr_code = generator.generate_pix(
    email="cliente@exemplo.com",      # Email do cliente
    name="Nome Completo",             # Nome do cliente
    phone="11999999999",              # Telefone (apenas números)
    cpf="12345678901"                 # CPF (apenas números)
)
```

**Exemplo de uso:**

```python
# Dados de teste fictícios
# Foram gerados no https://www.4devs.com.br/gerador_de_pessoas

qr_code = generator.generate_pix(
    email="iago.heitor.souza@inglesasset.com.br",
    name="Iago Heitor Souza",
    phone="95997984584",
    cpf="25252856974"
)
```

### Configuração

As configurações são feitas através do arquivo `.env`:

- `PERFECTPAY_CHECKOUT_URL`: URL do checkout Perfect Pay

### Estrutura do Projeto

```markdown
perfectpay-generate-QrCodePix/
├── app.py                 # Arquivo principal de execução
├── config/
│   └── config.py         # Configurações do projeto
├── generate/
│   └── qrcode_pix.py     # Classe principal de geração
├── logs/                 # Arquivos de log (criado automaticamente)
├── images/               # Imagens dos QR Codes (criado automaticamente)
│   └── prints/          # Screenshots de debug
└── pyproject.toml        # Dependências do projeto
```

## 🔧 Funcionalidades

- ✅ Geração automática de códigos PIX
- ✅ Captura e salvamento das imagens dos QR Codes
- ✅ Logs detalhados das operações
- ✅ Screenshots automáticos em caso de erro
- ✅ Configuração anti-detecção do Selenium

## 📁 Arquivos Gerados

- **QR Codes**: `images/qrcode_pix_{CPF}_{timestamp}.png`
- **Screenshots**: `images/prints/{tipo}_{timestamp}.png`
- **Logs**: `logs/generate_qrcode_pix.log`

## ⚠️ Requisitos

- Python 3.12+
- Chrome/Chromium instalado
- Dados válidos do cliente (email, nome, telefone, CPF)

## 🐛 Solução de Problemas

Se encontrar erros:

1. Verifique se o Chrome está instalado
2. Confirme se o arquivo `.env` está configurado corretamente
3. Verifique os logs em `logs/generate_qrcode_pix.log`
4. Screenshots de erro são salvos em `images/prints/`
