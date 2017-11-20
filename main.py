from myeuclid_gui.main_gui import MyEuclid
from myeuclid_util.load_config_from_ini import load_config_from_ini

version_info = (0, 4, 2)

if __name__ == '__main__':
    cfg = load_config_from_ini()  # 加载外部配置
    MyEuclid(p_cfg=cfg)
