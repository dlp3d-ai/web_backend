from .motion_file_api_v1 import MotionFileApiV1

_API = dict(
    MotionFileApiV1=MotionFileApiV1,
)


async def build_api(cfg: dict) -> MotionFileApiV1:
    """Build an API instance from a configuration dictionary.

    This function creates and initializes a motion file API instance based on
    the provided configuration. It supports different API types and performs
    startup initialization after instantiation.

    Args:
        cfg (dict):
            Configuration dictionary containing API settings. Must include
            'type' key specifying the API class name, and other parameters
            required for the specific API implementation.

    Returns:
        MotionFileApiV1:
            Initialized and started motion file API instance.

    Raises:
        TypeError:
            If the specified API type is not supported or not found in
            the available API registry.
    """
    cfg = cfg.copy()
    cls_name = cfg.pop('type')
    if cls_name not in _API:
        msg = f'Unknown api type: {cls_name}'
        raise TypeError(msg)
    ret_inst = _API[cls_name](**cfg)
    await ret_inst.startup()
    return ret_inst
