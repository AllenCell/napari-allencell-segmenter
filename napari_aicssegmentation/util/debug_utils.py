import functools
import logging
import time

log = logging.getLogger(__name__)

def debug_func(func, _cls=None):
    """
    Decorator: applies set of debug features (such as logging and performance counter) to a function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        name = func.__name__ if _cls is None else f"{_cls.__name__}::{func.__name__}"
        log.setLevel(logging.DEBUG)        
        log.debug(f"START {name}")

        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()    
        run_time = end_time - start_time

        log.debug(f"END {name}. Finished in {run_time:.4f} secs")
        return value
    return wrapper

def debug_class(_cls=None):
    """
    Decorator: applies set of debug features (such as logging and performance counter) to a all methods of a class
    """    
    def wrap(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, debug_func(getattr(cls, attr), cls))
        return cls                
    
    if _cls is None:        
        return wrap
    
    return wrap(_cls)    