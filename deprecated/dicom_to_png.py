def deprecated_dicom_to_png(input_folder: str, output_folder_name: str) -> tuple:
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


def deprecated_dicom_to_pet(self, input_folder: str, output_folder_name: str) -> tuple:
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
