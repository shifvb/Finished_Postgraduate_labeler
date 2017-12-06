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