"""
Logging utility for the Course AI Assistant.
Provides structured logging with color output and file logging.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
import json
import colorlog


def setup_logger(name: str, log_file: str = None, level: str = "INFO") -> logging.Logger:
    """
    Setup logger with color output and file logging.
    
    Args:
        name: Logger name
        log_file: Path to log file (optional)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler with colors
    console_handler = colorlog.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    console_format = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s%(reset)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (if log_file is provided)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level.upper()))
        
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


def log_interaction(
    question: str,
    answer: str,
    sources: list,
    session_id: str,
    response_time: float,
    log_file: str = "./logs/interactions.jsonl"
):
    """
    Log user interaction to JSONL file for analysis.
    
    Args:
        question: User question
        answer: AI-generated answer
        sources: List of source documents
        session_id: Session identifier
        response_time: Response time in seconds
        log_file: Path to interaction log file
    """
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    interaction = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "question": question,
        "answer": answer,
        "sources": sources,
        "response_time": response_time
    }
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(interaction, ensure_ascii=False) + '\n')
