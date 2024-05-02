import importlib

# https://stackoverflow.com/a/19228066
def import_class(path):
    module = importlib.import_module(path)
    return getattr(module, 'MyClass')