import importlib.util
import os
import sys


def _load_cre_cache():
    module_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'datashader', 'cre_cache.py'
    )
    spec = importlib.util.spec_from_file_location('cre_cache', module_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['cre_cache'] = mod
    spec.loader.exec_module(mod)
    return mod


def test_precise_cache_skips_unpicklable_global():
    cre_cache = _load_cre_cache()

    class Bad:
        def __getstate__(self):
            raise RuntimeError('no pickle')

        def __bool__(self):
            return True

    bad_obj = Bad()

    def func(x):
        if bad_obj:
            return x + 1
        return x

    locator = cre_cache._PreciseCacheLocator.from_function(func, func.__code__.co_filename)
    assert isinstance(locator.get_source_stamp(), str)
