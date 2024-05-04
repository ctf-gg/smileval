import importlib
from .models import ChatCompletionOptions

# https://stackoverflow.com/a/19228066
def import_class(path, classname):
    module = importlib.import_module(path)
    return getattr(module, classname)

def import_class_short(fullpath):
    split: list[str] = fullpath.split(".")
    classname = split.pop()
    path = ".".join(split)
    return import_class(path, classname)

import hashlib
def sha256(input_string) -> str:
    return hashlib.sha256(input_string.encode()).hexdigest()

def map_attribute(options: ChatCompletionOptions, target: dict, option_key: str, target_key: str):
    if options.__dict__[option_key] is not None:
        target[target_key] = options.__dict__[option_key] # copy value