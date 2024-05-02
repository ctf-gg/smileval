import importlib

# https://stackoverflow.com/a/19228066
def import_class(path, classname):
    module = importlib.import_module(path)
    return getattr(module, classname)

def import_class_short(fullpath):
    split: list[str] = fullpath.split(".")
    classname = split.pop()
    path = ".".join(split)
    return import_class(path, classname)