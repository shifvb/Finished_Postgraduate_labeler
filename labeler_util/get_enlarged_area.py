def enlarged_area(p_x1: float, p_y1: float, p_x2: float, p_y2: float,
                  enlarge_coefficient: float = 2.0, min_ratio_of_enlarged_image: float = 0.3):
    """
    给定一个区域，返回一个放大的区域范围
    :param p_x1: 左上方x坐标(正则化到0~1)
    :param p_y1: 左上方y坐标(正则化到0~1)
    :param p_x2: 右下方x坐标(正则化到0~1)
    :param p_y2: 右下方y坐标(正则化到0~1)
    :param enlarge_coefficient
    :param min_ratio_of_enlarged_image
    :return: 正则化到0~1的： (放大后的左上方x坐标, 放大后的左上方y坐标, 放大后的右下方x坐标 ,放大后的右下方y坐标)
    """
    # 确定半径r
    _w = (p_x2 - p_x1) * enlarge_coefficient
    _h = (p_y2 - p_y1) * enlarge_coefficient
    _r = max(_w, _h)
    if _r < min_ratio_of_enlarged_image:
        _r = min_ratio_of_enlarged_image
    # 根据半径r来确定缩放的区域
    _x1 = max(0., (p_x1 + p_x2 - _r) / 2)
    _y1 = max(0., (p_y1 + p_y2 - _r) / 2)
    _x2 = min(1., (p_x1 + p_x2 + _r) / 2)
    _y2 = min(1., (p_y1 + p_y2 + _r) / 2)
    # 计算一下原来的坐标在新的放大区域的位置（正则化到0~1之间）
    ori_x1 = (p_x1 - _x1) / (_x2 - _x1) - 0.03  # 减去一个常数的原因是因为图片采样的时候有一些偏差，算是亡羊补牢
    ori_y1 = (p_y1 - _y1) / (_y2 - _y1) - 0.02
    ori_x2 = (p_x2 - _x1) / (_x2 - _x1) - 0.03
    ori_y2 = (p_y2 - _y1) / (_y2 - _y1) - 0.02
    # 返回值
    return _x1, _y1, _x2, _y2, ori_x1, ori_y1, ori_x2, ori_y2


if __name__ == '__main__':
    r = enlarged_area(185 / 512, 217 / 512, 281 / 512, 358 / 512)
    print([int(x * 512) for x in r])
