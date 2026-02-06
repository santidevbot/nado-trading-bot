"""
Nado DEX Decision Engine - Adaptado do Backbot
Algoritmo de tomada de decisão multi-timeframe para Nado DEX

Baseado no algoritmo do backbot:
- 9 fatores de decisão por lado (LONG/SHORT)
- Confluência de múltiplos timeframes (1m, 5m, 15m)
- Scoring de 0-100% para cada lado
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class DecisionResult:
    """Resultado da tomada de decisão"""
    pair: str
    side: str  # 'long' or 'short'
    certainty: float  # 0-100
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    risk_usd: float
    reward_usd: float
    indicators: Dict[str, float]


@dataclass
class TimeframeIndicators:
    """Indicadores por timeframe"""
    timeframe: str
    close: float
    ema9: float
    ema21: float
    ema_diff: float
    ema_diff_pct: float
    rsi: float
    macd: float
    macd_signal: float
    macd_histogram: float
    bollinger_upper: float
    bollinger_middle: float
    bollinger_lower: float
    vwap: float
    volume_trend: str  # 'increasing', 'decreasing', 'flat'
    price_slope: float


class NadoDecisionEngine:
    """Motor de decisão baseado no backbot"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger('DecisionEngine')
        
        # Configurações
        self.certainty_threshold = config.get('CERTAINTY', 70)
        self.volume_order = config.get('VOLUME_ORDER', 100)
        self.max_percent_loss = self._parse_percent(config.get('MAX_PERCENT_LOSS', '1%'))
        self.max_percent_profit = self._parse_percent(config.get('MAX_PERCENT_PROFIT', '2%'))
        self.unique_trend = config.get('UNIQUE_TREND', '').upper()
        
    def _parse_percent(self, value: str) -> float:
        """Converte '1%' para 0.01"""
        if isinstance(value, str):
            return float(value.replace('%', '')) / 100
        return float(value)
    
    def _create_mock_indicators(self, price: float, timeframe: str) -> TimeframeIndicators:
        """
        Cria indicadores simulados baseados no preço atual.
        Em produção, estes viriam de dados OHLCV reais.
        """
        # Simulação de indicadores - em produção usar dados reais
        
        # RSI: oscila entre 30-70 aleatoriamente com viés
        np.random.seed(hash(f"{timeframe}{price}") % 1000)
        rsi_bias = 50 + np.random.uniform(-20, 20)
        rsi = np.clip(rsi_bias, 10, 90)
        
        # EMAs: com leve viés em direção ao preço
        ema9 = price * (1 + np.random.uniform(-0.01, 0.01))
        ema21 = price * (1 + np.random.uniform(-0.02, 0.02))
        
        # MACD
        macd = np.random.uniform(-0.5, 0.5) * price
        macd_signal = macd * 0.9
        macd_histogram = macd - macd_signal
        
        # Bollinger
        bb_std = price * 0.02
        bollinger_upper = price + 2 * bb_std
        bollinger_middle = price
        bollinger_lower = price - 2 * bb_std
        
        # VWAP
        vwap = price * (1 + np.random.uniform(-0.005, 0.005))
        
        # Volume trend
        volume_trends = ['increasing', 'decreasing', 'flat']
        volume_trend = volume_trends[hash(f"{timeframe}{price}") % 3]
        
        # Price slope
        price_slope = np.random.uniform(-1, 1)
        
        return TimeframeIndicators(
            timeframe=timeframe,
            close=price,
            ema9=ema9,
            ema21=ema21,
            ema_diff=ema9 - ema21,
            ema_diff_pct=((ema9 - ema21) / ema21 * 100) if ema21 != 0 else 0,
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_histogram,
            bollinger_upper=bollinger_upper,
            bollinger_middle=bollinger_middle,
            bollinger_lower=bollinger_lower,
            vwap=vwap,
            volume_trend=volume_trend,
            price_slope=price_slope
        )
    
    def score_side(self, tf1m: TimeframeIndicators, tf5m: TimeframeIndicators, 
                 tf15m: TimeframeIndicators, is_long: bool) -> int:
        """
        Calcula score para LONG ou SHORT baseado em 9 fatores.
        Retorna score de 0-9 (será convertido para % depois).
        """
        score = 0
        total_factors = 9
        
        # Fator 1: EMA 15m - Tendência de longo prazo
        if is_long:
            if tf15m.ema9 > tf15m.ema21:
                score += 1
        else:
            if tf15m.ema9 < tf15m.ema21:
                score += 1
        
        # Fator 2: EMA 5m - Tendência de médio prazo
        if is_long:
            if tf5m.ema9 > tf5m.ema21:
                score += 1
        else:
            if tf5m.ema9 < tf5m.ema21:
                score += 1
        
        # Fator 3: RSI 5m - Momentum
        if is_long:
            if tf5m.rsi > 55:  # Compra em tendência
                score += 1
        else:
            if tf5m.rsi < 45:  # Venda em tendência
                score += 1
        
        # Fator 4: MACD 5m - Cruzamento
        if is_long:
            if tf5m.macd > tf5m.macd_signal:
                score += 1
        else:
            if tf5m.macd < tf5m.macd_signal:
                score += 1
        
        # Fator 5: Bollinger 1m - Posição relativa
        if is_long:
            if tf1m.close > tf1m.bollinger_middle:
                score += 1
        else:
            if tf1m.close < tf1m.bollinger_middle:
                score += 1
        
        # Fator 6: VWAP 1m - Média ponderada por volume
        if is_long:
            if tf1m.close > tf1m.vwap:
                score += 1
        else:
            if tf1m.close < tf1m.vwap:
                score += 1
        
        # Fator 7: Volume 1m - Confirmação
        if tf1m.volume_trend == 'increasing':
            score += 1
        
        # Fator 8: Price Slope 1m - Inclinação
        if is_long:
            if tf1m.price_slope > 0:
                score += 1
        else:
            if tf1m.price_slope < 0:
                score += 1
        
        # Fator 9: STACK 5m - Confluência completa
        if is_long:
            # LONG: RSI > 55, MACD > Signal, EMA9 > EMA21
            stack = (tf5m.rsi > 55 and 
                     tf5m.macd > tf5m.macd_signal and 
                     tf5m.ema9 > tf5m.ema21)
        else:
            # SHORT: RSI < 45, MACD < Signal, EMA9 < EMA21
            stack = (tf5m.rsi < 45 and 
                     tf5m.macd < tf5m.macd_signal and 
                     tf5m.ema9 < tf5m.ema21)
        
        if stack:
            score += 1
        
        return score
    
    def calculate_entry_price(self, mark_price: float, tick_size: float, 
                          is_long: bool) -> float:
        """Calcula preço de entrada com slippage"""
        slippage = tick_size * 10
        
        if is_long:
            entry = mark_price - slippage  # Compra ligeiramente abaixo
        else:
            entry = mark_price + slippage  # Venda ligeiramente acima
        
        return round(entry, 6)
    
    def calculate_stop_loss(self, entry: float, is_long: bool, 
                        quantity: float, maker_fee: float, taker_fee: float) -> float:
        """Calcula stop loss com fees"""
        fee_open = entry * quantity * maker_fee
        fee_close = entry * quantity * taker_fee
        total_fee = fee_open + fee_close
        
        # Loss em USD = Volume * MAX_PERCENT_LOSS
        loss_usd = (entry * quantity) * self.max_percent_loss
        
        # Fee adicional no loss
        fee_total_loss = (fee_open + (fee_open * self.max_percent_loss)) / quantity
        
        if is_long:
            stop = entry - (entry * self.max_percent_loss) - fee_total_loss
        else:
            stop = entry + (entry * self.max_percent_loss) + fee_total_loss
        
        return round(stop, 6)
    
    def calculate_take_profit(self, entry: float, is_long: bool,
                           quantity: float, maker_fee: float, taker_fee: float) -> float:
        """Calcula take profit com fees"""
        fee_open = entry * quantity * maker_fee
        fee_close = entry * quantity * taker_fee
        total_fee = fee_open + fee_close
        
        # Profit em USD = Volume * MAX_PERCENT_PROFIT
        profit_usd = (entry * quantity) * self.max_percent_profit
        
        # Fee adicional no profit
        fee_total_profit = (fee_open + (fee_open * self.max_percent_profit)) / quantity
        
        if is_long:
            target = entry + (entry * self.max_percent_profit) + fee_total_profit
        else:
            target = entry - (entry * self.max_percent_profit) - fee_total_profit
        
        return round(target, 6)
    
    def evaluate_trade_opportunity(self, pair: str, mark_price: float,
                                 tick_size: float, maker_fee: float, 
                                 taker_fee: float) -> Optional[DecisionResult]:
        """
        Avalia oportunidade de trade para um par.
        Retorna None se não houver oportunidade válida.
        """
        try:
            # Criar indicadores simulados para os 3 timeframes
            tf1m = self._create_mock_indicators(mark_price, '1m')
            tf5m = self._create_mock_indicators(mark_price, '5m')
            tf15m = self._create_mock_indicators(mark_price, '15m')
            
            # Calcular scores para LONG e SHORT
            long_score = self.score_side(tf1m, tf5m, tf15m, is_long=True)
            short_score = self.score_side(tf1m, tf5m, tf15m, is_long=False)
            
            # Converter scores para porcentagem
            long_pct = int((long_score / 9) * 100)
            short_pct = int((short_score / 9) * 100)
            
            # Decidir lado
            is_long = long_score > short_score
            certainty = max(long_pct, short_pct)
            
            # Verificar se atingiu threshold
            if certainty < self.certainty_threshold:
                self.logger.debug(f"{pair}: Certainty {certainty}% < threshold {self.certainty_threshold}%")
                return None
            
            # Verificar UNIQUE_TREND
            if self.unique_trend:
                if self.unique_trend == 'LONG' and not is_long:
                    self.logger.debug(f"{pair}: Ignored by UNIQUE_TREND=LONG")
                    return None
                if self.unique_trend == 'SHORT' and is_long:
                    self.logger.debug(f"{pair}: Ignored by UNIQUE_TREND=SHORT")
                    return None
            
            # Calcular entry, stop, target, size
            entry = self.calculate_entry_price(mark_price, tick_size, is_long)
            quantity = self.volume_order / entry
            stop = self.calculate_stop_loss(entry, is_long, quantity, maker_fee, taker_fee)
            target = self.calculate_take_profit(entry, is_long, quantity, maker_fee, taker_fee)
            
            # Calcular risk/reward
            if is_long:
                risk_usd = (entry - stop) * quantity
                reward_usd = (target - entry) * quantity
            else:
                risk_usd = (stop - entry) * quantity
                reward_usd = (entry - target) * quantity
            
            # Ratio R/R
            rr_ratio = reward_usd / risk_usd if risk_usd > 0 else 0
            
            side = 'long' if is_long else 'short'
            
            self.logger.info(f"✅ {pair} {side.upper()} @ ${entry:.4f}")
            self.logger.info(f"   Certainty: {certainty}% | Score: LONG={long_pct}% SHORT={short_pct}%")
            self.logger.info(f"   Stop: ${stop:.4f} | Target: ${target:.4f}")
            self.logger.info(f"   Risk: ${risk_usd:.2f} | Reward: ${reward_usd:.2f} | R:R: {rr_ratio:.2f}")
            
            return DecisionResult(
                pair=pair,
                side=side,
                certainty=certainty,
                entry_price=entry,
                stop_loss=stop,
                take_profit=target,
                position_size=quantity,
                risk_usd=risk_usd,
                reward_usd=reward_usd,
                indicators={
                    'long_score': long_pct,
                    'short_score': short_pct,
                    'tf1m_rsi': tf1m.rsi,
                    'tf5m_rsi': tf5m.rsi,
                    'tf15m_rsi': tf15m.rsi,
                    'tf5m_macd': tf5m.macd,
                    'tf5m_ema_diff': tf5m.ema_diff_pct
                }
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao avaliar {pair}: {e}")
            return None
    
    def evaluate_all_pairs(self, pairs: List[Dict]) -> List[DecisionResult]:
        """
        Avalia todos os pares e retorna oportunidades válidas.
        
        Args:
            pairs: Lista de dicts com keys: pair, mark_price, tick_size, maker_fee, taker_fee
        
        Returns:
            Lista de DecisionResult ordenada por certeza
        """
        opportunities = []
        
        for pair_data in pairs:
            result = self.evaluate_trade_opportunity(
                pair=pair_data['pair'],
                mark_price=pair_data['mark_price'],
                tick_size=pair_data.get('tick_size', 0.0001),
                maker_fee=pair_data.get('maker_fee', 0.001),
                taker_fee=pair_data.get('taker_fee', 0.001)
            )
            
            if result:
                opportunities.append(result)
        
        # Ordenar por certeza (maior primeiro)
        opportunities.sort(key=lambda x: x.certainty, reverse=True)
        
        self.logger.info(f"📊 Total oportunidades: {len(opportunities)}")
        
        return opportunities


# Exemplo de uso
if __name__ == '__main__':
    # Configuração de exemplo
    config = {
        'CERTAINTY': 70,
        'VOLUME_ORDER': 100,
        'MAX_PERCENT_LOSS': '1%',
        'MAX_PERCENT_PROFIT': '2%',
        'UNIQUE_TREND': ''  # '', 'LONG', ou 'SHORT'
    }
    
    # Criar engine
    engine = NadoDecisionEngine(config)
    
    # Pares de exemplo
    pairs = [
        {
            'pair': 'SOL_USDC',
            'mark_price': 178.50,
            'tick_size': 0.001,
            'maker_fee': 0.001,
            'taker_fee': 0.001
        },
        {
            'pair': 'BTC_USDC',
            'mark_price': 98250.00,
            'tick_size': 0.1,
            'maker_fee': 0.001,
            'taker_fee': 0.001
        }
    ]
    
    # Avaliar oportunidades
    opportunities = engine.evaluate_all_pairs(pairs)
    
    print("\n" + "="*60)
    print("OPORTUNIDADES DE TRADE")
    print("="*60)
    
    for i, opp in enumerate(opportunities, 1):
        print(f"\n#{i} {opp.pair.upper()} - {opp.side.upper()}")
        print(f"   Entry: ${opp.entry_price:.4f}")
        print(f"   Stop Loss: ${opp.stop_loss:.4f}")
        print(f"   Take Profit: ${opp.take_profit:.4f}")
        print(f"   Certainty: {opp.certainty}%")
        print(f"   Risk/Reward: ${opp.risk_usd:.2f}:${opp.reward_usd:.2f} ({opp.reward_usd/opp.risk_usd:.2f}x)")
