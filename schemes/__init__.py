import importlib

from schemes.interface.module_loader import SSEModuleClassLoader

__builtin_module_class_loader_cache = {}

__loader_name = "sse_module_class_loader"
__schemes_module_path = "schemes"  #


def load_sse_module(sse_module_name: str) -> SSEModuleClassLoader:
    if sse_module_name in __builtin_module_class_loader_cache:
        return __builtin_module_class_loader_cache[sse_module_name]

    try:
        module = importlib.import_module(__schemes_module_path + "." + sse_module_name)
        if not hasattr(module, __loader_name):
            raise ImportError()
        loader = getattr(module, __loader_name)
        __builtin_module_class_loader_cache[sse_module_name] = loader
        return loader
    except ImportError:
        raise ValueError(f"Unsupported SSE Scheme: {sse_module_name}")
