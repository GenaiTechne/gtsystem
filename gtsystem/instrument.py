import time
import sys
import pandas as pd
from contextlib import contextmanager

class Instrument:
    def __init__(self):
        self.stats_data = {}
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
                module_func = func.__module__ + '.' + func.__name__
                if module_func not in self.stats_data:
                    self.stats_data[module_func] = {'calls': 1, 'total_time': duration, 
                                                'total_return_size': size_in_bytes}
                else:
                    self.stats_data[module_func]['calls'] += 1
                    self.stats_data[module_func]['total_time'] += duration
                    self.stats_data[module_func]['total_time'] = round(self.stats_data[module_func]['total_time'], 2)
                    self.stats_data[module_func]['total_return_size'] += size_in_bytes
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

    def stats(self):
        models = []
        calls = []
        total_times = []
        total_return_sizes = []
        for key, value in self.stats_data.items():
            models.append(key)
            calls.append(value['calls'])
            total_times.append(value['total_time'])
            total_return_sizes.append(value['total_return_size'])

        average_times = [total_time / call for total_time, call in zip(total_times, calls)]
        average_sizes = [total_return_size / call for total_return_size, call in zip(total_return_sizes, calls)]

        # Sort the data based on average times in ascending order
        sorted_indices = sorted(range(len(average_times)), key=lambda i: average_times[i])
        models = [models[i] for i in sorted_indices]
        calls = [calls[i] for i in sorted_indices]
        total_times = [total_times[i] for i in sorted_indices]
        total_return_sizes = [total_return_sizes[i] for i in sorted_indices]
        average_times = [average_times[i] for i in sorted_indices]
        average_sizes = [average_sizes[i] for i in sorted_indices]

        # Start constructing the Markdown table
        markdown_table = "| Model | Calls | Total Time | Total Return Size | Average Time | Average Size |\n"
        markdown_table += "|-------|-------|------------|-------------------|--------------|--------------|\n"

        # Fill the table with sorted data
        for i in range(len(models)):
            markdown_table += f"| {models[i]} | {calls[i]} | {total_times[i]:.2f} | {total_return_sizes[i]:.2f} | {average_times[i]:.2f} | {average_sizes[i]:.2f} |\n"

        return markdown_table


metrics = Instrument()
