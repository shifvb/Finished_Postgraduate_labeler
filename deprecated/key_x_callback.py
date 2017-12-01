def key_x_callback(self, event):
    """当x键位按下的时候，相当于点击鼠标，所以模拟点击鼠标进行调用，坐标就取当前鼠标坐标"""
    # 没有加载图像不处理
    if not self.load_mode:
        return
    if self.current_mouse_x > self.ct_tk_img.width() or self.current_mouse_y > self.ct_tk_img.height():
        return
    self._create_label_box(self.current_mouse_x, self.current_mouse_y)