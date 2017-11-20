class InterNationalization(object):
    def register(self, name, obj):
        if name in dir(self):  # 不能注册相同的name
            raise Exception("Cannot register name {}!".format(name))
        self.__setattr__(name, obj)

    def __init__(self):
        # 占位用的，方便修改
        self.error_title = ""
        self.load_dir_not_exist_message = ""
        self.load_img_not_exist_message = ""
        self.info_title = ""
        self.no_more_previous_file_message = ""
        self.no_more_next_file_message = ""

    def to_language(self, language_code: str):
        if language_code == 'zh_CN':
            self._zh_CN()
        elif language_code == 'en_US':
            self._en_US()
        else:
            raise Exception("Unknown language: {}".format(language_code))

    def _zh_CN(self):
        self.root.title("医用病理图像标注系统")
        self.bboxControlPanelFrame['text'] = '标签列表'
        self.imagePanelFrame['text'] = "图像浏览"
        self.labelControlPanelFrame['text'] = '标签类选择'
        self.FileControlPanelFrame['text'] = '加载文件'
        self.naviPanelFrame['text'] = '导航'
        self.selectDirBtn['text'] = '选择文件夹'
        self.loadBtn['text'] = "加载"
        self.prevBtn['text'] = '<< 向前'
        self.nextBtn['text'] = '向后 >>'
        self.saveLabelBtn['text'] = '保存当前标签'
        self.delBtn['text'] = '删除选定标签'
        self.clearAllBtn['text'] = '清除所有标签'
        self.progressNameLabel['text'] = "进度:"
        self.goToImageLabel['text'] = "跳转到图像："
        self.currentClassLabel['text'] = '当前标签类:'
        self.optimized_label_frame['text'] = "优化标签"

        # 对话框提示文本
        self.error_title = "错误"
        self.info_title = "提示"
        self.load_dir_not_exist_message = "未找到文件夹:\n{}"
        self.load_img_not_exist_message = "未找到图像！"
        self.no_more_previous_file_message = "已到达第一张图像"
        self.no_more_next_file_message = "已到达最后一张图像"

    def _en_US(self):
        self.root.title("MyEuclid Labeler")
        self.imagePanelFrame['text'] = "Image View"
        self.bboxControlPanelFrame['text'] = 'Bounding box / Label list'
        self.labelControlPanelFrame['text'] = "Class Select"
        self.FileControlPanelFrame['text'] = 'Load'
        self.naviPanelFrame['text'] = 'Navigation'
        self.selectDirBtn['text'] = 'Select Dir'
        self.loadBtn['text'] = "Load"
        self.prevBtn['text'] = '<< Prev'
        self.nextBtn['text'] = 'Next >>'
        self.saveLabelBtn['text'] = 'Save Current Labels'
        self.delBtn['text'] = 'Delete'
        self.clearAllBtn['text'] = 'Clear All'
        self.progressNameLabel['text'] = "Progress:"
        self.goToImageLabel['text'] = "Go to Image No."
        self.currentClassLabel['text'] = 'Current Class:'
        self.optimized_label_frame['text'] = "optimized label"

        # 对话框提示文本
        self.error_title = "Error"
        self.info_title = "Info"
        self.load_dir_not_exist_message = "Cannot find Directory:\n{}"
        self.load_img_not_exist_message = "No images found in folder!"
        self.no_more_previous_file_message = "No more previous files!"
        self.no_more_next_file_message = "You have reached the last file!"

        # 这些是使用的方式
        # 国际化支持
        # self.i18n.register("root", self.root)
        # self.i18n.register("imagePanelFrame", self.imagePanelFrame)
        # self.i18n.register("bbox_frame", self.bbox_frame)
        # self.i18n.register("labelControlPanelFrame", self.labelControlPanelFrame)
        # self.i18n.register("load_dir_frame", self.load_dir_frame)
        # self.i18n.register('naviPanelFrame', self.naviPanelFrame)
        # self.i18n.register('selectDirBtn', self.selectDirBtn)
        # self.i18n.register('loadBtn', self.loadBtn)
        # self.i18n.register('prevBtn', self.prevBtn)
        # self.i18n.register('nextBtn', self.nextBtn)
        # self.i18n.register('saveLabelBtn', self.saveLabelBtn)
        # self.i18n.register('delBtn', self.delBtn)
        # self.i18n.register('clearAllBtn', self.clearAllBtn)
        # self.i18n.register("progressNameLabel", self.progress_name_label)
        # self.i18n.register("goToImageLabel", self.go_to_image_label)
        # self.i18n.register("currentClassLabel", self.current_class_label)
        # self.i18n.register("optimized_label_frame", self.optimized_label_frame)
        # 设置默认语言
        # self.i18n.to_language(self.cfg['default_language'])
