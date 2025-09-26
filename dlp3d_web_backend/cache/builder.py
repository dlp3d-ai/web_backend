from .local_cache import LocalCache

_CACHE = dict(
    LocalCache=LocalCache)


def build_cache(cfg: dict) -> LocalCache:
    """Build a cache instance from a configuration dictionary.

    This function creates and initializes a cache instance based on the
    provided configuration. It supports different cache types and returns
    the appropriate cache implementation.

    Args:
        cfg (dict):
            Configuration dictionary containing cache settings. Must include
            'type' key specifying the cache class name, and other parameters
            required for the specific cache implementation.

    Returns:
        LocalCache:
            Initialized cache instance ready for use.

    Raises:
        TypeError:
            If the specified cache type is not supported or not found in
            the available cache registry.
    """
    cfg = cfg.copy()
    cls_name = cfg.pop('type')
    if cls_name not in _CACHE:
        msg = f'Unknown cache type: {cls_name}'
        raise TypeError(msg)
    ret_inst = _CACHE[cls_name](**cfg)
    return ret_inst
