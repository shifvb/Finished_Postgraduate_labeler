def enlarged_area(abs_x1: float, abs_y1: float, abs_x2: float, abs_y2: float,
                  enlarge_coefficient: float = 2.0, min_ratio_of_enlarged_image: float = 0.3):
    """
    给定一个区域，返回一个放大的区域范围
    :param abs_x1: 左上方x坐标(正则化到0~1)
    :param abs_y1: 左上方y坐标(正则化到0~1)
    :param abs_x2: 右下方x坐标(正则化到0~1)
    :param abs_y2: 右下方y坐标(正则化到0~1)
    :param enlarge_coefficient
    :param min_ratio_of_enlarged_image
    :return: 正则化到0~1的： (放大后的左上方x坐标, 放大后的左上方y坐标, 放大后的右下方x坐标 ,放大后的右下方y坐标)
    """
    # 确定半径r
    _w = (abs_x2 - abs_x1) * enlarge_coefficient
    _h = (abs_y2 - abs_y1) * enlarge_coefficient
    _r = max(_w, _h)
    if _r < min_ratio_of_enlarged_image:
        _r = min_ratio_of_enlarged_image
    # 根据半径r来确定缩放的区域
    _x1 = max(0., (abs_x1 + abs_x2 - _r) / 2)
    _y1 = max(0., (abs_y1 + abs_y2 - _r) / 2)
    _x2 = min(1., (abs_x1 + abs_x2 + _r) / 2)
    _y2 = min(1., (abs_y1 + abs_y2 + _r) / 2)
    # 返回值
    return _x1, _y1, _x2, _y2


if __name__ == '__main__':
    r = enlarged_area(185 / 512, 217 / 512, 281 / 512, 358 / 512)
    print([int(x * 512) for x in r])
