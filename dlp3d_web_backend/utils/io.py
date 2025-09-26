import io

import numpy as np


def load_npz(file_to_load: io.BytesIO | str,
             float_dtype: np.floating | None = None) -> dict:
    """Load npz file with allow_pickle=True.

    Args:
        file_to_load (Union[io.BytesIO, str]):
            Path to a npz file, or a io.BytesIO object.
    Returns:
        dict: Loaded data.
    """
    with np.load(file_to_load, allow_pickle=True) as npz_file:
        tmp_data_dict = dict(npz_file)
        npz_dict = dict()
        for key, value in tmp_data_dict.items():
            if isinstance(value, np.ndarray) and\
                    len(value.shape) == 0:
                # value is not an ndarray before dump
                value = value.item()
            elif isinstance(value, np.ndarray) and\
                    len(value.shape) == 1 and\
                    isinstance(value[0], np.str_):
                value = value.tolist()
            elif float_dtype is not None and \
                    isinstance(value, np.ndarray) and \
                    value.dtype.kind == 'f':
                value = value.astype(float_dtype)
            npz_dict.__setitem__(key, value)
    return npz_dict


