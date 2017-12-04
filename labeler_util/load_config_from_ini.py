import configparser


def load_config_from_ini():
    """load config from relative path 'config.ini'"""
    cfg = configparser.ConfigParser()
    cfg.read("config.ini")
    cfg_dict = {}
    # read config
    for section_name in cfg.sections():
        for k, v in cfg.items(section_name):
            cfg_dict[k] = v
    # handle read config
    cfg_dict["label_number"] = int(cfg_dict["label_number"])
    cfg_dict["show_patient_name"] = cfg_dict["show_patient_name"] == "1"
    cfg_dict['debug'] = cfg_dict["debug"] == "True"
    cfg_dict["enlarge_coefficient"] = float(cfg_dict["enlarge_coefficient"])
    cfg_dict["min_ratio_of_enlarged_image"] = float(cfg_dict["min_ratio_of_enlarged_image"])
    # return
    return cfg_dict
