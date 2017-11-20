import os
import pydicom
from pydicom.errors import InvalidDicomError
import numpy as np
from PIL import Image
from myeuclid_util.SUV import getSUV

__all__ = ['ImageLoader']
_suffix = ".png"


class ImageLoader(object):
    def __init__(self):
        self._ct_img_list = None
        self._suv_img_list = None
        self._pet_img_list = None
        self._suv2_img_list = None  # todo delete it

    def load_image(self, mode: str, output_image_suffix: str,
                   ct_path=None, ct_output_folder_name=None,
                   pet_path=None, suv_output_folder_name=None, pet_output_folder_name=None):
        global _suffix
        _suffix = output_image_suffix
        if mode == 'CT':
            self._ct_img_list = dicom_to_png(ct_path, ct_output_folder_name)
        elif mode == "PET_CT":
            self._ct_img_list = dicom_to_png(ct_path, ct_output_folder_name)
            self._suv_img_list = self._dicom_to_suv(pet_path, suv_output_folder_name)
            self._pet_img_list = self._dicom_to_pet(pet_path, pet_output_folder_name)
            self._suv2_img_list = self._dicom_to_suv2(pet_path, "suv2_image_data") # todo: moveit

    def _dicom_to_suv2(self, input_folder: str, output_folder_name: str) -> tuple:
        # 如果输出文件夹不存在，那么久创建输出文件夹
        abs_output_folder = os.path.join(input_folder, output_folder_name)
        if not os.path.isdir(abs_output_folder):
            os.mkdir(abs_output_folder)
        # 遍历文件夹内所有PET文件
        from myeuclid_util.SUV_2 import getASuv  # todo: moveit
        succeed_list = list()
        abs_output_folder = os.path.join(input_folder, output_folder_name)
        for filename in os.listdir(input_folder):
            abs_filename = os.path.join(input_folder, filename)
            abs_output_filename = os.path.join(abs_output_folder, filename + _suffix)
            if os.path.isfile(abs_output_filename) and os.path.exists(abs_output_filename):
                succeed_list.append(abs_output_filename)
                continue
            if os.path.isfile(abs_filename) and filename.startswith("PT"):
                _arr = getASuv(abs_filename)  # 计算SUV值
                _mask = np.array(_arr > 2, dtype=np.uint8)
                _arr *= _mask  # SUV < 2.0 的全部置为0
                if not _arr.min() == _arr.max():  # 归一化
                    _arr = (_arr - _arr.min()) / (_arr.max() - _arr.min()) * 255  # 最大值等于最小值，正常归一化
                _arr = np.array(_arr, dtype=np.uint8)  # 改变类型 np.float64 -> np.uint8
                Image.fromarray(_arr).save(abs_output_filename)
                succeed_list.append(abs_output_filename)
        # todo: remove it
        print("suv2: ", succeed_list)
        return tuple(succeed_list)


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

    def _dicom_to_suv(self, input_folder: str, output_folder_name: str) -> tuple:
        # # 如果输出文件夹不存在，那么久创建输出文件夹
        # abs_output_folder = os.path.join(input_folder, output_folder_name)
        # if not os.path.isdir(abs_output_folder):
        #     os.mkdir(abs_output_folder)
        # # 遍历文件夹内所有PET文件
        # from myeuclid_util.SUV_2 import getASuv  # todo: moveit
        # succeed_list = list()
        # abs_output_folder = os.path.join(input_folder, output_folder_name)
        # for filename in os.listdir(input_folder):
        #     abs_filename = os.path.join(input_folder, filename)
        #     abs_output_filename = os.path.join(abs_output_folder, filename + _suffix)
        #     if os.path.isfile(abs_filename) and filename.startswith("PT"):
        #         _arr = getASuv(abs_filename)  # 计算SUV值
        #         _mask = np.array(_arr > 2, dtype=np.uint8)
        #         _arr *= _mask  # SUV < 2.0 的全部置为0\
        #         if _arr.min() == _arr.max():  # 归一化
        #             _arr = np.zeros(shape=_arr.shape, dtype=np.uint8)  # 最大值等于最小值，意味着整个数组都是0
        #         else:
        #             _arr = (_arr - _arr.min()) / (_arr.max() - _arr.min()) * 255  # 最大值等于最小值，正常归一化
        #         _arr = np.array(_arr, dtype=np.uint8)  # 改变类型 np.float64 -> np.uint8
        #         Image.fromarray(_arr).save(abs_output_filename)
        #         succeed_list.append(abs_output_filename)
        # return tuple(succeed_list)


        # 如果输出文件夹不存在，那么久创建输出文件夹
        abs_output_folder = os.path.join(input_folder, output_folder_name)
        if not os.path.isdir(abs_output_folder):
            os.mkdir(abs_output_folder)
        abs_output_folder = os.path.join(input_folder, output_folder_name)
        # 计算所有PET图像对应的输出文件的绝对路径
        abs_output_img_paths = [os.path.join(abs_output_folder, _ + _suffix) for _ in os.listdir(input_folder)
                                if os.path.isfile(os.path.join(input_folder, _)) and _.startswith("PT")]
        # 计算输入文件夹内的PET图像的SUV值
        imgs = getSUV(input_folder)
        assert len(imgs) == len(abs_output_img_paths)
        # 将所有 SUV <= 2.0 的像素置为0
        _mask = np.array(imgs > 2, dtype=np.uint8)
        imgs *= _mask
        succeed_list = []
        # 遍历生成的suv数组（保存了所有图像的信息）
        for i in range(len(imgs)):
            abs_output_img_path = abs_output_img_paths[i]  # 得到输出文件绝对路径
            if os.path.exists(abs_output_img_path):  # 如果存在就跳过这个图像的输出
                succeed_list.append(abs_output_img_path)
                continue
            # 保存图像
            img_data = imgs[i]
            if not img_data.max() == img_data.min():  # 如果相等则整个数组都是0
                img_data = (img_data - img_data.min()) / (img_data.max() - img_data.min()) * 255  # 正则化
            img_data = np.array(img_data, dtype=np.uint8)  # 转换诚uint8格式
            Image.fromarray(img_data).save(abs_output_img_path)
            succeed_list.append(abs_output_img_path)
        # 返回列表
        # todo remove it
        print("suv: ", succeed_list)
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


if __name__ == '__main__':
    r = ImageLoader()._dicom_to_suv(r"G:\临时空间\PT00998-2\5", "suv_image_data_v2")
    print(r)
