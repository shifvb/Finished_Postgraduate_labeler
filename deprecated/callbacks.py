def goto_image_btn_callback(self):
    """navigation面板 跳转图片按钮 callback"""
    if not self.load_mode:  # 没加载文件夹之前此按钮无反应
        return
    _index_str = self.goto_img_entry.get()  # 从GUI得到想要goto的页数
    if _index_str == '':  # 如果没有填就无反应
        return
    try:
        _index = int(_index_str)
    except ValueError:  # 如果不是数字就报错
        showinfo(title="信息", message="请填入数字")
        return
    if 1 <= _index <= len(self.ct_image_list):
        self.image_cursor = _index
        self._load_image()
        self._load_labels()
    else:
        showinfo(title="信息", message="请填入有效数字！")
        return
