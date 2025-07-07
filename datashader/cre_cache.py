from __future__ import annotations

import hashlib
from numba.core.caching import Cache, _UserProvidedCacheLocator, CompileResultCacheImpl
from numba.core.serialize import dumps
from numba.core.dispatcher import Dispatcher
from numba.extending import _Intrinsic


class _PreciseCacheLocator(_UserProvidedCacheLocator):
    """Cache locator hashing function bytecode and referenced globals."""

    def __init__(self, py_func, py_file):
        super().__init__(py_func, py_file)
        self._py_func = py_func

        code = py_func.__code__
        glbs = py_func.__globals__

        used_globals = {}
        for k in code.co_names:
            if k not in glbs:
                continue
            v = glbs[k]
            if isinstance(v, _Intrinsic):
                v_code = v._defn.__code__.co_code
                used_globals[k] = v_code
            elif isinstance(v, Dispatcher):
                v_code = v.py_func.__code__.co_code
                used_globals[k] = v_code
            else:
                try:
                    # Ensure the global is picklable, otherwise skip it to
                    # avoid failures during caching (e.g. builtins.input in
                    # interactive environments)
                    dumps(v)
                except Exception:
                    continue
                used_globals[k] = v

        func_bytes = code.co_code + dumps(used_globals)
        self._func_hash = hashlib.sha256(func_bytes).hexdigest()

    def get_source_stamp(self):
        return self._func_hash

    def get_disambiguator(self):
        return self._func_hash[:10]

    @classmethod
    def from_function(cls, py_func, py_file):
        return cls(py_func, py_file)


class PreciseCacheImpl(CompileResultCacheImpl):
    _locator_classes = [_PreciseCacheLocator, *CompileResultCacheImpl._locator_classes]


class PreciseCache(Cache):
    """Cache that saves and loads CompileResult objects using precise hashing."""

    _impl_class = PreciseCacheImpl


def enable_precise_caching(self):
    """Enable caching using :class:`PreciseCache` on a Dispatcher."""

    self._cache = PreciseCache(self.py_func)


# Expose method on Dispatcher
Dispatcher.enable_precise_caching = enable_precise_caching
