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

    def stats(self, benchmark=""):
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

        # Parse the benchmark table if provided
        quality_scores = {}
        include_quality_score = False  # Flag to indicate if the quality score should be included
        if benchmark:
            lines = benchmark.strip().split('\n')[2:]  # skip the header lines
            for line in lines:
                parts = line.split('|')
                model = parts[1].strip()
                score = parts[2].strip()
                quality_scores[model] = score
            include_quality_score = True

        # Start constructing the Markdown table
        markdown_table = "| Model | Calls | Total Time | Total Return Size | Average Time | Average Size |"
        if include_quality_score:
            markdown_table += " Quality Score |\n"
            markdown_table += "|-------|-------|------------|-------------------|--------------|--------------|---------------|\n"
        else:
            markdown_table += "\n"
            markdown_table += "|-------|-------|------------|-------------------|--------------|--------------|\n"

        # Fill the table with sorted data
        for model, call, total_time, total_return_size, average_time, average_size in zip(models, calls, total_times, total_return_sizes, average_times, average_sizes):
            model_clean = model.replace('gtsystem.','')
            markdown_table += f"| {model_clean} | {call} | {total_time:.2f} | {total_return_size:.2f} | {average_time:.2f} | {average_size:.2f} |"
            if include_quality_score:
                quality_score = quality_scores.get(model_clean, 'N/A')
                markdown_table += f" {quality_score} |"
            markdown_table += "\n"

        return markdown_table

metrics = Instrument()
