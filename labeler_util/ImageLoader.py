import os
import numpy as np
import pickle
import pydicom
from PIL import Image
from pydicom.errors import InvalidDicomError
from labeler_util.SUV import getASuv

__all__ = ['ImageLoader']
_suffix = ".png"


class ImageLoader(object):
    """封装加载图像的类"""

    def __init__(self):
        self._ct_img_list = None  # 存储生成CT图像绝对路径字符串的列表
        self._suv_img_list = None  # 存储生成SUV图像绝对路径字符串的列表
        self._pet_img_list = None  # 存储生成PET图像绝对路径字符串的列表
        self._original_suv_img_list = None  # 存储生成原SUV图像绝对路径字符串的列表

    @property
    def cts(self):
        return self._ct_img_list

    @property
    def suvs(self):
        return self._suv_img_list

    @property
    def ori_suvs(self):
        return self._original_suv_img_list

    @property
    def pets(self):
        return self._pet_img_list

    def load_image(self, mode: str, output_image_suffix: str,
                   ct_path=None, ct_output_folder_name=None,
                   pet_path=None, suv_output_folder_name=None, pet_output_folder_name=None,
                   ori_suv_output_folder_name=None) -> None:
        """
        加载病理图像，并生成提取出来的图像，缓存到磁盘上
        :param mode:                        加载模式，目前支持两种：" CT"和"PET-CT"
        :param output_image_suffix:         生成缓存的图像的后缀名, 默认为".png"
        :param ct_path:                     存储CT图像文件夹的绝对路径
        :param ct_output_folder_name:       存储生成缓存的CT图像的文件夹名，例如"ctdata"
        :param pet_path:                    存储PET图像文件夹的绝对路径
        :param suv_output_folder_name:      存储生成缓存的SUV图像的文件夹名，例如"suvdata"
        :param pet_output_folder_name:      存储生成缓存的PET图像的文件夹名，例如"petdata"
        :param ori_suv_output_folder_name:  存储生成缓存的原始SUV图像的文件夹名，例如"ori_suv_data"
        """
        global _suffix
        _suffix = output_image_suffix  # 从配置中设置存储图像后缀名
        if mode == 'CT':  # 如果是CT模式，那么加载CT图像
            self._ct_img_list = dicom_to_png(ct_path, ct_output_folder_name)
        elif mode == "PET_CT":  # 如果是PET_CT模式，那么加载CT图像和PET图像
            self._ct_img_list = dicom_to_png(ct_path, ct_output_folder_name)
            self._original_suv_img_list, self._suv_img_list = self._dicom_to_suv(pet_path, suv_output_folder_name,
                                                                                 ori_suv_output_folder_name)
            self._pet_img_list = self._dicom_to_pet(pet_path, pet_output_folder_name)

    def _dicom_to_suv(self, input_folder: str, output_folder_name: str, ori_output_folder_name: str) -> tuple:
        """
        扫描input_folder中的所有以"PT"开头的文件，计算SUV值和归一化并阈值化的SUV图像，分别存储到文件夹中
        :param input_folder: 输入文件夹绝对路径
        :param output_folder_name: 存储归一化并阈值化的SUV图像文件夹的名称
        :param ori_output_folder_name: 存储原始SUV值文件的文件夹的名称
        :return: 两个tuple组成的tuple，分别是:
                                                (1)阈值化的SUV图像的绝对路径字符串列表
                                                (2)原始SUV值文件的绝对路径字符串列表
        """
        # 如果输出文件夹不存在，那么就创建输出文件夹
        abs_output_folder = os.path.join(input_folder, output_folder_name)
        ori_abs_output_folder = os.path.join(input_folder, ori_output_folder_name)
        if not os.path.isdir(abs_output_folder):
            os.mkdir(abs_output_folder)
        if not os.path.isdir(ori_abs_output_folder):
            os.mkdir(ori_abs_output_folder)
        # 遍历文件夹内所有PET文件
        succeed_list, ori_succeed_list = list(), list()
        for filename in os.listdir(input_folder):
            abs_filename = os.path.join(input_folder, filename)  # 原文件绝对路径
            abs_output_filename = os.path.join(abs_output_folder, filename + _suffix)  # 输出阈值化SUV图像绝对路径
            abs_ori_output_fliename = os.path.join(ori_abs_output_folder, filename + ".suv")  # 输出SUV文件绝对路径
            # 如果已存在就跳过
            if os.path.isfile(abs_output_filename) and os.path.isfile(abs_ori_output_fliename):
                succeed_list.append(abs_output_filename)
                ori_succeed_list.append(abs_ori_output_fliename)
                continue
            # 如果输入不是文件或者不是PT开头则跳过
            if not (os.path.isfile(abs_filename) and filename.startswith("PT")):
                continue
            # 得到SUV值
            _arr = getASuv(abs_filename)
            # 存储原始SUV值
            with open(abs_ori_output_fliename, 'wb') as f:
                pickle.dump(_arr, f)
                ori_succeed_list.append(abs_ori_output_fliename)
            # 计算并存储阈值化图像
            _mask = np.array(_arr > 2.0, dtype=np.uint8)
            _arr *= _mask  # SUV < 2.0 的全部置为0
            if not _arr.min() == _arr.max():  # 归一化
                _arr = (_arr - _arr.min()) / (_arr.max() - _arr.min()) * 255  # 最大值等于最小值，正常归一化
            _arr = np.array(_arr, dtype=np.uint8)  # 改变类型 np.float64 -> np.uint8
            Image.fromarray(_arr).save(abs_output_filename)
            succeed_list.append(abs_output_filename)
        return tuple(ori_succeed_list), tuple(succeed_list)

    def _dicom_to_pet(self, input_folder: str, output_folder_name: str) -> tuple:
        # 如果输出文件夹不存在，那么久创建输出文件夹
        abs_output_folder = os.path.join(input_folder, output_folder_name)
        if not os.path.isdir(abs_output_folder):
            os.mkdir(abs_output_folder)
        # 遍历文件夹内所有PET文件
        succeed_list = list()
        for filename in os.listdir(input_folder):
            abs_filename = os.path.join(input_folder, filename)
            abs_output_folder = os.path.join(input_folder, output_folder_name)
            if os.path.isfile(abs_filename) and filename.startswith("PT"):
                _result = _dicom_to_png(abs_filename, abs_output_folder)
                if _result[0] is True:
                    succeed_list.append(_result[1])
        # 返回所有成功的输出图像的绝对路径
        return tuple(succeed_list)


def dicom_to_png(input_folder: str, output_folder_name: str) -> tuple:
    """
    dicom to png
    :param input_folder: input folder name(absolute path)
    :param output_folder_name: output folder name(just a name, will join to input_folder)
        e.g.
            input_folder =  a\b
            output_folder_name = ddd
        then imgs will puts into a\b\ddd
    :param output_image_suffix: output image suffix, such as .png or .jpg
    :return: a tuple of succeed transformed image file absolute path
    """

    succeed_list = []
    # Traverse files in folder
    for filename in os.listdir(input_folder):
        abs_filename = os.path.join(input_folder, filename)  # abs means absolute
        abs_output_folder = os.path.join(input_folder, output_folder_name)
        if os.path.isfile(abs_filename) and not filename.startswith("OT"):  # OT的我处理不了。。。。
            _result = _dicom_to_png(abs_filename, abs_output_folder)
            if _result[0] is True:
                succeed_list.append(_result[1])
    return tuple(succeed_list)


def _dicom_to_png(dicom_file_path: str, output_folder: str) -> tuple:
    """
    Helper function, generate image file from single dicom file."
    :param dicom_file_path: input dicom file path, must be absolute path
    :param output_folder:  output file dir, must be absolute path
    :return: tuple 
        (if the transformation is successful, generated img path / None)
    """""
    # create image output folder if not exists
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)
    # check if output file exists
    output_filename = os.path.split(dicom_file_path)[1] + _suffix
    abs_output_filename = os.path.join(output_folder, output_filename)
    if os.path.exists(abs_output_filename):
        return True, abs_output_filename
    # load image data
    try:
        data = pydicom.read_file(dicom_file_path)
    except InvalidDicomError:
        return False, None
    # process image data
    arr = data.pixel_array
    img_data = (arr - arr.min()) / (arr.max() - arr.min()) * 255  # 归一化
    img_data = np.array(img_data, dtype=np.uint8)  # 改成uint8类型
    # save image data as png file
    img = Image.fromarray(img_data)
    img.save(abs_output_filename)
    return True, abs_output_filename
