import numpy as np


class ThresholdImageGenerator(object):
    @staticmethod
    def arr_to_arr(arr: np.ndarray, threshold: float):
        """
        将一个numpy数组形式的图像阈值化，并归一化
        :param arr: 要处理的numpy数组
        :param threshold: 阈值
        :return: 阈值化并归一化的， numpy array形式的图像
        """
        # 计算并存储阈值化图像
        _mask = np.array(arr > threshold, dtype=np.uint8)
        _arr = arr * _mask  # SUV < 2.0 的全部置为0
        if not _arr.min() == _arr.max():  # 归一化
            _arr = (_arr - _arr.min()) / (_arr.max() - _arr.min()) * 255  # 最大值等于最小值，正常归一化
        return np.array(_arr, dtype=np.uint8)  # 改变类型 np.float64 -> np.uint8
