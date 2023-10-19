import io
import sys
import time
from types import FunctionType
from contextlib import contextmanager


class Measure(object):
    """
    A toolbox in which you can put a default output
    stream and change this stream for given methods.
    """
    def __init__(self, output: io.IOBase=sys.stdout) -> None:
        self.output = output

    def _function(self, output):
        """
        A special method to mitigate the edge case of the Measure.function.
        """
        def wrapper(func):
            func = self.function(func, output)
            return func
        return wrapper

    def function(self, func_or_output=None, __output=None):
        """
        A decorator to measure the execution
        time of a function or method.
        """
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            diff = round(time.perf_counter() - start, 3)
            output.write(f"{func.__name__} - {diff}s\n")
            return result
        if callable(func_or_output):
            func, output = func_or_output, (__output if __output is not None else self.output)
        elif isinstance(func_or_output, io.IOBase):
            return self._function(func_or_output)
        else:
            return self.function
        return wrapper

    @contextmanager
    def context(self, name="measure.context", output=None):
        """
        Use this with a "with" expression.
        """
        if output is None:
            output = self.output
        try:
            start = time.perf_counter()
            yield None
        finally:
            diff = round(time.perf_counter() - start, 3)
            output.write(f"{name} - {diff}s\n")

    def _class_methods(self, output):
        """
        A special method to mitigate the edge case of the Measure.function.
        """
        def wrapper(cls):
            cls = self.class_methods(cls, output)
            return cls
        return wrapper

    def class_methods(self, cls_or_output=None, __output=None):
        """
        A method that decorates a class to wrap all methods 
        of this class in the Measure.function method.
        """
        if isinstance(cls_or_output, type):
            output = __output
        elif isinstance(cls_or_output, io.IOBase):
            return self._class_methods(cls_or_output)
        else:
            return self.class_methods
        cls = cls_or_output
        namespace = cls.__dict__
        for name, attr in namespace.items():
            if isinstance(attr, FunctionType):
                setattr(cls, name, self.function(attr, output))
        return cls



measure = Measure()
function = measure.function
context = measure.context
class_methods = measure.class_methods