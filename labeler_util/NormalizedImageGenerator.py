import numpy as np


class NormalizedImageGenerator(object):
    @staticmethod
    def arr_to_arr(_arr: np.ndarray):
        """
        将一个numpy数组正则化（0~255）,并转成np.uint8类型
        :param arr: 要处理的numpy数组
        :return: 值域在0~255之间的uint8数组
        """
        if not _arr.min() == _arr.max():
            _arr = (_arr - _arr.min()) / (_arr.max() - _arr.min()) * 255
        return np.array(_arr, dtype=np.uint8)
