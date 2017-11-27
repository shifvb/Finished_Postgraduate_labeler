from labeler_gui.main_gui import Labeler
from labeler_util.load_config_from_ini import load_config_from_ini

version_info = (0, 4, 3)

if __name__ == '__main__':
    cfg = load_config_from_ini()  # 加载外部配置
    Labeler(p_cfg=cfg)
