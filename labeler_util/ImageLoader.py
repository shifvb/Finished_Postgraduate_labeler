import os
import pickle
import pydicom
from labeler_util.SUV import getASuv


class ImageLoader(object):
    """封装加载图像的类"""

    def __init__(self):
        self._ct_img_list = None  # 存储生成CT图像绝对路径字符串的列表
        self._suv_value_list = None  # 存储生成SUV文件绝对路径字符串的列表
        self._pet_img_list = None  # 存储生成PET图像绝对路径字符串的列表

    @property
    def cts(self):
        return self._ct_img_list

    @property
    def pets(self):
        return self._pet_img_list

    @property
    def suvs(self):
        return self._suv_value_list

    def load_image(self, ct_path=None, ct_output_folder_name=None,
                   pet_path=None, suv_output_folder_name=None, pet_output_folder_name=None) -> None:
        """
        加载病理图像，并生成提取出来的图像，缓存到磁盘上
        :param ct_path:                     存储CT图像文件夹的绝对路径
        :param ct_output_folder_name:       存储生成缓存的CT图像的文件夹名，例如"ctdata"
        :param pet_path:                    存储PET图像文件夹的绝对路径
        :param suv_output_folder_name:      存储生成缓存的SUV文件的文件夹名，例如"suvdata"
        :param pet_output_folder_name:      存储生成缓存的PET图像的文件夹名，例如"petdata"
        """
        self._ct_img_list = self._dicom_to_ct(ct_path, ct_output_folder_name)
        self._suv_value_list = self._dicom_to_suv(pet_path, suv_output_folder_name)
        self._pet_img_list = self._dicom_to_pet(pet_path, pet_output_folder_name)

    def _dicom_to_suv(self, input_folder: str, output_folder_name: str) -> tuple:
        """
        扫描input_folder中的所有以"PT"开头的文件，计算SUV值，存储到文件夹中
        :param input_folder: 输入文件夹绝对路径
        :param output_folder_name: 存储SUV值的文件夹的名称
        :return: SUV值文件的绝对路径字符串列表
        """
        # 如果输出文件夹不存在，那么就创建输出文件夹
        abs_output_folder = os.path.join(input_folder, output_folder_name)
        if not os.path.isdir(abs_output_folder):
            os.mkdir(abs_output_folder)
        # 遍历文件夹内所有PET文件
        succeed_list = list()
        for filename in os.listdir(input_folder):
            abs_filename = os.path.join(input_folder, filename)  # 原文件绝对路径
            abs_output_filename = os.path.join(abs_output_folder, filename + ".suv")  # 输出SUV值文件的绝对路径
            # 如果已存在就跳过
            if os.path.isfile(abs_output_filename):
                succeed_list.append(abs_output_filename)
                continue
            # 如果输入不是文件或者不是PT开头则跳过
            if not (os.path.isfile(abs_filename) and filename.startswith("PT")):
                continue
            # 得到SUV值
            _arr = getASuv(abs_filename)
            # 存储SUV值
            with open(abs_output_filename, 'wb') as f:
                pickle.dump(_arr, f)
                succeed_list.append(abs_output_filename)
        return tuple(succeed_list)

    def _dicom_to_pet(self, input_folder: str, output_folder_name: str) -> tuple:
        """
        扫描input_folder中的所有以"PT"开头的文件，
        计算PET值，存储到文件夹中
        :param input_folder: 输入文件夹绝对路径
        :param output_folder_name: 存储PET值的文件夹的名称
        :return: PET值的文件的绝对路径字符串列表
        """
        # 如果输入文件夹不存在，那么就创建输出文件夹
        abs_output_folder = os.path.join(input_folder, output_folder_name)
        if not os.path.isdir(abs_output_folder):
            os.mkdir(abs_output_folder)
        # 遍历文件夹内所有PET文件
        succeed_list = list()
        for filename in os.listdir(input_folder):
            abs_filename = os.path.join(input_folder, filename)  # 原文件绝对路径
            abs_output_filename = os.path.join(abs_output_folder, filename + ".pet")  # 输入PET值文件的绝对路径
            # 如果已经存在就跳过
            if os.path.isfile(abs_output_filename):
                succeed_list.append(abs_output_filename)
                continue
            # 如果输入不是文件或者不是PT开头则跳过
            if not (os.path.isfile(abs_filename) and filename.startswith("PT")):
                continue
            # 得到PET值
            _arr = pydicom.read_file(abs_filename).pixel_array
            with open(abs_output_filename, 'wb') as f:
                pickle.dump(_arr, f)
                succeed_list.append(abs_output_filename)
        return tuple(succeed_list)

    def _dicom_to_ct(self, input_folder: str, output_folder_name: str) -> tuple:
        """
        扫描input_folder中的所有以"CT"开头的文件，
        计算SUV值
            (shape: (512, 512), min: 0, max: 4096, dtype: int16)，
        存储到文件夹中
        :param input_folder: 输入文件夹的绝对路径
        :param output_folder_name: 存储CT值的文件夹的名称
        :return: CT值文件的绝对路径字符串列表
        """
        # 如果输出文件夹不存在，那么就创建输出文件夹
        abs_output_folder = os.path.join(input_folder, output_folder_name)
        if not os.path.isdir(abs_output_folder):
            os.mkdir(abs_output_folder)
        # 遍历文件夹内所有CT文件
        succeed_list = list()
        for filename in os.listdir(input_folder):
            abs_filename = os.path.join(input_folder, filename)  # 原文件绝对路径
            abs_output_filename = os.path.join(abs_output_folder, filename + ".ct")  # 输出CT值文件的绝对路径
            # 如果已存在就跳过
            if os.path.isfile(abs_output_filename):
                succeed_list.append(abs_output_filename)
                continue
            # 如果输入不是文件或者不是CT开头则跳过
            if not (os.path.isfile(abs_filename) and filename.startswith("CT")):
                continue
            # 得到CT值
            _arr = pydicom.read_file(abs_filename).pixel_array
            with open(abs_output_filename, 'wb') as f:
                pickle.dump(_arr, f)
                succeed_list.append(abs_output_filename)
        return tuple(succeed_list)


if __name__ == '__main__':
    image_loader = ImageLoader()
    image_loader._dicom_to_pet(r"C:\Users\anonymous\Desktop\PT00998-2\5", "test_pet")
