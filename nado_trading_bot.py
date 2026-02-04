"""
Nado Trading Bot - Bot de trading para Nado DEX
Executa ordens de volume baseadas em análise técnica multi-timeframe
"""

import asyncio
import ccxt
from typing import Dict, List, Optional
from datetime import datetime
import logging
from config import NadoConfig
from nado_data_collector import NadoDataCollector
from nado_multi_timeframe import NadoMultiTimeframeAnalyzer


class NadoTradingBot:
    """Bot de trading para Nado DEX"""
    
    def __init__(self, config: NadoConfig):
        self.config = config
        self.data_collector = NadoDataCollector(config)
        self.analyzer = NadoMultiTimeframeAnalyzer(config)
        self.logger = self._setup_logger()
        self.exchange = None
        
        # Posições ativas
        self.positions = {}  # {pair: {entry_price, size, stop_loss, take_profit, side, entry_time}}
        
        # Estados
        self.running = False
        
        # Métricas de performance
        self.trades_history = []
        self.total_profit = 0.0
        self.total_loss = 0.0
        self.win_count = 0
        self.loss_count = 0
    
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
        return logging.getLogger('NadoTradingBot')
    
    async def init_exchange(self):
        """Inicializa exchange Nado via CCXT"""
        try:
            self.exchange = ccxt.nado({
                'options': {
                    'defaultType': 'swap',
                    'adjustForTimeDifference': True
                },
                'enableRateLimit': True
            })
            self.logger.info(f"✅ Exchange Nado inicializado")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar Nado: {e}")
            return False
    
    def calculate_position_size(self, price: float, risk_percent: float) -> float:
        """Calcula tamanho da posição baseado no risco"""
        account_balance = 10000.0  # Placeholder - na prática buscar do saldo da wallet
        risk_amount = account_balance * (risk_percent / 100)
        position_size = risk_amount / price
        return position_size
    
    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """Calcula stop loss"""
        if side == 'buy':
            return entry_price * (1 - self.config.stop_loss_percent / 100)
        else:  # sell
            return entry_price * (1 + self.config.stop_loss_percent / 100)
    
    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """Calcula take profit"""
        if side == 'buy':
            return entry_price * (1 + self.config.take_profit_percent / 100)
        else:  # sell
            return entry_price * (1 - self.config.take_profit_percent / 100)
    
    async def check_entry_signal(self, analysis: Dict[str, Dict]) -> List[Dict]:
        """Verifica sinais de entrada baseados na análise"""
        signals = []
        
        for pair, data in analysis.items():
            for tf, tf_data in data['timeframes'].items():
                if tf in ['5m', '15m']:  # Prioriza timeframes curtos para entry
                    trend = tf_data.get('trend', {})
                    direction = trend.get('direction', '')
                    
                    # Sinais de Compra
                    if direction == 'uptrend':
                        rsi = tf_data.get('indicators', {}).get('rsi', 50)
                        
                        if 30 <= rsi <= 60:  # RSI em zona neutra/oversold
                            signals.append({
                                'pair': pair,
                                'timeframe': tf,
                                'signal': 'buy',
                                'confidence': 'high',
                                'price': tf_data.get('price'),
                                'stop_loss': self.calculate_stop_loss(tf_data['price'], 'buy'),
                                'take_profit': self.calculate_take_profit(tf_data['price'], 'buy'),
                                'risk_percent': self.config.stop_loss_percent,
                                'reason': f"Uptrend + RSI {rsi:.1f} (oversold zone)"
                            })
                    
                    # Sinais de Venda
                    elif direction == 'downtrend':
                        rsi = tf_data.get('indicators', {}).get('rsi', 50)
                        
                        if 40 <= rsi <= 70:  # RSI em zona neutra/overbought
                            signals.append({
                                'pair': pair,
                                'timeframe': tf,
                                'signal': 'sell',
                                'confidence': 'high',
                                'price': tf_data.get('price'),
                                'stop_loss': self.calculate_stop_loss(tf_data['price'], 'sell'),
                                'take_profit': self.calculate_take_profit(tf_data['price'], 'sell'),
                                'risk_percent': self.config.stop_loss_percent,
                                'reason': f"Downtrend + RSI {rsi:.1f} (overbought zone)"
                            })
        
        # Prioriza sinais de maior confiança
        signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        return signals
    
    async def execute_trade(self, signal: Dict) -> bool:
        """Executa trade na Nado DEX (simulado - na prática usaria SDK do Nado)"""
        try:
            pair = signal['pair']
            side = signal['signal']
            price = signal['price']
            size = self.calculate_position_size(price, self.config.max_risk_per_trade)
            
            self.logger.info(f"🚀 Executando {side.upper()} {pair}")
            self.logger.info(f"   Preço: ${price:.4f}")
            self.logger.info(f"   Tamanho: {size:.4f}")
            self.logger.info(f"   Stop Loss: ${signal['stop_loss']:.4f}")
            self.logger.info(f"   Take Profit: ${signal['take_profit']:.4f}")
            
            # Na prática, aqui seria:
            # 1. Assinar transação com wallet Nado
            # 2. Criar ordem via Nado SDK
            # 3. Submeter para execução
            
            # Simulação de execução:
            execution_success = True  # Na prática verificar se execução ocorreu
            
            if execution_success:
                self.positions[pair] = {
                    'entry_price': price,
                    'size': size,
                    'side': side,
                    'stop_loss': signal['stop_loss'],
                    'take_profit': signal['take_profit'],
                    'entry_time': datetime.now(),
                    'reason': signal['reason']
                }
                
                self.logger.info(f"✅ Trade executado: {side.upper()} {pair} @ ${price:.4f}")
                return True
            else:
                self.logger.error(f"❌ Falha ao executar trade: {pair}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao executar trade: {e}")
            return False
    
    def check_positions(self):
        """Verifica positions ativas"""
        current_time = datetime.now()
        closed_positions = []
        
        for pair, position in self.positions.items():
            entry_price = position['entry_price']
            side = position['side']
            stop_loss = position['stop_loss']
            take_profit = position['take_profit']
            
            # Buscar preço atual (simulação)
            current_price = entry_price * 0.99  # Placeholder
            
            # Verificar stop loss
            if side == 'buy':
                if current_price <= stop_loss:
                    self.logger.info(f"🛑 Stop Loss atingido: {pair}")
                    closed_positions.append(pair)
                elif current_price >= take_profit:
                    self.logger.info(f"🎯 Take Profit atingido: {pair}")
                    closed_positions.append(pair)
            else:  # sell
                if current_price >= stop_loss:
                    self.logger.info(f"🛑 Stop Loss atingido: {pair}")
                    closed_positions.append(pair)
                elif current_price <= take_profit:
                    self.logger.info(f"🎯 Take Profit atingido: {pair}")
                    closed_positions.append(pair)
        
        # Remover positions fechadas
        for pair in closed_positions:
            self._close_position(pair, current_price)
    
    def _close_position(self, pair: str, exit_price: float):
        """Fecha posição e registra métricas"""
        if pair not in self.positions:
            return
        
        position = self.positions[pair]
        entry_price = position['entry_price']
        side = position['side']
        size = position['size']
        
        # Calcular PnL
        if side == 'buy':
            pnl = (exit_price - entry_price) * size
        else:
            pnl = (entry_price - exit_price) * size
        
        # Registrar métricas
        self.trades_history.append({
            'pair': pair,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'side': side,
            'size': size,
            'pnl': pnl,
            'timestamp': datetime.now()
        })
        
        if pnl > 0:
            self.total_profit += pnl
            self.win_count += 1
        elif pnl < 0:
            self.total_loss += abs(pnl)
            self.loss_count += 1
        
        # Remover de positions ativas
        del self.positions[pair]
        
        self.logger.info(f"📊 Position {pair} fechada | PnL: ${pnl:.4f}")
    
    def print_performance_summary(self):
        """Imprime resumo de performance"""
        total_trades = len(self.trades_history)
        win_rate = (self.win_count / total_trades * 100) if total_trades > 0 else 0
        
        print("\n" + "="*80)
        print("📊 PERFORMANCE SUMMARY")
        print("="*80)
        print(f"Trades Totais: {total_trades}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Wins: {self.win_count}")
        print(f"Losses: {self.loss_count}")
        print(f"Lucro Total: ${self.total_profit:.4f}")
        print(f"Perda Total: ${self.total_loss:.4f}")
        print(f"Net PnL: ${self.total_profit - self.total_loss:.4f}")
        print("="*80 + "\n")
    
    async def run_trading_loop(self):
        """Loop principal de trading"""
        self.running = True
        self.logger.info("🚀 Iniciando bot de trading...")
        
        await self.init_exchange()
        
        if not self.exchange:
            return
        
        cycle_count = 0
        
        while self.running:
            try:
                cycle_count += 1
                self.logger.info(f"\n📊 Ciclo #{cycle_count}")
                
                # Coletar dados
                await self.data_collector.collect_all_data()
                
                # Analisar
                analysis = await self.analyzer.analyze_all()
                
                # Verificar sinais
                signals = await self.check_entry_signal(analysis)
                
                # Executar trades (limitado pelo max_positions)
                for signal in signals[:self.config.max_positions]:
                    if len(self.positions) < self.config.max_positions:
                        await self.execute_trade(signal)
                
                # Verificar positions ativas
                self.check_positions()
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.config.execution_interval)
                
            except KeyboardInterrupt:
                self.logger.info("⛑ Bot interrompido pelo usuário")
                break
            except Exception as e:
                self.logger.error(f"❌ Erro no ciclo de trading: {e}")
                await asyncio.sleep(10)  # Aguardar antes de tentar novamente
        
        # Parar e imprimir resumo
        self.running = False
        self.print_performance_summary()
        self.logger.info("✅ Bot finalizado!")
    
    def stop(self):
        """Para o bot"""
        self.running = False
        self.logger.info("🛑 Parando bot de trading...")


async def main():
    """Função principal"""
    config = NadoConfig.from_env()
    
    bot = NadoTradingBot(config)
    await bot.run_trading_loop()


if __name__ == "__main__":
    asyncio.run(main())
