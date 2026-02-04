"""
Nado Trading Bot - Utility Functions
Funções auxiliares comuns para o bot
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta


def setup_logger(name: str, log_file: str = "logs/nado_bot.log", level: str = "INFO"):
    """Configura logger padronizado"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
    )
    return logging.getLogger(name)


def format_currency(value: float, decimals: int = 4) -> str:
    """Formata valor como moeda"""
    return f"${value:,.{decimals}f}"


def format_percent(value: float, decimals: int = 2) -> str:
    """Formata valor como percentual"""
    return f"{value:.{decimals}f}%"


def calculate_risk_reward_ratio(risk: float, reward: float) -> float:
    """Calcula ratio risco/recompensa"""
    if risk == 0:
        return 0
    return reward / risk


def validate_pair(pair: str) -> bool:
    """Valida se par é válido (formato BASE/QUOTE)"""
    if '/' not in pair:
        return False
    parts = pair.split('/')
    if len(parts) != 2:
        return False
    if not parts[0] or not parts[1]:
        return False
    return True


def validate_timeframe(timeframe: str, valid_timeframes: List[str] = None) -> bool:
    """Valida se timeframe é válido"""
    if valid_timeframes is None:
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '12h', '1d', '1w']
    
    return timeframe in valid_timeframes


def parse_position_size(config_size: float, account_balance: float = 10000.0) -> float:
    """Calcula tamanho da posição baseado no saldo da conta"""
    if account_balance == 0:
        return config_size  # Valor padrão
    return (config_size / 100) * account_balance


def time_until(target_time: datetime) -> str:
    """Calcula tempo restante até momento"""
    now = datetime.now()
    if target_time <= now:
        return "já passou"
    
    delta = target_time - now
    
    if delta.total_seconds() < 60:
        return f"{int(delta.total_seconds())} segundos"
    elif delta.total_seconds() < 3600:
        return f"{int(delta.total_seconds() // 60)} minutos"
    elif delta.total_seconds() < 86400:
        return f"{int(delta.total_seconds() // 3600)} horas"
    else:
        return f"{int(delta.total_seconds() // 86400)} dias"


def truncate_address(address: str, prefix_length: int = 6, suffix_length: int = 4) -> str:
    """Trunca endereço para exibição"""
    if len(address) <= prefix_length + suffix_length:
        return address
    
    return f"{address[:prefix_length]}...{address[-suffix_length:]}"


class TradeTracker:
    """Rastreador de trades para análise de performance"""
    
    def __init__(self):
        self.trades = []
        self.logger = setup_logger('TradeTracker')
    
    def add_trade(self, trade: Dict):
        """Adiciona trade ao histórico"""
        self.trades.append(trade)
        self.logger.info(f"Trade registrado: {trade.get('pair')} {trade.get('side')} @ {trade.get('entry_price')}")
    
    def get_win_rate(self) -> float:
        """Calcula win rate"""
        if not self.trades:
            return 0.0
        
        wins = sum(1 for t in self.trades if t.get('pnl', 0) > 0)
        total = len(self.trades)
        
        return (wins / total * 100) if total > 0 else 0.0
    
    def get_total_pnl(self) -> float:
        """Calcula PnL total"""
        return sum(t.get('pnl', 0) for t in self.trades)
    
    def get_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calcula Sharpe Ratio"""
        if not self.trades:
            return 0.0
        
        pnls = [t.get('pnl', 0) for t in self.trades]
        returns = [pnl / 10000.0 for pnl in pnls]  # Normalizando
        
        if not returns or len(returns) < 2:
            return 0.0
        
        avg_return = sum(returns) / len(returns)
        std_dev = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
        
        if std_dev == 0:
            return 0.0
        
        return (avg_return - risk_free_rate) / std_dev
    
    def get_max_drawdown(self) -> float:
        """Calcula máximo drawdown"""
        if not self.trades:
            return 0.0
        
        cumulative_pnl = []
        running_pnl = 0.0
        max_drawdown = 0.0
        
        for trade in self.trades:
            pnl = trade.get('pnl', 0)
            running_pnl += pnl
            cumulative_pnl.append(running_pnl)
            
            peak = max(cumulative_pnl)
            drawdown = peak - running_pnl
            
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown
    
    def print_summary(self):
        """Imprime resumo de performance"""
        if not self.trades:
            print("\n📊 Nenhum trade registrado ainda")
            return
        
        print("\n" + "="*80)
        print("📊 PERFORMANCE TRACKER")
        print("="*80)
        print(f"Total Trades: {len(self.trades)}")
        print(f"Win Rate: {self.get_win_rate():.2f}%")
        print(f"Total PnL: ${self.get_total_pnl():.2f}")
        print(f"Sharpe Ratio: {self.get_sharpe_ratio():.2f}")
        print(f"Max Drawdown: ${self.get_max_drawdown():.2f}")
        print("="*80 + "\n")


class AlertManager:
    """Gerenciador de alertas"""
    
    def __init__(self, telegram_token: str = None, chat_id: str = None):
        self.telegram_token = telegram_token
        self.chat_id = chat_id
        self.logger = setup_logger('AlertManager')
        self.alerts_sent = []
    
    async def send_alert(self, message: str, priority: str = "normal"):
        """Envia alerta via Telegram"""
        if not self.telegram_token or not self.chat_id:
            self.logger.warning("Telegram não configurado - alerta não enviado")
            return False
        
        alert_key = f"{priority}:{message[:50]}"
        
        if alert_key in self.alerts_sent:
            self.logger.warning(f"Alerta já enviado: {alert_key}")
            return False
        
        # Aqui seria enviado via Telegram API
        # Por enquanto, apenas log
        self.logger.info(f"🚨 ALERTA [{priority.upper()}]: {message}")
        self.alerts_sent.append(alert_key)
        
        return True
    
    def send_trade_alert(self, trade: Dict):
        """Envia alerta de trade"""
        pair = trade.get('pair', '')
        side = trade.get('side', '')
        price = trade.get('entry_price', 0)
        size = trade.get('size', 0)
        pnl = trade.get('pnl', 0)
        
        emoji = "💰" if pnl > 0 else "📉"
        direction = "COMPRADO" if side == 'buy' else "VENDIDO"
        
        message = f"{emoji} {pair} {direction} @ ${price:.4f} | Tamanho: {size:.4f} | PnL: ${pnl:.2f}"
        
        return self.send_alert(message, priority="normal")
    
    def send_error_alert(self, error: str, pair: str = ""):
        """Envia alerta de erro"""
        message = f"❌ Erro: {error}"
        if pair:
            message += f" | Par: {pair}"
        
        return self.send_alert(message, priority="critical")


if __name__ == "__main__":
    # Testes
    tracker = TradeTracker()
    
    # Adicionar trades de teste
    tracker.add_trade({
        'pair': 'SOL/USDC',
        'side': 'buy',
        'entry_price': 100.0,
        'exit_price': 105.0,
        'size': 10.0,
        'pnl': 50.0
    })
    
    tracker.add_trade({
        'pair': 'SOL/USDC',
        'side': 'sell',
        'entry_price': 105.0,
        'exit_price': 98.0,
        'size': 10.0,
        'pnl': -70.0
    })
    
    tracker.add_trade({
        'pair': 'ETH/USDC',
        'side': 'buy',
        'entry_price': 2000.0,
        'exit_price': 2100.0,
        'size': 5.0,
        'pnl': 500.0
    })
    
    tracker.print_summary()
