"""
Logging configuration with colored terminal output and clean log files.
"""

import logging
import os
import sys
import io
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, TextIO, Set

from colorama import init, Fore, Style

# Initialize colorama for Windows support
init()

# Regular expression to match ANSI escape sequences
ANSI_ESCAPE_PATTERN = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

# Regular expression to match emoji characters (a basic version)
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251" 
    "]+")

# Set to track messages already logged to prevent duplicates
LOGGED_MESSAGES: Set[str] = set()

class LogSymbols:
    """Symbols for different log levels and states."""
    # Use plain ASCII characters instead of emojis for Windows compatibility
    DEBUG = "[DEBUG]"
    INFO = "[INFO]"
    SUCCESS = "[SUCCESS]"
    WARNING = "[WARNING]"
    ERROR = "[ERROR]"
    CRITICAL = "[CRITICAL]"
    START = "[START]"
    END = "[END]"
    DIVIDER = "-"
    TEST = "[TEST]"
    API = "[API]"
    MODEL = "[MODEL]"

def clean_text(text: str) -> str:
    """Remove ANSI escape sequences and emoji characters from text."""
    # First remove ANSI escape sequences
    text = ANSI_ESCAPE_PATTERN.sub('', text)
    
    # Then remove emoji characters
    text = EMOJI_PATTERN.sub('', text)
    
    # Handle specific problematic Unicode characters that may not be caught by the emoji pattern
    text = text.replace('\U0001f680', '')  # rocket emoji
    text = text.replace('\u274c', '')      # red X mark
    text = text.replace('\u2705', '')      # white check mark
    text = text.replace('\u2728', '')      # sparkles
    text = text.replace('\u26a0', '')      # warning sign
    text = text.replace('\u2757', '')      # exclamation mark
    
    # Replace other non-ASCII characters with their closest ASCII equivalent or empty string
    text = ''.join(c if ord(c) < 128 else '' for c in text)
    
    return text

class ConsoleFormatter(logging.Formatter):
    """Formatter for console output with colors."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }
    
    SYMBOLS = {
        'DEBUG': LogSymbols.DEBUG,
        'INFO': LogSymbols.INFO,
        'WARNING': LogSymbols.WARNING,
        'ERROR': LogSymbols.ERROR,
        'CRITICAL': LogSymbols.CRITICAL
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Check if message already contains formatting
        if hasattr(record, 'formatted') and record.formatted:
            return super().format(record)
        
        log_color = self.COLORS.get(record.levelname, Fore.WHITE)
        log_symbol = self.SYMBOLS.get(record.levelname, "")
        
        # Ensure consistent width for all log levels - padding to match WARNING (7 chars)
        # Store original levelname for restoration later
        original_levelname = record.levelname
        
        # Create padded colored levelname with consistent width
        if record.levelname == 'INFO':
            # INFO needs 3 spaces to match WARNING
            record.levelname = f"{log_color}{'INFO    '}{Style.RESET_ALL}"
        elif record.levelname == 'ERROR':
            # ERROR needs 2 spaces to match WARNING
            record.levelname = f"{log_color}{'ERROR   '}{Style.RESET_ALL}"
        elif record.levelname == 'DEBUG':
            # DEBUG needs 2 spaces to match WARNING
            record.levelname = f"{log_color}{'DEBUG   '}{Style.RESET_ALL}"
        elif record.levelname == 'CRITICAL':
            # CRITICAL is longer than WARNING
            record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        else:
            # WARNING and others
            record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        
        # Save original message
        original_msg = record.msg
        
        # Replace emojis with plain text alternatives in the message
        if isinstance(original_msg, str):
            # Clean the message - remove emojis
            original_msg = clean_text(original_msg)
            
            if 'LLM' in original_msg:
                record.msg = f"{LogSymbols.MODEL} {original_msg}"
            elif 'API' in original_msg:
                record.msg = f"{LogSymbols.API} {original_msg}"
            elif 'TEST' in original_msg:
                record.msg = f"{LogSymbols.TEST} {original_msg}"
            else:
                record.msg = f"{log_symbol} {original_msg}"
        
        record.formatted = True
        result = super().format(record)
        
        # Restore original values for potential reuse
        record.levelname = original_levelname
        record.msg = original_msg
        
        return result

class FileFormatter(logging.Formatter):
    """Clean formatter for log files without colors."""
    
    SYMBOLS = {
        'DEBUG': LogSymbols.DEBUG,
        'INFO': LogSymbols.INFO,
        'WARNING': LogSymbols.WARNING,
        'ERROR': LogSymbols.ERROR,
        'CRITICAL': LogSymbols.CRITICAL
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Check if message already contains formatting
        if hasattr(record, 'formatted') and record.formatted:
            formatted_message = super().format(record)
            # Clean the message of ANSI and emojis
            return clean_text(formatted_message)
        
        log_symbol = self.SYMBOLS.get(record.levelname, "")
        
        # Save original values
        original_levelname = record.levelname
        original_msg = record.msg
        
        # Clean the message of emojis
        if isinstance(original_msg, str):
            original_msg = clean_text(original_msg)
            
            # Check if this is a TERMINAL: message to avoid double formatting
            if original_msg.startswith("TERMINAL:"):
                # Just clean and pass through
                record.msg = original_msg
            else:
                if 'LLM' in original_msg:
                    record.msg = f"{LogSymbols.MODEL} {original_msg}"
                elif 'API' in original_msg:
                    record.msg = f"{LogSymbols.API} {original_msg}"
                elif 'TEST' in original_msg:
                    record.msg = f"{LogSymbols.TEST} {original_msg}"
                else:
                    record.msg = f"{log_symbol} {original_msg}"
        
        record.formatted = True
        formatted_message = super().format(record)
        
        # Restore original values
        record.levelname = original_levelname
        record.msg = original_msg
        if hasattr(record, 'formatted'):
            delattr(record, 'formatted')
        
        # Clean the message of ANSI and emojis
        return clean_text(formatted_message)

class StdoutInterceptor(io.TextIOBase):
    """Class to intercept stdout/stderr and log it."""
    def __init__(self, original_stream: TextIO, logger: logging.Logger, level: int = logging.INFO):
        self.original_stream = original_stream
        self.logger = logger
        self.level = level
        self.buffer = ""
        self.in_logging = False  # To prevent recursive logging
        self.thread_local_context = {}  # To track context per thread

    def write(self, text: str) -> int:
        """
        Write text to the original stream and capture it for logging.
        Returns the number of characters written.
        """
        if self.in_logging:
            # Prevent recursion when logging is calling write
            return self.original_stream.write(text)
        
        try:
            self.in_logging = True
            
            # Clean the text to remove emojis and ANSI codes before logging
            # First clean the text to make it Windows-compatible
            clean_message = clean_text(text)
            
            # Try to write the original text, but fall back to cleaned text if it fails
            try:
                result = self.original_stream.write(text)
            except UnicodeEncodeError:
                # If writing with emojis fails, write the cleaned version
                result = self.original_stream.write(clean_message)
            
            # Process the message for logging
            # Skip if this appears to be a log message (to avoid duplicates)
            if not (re.match(r'\d{2}:\d{2}:\d{2}', clean_message) and "|" in clean_message[:20]):
                self.buffer += clean_message
                if '\n' in self.buffer:
                    lines = self.buffer.split('\n')
                    for line in lines[:-1]:  # Process all complete lines
                        if line.strip():  # Skip empty lines
                            # Skip logging if this line appears to be a log formatting artifact
                            if not (re.match(r'\d{2}:\d{2}:\d{2}', line) and "|" in line[:20]):
                                # Only log if we haven't logged this exact message before
                                msg_hash = f"{line}"
                                if msg_hash not in LOGGED_MESSAGES:
                                    LOGGED_MESSAGES.add(msg_hash)
                                    self.logger.log(self.level, f"TERMINAL: {line}")
                    self.buffer = lines[-1]  # Keep the last incomplete line
        
            return result
        finally:
            self.in_logging = False

    def flush(self) -> None:
        # If there's anything left in the buffer, log it
        if self.buffer.strip() and not self.in_logging:
            self.in_logging = True
            try:
                clean_buffer = clean_text(self.buffer.rstrip())
                # Only log if we haven't logged this exact message before and it doesn't look like a log line
                if (clean_buffer and not re.match(r'\d{2}:\d{2}:\d{2}', clean_buffer) 
                    and "|" not in clean_buffer[:20]):
                    msg_hash = f"{clean_buffer}"
                    if msg_hash not in LOGGED_MESSAGES:
                        LOGGED_MESSAGES.add(msg_hash)
                        self.logger.log(self.level, f"TERMINAL: {clean_buffer}")
                self.buffer = ""
            finally:
                self.in_logging = False
        self.original_stream.flush()
        
    def isatty(self) -> bool:
        return hasattr(self.original_stream, 'isatty') and self.original_stream.isatty()
        
class Logger:
    """Clean logger configuration with separate formatters for console and file."""
    
    @staticmethod
    def get_default_log_file() -> str:
        """Get the default log file path."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        return str(log_dir / f"KeynoteGenie_{datetime.now().strftime('%Y%m%d-%H%M%S')}.log")

    @staticmethod
    def setup(log_file: Optional[str] = None) -> logging.Logger:
        """Set up and configure the logger.
        
        Args:
            log_file: Optional path to the log file. If None, logs to console only.
            
        Returns:
            logging.Logger: Configured logger instance.
        """
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
        # Create console handler with colored formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ConsoleFormatter(
            fmt='%(asctime)s | %(levelname)s | %(name)-12s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)
        
        # File handler if specified with clean formatter
        if log_file:
            try:
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_formatter = FileFormatter(
                    fmt='%(asctime)s | %(levelname)-7s | %(name)-12s | %(message)s',
                    datefmt='%H:%M:%S'
                )
                file_handler.setFormatter(file_formatter)
                file_handler.setLevel(logging.INFO)
                root_logger.addHandler(file_handler)
                print(f"{LogSymbols.SUCCESS} Log file: {log_file}")
            except Exception as e:
                print(f"{LogSymbols.ERROR} Could not create log file: {e}")
        
        # Intercept stdout and stderr
        stdout_interceptor = StdoutInterceptor(sys.stdout, root_logger, logging.INFO)
        stderr_interceptor = StdoutInterceptor(sys.stderr, root_logger, logging.ERROR)
        
        # Save original streams for restoration if needed
        sys._original_stdout = sys.stdout
        sys._original_stderr = sys.stderr
        
        # Replace with interceptors
        sys.stdout = stdout_interceptor
        sys.stderr = stderr_interceptor
        
        # Log startup
        divider = f"{LogSymbols.DIVIDER * 50}"
        root_logger.info(f"KeynoteGenie Starting {LogSymbols.START}")
        root_logger.info(divider)
        
        return root_logger

# Create the default logger instance
default_log_file = Logger.get_default_log_file()
main_logger = Logger.setup(log_file=default_log_file)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    module_name = name.split('.')[-1]
    return logging.getLogger(module_name)

def restore_stdout_stderr():
    """Restore original stdout and stderr streams."""
    if hasattr(sys, '_original_stdout'):
        sys.stdout = sys._original_stdout
    if hasattr(sys, '_original_stderr'):
        sys.stderr = sys._original_stderr 