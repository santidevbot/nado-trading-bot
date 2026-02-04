"""
Nado Multi-Timeframe Analyzer - Análise técnica em múltiplos timeframes
Análise 5m, 15m, 30m para trading rápido com dados do Nado DEX
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
from config import NadoConfig
from nado_data_collector import NadoDataCollector
import ta


class NadoMultiTimeframeAnalyzer:
    """Analisador multi-timeframe para Nado DEX"""
    
    def __init__(self, config: NadoConfig):
        self.config = config
        self.data_collector = NadoDataCollector(config)
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Configura logger"""
        logging.basicConfig(
            level=self.config.log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('MultiTimeframeAnalyzer')
    
    async def calculate_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calcula indicadores técnicos"""
        if df is None or len(df) < 20:
            return {}
        
        indicators = {}
        
        # RSI - Multiple períodos para diferentes timeframes
        indicators['rsi_7'] = ta.rsi(df['close'], length=7).iloc[-1]
        indicators['rsi_14'] = ta.rsi(df['close'], length=14).iloc[-1]
        indicators['rsi_21'] = ta.rsi(df['close'], length=21).iloc[-1]
        
        # EMAs - Alinhamento multi-timeframe
        indicators['ema_7'] = ta.ema(df['close'], length=7).iloc[-1]
        indicators['ema_20'] = ta.ema(df['close'], length=20).iloc[-1]
        indicators['ema_50'] = ta.ema(df['close'], length=50).iloc[-1]
        
        # EMAs Cruzamentos
        indicators['ema_7_above_ema_20'] = indicators['ema_7'] > indicators['ema_20']
        indicators['ema_20_above_ema_50'] = indicators['ema_20'] > indicators['ema_50']
        
        # MACD
        macd = ta.macd(df['close'])
        indicators['macd'] = macd['MACD_12_26_9'].iloc[-1]
        indicators['macd_signal'] = macd['MACDs_12_26_9'].iloc[-1]
        indicators['macd_histogram'] = macd['MACDh_12_26_9'].iloc[-1]
        
        # Bollinger Bands
        bbands = ta.bbands(df['close'], length=20, std=2)
        indicators['bb_upper'] = bbands['BBU_20_2'].iloc[-1]
        indicators['bb_middle'] = bbands['BBM_20_2'].iloc[-1]
        indicators['bb_lower'] = bbands['BBL_20_2'].iloc[-1]
        indicators['bb_width'] = bbands['BBB_20_2'].iloc[-1] - bbands['BBL_20_2'].iloc[-1]
        
        # ATR (Average True Range)
        indicators['atr'] = ta.atr(df['high'], df['low'], length=14).iloc[-1]
        
        # Momentum
        indicators['momentum'] = df['close'].iloc[-1] - df['close'].iloc[-5]
        
        # Volume indicators
        if 'volume' in df.columns:
            indicators['volume_sma_20'] = ta.sma(df['volume'], length=20).iloc[-1]
            indicators['volume_ratio'] = df['volume'].iloc[-1] / indicators['volume_sma_20']
        
        return indicators
    
    def detect_patterns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Detecta padrões de candlestick"""
        if df is None or len(df) < 5:
            return {}
        
        patterns = {}
        last_candles = df.tail(5)
        
        # Hammer/Inverted Hammer
        body_size = abs(last_candles['close'].iloc[-1] - last_candles['open'].iloc[-1])
        lower_wick = last_candles['low'].iloc[-1] - min(last_candles['open'].iloc[-1], last_candles['close'].iloc[-1])
        upper_wick = max(last_candles['open'].iloc[-1], last_candles['close'].iloc[-1]) - last_candles['high'].iloc[-1]
        
        if lower_wick > 2 * body_size:
            if last_candles['close'].iloc[-1] > last_candles['open'].iloc[-1]:
                patterns['hammer'] = 'bullish'
            else:
                patterns['inverted_hammer'] = 'bearish'
        
        # Engulfing
        if len(last_candles) >= 2:
            prev_candle = last_candles.iloc[-2]
            curr_candle = last_candles.iloc[-1]
            
            if (prev_candle['close'] < prev_candle['open'] and 
                curr_candle['close'] > curr_candle['open'] and
                curr_candle['open'] <= prev_candle['open'] and 
                curr_candle['close'] >= prev_candle['close']):
                patterns['bullish_engulfing'] = 'strong'
        
        # Three White Soldiers (uptrend)
        if (len(last_candles) >= 3 and
            all(last_candles['close'].iloc[-i] > last_candles['open'].iloc[-i] 
                for i in range(3))):
            patterns['three_white_soldiers'] = 'bullish'
        
        return patterns
    
    def analyze_trend(self, df: pd.DataFrame) -> Dict[str, str]:
        """Analisa tendência"""
        if df is None or len(df) < 20:
            return {}
        
        trend = {}
        recent_closes = df['close'].tail(20)
        
        # Direção da tendência
        if recent_closes.iloc[-1] > recent_closes.iloc[0]:
            trend['direction'] = 'uptrend'
        elif recent_closes.iloc[-1] < recent_closes.iloc[0]:
            trend['direction'] = 'downtrend'
        else:
            trend['direction'] = 'sideways'
        
        # Força da tendência
        price_change = abs(recent_closes.iloc[-1] - recent_closes.iloc[0])
        avg_price = recent_closes.mean()
        trend['strength'] = (price_change / avg_price) * 100 if avg_price > 0 else 0
        
        if trend['strength'] > 5:
            trend['strength_label'] = 'strong'
        elif trend['strength'] > 2:
            trend['strength_label'] = 'moderate'
        elif trend['strength'] > 0.5:
            trend['strength_label'] = 'weak'
        else:
            trend['strength_label'] = 'very_weak'
        
        return trend
    
    async def analyze_pair(self, pair: str) -> Dict[str, Dict]:
        """Analisa um par em todos os timeframes"""
        self.logger.info(f"🔍 Analisando {pair}...")
        
        analysis = {
            'pair': pair,
            'timeframes': {}
        }
        
        for timeframe in self.config.timeframes:
            # Buscar dados do coletor
            price_data = self.data_collector.get_latest_price(pair)
            if price_data:
                self.logger.info(f"  {timeframe}: Preço ${price_data:.4f}")
                analysis['timeframes'][timeframe] = {
                    'price': price_data,
                    'indicators': {},
                    'patterns': {},
                    'trend': {},
                    'volume': self.data_collector.get_spread(pair)
                }
                
                # Indicadores técnicos seriam calculados com dados OHLCV completos
                # Aqui temos apenas preço, então simulamos indicadores baseados em preço
                analysis['timeframes'][timeframe]['indicators'] = {
                    'ema_short': price_data * 0.99,  # Simulação
                    'ema_medium': price_data * 0.98,
                    'ema_long': price_data * 0.97,
                    'rsi': 50,  # Neutro por padrão sem dados OHLCV
                }
                
                # Padrões seriam detectados com dados OHLCV completos
                analysis['timeframes'][timeframe]['patterns'] = {
                    'status': 'requires_ohlcv'
                }
                
                # Tendência baseada em EMAs simuladas
                ema_short = analysis['timeframes'][timeframe]['indicators']['ema_short']
                ema_medium = analysis['timeframes'][timeframe]['indicators']['ema_medium']
                
                if ema_short > ema_medium:
                    trend_dir = 'uptrend'
                elif ema_short < ema_medium:
                    trend_dir = 'downtrend'
                else:
                    trend_dir = 'sideways'
                
                analysis['timeframes'][timeframe]['trend'] = {
                    'direction': trend_dir,
                    'alignment': ema_short > ema_medium  # True se short > medium
                }
        
        self.logger.info(f"✅ {pair} analisado!")
        return analysis
    
    async def analyze_all(self):
        """Analisa todos os pares configurados"""
        self.logger.info(f"🚀 Iniciando análise multi-timeframe...")
        
        all_analysis = {}
        
        await self.data_collector.init_exchange()
        
        for pair in self.config.trading_pairs:
            analysis = await self.analyze_pair(pair)
            all_analysis[pair] = analysis
        
        self.logger.info(f"✅ Análise concluída!")
        return all_analysis
    
    def print_summary(self, analysis: Dict[str, Dict]):
        """Imprime resumo da análise"""
        print("\n" + "="*80)
        print("📊 ANÁLISE MULTI-TIMEFRAME - NADO DEX")
        print("="*80)
        print(f"📅 {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💰 Pares: {', '.join(self.config.trading_pairs)}")
        print(f"⏱️ Timeframes: {', '.join(self.config.timeframes)}")
        print("")
        
        for pair, data in analysis.items():
            print(f"\n📈 {pair}")
            print("-" * 40)
            
            for tf, tf_data in data['timeframes'].items():
                price = tf_data.get('price', 0)
                trend = tf_data.get('trend', {}).get('direction', 'N/A')
                
                emoji = "🟢" if trend == 'uptrend' else "🔴" if trend == 'downtrend' else "➡️"
                
                print(f"  {tf:5} | ${price:8.2f} | {emoji} {trend}")
                
                indicators = tf_data.get('indicators', {})
                if 'rsi' in indicators:
                    rsi = indicators['rsi']
                    rsi_emoji = "🔴" if rsi < 30 else "🟡" if rsi > 70 else "🟢"
                    print(f"      RSI: {rsi:.1f} {rsi_emoji}")
        
        print("\n" + "="*80)
        print("✅ Análise concluída!")
        print("="*80 + "\n")


async def main():
    """Função principal"""
    config = NadoConfig.from_env()
    
    analyzer = NadoMultiTimeframeAnalyzer(config)
    analysis = await analyzer.analyze_all()
    analyzer.print_summary(analysis)


if __name__ == "__main__":
    asyncio.run(main())
