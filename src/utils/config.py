"""
Configuration management utilities
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file"""
    if config_path is None:
        # Try to find config file
        possible_paths = [
            'config/config.yaml',
            'config/config.yml',
            '../config/config.yaml',
            '../config/config.yml',
            '../../config/config.yaml',
            '../../config/config.yml'
        ]
        
        config_path = None
        for path in possible_paths:
            if os.path.exists(path):
                config_path = path
                break
        
        if config_path is None:
            raise FileNotFoundError(
                "Configuration file not found. Please create config/config.yaml "
                "from config/config.example.yaml"
            )
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate required sections
        validate_config(config)
        
        # Apply environment variable overrides
        config = apply_env_overrides(config)
        
        logger.info(f"Configuration loaded from: {config_path}")
        return config
        
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {e}")


def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration structure"""
    required_sections = ['slack', 'openai', 'sources', 'database']
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate Slack config
    slack_config = config['slack']
    if not slack_config.get('bot_token'):
        raise ValueError("Slack bot_token is required")
    
    # Validate OpenAI config
    openai_config = config['openai']
    if not openai_config.get('api_key'):
        raise ValueError("OpenAI api_key is required")
    
    # Validate database config
    db_config = config['database']
    if not db_config.get('path'):
        raise ValueError("Database path is required")


def apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to configuration"""
    
    # Slack configuration
    if os.getenv('SLACK_BOT_TOKEN'):
        config['slack']['bot_token'] = os.getenv('SLACK_BOT_TOKEN')
    
    if os.getenv('SLACK_APP_TOKEN'):
        config['slack']['app_token'] = os.getenv('SLACK_APP_TOKEN')
    
    if os.getenv('SLACK_SIGNING_SECRET'):
        config['slack']['signing_secret'] = os.getenv('SLACK_SIGNING_SECRET')
    
    # OpenAI configuration
    if os.getenv('OPENAI_API_KEY'):
        config['openai']['api_key'] = os.getenv('OPENAI_API_KEY')
    
    if os.getenv('OPENAI_MODEL'):
        config['openai']['model'] = os.getenv('OPENAI_MODEL')
    
    # Database configuration
    if os.getenv('DATABASE_PATH'):
        config['database']['path'] = os.getenv('DATABASE_PATH')
    
    # Twitter API (if using social media collection)
    if os.getenv('TWITTER_BEARER_TOKEN'):
        if 'social' not in config:
            config['social'] = {}
        config['social']['twitter_bearer_token'] = os.getenv('TWITTER_BEARER_TOKEN')
    
    return config


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """Get configuration value using dot notation (e.g., 'slack.bot_token')"""
    keys = key_path.split('.')
    value = config
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def setup_logging(config: Dict[str, Any]) -> None:
    """Setup logging based on configuration"""
    logging_config = config.get('logging', {})
    
    # Create logs directory if it doesn't exist
    log_files = logging_config.get('files', {})
    for log_file in log_files.values():
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    log_level = getattr(logging, logging_config.get('level', 'INFO').upper())
    log_format = logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Basic configuration
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # Console output
            logging.FileHandler(
                log_files.get('main', 'logs/ai_news_bot.log'),
                encoding='utf-8'
            )
        ]
    )
    
    # Setup error logging
    error_handler = logging.FileHandler(
        log_files.get('errors', 'logs/errors.log'),
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format))
    
    # Add error handler to root logger
    logging.getLogger().addHandler(error_handler)
    
    # Setup collection logging
    collection_logger = logging.getLogger('collection')
    collection_handler = logging.FileHandler(
        log_files.get('collection', 'logs/collection.log'),
        encoding='utf-8'
    )
    collection_handler.setFormatter(logging.Formatter(log_format))
    collection_logger.addHandler(collection_handler)
    collection_logger.setLevel(log_level)


def create_example_config() -> None:
    """Create example configuration file if it doesn't exist"""
    config_dir = Path('config')
    config_dir.mkdir(exist_ok=True)
    
    example_path = config_dir / 'config.example.yaml'
    config_path = config_dir / 'config.yaml'
    
    if not config_path.exists() and example_path.exists():
        # Copy example to actual config
        with open(example_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Created configuration file: {config_path}")
        print("Please edit the configuration file with your actual API keys and settings.")


def get_sources_config(config: Dict[str, Any], language: Optional[str] = None) -> Dict[str, Any]:
    """Get sources configuration, optionally filtered by language"""
    sources = config.get('sources', {})
    
    if language:
        return sources.get(language, {})
    
    return sources


def get_tagging_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get tagging configuration"""
    return config.get('tagging', {})


def get_slack_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get Slack configuration"""
    return config.get('slack', {})


def get_openai_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get OpenAI configuration"""
    return config.get('openai', {})


def get_schedule_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get schedule configuration"""
    return config.get('schedule', {})


def get_performance_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get performance configuration"""
    return config.get('performance', {
        'max_concurrent_requests': 10,
        'request_timeout': 30,
        'retry_attempts': 3,
        'retry_delay': 5,
        'rate_limiting': {
            'requests_per_minute': 60,
            'burst_limit': 10
        }
    })


def get_filtering_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get content filtering configuration"""
    return config.get('filtering', {
        'min_article_length': 100,
        'max_article_age_days': 7,
        'duplicate_detection': {
            'enabled': True,
            'similarity_threshold': 0.8
        },
        'blocked_domains': [],
        'required_keywords': []
    })
