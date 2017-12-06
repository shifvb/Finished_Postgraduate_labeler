import os
import pydicom


class PatientInfoLoader(object):
    def __init__(self):
        self._info = dict()

    @property
    def patient_info(self):
        return self._info

    def load_patient_info(self, ct_workspace: str, pet_workspace: str) -> dict:
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

        pt_d = {  # d for 'dict'
            "patient_id": 'PatientID',
            "patient_name": 'PatientName',
            "patient_birthday": "PatientBirthDate",
            "patient_sex": "PatientSex",
            "patient_age": "PatientAge",
            "patient_weight": "PatientWeight",
            "patient_height": "PatientSize",
            "pet_tracer_name": (0x9, 0x1036),
            "patient_tracer_activity": "RadiopharmaceuticalInformationSequence",
        }

        ct_d = {
            "rescale_slope": (0x0028, 0x1053),
            "rescale_intercept": (0x0028, 0x1052)
        }

        for key in pt_d:
            pt_d[key] = pet_data.get(pt_d[key], "")
        for key in ct_d:
            ct_d[key] = ct_data.get(ct_d[key], "")

        # 处理生日: '19920909' -> '1992年09月09日'
        if not pt_d["patient_birthday"] == "":
            _ = pt_d["patient_birthday"]
            pt_d["patient_birthday"] = _[:4] + "年" + _[4:6] + "月" + _[6:] + "日"
        # 处理性别: 'M' -> '男'
        if not pt_d["patient_sex"] == "":
            pt_d["patient_sex"] = '男' if pt_d["patient_sex"] == 'M' else '女'
        # 处理年龄: '022Y' -> '22岁'
        if not pt_d["patient_age"] == "":
            pt_d["patient_age"] = str(int(pt_d["patient_age"][:-1])) + "岁"
        # 处理体重: '65.4' -> '65.4kg'
        if not pt_d["patient_weight"] == "":
            pt_d["patient_weight"] = str(pt_d["patient_weight"]) + "kg"
        # 处理身高：'1.70' -> "170cm"
        if not pt_d["patient_height"] == "":
            pt_d["patient_height"] = str(float(pt_d["patient_height"]) * 100) + "cm"
        # 处理示踪剂类型
        if not pt_d["pet_tracer_name"] == "":
            pt_d["pet_tracer_name"] = pt_d["pet_tracer_name"].value
        # 处理示踪剂注射计量
        if not pt_d["patient_tracer_activity"] == "":
            pt_d["patient_tracer_activity"] = str(
                pt_d["patient_tracer_activity"][0].get("RadionuclideTotalDose")) + " Bq"

        # 处理CT图像rescale intercept
        if not ct_d["rescale_intercept"] == "":
            ct_d["rescale_intercept"] = int(ct_d["rescale_intercept"].value)
        # 处理CT图像rescale slope
        if not ct_d["rescale_slope"] == "":
            ct_d["rescale_slope"] = int(ct_d["rescale_slope"].value)

        self._info.update(ct_d)
        self._info.update(pt_d)


if __name__ == '__main__':
    L = PatientInfoLoader()
    L.load_patient_info(ct_workspace=r"C:/Users/anonymous/Desktop/PT00998-2/4",
                        pet_workspace=r"C:/Users/anonymous/Desktop/PT00998-2/5")
    from pprint import pprint

    pprint(L.patient_info)
