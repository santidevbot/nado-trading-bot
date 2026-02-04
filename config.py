"""
Nado Trading Bot - Configuration Manager
Gerencia configurações e credenciais do bot
"""

import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv
from pathlib import Path


@dataclass
class NadoConfig:
    """Configurações do Nado Trading Bot"""
    
    # Wallet
    wallet_private_key: str
    wallet_address: str
    nado_subaccount_id: str = None
    
    # Nado DEX
    nado_chain_id: int = 1  # Nada mainnet
    trading_pairs: List[str] = None
    timeframes: List[str] = None
    
    # Trading
    position_size: float = 100.0  # USDC
    stop_loss_percent: float = 2.0
    take_profit_percent: float = 3.0
    max_positions: int = 3
    
    # Risk Management
    max_risk_per_trade: float = 1.0  # % do capital
    target_win_loss_ratio: float = 2.0
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/trading_bot.log"
    
    # Telegram (opcional)
    telegram_bot_token: str = None
    telegram_chat_id: str = None
    
    # Monitoring
    data_collection_interval: int = 5  # segundos
    analysis_interval: int = 10  # segundos
    execution_interval: int = 15  # segundos
    
    @classmethod
    def from_env(cls, env_file: str = ".env"):
        """Carrega configurações de arquivo .env"""
        env_path = Path(env_file)
        
        if not env_path.exists():
            raise FileNotFoundError(f"Arquivo {env_file} não encontrado. Copie .env.example para .env")
        
        load_dotenv(env_file)
        
        # Pairs e timeframes
        pairs_str = os.getenv("TRADING_PAIRS", "SOL/USDC,ETH/USDC")
        timeframes_str = os.getenv("TIMEFRAMES", "5m,15m,30m")
        
        return cls(
            # Wallet
            wallet_private_key=os.getenv("WALLET_PRIVATE_KEY", ""),
            wallet_address=os.getenv("WALLET_ADDRESS", ""),
            nado_subaccount_id=os.getenv("NADO_SUBACCOUNT_ID"),
            
            # Nado DEX
            nado_chain_id=int(os.getenv("NADO_CHAIN_ID", "1")),
            trading_pairs=[p.strip() for p in pairs_str.split(",")],
            timeframes=[t.strip() for t in timeframes_str.split(",")],
            
            # Trading
            position_size=float(os.getenv("POSITION_SIZE", "100")),
            stop_loss_percent=float(os.getenv("STOP_LOSS_PERCENT", "2")),
            take_profit_percent=float(os.getenv("TAKE_PROFIT_PERCENT", "3")),
            max_positions=int(os.getenv("MAX_POSITIONS", "3")),
            
            # Risk Management
            max_risk_per_trade=float(os.getenv("MAX_RISK_PER_TRADE", "1")),
            target_win_loss_ratio=float(os.getenv("TARGET_WIN_LOSS_RATIO", "2")),
            
            # Logging
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "logs/trading_bot.log"),
            
            # Telegram
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
            
            # Monitoring
            data_collection_interval=int(os.getenv("DATA_COLLECTION_INTERVAL", "5")),
            analysis_interval=int(os.getenv("ANALYSIS_INTERVAL", "10")),
            execution_interval=int(os.getenv("EXECUTION_INTERVAL", "15"))
        )
    
    def validate(self) -> bool:
        """Valida configurações"""
        if not self.wallet_private_key and not self.nado_subaccount_id:
            print("❌ Erro: WALLET_PRIVATE_KEY ou NADO_SUBACCOUNT_ID deve ser definido")
            return False
        
        if not self.wallet_address:
            print("❌ Erro: WALLET_ADDRESS deve ser definido")
            return False
        
        if not self.trading_pairs:
            print("❌ Erro: TRADING_PAIRS deve ser definido")
            return False
        
        if not self.timeframes:
            print("❌ Erro: TIMEFRAMES deve ser definido")
            return False
        
        print("✅ Configurações válidas!")
        return True


def get_config() -> NadoConfig:
    """Retorna instância de configuração"""
    try:
        config = NadoConfig.from_env()
        config.validate()
        return config
    except Exception as e:
        print(f"❌ Erro ao carregar configurações: {e}")
        raise


if __name__ == "__main__":
    config = get_config()
    print("\n📊 Configurações Atuais:")
    print(f"Wallet Address: {config.wallet_address[:10]}...{config.wallet_address[-4:]}")
    print(f"Trading Pairs: {', '.join(config.trading_pairs)}")
    print(f"Timeframes: {', '.join(config.timeframes)}")
    print(f"Position Size: ${config.position_size}")
    print(f"Stop Loss: {config.stop_loss_percent}%")
    print(f"Take Profit: {config.take_profit_percent}%")
