import time
import sys
from contextlib import contextmanager

class Instrument:
    def __init__(self):
        self.stats = {}
        self.tracking_enabled = True  # Default to tracking enabled

    def track(self, func):
        """
        Decorator to conditionally track function calls based on the tracking_enabled flag.
        """
        def wrapper(*args, **kwargs):
            if self.tracking_enabled:
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = round(end_time - start_time, 2)
                size_in_bytes = sys.getsizeof(result)

                if func.__name__ not in self.stats:
                    self.stats[func.__name__] = {'calls': 1, 'total_time': duration, 
                                                'total_return_size': size_in_bytes}
                else:
                    self.stats[func.__name__]['calls'] += 1
                    self.stats[func.__name__]['total_time'] += duration
                    self.stats[func.__name__]['total_time'] = round(self.stats[func.__name__]['total_time'], 2)
                    self.stats[func.__name__]['total_return_size'] += size_in_bytes
            else:
                result = func(*args, **kwargs)

            return result
        return wrapper

    @contextmanager
    def tracking(self, enabled=True):
        """
        Context manager to enable or disable tracking temporarily.
        """
        original_state = self.tracking_enabled
        self.tracking_enabled = enabled
        try:
            yield
        finally:
            self.tracking_enabled = original_state

    def get_stats(self):
        return self.stats

instrument = Instrument()
