import os
import pydicom


def load_patient_info(ct_workspace: str, pet_workspace: str) -> dict:
    """
    根据部分dicom文件加载病人信息
    :param ct_workspace: ct文件夹，绝对路径
    :param pet_workspace: pet文件夹，绝对路径
    :return: 一个病人信息的字典
    """
    abs_names = [os.path.join(ct_workspace, _) for _ in os.listdir(ct_workspace) if _.startswith("CT")]
    abs_file = [_ for _ in abs_names if os.path.isfile(_)][0]
    ct_data = pydicom.read_file(abs_file)
    abs_names = [os.path.join(pet_workspace, _) for _ in os.listdir(pet_workspace) if _.startswith("PT")]
    abs_file = [_ for _ in abs_names if os.path.isfile(_)][0]
    pet_data = pydicom.read_file(abs_file)

    d = {  # d for 'dict'
        "patient_id": 'PatientID',
        "patient_name": 'PatientName',
        "patient_birthday": "PatientBirthDate",
        "patient_sex": "PatientSex",
        "patient_age": "PatientAge",
        "patient_weight": "PatientWeight",
        "patient_height": "PatientSize",
        "pet_tracer_name": (0x9, 0x1036),
        "patient_tracer_activity": "RadiopharmaceuticalInformationSequence"
    }
    for key in d:
        d[key] = pet_data.get(d[key], "")

    # 处理生日: '19920909' -> '1992年09月09日'
    if not d["patient_birthday"] == "":
        _ = d["patient_birthday"]
        d["patient_birthday"] = _[:4] + "年" + _[4:6] + "月" + _[6:] + "日"
    # 处理性别: 'M' -> '男'
    if not d["patient_sex"] == "":
        d["patient_sex"] = '男' if d["patient_sex"] == 'M' else '女'
    # 处理年龄: '022Y' -> '22岁'
    if not d["patient_age"] == "":
        d["patient_age"] = str(int(d["patient_age"][:-1])) + "岁"
    # 处理体重: '65.4' -> '65.4kg'
    if not d["patient_weight"] == "":
        d["patient_weight"] = str(d["patient_weight"]) + "kg"
    # 处理身高：'1.70' -> "170cm"
    if not d["patient_height"] == "":
        d["patient_height"] = str(float(d["patient_height"]) * 100) + "cm"
    # 处理示踪剂类型
    if not d["pet_tracer_name"] == "":
        d["pet_tracer_name"] = d["pet_tracer_name"].value
    # 处理示踪剂注射计量
    if not d["patient_tracer_activity"] == "":
        d["patient_tracer_activity"] = str(d["patient_tracer_activity"][0].get("RadionuclideTotalDose")) + " Bq"

    return d


if __name__ == '__main__':
    r = load_patient_info(r"C:/Users/anonymous/Desktop/PT00998-2/4", r"C:/Users/anonymous/Desktop/PT00998-2/5")
    from pprint import pprint

    pprint(r)
