import inspect
from src.handlers.exception_handler import ExceptionHandler

instance_object = ExceptionHandler()

def get_json():
    exception_handlers = {}
    methods = inspect.getmembers(instance_object, predicate=inspect.ismethod)
    for name_method, method in methods: 
        if name_method.startswith("__"): continue
        signature = inspect.signature(method)
        params = list(signature.parameters.values())
        if len(params) == 2: 
            exception_handlers[params[1].annotation] = method
    return exception_handlers   
exception_handlers = get_json()


