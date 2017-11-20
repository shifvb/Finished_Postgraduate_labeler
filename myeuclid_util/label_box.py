class LabelBox(object):
    def __init__(self, class_id: int, x1: int, y1: int, x2: int, y2: int):
        """
        通过左上角和右下角坐标初始化LabelBox
        :param class_id: 类别，是个int数
        :param x1: 左上角x坐标
        :param y1: 左上角y坐标
        :param x2: 右下角x坐标
        :param y2: 右下角y坐标
        """
        self._class_id = class_id
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2

    @property
    def class_id(self):
        return self._class_id

    @class_id.setter
    def class_id(self, value):
        self._class_id = value

    @property
    def x1(self):
        return self._x1

    @x1.setter
    def x1(self, value):
        self._x1 = value

    @property
    def y1(self):
        return self._y1

    @y1.setter
    def y1(self, value):
        self._y1 = value

    @property
    def x2(self):
        return self._x2

    @x2.setter
    def x2(self, value):
        self._x2 = value

    @property
    def y2(self):
        return self._y2

    @y2.setter
    def y2(self, value):
        self._y2 = value

    def to_yolo(self, img_width: int, img_height: int) -> tuple:
        """
        得到此标签框的yolo格式
        :param img_width: 图像宽度
        :param img_height: 图像高度
        :return: 一个元组(标签类， 正则化中心坐标x，正则化中心坐标y，正则化宽度，正则化高度)
            例如：(4, 0.5, 0.5, 0.1, 0.1) 就表示在图像中心，宽度和高度都是图像1/10的一个标签框，而且是第4类
        """
        _center_x = ((self._x1 + self._x2) / 2) / img_width
        _center_y = ((self._y1 + self._y2) / 2) / img_height
        _box_width = (self._x2 - self._x1) / img_width
        _box_height = (self._y2 - self._y1) / img_height
        return self._class_id, _center_x, _center_y, _box_width, _box_height

    @classmethod
    def from_yolo(cls, class_id: int, center_x: float, center_y: float,
                  box_width: float, box_height: float, img_width: int, img_height: int):
        """
        从yolo格式加载标签
        :param class_id: 标签id，yolo格式第一个数据
        :param center_x: 中心x坐标，yolo格式第二个数据
        :param center_y: 中心y坐标，yolo格式第三个数据
        :param box_width: 标签宽度，yolo格式第四个数据
        :param box_height: 标签高度，yolo格式第五个数据
        :param img_width: 图像宽度
        :param img_height: 图像高度
        """
        x1 = int((center_x * img_width) - (box_width * img_width / 2))
        y1 = int((center_y * img_height) - (box_height * img_height / 2))
        x2 = int((center_x * img_width) + (box_width * img_width / 2))
        y2 = int((center_y * img_height) + (box_height * img_height / 2))
        return LabelBox(class_id, x1, y1, x2, y2)

    def __str__(self):
        _s = "<class 'LabelBox'> class{}, ({}, {}) -> ({}, {})"
        return _s.format(self._class_id, self._x1, self._y1, self._x2, self._y2)

    __repr__ = __str__


if __name__ == '__main__':
    r = LabelBox.from_yolo(3, 0.5, 0.5, 0.1, 0.1, 1024, 1024)
    print(r)
