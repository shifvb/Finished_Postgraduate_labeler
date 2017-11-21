__all__ = ['gen_colors']


def _gen_colors():
    """gen_colors()的辅助函数"""
    r = g = b = 128
    while True:
        increment_type = yield '#%02x%02x%02x' % (r, g, b)
        if increment_type == "r":
            r = (r + 45) % 255
        elif increment_type == "g":
            g = (g + 45) % 255
        elif increment_type == "b":
            b = (b + 45) % 255
        else:
            raise Exception("Invalid argument")


def gen_colors():
    """
    一个颜色生成器，每次调用next()函数可以生成一个字符串，例如"#4f1e3f"
    :return: 颜色生成器
    """
    _color_generator = _gen_colors()
    _color_generator.send(None)
    return _color_generator
