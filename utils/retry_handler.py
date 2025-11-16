"""
Retry logic with exponential backoff for file operations
"""

import time
import logging
from typing import Callable, TypeVar, Optional, Any
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryHandler:
    """Handles retries with exponential backoff"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        """
        Initialize retry handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff
            max_delay: Maximum delay in seconds
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def retry(self, exceptions: tuple = (Exception,), on_failure: Optional[Callable] = None):
        """
        Decorator for retrying function calls with exponential backoff.
        
        Args:
            exceptions: Tuple of exceptions to catch and retry on
            on_failure: Optional callback function to call on each failure
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> T:
                last_exception = None
                
                for attempt in range(self.max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt < self.max_retries:
                            # Calculate delay with exponential backoff
                            delay = min(
                                self.base_delay * (2 ** attempt),
                                self.max_delay
                            )
                            
                            logger.warning(
                                f"Attempt {attempt + 1}/{self.max_retries + 1} failed for {func.__name__}: {str(e)}. "
                                f"Retrying in {delay:.2f}s..."
                            )
                            
                            if on_failure:
                                try:
                                    on_failure(attempt + 1, e)
                                except Exception:
                                    pass
                            
                            time.sleep(delay)
                        else:
                            logger.error(
                                f"All {self.max_retries + 1} attempts failed for {func.__name__}: {str(e)}"
                            )
                
                # All retries exhausted, raise the last exception
                raise last_exception
            
            return wrapper
        return decorator


# Global retry handler instance
retry_handler = RetryHandler(max_retries=3, base_delay=1.0, max_delay=60.0)


def retry_file_operation(max_retries: int = 3):
    """
    Decorator specifically for file operations with retry logic.
    
    Args:
        max_retries: Maximum number of retry attempts
    """
    handler = RetryHandler(max_retries=max_retries, base_delay=0.5, max_delay=10.0)
    return handler.retry(exceptions=(IOError, OSError, PermissionError))

