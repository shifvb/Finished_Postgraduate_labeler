import os
import pydicom


def load_patient_info(ct_workspace: str, pet_workspace: str) -> dict:
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
        "pet_tracer_name": (0x9, 0x1036)
    }
    # for key in d:
    #     d[key] = ct_data.get(d[key], None)
    # pprint(d)
    for key in d:
        d[key] = pet_data.get(d[key], None)

    # 处理生日: '19920909' -> '1992-09-09'
    if d["patient_birthday"] is not None:
        _ = d["patient_birthday"]
        d["patient_birthday"] = _[:4] + "-" + _[4:6] + "-" + _[6:]
    # 处理性别: 'M' -> '男'
    if d["patient_sex"] is not None:
        d["patient_sex"] = '男' if d["patient_sex"] == 'M' else '女'
    # 处理年龄: '022Y' -> 22
    if d["patient_age"] is not None:
        d["patient_age"] = int(d["patient_age"][:-1])
    # 处理体重: '65.4' -> 65.4
    if d["patient_weight"] is not None:
        d["patient_weight"] = float(d["patient_weight"])
    # 处理身高：'1.70' -> 1.7
    if d["patient_height"] is not None:
        d["patient_height"] = float(d["patient_height"])
    # 处理示踪剂类型
    if d["pet_tracer_name"] is not None:
        d["pet_tracer_name"] = d["pet_tracer_name"].value

    # 最终为None的都变成空字符串
    for k, v in d.items():
        if v is None:
            d[k] = ""

    return d


if __name__ == '__main__':
    r = load_patient_info(r"C:/Users/anonymous/Desktop/PT00998-2/4", r"C:/Users/anonymous/Desktop/PT00998-2/5")
    from pprint import pprint
    pprint(r)
