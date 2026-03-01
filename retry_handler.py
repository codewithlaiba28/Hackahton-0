#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retry Handler - GOLD TIER
Personal AI Employee Hackathon 0

Provides reusable retry logic with exponential backoff for all AI Employee operations.

Usage:
    from retry_handler import with_retry, RetryConfig
    
    @with_retry(max_attempts=3, delay=1.0)
    def send_email(to, subject, body):
        # Your code here
        pass
"""

import time
import logging
from typing import Callable, Any, Optional, Tuple, Type
from functools import wraps
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential: bool = True,
        exceptions: Optional[Tuple[Type[Exception], ...]] = None,
        on_retry: Optional[Callable[[int, Exception, float], None]] = None,
        on_failure: Optional[Callable[[Exception, int], None]] = None
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of attempts (default: 3)
            base_delay: Base delay between retries in seconds (default: 1.0)
            max_delay: Maximum delay between retries (default: 60.0)
            exponential: Use exponential backoff (default: True)
            exceptions: Tuple of exception types to catch (default: all)
            on_retry: Callback(attempt, exception, delay) called before each retry
            on_failure: Callback(exception, attempts) called on final failure
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential = exponential
        self.exceptions = exceptions or (Exception,)
        self.on_retry = on_retry
        self.on_failure = on_failure


class RetryExhaustedError(Exception):
    """Raised when all retry attempts are exhausted."""
    
    def __init__(self, message: str, last_error: Exception, attempts: int):
        super().__init__(message)
        self.last_error = last_error
        self.attempts = attempts


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential: bool = True,
    exceptions: Optional[Tuple[Type[Exception], ...]] = None,
    logger: Optional[logging.Logger] = None
) -> Callable:
    """
    Decorator for automatic retry with configurable backoff.
    
    Args:
        max_attempts: Maximum retry attempts (default: 3)
        base_delay: Base delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exponential: Use exponential backoff (default: True)
        exceptions: Exception types to catch (default: all)
        logger: Logger for retry messages (default: creates one)
        
    Returns:
        Decorated function
        
    Example:
        @with_retry(max_attempts=3, base_delay=1.0)
        def fetch_data(url):
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential=exponential,
        exceptions=exceptions
    )
    
    # Setup logger
    if logger is None:
        logger = logging.getLogger('RetryHandler')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
            logger.addHandler(handler)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_error = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                
                except config.exceptions as e:
                    last_error = e
                    
                    # Calculate delay
                    if config.exponential:
                        delay = config.base_delay * (2 ** attempt)
                    else:
                        delay = config.base_delay
                    
                    delay = min(delay, config.max_delay)
                    
                    # Log retry
                    if attempt < config.max_attempts - 1:
                        logger.warning(
                            f"{func.__name__} attempt {attempt + 1}/{config.max_attempts} failed: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        
                        # Call retry callback if provided
                        if config.on_retry:
                            config.on_retry(attempt, e, delay)
                        
                        # Wait before retry
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"{func.__name__} failed after {config.max_attempts} attempts: {e}"
                        )
                        
                        # Call failure callback if provided
                        if config.on_failure:
                            config.on_failure(e, config.max_attempts)
            
            # All attempts exhausted
            raise RetryExhaustedError(
                f"{func.__name__} failed after {config.max_attempts} attempts",
                last_error,
                config.max_attempts
            )
        
        return wrapper
    return decorator


def retry_function(
    func: Callable,
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs
) -> Any:
    """
    Execute a function with retry logic (non-decorator usage).
    
    Args:
        func: Function to execute
        *args: Positional arguments for func
        config: RetryConfig object
        **kwargs: Keyword arguments for func
        
    Returns:
        Result of func
        
    Example:
        result = retry_function(
            send_email,
            to="user@example.com",
            subject="Test",
            body="Hello",
            config=RetryConfig(max_attempts=3)
        )
    """
    if config is None:
        config = RetryConfig()
    
    last_error = None
    
    for attempt in range(config.max_attempts):
        try:
            return func(*args, **kwargs)
        
        except config.exceptions as e:
            last_error = e
            
            # Calculate delay
            if config.exponential:
                delay = config.base_delay * (2 ** attempt)
            else:
                delay = config.base_delay
            
            delay = min(delay, config.max_delay)
            
            # Log retry
            if attempt < config.max_attempts - 1:
                logging.warning(
                    f"{func.__name__} attempt {attempt + 1}/{config.max_attempts} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                
                # Call retry callback if provided
                if config.on_retry:
                    config.on_retry(attempt, e, delay)
                
                # Wait before retry
                time.sleep(delay)
            else:
                logging.error(
                    f"{func.__name__} failed after {config.max_attempts} attempts: {e}"
                )
                
                # Call failure callback if provided
                if config.on_failure:
                    config.on_failure(e, config.max_attempts)
    
    # All attempts exhausted
    raise RetryExhaustedError(
        f"{func.__name__} failed after {config.max_attempts} attempts",
        last_error,
        config.max_attempts
    )


class RetryContext:
    """Context manager for retry logic."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """
        Initialize retry context.
        
        Args:
            config: RetryConfig object
        """
        self.config = config or RetryConfig()
        self.attempt = 0
        self.last_error: Optional[Exception] = None
    
    def __enter__(self) -> 'RetryContext':
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None:
            # No exception, success
            return True
        
        if not issubclass(exc_type, self.config.exceptions):
            # Not a retryable exception
            return False
        
        self.last_error = exc_val
        self.attempt += 1
        
        if self.attempt >= self.config.max_attempts:
            # All attempts exhausted
            logging.error(
                f"Operation failed after {self.attempt} attempts: {exc_val}"
            )
            return False  # Re-raise exception
        
        # Calculate delay
        if self.config.exponential:
            delay = self.config.base_delay * (2 ** (self.attempt - 1))
        else:
            delay = self.config.base_delay
        
        delay = min(delay, self.config.max_delay)
        
        # Log retry
        logging.warning(
            f"Attempt {self.attempt}/{self.config.max_attempts} failed: {exc_val}. "
            f"Retrying in {delay:.1f}s..."
        )
        
        # Call retry callback if provided
        if self.config.on_retry:
            self.config.on_retry(self.attempt - 1, exc_val, delay)
        
        # Wait before retry
        time.sleep(delay)
        
        return True  # Suppress exception, will retry
    
    def should_retry(self) -> bool:
        """Check if more retries are available."""
        return self.attempt < self.config.max_attempts


# Pre-configured retry decorators for common scenarios

# Quick retry (3 attempts, 1s base delay)
quick_retry = with_retry(max_attempts=3, base_delay=1.0)

# Standard retry (3 attempts, 2s base delay)
standard_retry = with_retry(max_attempts=3, base_delay=2.0)

# Aggressive retry (5 attempts, 1s base delay)
aggressive_retry = with_retry(max_attempts=5, base_delay=1.0)

# Conservative retry (3 attempts, 5s base delay)
conservative_retry = with_retry(max_attempts=3, base_delay=5.0)

# Network retry (for API calls)
network_retry = with_retry(
    max_attempts=3,
    base_delay=1.0,
    max_delay=30.0,
    exceptions=(ConnectionError, TimeoutError, OSError)
)


if __name__ == '__main__':
    # Test the retry handler
    print("\n" + "="*60)
    print("RETRY HANDLER TEST")
    print("="*60)
    
    # Test 1: Function that succeeds on first try
    @with_retry(max_attempts=3)
    def always_succeeds():
        return "Success!"
    
    result = always_succeeds()
    print(f"\n[OK] always_succeeds: {result}")
    
    # Test 2: Function that fails then succeeds
    attempt_count = 0
    
    @with_retry(max_attempts=3)
    def fails_twice_then_succeeds():
        global attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ValueError(f"Fail attempt {attempt_count}")
        return f"Success on attempt {attempt_count}"
    
    result = fails_twice_then_succeeds()
    print(f"[OK] fails_twice_then_succeeds: {result}")
    
    # Test 3: Function that always fails
    @with_retry(max_attempts=3)
    def always_fails():
        raise ValueError("Always fails")
    
    try:
        always_fails()
        print("[FAIL] always_fails should have raised exception")
    except RetryExhaustedError as e:
        print(f"[OK] always_fails correctly exhausted retries: {e.attempts} attempts")
    
    # Test 4: Using RetryContext
    print("\n[OK] Testing RetryContext...")
    with RetryContext(RetryConfig(max_attempts=3, base_delay=0.1)) as ctx:
        if ctx.attempt < 2:
            raise ValueError("Fail in context")
        print(f"[OK] RetryContext succeeded on attempt {ctx.attempt + 1}")
    
    # Test 5: Pre-configured decorators
    @quick_retry
    def quick_test():
        return "Quick!"
    
    result = quick_test()
    print(f"[OK] quick_retry: {result}")
    
    print("\n" + "="*60)
    print("RETRY HANDLER READY")
    print("="*60 + "\n")
