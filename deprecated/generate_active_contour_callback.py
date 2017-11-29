# ------- 显示优化标签 面板 callback start ---------
# 1.4 用来显示算法结果的副面板
self.optimized_label_frame = LabelFrame(self.root, text="优化标签")
self.optimized_label_frame.grid(row=1, column=1, sticky=NW, padx=5)
self.opt_panel = Canvas(self.optimized_label_frame, height=self._PSIZE, width=self._PSIZE)
self.opt_panel.pack()
self.opt_btn = Button(self.optimized_label_frame, text='generate active contour',
                      command=self.generate_active_contour_callback)
self.opt_btn.pack()


def generate_active_contour_callback(self):
    # 没有加载图像此按钮无效
    if not self.load_mode:
        return
    # 如果没有选定删除标签，那么直接结束
    if not self.bbox_listbox.curselection():
        return
    # 返回当前选定的标签的index
    index = self.bbox_listbox.curselection()[0]

    from skimage.segmentation import active_contour
    import numpy
    print(self.label_list[index])
    _x1 = self.label_list[index].x1
    _y1 = self.label_list[index].y1
    _x2 = self.label_list[index].x2
    _y2 = self.label_list[index].y2
    # 生成图像
    _img = Image.open(self.ct_image_list[self.image_cursor - 1])
    self.opt_tk_img = ImageTk.PhotoImage(_img)

    def _gen_points(start_point, end_point, n=50):
        a = numpy.linspace(start_point[0], end_point[0], num=n)
        b = numpy.linspace(start_point[1], end_point[1], num=n)
        c = numpy.empty(shape=[n, 2])
        for row_num in range(c.shape[0]):
            for col_num in range(c.shape[1]):
                c[row_num][col_num] = a[row_num] if col_num == 0 else b[row_num]
        return c

    _r = active_contour(_img, snake=numpy.concatenate(
        (_gen_points([_x1, _y1], [_x1, _y2]), _gen_points([_x1, _y2], [_x2, _y2]),
         _gen_points([_x2, _y2], [_x2, _y1]), _gen_points([_x2, _y1], [_x1, _y1])), axis=0)
                        )

    # 显示图像
    self.opt_panel.create_image(0, 0, image=self.opt_tk_img, anchor=NW)
    self.opt_panel.delete(self.opt_mask_id) if hasattr(self, "opt_mask_id") else None  # todo : define it
    # 显示点
    for x, y in _r:
        print(x, y)
        self.opt_panel.create_rectangle(x - 1, y - 1, x, y, width=1, outline="#ff0000")

        # -------- 显示优化标签 面板 callback end ----------
