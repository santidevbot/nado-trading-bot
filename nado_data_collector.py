"""
Nado Data Collector - Coleta dados on-chain da Nado DEX
Busca preços, volume, order book e TVL em tempo real
"""

import asyncio
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import logging
from config import NadoConfig


class NadoDataCollector:
    """Coleta dados on-chain da Nado DEX"""
    
    def __init__(self, config: NadoConfig):
        self.config = config
        self.exchange = None
        self.logger = self._setup_logger()
        
        # Cache de dados
        self.price_cache = {}
        self.volume_cache = {}
        self.orderbook_cache = {}
        
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
        return logging.getLogger('NadoCollector')
    
    async def init_exchange(self):
        """Inicializa exchange Nado via CCXT"""
        try:
            self.exchange = ccxt.nado({
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'swap',  # Nado usa swaps
                    'adjustForTimeDifference': True
                }
            })
            self.logger.info(f"✅ Exchange Nado inicializado")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar Nado: {e}")
            return False
    
    async def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """Busca dados OHLCV"""
        try:
            ohlcv = await self.exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                limit=limit
            )
            
            if not ohlcv:
                self.logger.warning(f"⚠️ Sem dados OHLCV para {symbol}")
                return None
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['returns'] = df['close'].pct_change() * 100
            
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar OHLCV {symbol}: {e}")
            return None
    
    async def fetch_orderbook(self, symbol: str, limit: int = 20) -> Optional[Dict]:
        """Busca order book"""
        try:
            orderbook = await self.exchange.fetch_order_book(symbol, limit=limit)
            
            if not orderbook or not orderbook.get('bids') or not orderbook.get('asks'):
                return None
            
            bids = orderbook['bids'][:10]
            asks = orderbook['asks'][:10]
            
            best_bid = bids[0][0] if bids else None
            best_ask = asks[0][0] if asks else None
            spread = best_ask - best_bid if (best_bid and best_ask) else 0
            spread_pct = (spread / best_bid * 100) if best_bid else 0
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'bids': bids,
                'asks': asks,
                'best_bid': best_bid,
                'best_ask': best_ask,
                'spread': spread,
                'spread_pct': spread_pct,
                'mid_price': (best_bid + best_ask) / 2 if (best_bid and best_ask) else None
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar orderbook {symbol}: {e}")
            return None
    
    async def fetch_tvl(self, pools: List[str] = None) -> Dict[str, float]:
        """Busca TVL dos pools (simulado - em produção usaria API on-chain)"""
        # CCXT não tem TVL nativo, então isso seria implementado via API do Nado
        # Por enquanto, retorna placeholder
        return {}
    
    async def collect_all_data(self):
        """Coleta todos os dados para todos os pares e timeframes"""
        await self.init_exchange()
        
        if not self.exchange:
            return None
        
        self.logger.info(f"🚀 Iniciando coleta de dados...")
        self.logger.info(f"📊 Pares: {', '.join(self.config.trading_pairs)}")
        self.logger.info(f"⏱️ Timeframes: {', '.join(self.config.timeframes)}")
        
        all_data = {}
        
        for pair in self.config.trading_pairs:
            pair_data = {
                'symbol': pair,
                'timeframes': {}
            }
            
            for timeframe in self.config.timeframes:
                # OHLCV
                ohlcv_df = await self.fetch_ohlcv(pair, timeframe)
                if ohlcv_df is not None:
                    pair_data['timeframes'][timeframe] = {
                        'ohlcv': ohlcv_df,
                        'latest_price': ohlcv_df['close'].iloc[-1],
                        'volume_24h': ohlcv_df['volume'].sum()
                    }
            
            # Order Book (apenas um, geralmente o mesmo para todos timeframes)
            orderbook = await self.fetch_orderbook(pair, limit=20)
            if orderbook:
                pair_data['orderbook'] = orderbook
            
            all_data[pair] = pair_data
            self.logger.info(f"✅ {pair} coletado")
        
        # Salvar em cache
        self.price_cache = all_data
        
        self.logger.info(f"✅ Coleta concluída!")
        return all_data
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Retorna preço mais recente"""
        if symbol in self.price_cache:
            # Pegar preço do timeframe mais longo disponível
            timeframes = sorted(self.config.timeframes, key=lambda x: -x.index if x in ['5m', '15m', '30m', '1h', '4h'] else 0)
            
            for tf in timeframes:
                if tf in self.price_cache[symbol]['timeframes']:
                    return self.price_cache[symbol]['timeframes'][tf]['latest_price']
        
        return None
    
    def get_spread(self, symbol: str) -> Optional[float]:
        """Retorna spread atual"""
        if symbol in self.price_cache and 'orderbook' in self.price_cache[symbol]:
            ob = self.price_cache[symbol]['orderbook']
            return ob.get('spread_pct', 0)
        
        return None


async def main():
    """Função principal de teste"""
    config = NadoConfig.from_env()
    config.validate()
    
    collector = NadoDataCollector(config)
    await collector.collect_all_data()
    
    # Exemplo de uso
    print("\n📊 Dados Coletados:")
    for pair in config.trading_pairs:
        price = collector.get_latest_price(pair)
        spread = collector.get_spread(pair)
        if price:
            print(f"{pair}: ${price:.4f} | Spread: {spread:.4f}%")


if __name__ == "__main__":
    asyncio.run(main())
