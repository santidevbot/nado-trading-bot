# 🚀 Integração do Decision Engine no Nado Trading Bot

## 📋 Visão Geral

Este documento explica como integrar o algoritmo de tomada de decisão do Backbot no seu Nado DEX Trading Bot.

---

## 🔧 Arquivo: `nado_decision_engine.py`

### Principais Componentes

#### 1. `TimeframeIndicators` (Dataclass)
Guarda todos os indicadores calculados para um timeframe:

```python
@dataclass
class TimeframeIndicators:
    timeframe: str           # '1m', '5m', '15m'
    close: float            # Preço atual
    ema9: float            # EMA curto (tendência rápida)
    ema21: float           # EMA longo (tendência lenta)
    rsi: float             # RSI (0-100)
    macd: float            # MACD line
    macd_signal: float     # MACD signal line
    bollinger_upper: float  # Banda superior
    bollinger_middle: float # Banda média
    bollinger_lower: float  # Banda inferior
    vwap: float            # Volume Weighted Average Price
    volume_trend: str     # 'increasing', 'decreasing', 'flat'
    price_slope: float      # Inclinação do preço
```

#### 2. `NadoDecisionEngine` (Classe Principal)
Motor de decisão com os métodos principais:

| Método | Descrição |
|--------|------------|
| `evaluate_trade_opportunity()` | Avalia um par e decide LONG/SHORT |
| `evaluate_all_pairs()` | Avalia múltiplos pares simultaneamente |
| `score_side()` | Calcula score 0-9 para LONG/SHORT |
| `calculate_entry_price()` | Calcula preço de entrada com slippage |
| `calculate_stop_loss()` | Calcula SL com fees |
| `calculate_take_profit()` | Calcula TP com fees |

---

## 📊 Algoritmo de Decisão (9 Fatores)

### Fatores que Pontuam para LONG:

| # | Fator | Condição | Timeframe |
|---|--------|------------|------------|
| 1 | EMA Tendência | EMA9 > EMA21 | 15m |
| 2 | EMA Curto Prazo | EMA9 > EMA21 | 5m |
| 3 | RSI Momentum | RSI > 55 | 5m |
| 4 | MACD Cruzamento | MACD > Signal | 5m |
| 5 | Bollinger Posição | Preço > BB Middle | 1m |
| 6 | VWAP | Preço > VWAP | 1m |
| 7 | Volume | Trend = increasing | 1m |
| 8 | Price Slope | Slope > 0 | 1m |
| 9 | STACK Confluência | RSI>55 E MACD>Signal E EMA9>EMA21 | 5m |

### Fatores que Pontuam para SHORT:

| # | Fator | Condição | Timeframe |
|---|--------|------------|------------|
| 1 | EMA Tendência | EMA9 < EMA21 | 15m |
| 2 | EMA Curto Prazo | EMA9 < EMA21 | 5m |
| 3 | RSI Momentum | RSI < 45 | 5m |
| 4 | MACD Cruzamento | MACD < Signal | 5m |
| 5 | Bollinger Posição | Preço < BB Middle | 1m |
| 6 | VWAP | Preço < VWAP | 1m |
| 7 | Volume | Trend = increasing | 1m |
| 8 | Price Slope | Slope < 0 | 1m |
| 9 | STACK Confluência | RSI<45 E MACD<Signal E EMA9<EMA21 | 5m |

---

## 🔢 Cálculo de Score

```
scoreSide(isLong) = (pontos_ganhados / 9) * 100

longScore = scoreSide(true)
shortScore = scoreSide(false)

certainty = MAX(longScore, shortScore)
side = longScore > shortScore ? "long" : "short"
```

**Exemplo Prático:**

Se para um par temos:
- LONG Score: 7/9 = 77%
- SHORT Score: 3/9 = 33%

→ Decisão: **LONG** com **77% de certeza**

---

## 💰 Cálculo de Entry, Stop, Target

### Entry Price (com slippage)
```
Entry Long = markPrice - (tickSize * 10)
Entry Short = markPrice + (tickSize * 10)
```

**Por que slippage?**
- DEXs têm menos liquidez que CEXs
- Precisamos garantir que a ordem será executada
- 10 ticks é um valor conservador

### Stop Loss (com fees)
```
Quantity = Volume_Order / Entry
Fee_Open = Entry * Quantity * Maker_Fee
Fee_Close = Entry * Quantity * Taker_Fee
Total_Fee = Fee_Open + Fee_Close

Fee_Total_Loss = (Fee_Open + (Fee_Open * MAX_PERCENT_LOSS)) / Quantity

Stop Long = Entry - (Entry * MAX_PERCENT_LOSS) - Fee_Total_Loss
Stop Short = Entry + (Entry * MAX_PERCENT_LOSS) + Fee_Total_Loss
```

### Take Profit (com fees)
```
Fee_Total_Profit = (Fee_Open + (Fee_Open * MAX_PERCENT_PROFIT)) / Quantity

Target Long = Entry + (Entry * MAX_PERCENT_PROFIT) + Fee_Total_Profit
Target Short = Entry - (Entry * MAX_PERCENT_PROFIT) - Fee_Total_Profit
```

---

## 🔌 Integração com Nado DEX

### Passo 1: Atualizar `config.py`

Adicionar configurações do decision engine:

```python
# Configurações de Decisão
CERTAINTY = int(os.getenv('CERTAINTY', '70'))  # 0-100
VOLUME_ORDER = float(os.getenv('VOLUME_ORDER', '100'))
MAX_PERCENT_LOSS = os.getenv('MAX_PERCENT_LOSS', '1%')
MAX_PERCENT_PROFIT = os.getenv('MAX_PERCENT_PROFIT', '2%')
UNIQUE_TREND = os.getenv('UNIQUE_TREND', '')  # '', 'LONG', ou 'SHORT'

# Configurações de Fees para Nado
MAKER_FEE = float(os.getenv('MAKER_FEE', '0.001'))  # 0.1%
TAKER_FEE = float(os.getenv('TAKER_FEE', '0.001'))  # 0.1%
```

### Passo 2: Integrar no `nado_trading_bot.py`

Importar e usar o decision engine:

```python
from nado_decision_engine import NadoDecisionEngine, DecisionResult

class NadoTradingBot:
    def __init__(self):
        # Configurações existentes
        self.config = NadoConfig()
        
        # Inicializar Decision Engine
        self.decision_engine = NadoDecisionEngine({
            'CERTAINTY': self.config.certainty,
            'VOLUME_ORDER': self.config.volume_order,
            'MAX_PERCENT_LOSS': self.config.max_percent_loss,
            'MAX_PERCENT_PROFIT': self.config.max_percent_profit,
            'UNIQUE_TREND': self.config.unique_trend
        })
    
    async def analyze_markets(self):
        """Analisar mercados com decision engine"""
        
        # 1. Coletar dados de preços dos pares
        pairs_data = []
        for pair in self.config.pairs:
            price_data = await self.data_collector.get_latest_price(pair)
            
            if price_data:
                pairs_data.append({
                    'pair': pair,
                    'mark_price': price_data['price'],
                    'tick_size': price_data.get('tick_size', 0.001),
                    'maker_fee': self.config.maker_fee,
                    'taker_fee': self.config.taker_fee
                })
        
        # 2. Avaliar oportunidades com Decision Engine
        opportunities = self.decision_engine.evaluate_all_pairs(pairs_data)
        
        # 3. Filtrar por ordens abertas máximas
        open_positions = await self.get_open_positions()
        open_pairs = [pos['pair'] for pos in open_positions]
        
        available_opportunities = [
            opp for opp in opportunities 
            if opp.pair not in open_pairs and 
               len(open_positions) < self.config.max_positions
        ]
        
        # 4. Executar trades
        for opp in available_opportunities:
            await self.execute_trade(opp)
    
    async def execute_trade(self, decision: DecisionResult):
        """Executar trade baseado na decisão"""
        
        self.logger.info(f"🚀 Executando trade: {decision.pair} {decision.side}")
        
        # Calcular quantity precisa
        quantity = decision.position_size
        
        # Executar swap na Nado DEX
        try:
            tx_hash = await self.nado_client.execute_swap(
                pair=decision.pair,
                side=decision.side,
                quantity=quantity,
                min_price=decision.stop_loss,  # Preço mínimo
                max_price=decision.take_profit  # Preço máximo
            )
            
            self.logger.info(f"✅ Trade enviado: {tx_hash}")
            
            # Guardar trade no tracking
            self.track_trade(decision, tx_hash)
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao executar trade: {e}")
    
    async def manage_positions(self):
        """Gerenciar posições abertas"""
        
        positions = await self.get_open_positions()
        
        for position in positions:
            # Verificar se atingiu SL ou TP
            current_price = await self.get_current_price(position['pair'])
            
            if position['side'] == 'long':
                if current_price <= position['stop_loss']:
                    await self.close_position(position, 'stop_loss')
                elif current_price >= position['take_profit']:
                    await self.close_position(position, 'take_profit')
            else:  # short
                if current_price >= position['stop_loss']:
                    await self.close_position(position, 'stop_loss')
                elif current_price <= position['take_profit']:
                    await self.close_position(position, 'take_profit')
```

### Passo 3: Integrar Dados OHLCV Reais

O arquivo atual usa indicadores simulados. Para dados reais:

```python
from nado_data_collector import NadoDataCollector

async def get_real_indicators(self, pair: str) -> Dict[str, TimeframeIndicators]:
    """
    Busca dados OHLCV reais e calcula indicadores.
    Requer implementação de coleta de candles na Nado.
    """
    collector = NadoDataCollector(self.config)
    
    # Buscar candles dos 3 timeframes
    candles_1m = await collector.get_ohlcv(pair, '1m', limit=30)
    candles_5m = await collector.get_ohlcv(pair, '5m', limit=30)
    candles_15m = await collector.get_ohlcv(pair, '15m', limit=30)
    
    # Converter para pandas DataFrame
    df_1m = pd.DataFrame(candles_1m)
    df_5m = pd.DataFrame(candles_5m)
    df_15m = pd.DataFrame(candles_15m)
    
    # Calcular indicadores usando pandas-ta
    tf1m = self.calculate_indicators_from_df(df_1m, '1m')
    tf5m = self.calculate_indicators_from_df(df_5m, '5m')
    tf15m = self.calculate_indicators_from_df(df_15m, '15m')
    
    return {
        '1m': tf1m,
        '5m': tf5m,
        '15m': tf15m
    }
```

---

## 📝 Exemplo de Uso

### Configuração (.env)
```bash
# Decision Engine
CERTAINTY=70
VOLUME_ORDER=100
MAX_PERCENT_LOSS=1%
MAX_PERCENT_PROFIT=2%
UNIQUE_TREND=

# Nado Fees
MAKER_FEE=0.001
TAKER_FEE=0.001

# Bot
MAX_POSITIONS=3
LOG_LEVEL=INFO
```

### Exemplo de Execução
```python
from nado_decision_engine import NadoDecisionEngine

# Criar engine
config = {
    'CERTAINTY': 70,
    'VOLUME_ORDER': 100,
    'MAX_PERCENT_LOSS': '1%',
    'MAX_PERCENT_PROFIT': '2%',
    'UNIQUE_TREND': ''
}

engine = NadoDecisionEngine(config)

# Avaliar oportunidades
pairs = [
    {
        'pair': 'SOL_USDC',
        'mark_price': 178.50,
        'tick_size': 0.001,
        'maker_fee': 0.001,
        'taker_fee': 0.001
    }
]

opportunities = engine.evaluate_all_pairs(pairs)

# Resultado esperado:
# ✅ SOL_USDC LONG @ $178.473
#    Certainty: 78% | Score: LONG=78% SHORT=33%
#    Stop: $176.564 | Target: $180.862
#    Risk: $1.91 | Reward: $3.89 | R:R: 2.04x
```

---

## 🔄 Fluxo Completo

```
┌─────────────────────────────────────────┐
│ 1. Coletar Dados On-Chain      │
│    - Preços OHLCV (1m, 5m, 15m) │
│    - Volume, Order Book          │
└─────────────┬─────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ 2. Calcular Indicadores          │
│    - RSI, EMA, MACD, BB      │
│    - VWAP, Volume Trend          │
└─────────────┬─────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ 3. Decision Engine              │
│    - Score LONG vs SHORT        │
│    - 9 fatores por lado          │
│    - Filtrar por CERTAINTY       │
│    - Respeitar UNIQUE_TREND      │
└─────────────┬─────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ 4. Calcular Setup              │
│    - Entry (slippage 10 ticks)  │
│    - Stop Loss (com fees)         │
│    - Take Profit (com fees)       │
│    - Risk/Reward Ratio           │
└─────────────┬─────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ 5. Executar Swap na Nado DEX   │
│    - SDK Oficial Nado           │
│    - Min/Max Price (SL/TP)     │
│    - Confirmar Transação        │
└─────────────┬─────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ 6. Gerenciar Position          │
│    - Monitorar preço atual        │
│    - Fechar em SL ou TP        │
│    - Trackear PnL              │
└─────────────────────────────────────────┘
```

---

## ⚠️ Diferenças Importantes entre Backpack e Nado DEX

| Aspecto | Backpack (Backbot) | Nado DEX (Sua implementação) |
|---------|---------------------|-------------------------------|
| Ordem | Limit Order | Swap direto |
| Slippage | Controlado | Dependente de liquidez |
| Fees | Maker/Taker fixos | Maker/Taker + Gas |
| Latência | Baixa | Maior (block time) |
| Price Oracle | MarkPrice | AMM Pool Price |
| Candle Data | Disponível | Precisa de DEX Aggregator |

---

## 🎯 Próximos Passos

1. **Implementar coleta de dados OHLCV** na Nado DEX
2. **Integrar dados reais** no decision engine (substituir simulados)
3. **Implementar execução de swap** via SDK Nado
4. **Adicionar trailing stop** opcional (como no backbot)
5. **Implementar Grid Mode** para mercados laterais
6. **Adicionar performance tracking** (win rate, Sharpe, etc.)

---

## 📚 Recursos

- **Backbot:** https://github.com/santidev95/backbot
- **Nado Trading Bot:** https://github.com/santidevbot/nado-trading-bot
- **Nado SDK:** https://github.com/nados-labs/nado-sdk
- **Technical Indicators:** https://github.com/bukosabino/ta

---

**Sucesso na integração!** 🚀
