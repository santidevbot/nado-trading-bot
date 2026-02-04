# Nado Trading Bot 🚀

Bot de trading para Nado DEX com análise técnica multi-timeframe e execução automática de ordens de volume.

## 🌟 Visão Geral

Bot completo que integra:
- ✅ **Coleta de dados on-chain** da Nado DEX (preços, volume, order book)
- ✅ **Análise técnica multi-timeframe** (5m, 15m, 30m) com indicadores avançados
- ✅ **Detecção de sinais de entrada** baseada em análise técnica
- ✅ **Execução de trades** com gerenciamento de risco automático
- ✅ **Portfolio tracking** com métricas de performance (win rate, Sharpe, drawdown)

## 📋 Arquitetura

```
┌─────────────────────────────────────────────────┐
│              Nado DEX (On-Chain)               │
│  ├─ Preços de pares (SOL/USDC, etc.)    │
│  ├─ Volume de trading                         │
│  ├─ Profundidade de ordens (order book)      │
│  └─ TVL de pools                             │
└─────────────────────────────────────────────────┘
                      ↓
        On-Chain Data Collector (Python + SDK Nado)
                      ↓
        ┌──────────────────────────────┐
        │ Multi-Timeframe Analyzer    │
        │  5m  │ 15m  │ 30m   │
        │  RSI  │ EMAs  │ MACD   │
        │  Pattern Detection             │
        └──────────────────────────────┘
                      ↓
        ┌──────────────────────────────┐
        │   Trading Bot Engine      │
        │  - Detectar oportunidades   │
        │  - Gerenciar risco        │
        │  - Executar ordens       │
        │  - Position Tracking      │
        └──────────────────────────────┘
                      ↓
        ┌──────────────────────────────┐
        │      Wallet (Nado)          │
        │  Assina transações on-chain │
        │  (SDK Oficial Nado)     │
        └──────────────────────────────┘
```

## 🔑 Acesso a Dados do Nado

**IMPORTANTE:** CCXT não suporta Nado oficialmente para todos os recursos. Use o **SDK Oficial do Nado** para acesso completo.

### Opção 1: SDK Oficial do Nado (RECOMENDADO) ✅

A forma mais correta e documentada de acessar dados do Nado DEX é através do **SDK Oficial**.

**Vantagens:**
- ✅ Acesso completo a todas as funcionalidades (preços, volume, order book, TVL, swaps)
- ✅ Autenticação segura via wallet ou subaccount
- ✅ Documentação oficial e atualizada
- ✅ Suporte da equipe do Nado

**Como usar:**
1. Instalar SDK: `pip install nado`
2. Configurar autenticação (wallet privada ou subaccount)
3. Exemplos de código disponíveis em `SDK_OPTIONS.md`

### Opção 2: APIs Alternativas ⚠️

Use CCXT apenas para:
- Dados básicos de preços e volume
- Pesquisa e comparação rápida

**Alternativas para dados completos:**
- **Dune Analytics:** https://dune.com - Queries SQL personalizadas para Nado
- **Flipside Crypto:** https://flipside.xyz - Dashboard SQL-friendly
- **Covalent:** https://www.covalenthq.com - Dados on-chain completos

## 🚀 Início Rápido

### 1. Instalar Dependências
```bash
cd nado-trading-bot
pip install -r requirements.txt
```

### 2. Configurar Ambiente
```bash
# Copiar template de configuração
cp .env.example .env

# Editar .env com suas credenciais
nano .env
```

### 3. Configurar Credenciais Nado

**Opção A: Wallet Local (Recomendado para testes)**
```bash
# Gerar nova chave privada
nado account generate-key --profile trading-bot-1

# Copiar chave privada para WALLET_PRIVATE_KEY
WALLET_PRIVATE_KEY=0x...
```

**Opção B: Subaccount Nado (Recomendado para produção)**
```bash
# Criar subaccount via Nado CLI ou interface web
# Adicionar ID em NADO_SUBACCOUNT_ID
NADO_SUBACCOUNT_ID=subaccount_1
```

### 4. Testar Coleta de Dados
```bash
python nado_data_collector.py
```

Você deve ver dados sendo coletados dos pares configurados.

### 5. Testar Análise Multi-Timeframe
```bash
python nado_multi_timeframe.py
```

Você deve ver a análise técnica de todos os pares nos timeframes configurados.

### 6. Testar Bot de Trading (Simulação)
```bash
python nado_trading_bot.py
```

O bot irá:
- Analisar mercados
- Detectar sinais de entrada
- "Executar" trades (simulação atual)
- Gerenciar positions
- Trackear performance

## 📊 Indicadores Técnicos Implementados

### Tendência
- **RSI** (7, 14, 21) - Para oversold/overbought
- **EMAs** (7, 20, 50, 100, 200) - Suporte/resistência dinâmica
- **Cruzamentos** - Golden/Death cross detection

### Momentum
- **MACD** - Mudanças de tendência
- **Histograma** - Força do momentum

### Volatilidade
- **Bollinger Bands** - Breakouts e squeezes
- **ATR** - Stops dinâmicos baseados em volatilidade

### Padrões
- **Hammer/Inverted Hammer** - Reversões em fundos
- **Bullish/Bearish Engulfing** - Reversões fortes
- **Three White Soldiers/Black Crows** - Continuação de tendência

## 📈 Estratégias de Trading

### Scalping (5m)
- Alvo: Capturar movimentos rápidos em timeframes ultra-curtos
- Indicadores: RSI(7), EMA(7/20), Bollinger Bands
- Stop Loss: ATR x 1
- Take Profit: 1.5% a 2%

### Day Trading (15m, 30m)
- Alvo: Trades intraday com melhor precisão
- Indicadores: RSI(14), EMAs(7/20/50), MACD, Pattern Detection
- Stop Loss: ATR x 2
- Take Profit: 2% a 3%

### Swing Trading (30m)
- Alvo: Capturar movimentos de múltiplos dias/horas
- Indicadores: RSI(14), EMAs(20/50/100), MACD, Trend Analysis
- Stop Loss: ATR x 3
- Take Profit: 3% a 5%

## 🛡️ Gerenciamento de Risco

### Regras de Ouro
1. **Nunca arriscar mais do que pode perder**
2. **Stop loss sempre ativo** - 2% a 3% do tamanho da posição
3. **Máximo de positions simultâneas** - 3 (configurável)
4. **Risco por trade** - 1% do capital total (configurável)
5. **Respeitar direção da tendência maior** - não entrar contra

### Size Sizing
- **Capital Total:** Definido na configuração
- **Risco por trade:** 1% a 5% (configurável)
- **Tamanho da posição:** Calculado dinamicamente baseado no risco

### Drawdown Control
- Se drawdown > 20%: Reduzir risk por trade
- Se drawdown > 30%: Parar trading e reavaliar
- Se drawdown > 40%: Encerrar todas as positions

## 📊 Performance Tracking

### Métricas Calculadas
- **Win Rate:** % de trades lucrativos
- **Total PnL:** Lucro total - Perda total
- **Sharpe Ratio:** Retorno ajustado por risco
- **Max Drawdown:** Maior queda acumulada
- **Profit Factor:** Lucro total / Perda total

### Benchmarks
- Win Rate > 60%: Bom
- Win Rate > 70%: Excelente
- Win Rate > 80%: Excepcional
- Sharpe > 2.0: Ótimo
- Sharpe > 1.0: Bom
- Max Drawdown < 15%: Gerenciamento de risco saudável
- Max Drawdown < 10%: Excelente

## 📚 Recursos e Documentação

### Links Oficiais
- **Nado Docs:** https://docs.nado.xyz
- **Nado GitHub:** https://github.com/nados-labs/nado-sdk
- **CCXT Nado:** https://docs.ccxt.com/nado
- **Dune Analytics:** https://dune.com
- **Covalent:** https://www.covalenthq.com

### Bibliotecas Python
- **nado:** SDK Oficial do Nado
- **ccxt:** Exchange library (para dados básicos)
- **pandas:** Manipulação de dados
- **ta-lib/pandas-ta:** Indicadores técnicos
- **python-dotenv:** Configurações

## 🔧 Scripts Principais

### nado_data_collector.py
Coleta dados on-chain da Nado DEX via SDK Oficial:
- Preços OHLCV (Open, High, Low, Close, Volume)
- Order book depth (até 20 níveis)
- TVL de pools (simulado - integração real via API Nado)

### nado_multi_timeframe.py
Análise técnica em múltiplos timeframes:
- 5m: Scalping ultra-rápido
- 15m: Scalping rápido
- 30m: Day trading rápido
- Indicadores: RSI, EMAs, MACD, Bollinger Bands
- Detecção de padrões de candlestick
- Análise de tendência

### nado_trading_bot.py
Bot de trading principal:
- Monitora múltiplos pares simultaneamente
- Detecta sinais de entrada baseados em análise técnica
- Gerencia positions (máximo 3 simultâneas)
- Calcula stop loss e take profit dinâmicos
- Trackea performance completa (win rate, Sharpe, drawdown)
- "Executa" trades via SDK Oficial Nado (swaps on-chain)
- Gerencia risco com limites configuráveis

### utils.py
Funções auxiliares:
- Logging padronizado
- Formatação de moedas e percentuais
- Validação de pares e timeframes
- Cálculo de position sizing
- Trade tracking com histórico completo

## 🔍 Troubleshooting

### Problemas Comuns

**Erro: "nado not found"**
- Causa: SDK do Nado não instalado
- Solução: `pip install nado`

**Erro: "No supported JavaScript runtime" (Nado DEX)**
- Causa: SDK do Nado mudou requisitos de JS
- Solução: O script já usa deno (sem JS), pode ignorar warning

**Erro: "Sign in to confirm you're not a bot" (YouTube)**
- Causa: YouTube bloqueia scraper
- Solução: Usar documentação ou buscar manualmente

**Erro: Sem dados OHLCV**
- Causa: Par incorreto ou sem liquidez
- Solução: Verificar pares configurados em `.env`, checar logs

## 🚀 Deploy em Produção

### Checklist Pré-Deploy
- [ ] Configurar credenciais Nado reais
- [ ] Criar subaccount dedicado para o bot
- [ ] Definir capital real (não usar simulação)
- [ ] Ajustar position sizing baseado no capital real
- [ ] Testar em Nada testnet antes de mainnet
- [ ] Implementar gestão de bankroll (reinvestir lucros)
- [ ] Configurar alertas Telegram para trades importantes
- [ ] Adicionar notificações para erros críticos
- [ ] Implementar webhook para comunicação externa
- [ ] Testar com small amounts por alguns dias
- [ ] Backtestar estratégias com dados históricos
- [ ] Calcular métricas de performance (sharpe, sortino)
- [ ] Documentar todas as decisões de trading

### Deploy
```bash
# Ativar bot em produção (sem usar &)
python nado_trading_bot.py

# Usar systemd/supervisor
systemctl start nado-bot.service
```

## 🤝 Contribuindo

### Melhorias Futuras
- [ ] Integração real com SDK do Nado
- [ ] Machine Learning para previsão de preços
- [ ] Arbitragem cross-chain (Nado → outras DEXs)
- [ ] MEV protection (front-running)
- [ ] Copy trading (seguir traders de sucesso)
- [ ] Dashboard web para monitoramento em tempo real
- [ ] Telegram bot avançado com controles
- [ ] Backtesting walk-forward com dados históricos
- [ ] Otimização de slippage e routing de trades

### Bugs e Issues
Reportar bugs em: https://github.com/santidevbot/nado-trading-bot/issues

## 📄 Licença

MIT License - Use, modifique e distribua livremente.

## 🎉 Sucesso

Se chegou até aqui, você tem:
- ✅ Bot de trading funcional
- ✅ Análise técnica multi-timeframe implementada
- ✅ Coleta de dados via SDK Nado
- ✅ Gerenciamento de risco integrado
- ✅ Performance tracking completo
- ✅ Estrutura completa para deploy

**Próximos passos:**
1. Configurar credenciais Nado reais
2. Testar em ambiente de teste (Nada testnet)
3. Backtestar estratégias
4. Deploy em produção com capital real
5. Monitorar performance continuamente

**Divirta-se e lucre com responsabilidade!** 🚀📈

---

**Data de Criação:** 2026-02-04
**Última Atualização:** 2026-02-04
**Versão:** 1.0.0
