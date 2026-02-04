# Nado Trading Bot - On-Chain Analysis & Volume Trading

## Visão Geral
Bot de trading que usa dados on-chain da DEX Nado para análise técnica multi-timeframe e execução de ordens de volume.

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│              Nado DEX (On-Chain)               │
│  ├─ Preços de pares (SOL/USDC, etc.)    │
│  ├─ Volume de trading                         │
│  ├─ Profundidade de ordens (order book)      │
│  └─ TVL de pools                             │
└─────────────────────────────────────────────────────────┘
                      ↓
        On-Chain Data Collector (Python + CCXT)
                      ↓
        ┌──────────────────────────────┐
        │ Multi-Timeframe Analyzer    │
        │  5m  │  15m  │  30m   │
        │  RSI  │  EMAs  │  MACD   │
        └──────────────────────────────┘
                      ↓
        ┌──────────────────────────────┐
        │   Trading Bot Engine      │
        │  - Detectar oportunidades   │
        │  - Gerenciar risco        │
        │  - Executar ordens       │
        └──────────────────────────────┘
                      ↓
              Autenticação Wallet (Assinatura)
                      ↓
        ┌──────────────────────────────┐
        │      Nado DEX             │
        │  (Ordens On-Chain)       │
        └──────────────────────────────┘
```

## Stack Tecnológica

- **Python 3.10+**
- **CCXT** - Integração com Nado DEX
- **Pandas/Numpy** - Análise de dados
- **TA-Lib/Pandas-TA** - Indicadores técnicos
- **Web3.py** - Interagir com smart contracts (opcional)
- **Python-Ed25519** - Assinar transações (Ed25519)

## Componentes

### 1. nado_data_collector.py
Coleta dados on-chain da Nado DEX:
- Preços OHLCV (Open, High, Low, Close, Volume)
- Order book depth
- TVL de pools
- Tokenomics (supply, staking)

### 2. nado_multi_timeframe.py
Análise técnica em múltiplos timeframes:
- 5m: Scalping ultra-rápido
- 15m: Scalping rápido
- 30m: Day trading rápido

Indicadores calculados:
- RSI (7, 14, 21)
- EMAs (7, 20, 50)
- MACD
- Bollinger Bands
- Volume Profile

### 3. nado_trading_bot.py
Bot de trading que:
- Monitora pares em múltiplos timeframes
- Detecta padrões de entrada
- Gerencia positions
- Executa ordens de volume na Nado DEX
- Gerencia risco (stop loss, take profit)

## Autenticação Nado

Nado usa **wallet-based authentication**:

### Opções de Autenticação

#### Opção 1: Wallet Local (Recomendado)
```python
from eth_account import Account
from eth_keys import keys

# Carregar chave privada
private_key = keys.from_hex("SUAPRIVATEKEY")
account = Account.from_key(private_key)

# Assinar transação
signed_tx = account.sign_transaction(transaction)
```

#### Opção 2: Subaccount (Nativo Nado)
```python
import nado_sdk

# Criar subaccount
subaccount = nado_sdk.create_subaccount(
    parent_account=main_account,
    name="trading_bot_1"
)
```

### Segurança

⚠️ **CRITICAL:**
- NUNCA commitar chaves privadas em repositórios públicos
- Usar variáveis de ambiente ou arquivo `.env`
- Guardar chaves em lugar seguro (hardware wallet, etc.)

## Setup Inicial

### 1. Instalar Dependências
```bash
pip install ccxt pandas numpy ta-lib pandas-ta python-dotenv web3 eth-account
```

### 2. Configurar Ambiente
```bash
cd /root/.openclaw/workspace/nado-trading-bot
cp .env.example .env
# Editar .env com suas credenciais
```

### 3. Estrutura de Diretórios
```
nado-trading-bot/
├── .env                    # Credenciais (não commitar)
├── nado_data_collector.py
├── nado_multi_timeframe.py
├── nado_trading_bot.py
├── config.py               # Configurações do bot
├── utils/
│   ├── indicators.py       # Funções de indicadores
│   ├── nado_sdk.py       # Wrapper SDK Nado
│   └── wallet.py         # Funções de wallet
└── logs/                    # Logs de trades
```

## Funcionalidades Principais

### Data Collection
- ✅ Preços OHLCV em tempo real
- ✅ Order book depth (até 20 níveis)
- ✅ Volume de trading por par
- ✅ TVL dos principais pools
- ✅ Tokenomics (circulating supply, etc.)

### Multi-Timeframe Analysis
- ✅ Análise simultânea em 5m, 15m, 30m
- ✅ Indicadores técnicos completos
- ✅ Detecção de padrões
- ✅ Alertas de setup

### Trading Bot
- ✅ Monitorar múltiplos pares simultaneamente
- ✅ Executar ordens de volume (maker/taker)
- ✅ Gerenciar múltiplos positions
- ✅ Stop loss e take profit dinâmicos
- ✅ Risk management baseado em ATR

## Exemplo de Uso

### Coletar Dados
```bash
python nado_data_collector.py --pairs SOL/USDC,ETH/USDC --timeframes 5m,15m,30m
```

### Rodar Análise
```bash
python nado_multi_timeframe.py --pair SOL/USDC --timeframes 5m,15m,30m
```

### Iniciar Bot de Trading
```bash
python nado_trading_bot.py --config config.json
```

## Próximos Passos

1. ⚙️ Configurar arquivo `.env` com credenciais
2. 📊 Implementar `nado_data_collector.py`
3. 📈 Implementar `nado_multi_timeframe.py`
4. 🤖 Implementar `nado_trading_bot.py`
5. 🧪 Testar com dados históricos (backtesting)
6. 🚀 Testar em ambiente real (paper trading)

## Referências

- Nado Docs: https://docs.nado.xyz
- CCXT Nado: https://docs.ccxt.com/en/latest/ccxt/exchange_class/nado
- Dune Analytics: https://dune.com/

## Aviso Importante

Este bot usa fundos reais em criptoativos. Teste extensivamente antes de usar em produção. Sempre:

- ✅ Começar com capital mínimo
- ✅ Usar position sizing conservador
- ✅ Ter stop loss sempre ativo
- ✅ Monitorar positions 24/7
- ❌ Nunca arriscar mais do que pode perder

## Suporte

Para dúvidas ou problemas:
- Verificar logs em `logs/`
- Revisar documentação do Nado
- Consultar CCXT docs
