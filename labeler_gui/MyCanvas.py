from tkinter import Canvas


class MyCanvas(Canvas):
    """可以自定义处理滚动的Canvas"""

    def yview(self, *args):
        # 转换成列表方便修改
        _args = list(args)

        # 调整['scroll', '4', 'units']为['scroll', '1', 'units']
        if _args[0] == 'scroll' and _args[2] == 'units':
            _args[1] = "1" if int(_args[1]) > 0 else "-1"

        Canvas.yview(self, *_args)
