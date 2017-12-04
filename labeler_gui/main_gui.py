import os
import pickle
import numpy as np
from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import showerror, showinfo
from tkinter.font import Font
from PIL import Image, ImageTk
from deprecated.menubar import file_menu_exit_callback as exit_callback
from labeler_gui.init_class_select_panel import init_class_select_panel
from labeler_gui.MyCanvas import MyCanvas
from labeler_util.ImageLoader import ImageLoader
from labeler_util.gen_colors import gen_colors
from labeler_util.label_box import LabelBox
from labeler_util.load_patient_info import load_patient_info
from labeler_util.patient_remark import load_patient_remark, save_patient_remark
from labeler_util.ThresholdImageGenerator import ThresholdImageGenerator as TIG
from labeler_util.scrollbar_delay import is_enough_time_passed
from labeler_util.get_enlarged_area import enlarged_area
from labeler_util.debug_mode import debug_mode


class Labeler(object):
    def __init__(self, p_cfg):
        # 外部函数相关变量
        self.cfg = p_cfg  # 加载外部配置
        self.color_generator = gen_colors()  # 初始化颜色生成器，用来生成不同的颜色
        self.image_loader = ImageLoader()  # 初始化ImageLoader
        # 文件相关变量
        self.load_mode = str()  # 目前有 CT, PET_CT 两种
        self.ct_workspace = str()  # CT workspace
        self.pet_workspace = str()  # PET workspace
        self.ct_image_list = list()  # 加载CT图像的文件名列表（绝对路径）
        self.pet_image_list = list()  # 加载PET图像的文件名列表（绝对路径）
        self.suv_value_list = list()  # 加载SUV值文件的文件名列表(绝对路径)
        self.image_cursor = -1  # 当前UI中显示的图片为第几张，取值时self.ct_image_list[self.image_cursor-1]
        self.label_file_path = None  # 用来保存当前图片对应label的绝对路径
        # GUI相关变量
        self.root = Tk()  # 初始化主窗口
        self.ct_tk_img = None  # 创建标签面板的图像
        self._color = None  # 用来储存某些组件当前所用颜色的变量
        self.label_list = []  # 用来存储当前标签的list
        self.ct_label_id_list = []  # 用来存储当前标签在标签创建面板上的id的list，和self.label_list一一对应
        self.pet_label_id_list = []
        self.curr_ct_label_id = -1  # 用来储存当前创建的标签框id的变量
        self.curr_pet_label_id = -1
        # GUI相关常量
        self._PSIZE = 475  # PSIZE: panel size, 显示图像大小
        self._BIG_FONT = Font(size=15)  # big font size
        self._MID_FONT = Font(size=13)
        self.CT_F_TITLE = "CT({:03}/{:03}) x: {:03} y: {:03}"
        self.PET_F_TITLE = "PET({:03}/{:03}) 当前SUV值:{}, z分数:{}"
        # GUI_鼠标
        self.mouse_clicked = False  # 追踪鼠标是否点击，点击奇数次为True，偶数次为False
        self.current_mouse_x = 0  # 当前鼠标x
        self.current_mouse_y = 0  # 当前鼠标y
        self.old_mouse_x = 0  # 最近一次奇数次鼠标点击x
        self.old_mouse_y = 0  # 最近一次奇数次鼠标点击y
        # 加载GUI
        self.init_gui()  # 加载GUI组件

    # -------- 创建图像标签 面板 callback start ----------
    def mouse_click_callback(self, event):
        """创建标签面板鼠标按下回调函数"""
        # 没有加载图像不处理
        if not self.load_mode:
            return
        if self.current_mouse_x > self._PSIZE or self.current_mouse_y > self._PSIZE:
            return
        self._create_label_box(event.x, event.y)

    def key_esc_callback(self, event):
        """ESC键位用来取消当前创建的标签"""
        self._cancel_create_label(event)

    def mouse_move_callback(self, event):
        # 没有加载图像不处理鼠标移动
        if not self.load_mode:
            return

        # CT图像指示线
        self.ct_canvas.delete(self.horizontal_line_id) if hasattr(self, "horizontal_line_id") else None
        self.horizontal_line_id = self.ct_canvas.create_line(0, event.y, self._PSIZE, event.y, width=1, fill='yellow')
        self.ct_canvas.delete(self.vertical_line_id) if hasattr(self, "vertical_line_id") else None
        self.vertical_line_id = self.ct_canvas.create_line(event.x, 0, event.x, self._PSIZE, width=1, fill='yellow')
        # 标注现在鼠标坐标
        self.ct_frame_label.config(
            text=self.CT_F_TITLE.format(self.image_cursor, len(self.ct_image_list), event.x, event.y))
        # 如果是PET_CT模式
        if self.load_mode == 'PET_CT':
            # SUV图像指示线
            # self.suv_canvas.delete(self.suv_hori_line_id) if hasattr(self, "suv_hori_line_id") else None
            # self.suv_hori_line_id = self.suv_canvas.create_line(0, event.y, self._PSIZE, event.y, fill='yellow')
            # self.suv_canvas.delete(self.suv_vert_line_id) if hasattr(self, "suv_vert_line_id") else None
            # self.suv_vert_line_id = self.suv_canvas.create_line(event.x, 0, event.x, self._PSIZE, fill='yellow')
            # PET图像指示线
            self.pet_canvas.delete(self.pet_hori_line_id) if hasattr(self, "pet_hori_line_id") else None
            self.pet_hori_line_id = self.pet_canvas.create_line(0, event.y, self._PSIZE, event.y, fill='yellow')
            self.pet_canvas.delete(self.pet_vert_line_id) if hasattr(self, "pet_vert_line_id") else None
            self.pet_vert_line_id = self.pet_canvas.create_line(event.x, 0, event.x, self._PSIZE, fill='yellow')
            # 当前原始SUV值
            _x = min(int(event.x / self._PSIZE * self.suv_value_array.shape[0]), self.suv_value_array.shape[0] - 1)
            _y = min(int(event.y / self._PSIZE * self.suv_value_array.shape[1]), self.suv_value_array.shape[1] - 1)
            # 当前SUV值
            suv_value = self.suv_value_array[_x][_y] if self.suv_value_array[_x][_y] > 1e-2 else 0.0
            # 当前z分数
            _z_score = (suv_value - self.suv_value_array.mean()) / self.suv_value_array.std()
            self.pet_frame_label.config(text=self.PET_F_TITLE.format(
                self.image_cursor, len(self.ct_image_list), "%.3f" % suv_value, "%+.3f" % _z_score))

        # 画标签框
        if self.mouse_clicked:
            self.ct_canvas.delete(self.curr_ct_label_id) if self.curr_ct_label_id else None
            self.pet_canvas.delete(self.curr_pet_label_id) if self.curr_pet_label_id else None
            self._color = self.color_generator.send("b")
            self.curr_ct_label_id = self.ct_canvas.create_rectangle(self.old_mouse_x, self.old_mouse_y,
                                                                    event.x, event.y, width=2, outline=self._color)
            self.curr_pet_label_id = self.pet_canvas.create_rectangle(self.old_mouse_x, self.old_mouse_y,
                                                                      event.x, event.y, width=2, outline=self._color)
        # 因为这个函数是鼠标移动的回调函数，所以记录当前鼠标的坐标
        self.current_mouse_x = event.x
        self.current_mouse_y = event.y

    # -------- 创建图像标签 面板 callback end ----------


    # -------- 标签增删 面板 callback start ----------
    def del_label_btn_callback(self):
        """删除标签 callback"""
        # 没有加载图像此按钮无效
        if not self.load_mode:
            return
        # 如果没有选定删除标签，那么直接结束
        if not self.label_listbox.curselection():
            return
        # 返回当前选定的标签的index
        index = self.label_listbox.curselection()[0]
        # 删除面板上的标签
        self.ct_canvas.delete(self.ct_label_id_list[index])
        self.pet_canvas.delete(self.pet_label_id_list[index])
        # 删除标签显示面板上的标签
        self.label_listbox.delete(index)
        # 清除跟踪的列表
        self.ct_label_id_list.pop(index)
        self.pet_label_id_list.pop(index)
        self.label_list.pop(index)

    def clear_label_callback(self):
        """bboxControl 面板 清除所有标签 callback"""
        # 没有加载图像此按钮无效
        if not self.load_mode:
            return
        # 根据bbox_id_list，将主面板上的所有方框清除
        for bbox_id in self.ct_label_id_list:
            self.ct_canvas.delete(bbox_id)
        for bbox_id in self.pet_label_id_list:
            self.pet_canvas.delete(bbox_id)
        # 将bbox面板上listbox组件的所有元素删除
        self.label_listbox.delete(0, len(self.label_list))
        # 清除跟踪的列表
        self.ct_label_id_list = list()
        self.pet_label_id_list = list()
        self.label_list.clear()

    # -------- 标签增删 面板 callback end ----------

    # -------- load 面板 callback start ----------
    def load_ct_dir_btn_callback(self):
        """load 面板中 load_ct_dir 按钮回调事件"""
        _path = filedialog.askdirectory()  # 得到选定的文件夹路径
        if _path == "":
            return
        self.load_ct_dir_entry.delete(0, END)  # 先清空
        self.load_ct_dir_entry.insert(0, _path)  # 再填入

    def load_pet_dir_btn_callback(self):
        """load 面板中 load_pet_dir 按钮回调事件"""
        _path = filedialog.askdirectory()  # 得到选定的文件夹路径
        if _path == "":
            return
        self.load_pet_dir_entry.delete(0, END)  # 先清空
        self.load_pet_dir_entry.insert(0, _path)  # 再填入

    def load_btn_callback(self):
        """load 面板中 Load 按钮回调事件"""
        self.ct_workspace = self.load_ct_dir_entry.get()  # 用户选定的dicom图像文件夹就是workspace
        self.pet_workspace = self.load_pet_dir_entry.get()

        # 根据用户输入确定加载模式
        self.load_mode = "CT" if self.pet_workspace == "" else "PET_CT"

        # 检测文件夹路径是否存在
        if not os.path.isdir(self.ct_workspace):
            showerror(title="错误", message="未找到文件夹:\n{}".format(self.ct_workspace))
            return
        if self.load_mode == "PET_CT" and not os.path.isdir(self.pet_workspace):
            showerror(title="错误", message="未找到文件夹:\n{}".format(self.pet_workspace))
            return

        # 加载图像文件
        self.image_loader.load_image(self.load_mode, self.cfg["image_output_suffix"],
                                     self.ct_workspace,
                                     self.cfg['ct_output_folder_name'],
                                     self.pet_workspace,
                                     self.cfg['suv_output_folder_name'], self.cfg['pet_output_folder_name'])
        self.ct_image_list = self.image_loader.cts
        self.pet_image_list = self.image_loader.pets
        self.suv_value_list = self.image_loader.suvs

        # default to the 1st image in the collection
        self.image_cursor = 1

        # 如果没有找到图片就提示
        if len(self.ct_image_list) == 0:
            showerror(title="错误", message="未找到图像！")
            return

        # GUI加载
        self._load_image()
        self._load_labels()
        self._load_patient_info()
        self._load_patient_remark()

    # -------- load 面板 callback end ----------

    # -------- navigation 面板 callback start ----------
    def prev_image_btn_callback(self, event=None):
        """navigation面板 上一张图片按钮 callback"""
        # 没有加载图像此按钮无效
        if not self.load_mode:
            return
        # 如果没有上一张图像，报错
        if self.image_cursor == 1:
            showinfo(title="信息", message="已到达第一张图像")
            return
        # 切换图像之前先保存当前图像label
        self._save_label()
        # 最后加载前一张图像和对应标签(如果有的话)
        self.image_cursor -= 1
        self._load_image()
        self._load_labels()

    def next_image_btn_callback(self, event=None):
        """navigation面板  下一张图片按钮 callback"""
        # 没有加载图像此按钮无效
        if not self.load_mode:
            return
        # 如果没有下一张图像，报错
        if self.image_cursor == len(self.ct_image_list):
            showinfo(title="信息", message="已到达最后一张图像")
            return
        # 切换图像之前先保存当前图像label
        self._save_label()
        # 最后加载后一张图像和对应标签(如果有的话)
        self.image_cursor += 1
        self._load_image()
        self._load_labels()

    def save_label_btn_callback(self, *args):
        """navigation面板 保存当前图片标签按钮 callback"""
        # 没有加载图像此按钮无效
        if not self.load_mode:
            return
        self._save_label()

    # -------- navigation 面板 callback end ----------

    def save_remark_btn_callback(self):
        """保存病人诊断信息"""
        if not self.load_mode:  # 没有加载图像此按钮无效
            return
        _t = self.diagnosis_text.get("1.0", END)
        save_patient_remark(os.path.join(self.ct_workspace, self.cfg["patient_remark_name"]), _t)
        showinfo(title="信息",
                 message="已保存到:{}".format(os.path.join(self.ct_workspace, self.cfg["patient_remark_name"])))

        # -------- 功能性函数 start -----------

    def _save_label(self):
        # 如果label_file_path所在的文件夹不存在的话，就新建
        if not os.path.exists(os.path.split(self.label_file_path)[0]):
            os.mkdir(os.path.split(self.label_file_path)[0])
        # 向文件写入
        with open(self.label_file_path, 'w') as f:
            for label in self.label_list:
                _temp_result = label.to_yolo(self.ct_tk_img.width(), self.ct_tk_img.height())
                f.write("{} {:.7f} {:.7f} {:.7f} {:.7f}\n".format(*_temp_result))

    def _load_image(self):
        # 加载CT图像
        ct_image_path = self.ct_image_list[self.image_cursor - 1]
        self.ct_tk_img = ImageTk.PhotoImage(Image.open(ct_image_path).resize([self._PSIZE, self._PSIZE]))
        self.ct_canvas.create_image(0, 0, image=self.ct_tk_img, anchor=NW)
        self.ct_frame_label.config(text=self.CT_F_TITLE.format(self.image_cursor, len(self.ct_image_list), 0, 0))
        # 如果是PET_CT模式
        if self.load_mode == 'PET_CT':
            # 加载SUV值
            suv_value_path = self.suv_value_list[self.image_cursor - 1]
            self.suv_value_array = pickle.load(open(suv_value_path, 'rb'))
            # 加载SUV图像
            _arr = TIG.arr_to_arr(self.suv_value_array, 2.0)
            self.suv_tk_img = ImageTk.PhotoImage(
                Image.fromarray(_arr, 'L').resize([self._PSIZE, self._PSIZE], resample=Image.BILINEAR))
            self.suv_canvas.config(width=self._PSIZE, height=self._PSIZE)
            self.suv_canvas.create_image(0, 0, image=self.suv_tk_img, anchor=NW)
            # 加载PET图像
            pet_image_path = self.pet_image_list[self.image_cursor - 1]
            self.pet_tk_img = ImageTk.PhotoImage(
                Image.open(pet_image_path).resize([self._PSIZE, self._PSIZE], resample=Image.BILINEAR))
            self.pet_canvas.create_image(0, 0, image=self.pet_tk_img, anchor=NW)
            self.pet_frame_label.config(
                text=self.PET_F_TITLE.format(self.image_cursor, len(self.pet_image_list), "%.3f" % 0, "%+.3f" % 0))

    def _load_labels(self):
        # 清除已有标签
        self.clear_label_callback()
        # 计算标签绝对路径(self.ct_workspace + _output_label_folder_name + _file_name)
        _file_name = os.path.splitext(os.path.split(self.ct_image_list[self.image_cursor - 1])[-1])[0] + '.txt'
        self.label_file_path = os.path.join(self.ct_workspace, self.cfg['label_output_folder'], _file_name)
        # 加载标签(如果有)
        if os.path.exists(self.label_file_path):
            with open(self.label_file_path) as f:
                for line in f.readlines():
                    # 加载标签
                    self.label_list.append(LabelBox.from_yolo(
                        *[float(_) if i != 0 else int(_) for i, _ in enumerate(line.split())],
                        self._PSIZE, self._PSIZE
                    ))
                    # 设置颜色
                    self._color = self.color_generator.send("g")
                    # 在主面板上画框
                    _label = self.label_list[-1]
                    _temp_id = self.ct_canvas.create_rectangle(_label.x1, _label.y1, _label.x2, _label.y2,
                                                               width=2, outline=self._color)
                    self.ct_label_id_list.append(_temp_id)
                    _temp_id = self.pet_canvas.create_rectangle(_label.x1, _label.y1, _label.x2, _label.y2,
                                                                width=2, outline=self._color)
                    self.pet_label_id_list.append(_temp_id)
                    # 在标签增删面板上增加一个标签
                    self.label_listbox.insert(END, '({:3}, {:3})->({:3}, {:3}) [Class {}]'
                                              .format(_label.x1, _label.y1, _label.x2, _label.y2, _label.class_id))
                    self.label_listbox.itemconfig(len(self.label_list) - 1, fg=self._color)

    def _load_patient_info(self):
        if self.load_mode == 'CT':
            return
        self.patient_info = load_patient_info(self.ct_workspace, self.pet_workspace)
        self.patient_id_value.config(text=self.patient_info["patient_id"])
        if self.cfg["show_patient_name"] is True:
            self.patient_name_value.config(text=self.patient_info["patient_name"])
        self.patient_birthday_value.config(text=self.patient_info["patient_birthday"])
        self.patient_sex_value.config(text=self.patient_info["patient_sex"])
        self.patient_age_value.config(text=self.patient_info["patient_age"])
        self.patient_weight_value.config(text=self.patient_info["patient_weight"])
        self.patient_height_value.config(text=self.patient_info["patient_height"])
        self.patient_tracer_value.config(text=self.patient_info["pet_tracer_name"])

    def _load_patient_remark(self):
        """加载病人诊断信息"""
        _t = load_patient_remark(os.path.join(self.ct_workspace, self.cfg["patient_remark_name"]))
        self.diagnosis_text.delete("1.0", END)  # 先清空
        self.diagnosis_text.insert("1.0", _t)  # 再填入

    def _create_label_box(self, xCoord, yCoord):
        # 记录当前状态
        self.mouse_clicked = not self.mouse_clicked
        # 判断鼠标点击状态
        if self.mouse_clicked:
            # 如果当前鼠标按下，那么就是开始新建一个label，这时只需要记录当前创建坐标即可
            self.old_mouse_x = xCoord
            self.old_mouse_y = yCoord
        else:
            # 如果鼠标两次按下，就是完成新建一个label，此时点击了两次鼠标，所以值为False
            x1, x2 = min(self.old_mouse_x, xCoord), max(self.old_mouse_x, xCoord)
            y1, y2 = min(self.old_mouse_y, yCoord), max(self.old_mouse_y, yCoord)
            # 记录一下新建的label的（左上角，右下角）坐标
            self.label_list.append(LabelBox(self.current_class_number.get(), x1, y1, x2, y2))
            # 更新GUI界面中标签面板
            self.ct_label_id_list.append(self.curr_ct_label_id)
            self.pet_label_id_list.append(self.curr_pet_label_id)
            self.label_listbox.insert(END, '({:3}, {:3})->({:3}, {:3}) [Class {}]'.
                                      format(x1, y1, x2, y2, self.current_class_number.get()))
            self.label_listbox.itemconfig(len(self.ct_label_id_list) - 1, fg=self._color)
            self._color = self.color_generator.send("r")
            # 将当前的GUI矩形的id设为None，这样在鼠标移动的时候，就不会被处理鼠标移动的回调函数删除
            self.curr_ct_label_id = None
            self.curr_pet_label_id = None
            # 最后，显示一下放大的区域
            _ctimg = Image.open(self.ct_image_list[self.image_cursor - 1])
            _zoomed_coordinates = enlarged_area(x1 / self._PSIZE, y1 / self._PSIZE, x2 / self._PSIZE, y2 / self._PSIZE,
                                                self.cfg["enlarge_coefficient"],
                                                self.cfg["min_ratio_of_enlarged_image"])
            _zoomed_coordinates = [int(_ * _ctimg.width) for _ in _zoomed_coordinates]
            _arr = np.array(_ctimg)[
                   _zoomed_coordinates[1]: _zoomed_coordinates[3],
                   _zoomed_coordinates[0]: _zoomed_coordinates[2]]
            _img = Image.fromarray(_arr, 'L')
            self._zoomed_tk_img = ImageTk.PhotoImage(_img.resize([self._PSIZE, self._PSIZE]))
            self.zoomed_canvas.create_image(0, 0, image=self._zoomed_tk_img, anchor=NW)

            # ct_image_path = self.ct_image_list[self.image_cursor - 1]
            # self.ct2_tk_img = ImageTk.PhotoImage(Image.open(ct_image_path).resize([self._PSIZE, self._PSIZE]))
            # self.zoomed_canvas.create_image(100, 0, image=self.ct2_tk_img, anchor=NW)

    def _cancel_create_label(self, event):
        """取消创建标签 callback"""
        self.mouse_clicked = False
        self.ct_canvas.delete(self.curr_ct_label_id)

    def suv_scrl_scroll_callback(self, *args):
        """SUV滚动条滚动回调函数"""
        # 常量设置
        _len = 0.3  # 滚动条的长度占到整个滚动控件的比例
        _scrl_step = 0.5 * (1 - _len)  # 每次滚动多少， 0.5 * (1 - len)就是每次滚动50%
        _start_suv = 0  # 起始SUV
        _end_suv = self.suv_value_array.max()  # 终止SUV

        # 设置滚动条的位置
        if args[0] == "moveto":
            _first = float(args[1])
        else:  # args[0] == "scroll"
            if abs(int(args[1])) > 1:  # 修正一个鼠标滚轮过快滚动的bug
                _args_1 = int(args[1]) / abs(int(args[1]))
                _first = self.suv_scrl.get()[0] + int(_args_1) * _scrl_step * 0.5
            else:
                _first = self.suv_scrl.get()[0] + int(args[1]) * _scrl_step * 0.5
            _first = max(0., _first)
            _first = min(1 - _len, _first)
        self.suv_scrl.set(_first, _first + _len)

        # 未加载图像，就不会触发下面的函数
        if not self.load_mode:
            return
        # 如果没有经过足够的时间，就不会触发下面的函数
        if not is_enough_time_passed():
            return

        # 得到实际SUV值
        suv_scrl_progress = (self.suv_scrl.get()[0]) / (1 - _len)
        actual_suv = _start_suv + (_end_suv - _start_suv) * suv_scrl_progress

        # 根据SUV值生成阈值图像
        _arr = TIG.arr_to_arr(self.suv_value_array, actual_suv)
        self.suv_tk_img = ImageTk.PhotoImage(
            Image.fromarray(_arr, 'L').resize([self._PSIZE, self._PSIZE], resample=Image.BILINEAR))
        self.suv_canvas.config(width=self._PSIZE, height=self._PSIZE)
        self.suv_canvas.create_image(0, 0, image=self.suv_tk_img, anchor=NW)
        # 修改当前SUV阈值的显示值
        self.suv_frame_label.config(text="PET (SUV > %.3f)" % actual_suv)

    # -------- 功能性函数  end  -----------

    def init_gui(self):
        # 0. 设置root
        self.root.state("zoomed")  # 窗口最大化，只对windows有效 root.geometry("{}x{}-0+0".format(*self.root.maxsize()))
        self.root.title("医用病理图像标注系统")
        self.root.protocol("WM_DELETE_WINDOW", exit_callback)  # 绑定关闭窗口事件
        self.root.bind("<Escape>", self.key_esc_callback)  # press <Escape> to cancel current bbox
        self.root.bind("<Left>", self.prev_image_btn_callback)  # press 'Left Arrow' to go backforward
        self.root.bind("<Right>", self.next_image_btn_callback)  # press 'Right Arrow' to go forward
        self.root.bind("<Control-KeyPress-s>", self.save_label_btn_callback)  # Ctrl+s 保存当前标签

        # 1.1 CT图像面板
        ct_frame = Frame(self.root)
        ct_frame.grid(row=0, column=0, sticky=NW, padx=5)
        self.ct_frame_label = Label(ct_frame, text=self.CT_F_TITLE.format(0, 0, 0, 0), font=self._MID_FONT)
        self.ct_frame_label.pack()
        ct_canvas_frame = LabelFrame(ct_frame)
        ct_canvas_frame.pack()
        self.ct_canvas = Canvas(ct_canvas_frame, height=self._PSIZE, width=self._PSIZE)
        self.ct_canvas.bind("<Button-1>", self.mouse_click_callback)
        self.ct_canvas.bind("<Motion>", self.mouse_move_callback)
        self.ct_canvas.pack()

        # 1.2 PET图像面板
        pet_frame = Frame(self.root)
        pet_frame.grid(row=0, column=1, sticky=NW, padx=5)
        self.pet_frame_label = Label(pet_frame, font=self._MID_FONT)
        self.pet_frame_label.config(text=self.PET_F_TITLE.format(0, 0, "%.3f" % 0, "%+.3f" % 0))
        self.pet_frame_label.pack()
        pet_canvas_frame = LabelFrame(pet_frame)
        pet_canvas_frame.pack()
        self.pet_canvas = Canvas(pet_canvas_frame, height=self._PSIZE, width=self._PSIZE)
        self.pet_canvas.bind("<Motion>", self.mouse_move_callback)
        self.pet_canvas.bind("<Button-1>", self.mouse_click_callback)
        self.pet_canvas.pack()

        # 1.3 显示放大区域的面板
        zoomed_frame = Frame(self.root)
        zoomed_frame.grid(row=1, column=0, sticky=NW, padx=5)
        zoomed_frame_label = Label(zoomed_frame, text="标签放大", font=self._MID_FONT)
        zoomed_frame_label.pack()
        zoomed_area_frame = LabelFrame(zoomed_frame)
        zoomed_area_frame.pack()
        self.zoomed_canvas = Canvas(zoomed_area_frame, height=self._PSIZE, width=self._PSIZE)
        self.zoomed_canvas.pack()

        # 1.4 SUV图像面板
        suv_frame = Frame(self.root)
        suv_frame.grid(row=1, column=1, sticky=NW, padx=5)
        self.suv_frame_label = Label(suv_frame, text="PET (SUV > 2.000)", font=self._MID_FONT)
        self.suv_frame_label.pack()
        suv_canvas_frame = LabelFrame(suv_frame)
        suv_canvas_frame.pack()
        self.suv_canvas = Canvas(suv_canvas_frame, height=self._PSIZE, width=self._PSIZE)
        self.suv_canvas.pack()
        # 滚动条显示
        suv_scrl_frame = Frame(self.root)
        suv_scrl_frame.grid(row=1, column=2, sticky=NS, padx=0)
        suv_scrl_frame.rowconfigure(index=1, weight=1)
        Label(suv_scrl_frame, text=" ", font=self._MID_FONT).grid(row=0, column=0)
        self.suv_scrl = Scrollbar(suv_scrl_frame, orient=VERTICAL, command=self.suv_scrl_scroll_callback)
        self.suv_scrl.set(0, 0.3)
        self.suv_scrl.grid(row=1, column=0, sticky=NS + W)

        # 2. 右上角面板
        upper_right_frame = Frame(self.root)
        upper_right_frame.grid(row=0, column=2, sticky=NW, columnspan=2)

        # 2.1 显示标签面板
        self.bbox_frame = LabelFrame(upper_right_frame, text='标签', font=self._MID_FONT)
        self.bbox_frame.grid(row=0, column=0, sticky=NW)
        self.label_listbox = Listbox(self.bbox_frame, width=33, height=17, font=self._MID_FONT, relief=FLAT)
        self.label_listbox.grid(row=0, column=0)
        bbox_listbox_scroll_bar = Scrollbar(self.bbox_frame)
        bbox_listbox_scroll_bar.grid(row=0, column=1, sticky=NSEW)
        bbox_listbox_scroll_bar['command'] = self.label_listbox.yview
        self.label_listbox['yscrollcommand'] = bbox_listbox_scroll_bar.set
        del_bbox_btn = Button(self.bbox_frame, command=self.del_label_btn_callback, text='删除选定标签')
        del_bbox_btn.config(font=self._BIG_FONT)
        del_bbox_btn.grid(row=1, column=0, columnspan=2, sticky=NSEW, pady=1)
        clear_bbox_btn = Button(self.bbox_frame, command=self.clear_label_callback, text='清除所有标签')
        clear_bbox_btn.config(font=self._BIG_FONT)
        clear_bbox_btn.grid(row=2, column=0, columnspan=2, sticky=NSEW)

        # 2.2 选择标签类的按钮
        init_class_select_panel(self)
        label_scroll_frame = Frame(self.bbox_frame)
        label_scroll_frame.grid(row=0, column=2, rowspan=2)
        label_ctrl_scrollbar = Scrollbar(label_scroll_frame)
        label_ctrl_scrollbar.grid(row=0, column=3, sticky=NS)
        label_control_canvas = MyCanvas(label_scroll_frame, width=190, height=350)
        label_control_canvas.grid(row=0, column=2, sticky=NSEW)
        for i in range(self.cfg["label_number"]):
            _btn = Button(label_scroll_frame, text="class{}".format(i), height=2, width=18, font=self._BIG_FONT,
                          command=self.__getattribute__("set_class{}_btn_callback".format(i)))
            _btn.bind("<MouseWheel>",
                      lambda event: label_control_canvas.yview('scroll', '-1', "units")
                      if event.delta > 0 else label_control_canvas.yview('scroll', '1', "units"))
            label_control_canvas.create_window(0, i * 55, anchor=NW, window=_btn)

        label_control_canvas.config(scrollregion=label_control_canvas.bbox(ALL),
                                    yscrollcommand=label_ctrl_scrollbar.set)
        label_ctrl_scrollbar.config(command=label_control_canvas.yview)
        # 2.3 显示当前标签类
        label_display_frame = Frame(self.bbox_frame)
        label_display_frame.grid(row=2, column=2, sticky=S)
        current_class_label = Label(label_display_frame, text='当前标签类:', font=self._BIG_FONT)
        current_class_label.grid(row=0, column=0)
        self.current_class_number = IntVar(value=0)
        Label(label_display_frame, textvariable=self.current_class_number, font=self._BIG_FONT).grid(row=0, column=1)

        # 2.4 图片导航面板
        navi_frame = LabelFrame(upper_right_frame, text='图像导航', font=self._MID_FONT)
        navi_frame.grid(row=1, column=0, sticky=NW)
        prev_img_btn = Button(navi_frame, width=13, height=2, command=self.prev_image_btn_callback, text='前一张(←)')
        prev_img_btn.config(font=self._BIG_FONT)
        prev_img_btn.pack(side=LEFT, padx=6, pady=9)
        save_label_btn = Button(navi_frame, width=20, height=2, command=self.save_label_btn_callback,
                                text='保存标签(Ctrl+S)')
        save_label_btn.config(font=self._BIG_FONT)
        save_label_btn.pack(side=LEFT, padx=7, pady=3)
        next_img_btn = Button(navi_frame, width=13, height=2, command=self.next_image_btn_callback, text='后一张(→)')
        next_img_btn.config(font=self._BIG_FONT)
        next_img_btn.pack(side=LEFT, padx=7, pady=9)

        # 2.5 病人信息面板
        patient_info_frame = LabelFrame(upper_right_frame, text="基本信息", font=self._MID_FONT)
        patient_info_frame.grid(row=0, column=1, rowspan=2, sticky=NW, padx=5)
        patient_info_k_frame = Frame(patient_info_frame)  # k for "key", means the name of the value
        patient_info_k_frame.grid(row=0, column=0, sticky=W)
        patient_info_v_frame = Frame(patient_info_frame)
        patient_info_v_frame.grid(row=0, column=1)
        _p_pady = 16
        patient_id_label = Label(patient_info_k_frame, text="ID:", font=self._BIG_FONT)
        patient_id_label.grid(row=0, column=0, sticky=W, pady=_p_pady)
        patient_height_label = Label(patient_info_k_frame, text="身高:", font=self._BIG_FONT)
        patient_height_label.grid(row=2, column=0, sticky=W, pady=_p_pady)
        patient_weight_label = Label(patient_info_k_frame, text="体重:", font=self._BIG_FONT)
        patient_weight_label.grid(row=3, column=0, sticky=W, pady=_p_pady)
        patient_sex_label = Label(patient_info_k_frame, text="性别:", font=self._BIG_FONT)
        patient_sex_label.grid(row=4, column=0, sticky=W, pady=_p_pady)
        patient_birthday_label = Label(patient_info_k_frame, text="生日:", font=self._BIG_FONT)
        patient_birthday_label.grid(row=5, column=0, sticky=W, pady=_p_pady)
        patient_age_label = Label(patient_info_k_frame, text="年龄:", font=self._BIG_FONT)
        patient_age_label.grid(row=6, column=0, sticky=W, pady=_p_pady)
        patient_tracer_label = Label(patient_info_k_frame, text="示踪剂:", font=self._BIG_FONT)
        patient_tracer_label.grid(row=7, column=0, sticky=W, pady=13)
        Label(patient_info_frame, width=36, font=self._BIG_FONT).grid(row=1, column=0, columnspan=2, sticky=W)
        self.patient_id_value = Label(patient_info_v_frame, font=self._BIG_FONT)
        self.patient_id_value.grid(row=0, column=0, sticky=E, pady=_p_pady)
        self.patient_height_value = Label(patient_info_v_frame, font=self._BIG_FONT)
        self.patient_height_value.grid(row=2, column=0, sticky=E, pady=_p_pady)
        self.patient_weight_value = Label(patient_info_v_frame, font=self._BIG_FONT)
        self.patient_weight_value.grid(row=3, column=0, sticky=E, pady=_p_pady)
        self.patient_sex_value = Label(patient_info_v_frame, font=self._BIG_FONT)
        self.patient_sex_value.grid(row=4, column=0, sticky=E, pady=_p_pady)
        self.patient_birthday_value = Label(patient_info_v_frame, font=self._BIG_FONT)
        self.patient_birthday_value.grid(row=5, column=0, sticky=E, pady=_p_pady)
        self.patient_age_value = Label(patient_info_v_frame, font=self._BIG_FONT)
        self.patient_age_value.grid(row=6, column=0, sticky=E, pady=_p_pady)
        self.patient_tracer_value = Label(patient_info_v_frame, font=self._BIG_FONT)
        self.patient_tracer_value.grid(row=7, column=0, sticky=E, pady=11)
        if self.cfg["show_patient_name"] is True:
            patient_name_label = Label(patient_info_k_frame, text="姓名:", font=self._BIG_FONT)
            patient_name_label.grid(row=1, column=0, sticky=W, pady=_p_pady)
            self.patient_name_value = Label(patient_info_v_frame, font=self._BIG_FONT)
            self.patient_name_value.grid(row=1, column=0, sticky=E, pady=_p_pady)

        # 3. 右下角面板
        bottom_right_frame = Frame(self.root)
        bottom_right_frame.grid(row=1, column=3, sticky=NW)

        # 3.1 文件加载面板
        load_dir_frame = LabelFrame(bottom_right_frame, text='加载文件', font=self._MID_FONT)
        load_dir_frame.grid(row=0, column=0, sticky=NW, ipadx=5, ipady=0)
        load_ct_dir_btn = Button(load_dir_frame, command=self.load_ct_dir_btn_callback, width=17, text='CT文件夹路径')
        load_ct_dir_btn.config(font=self._BIG_FONT)
        load_ct_dir_btn.grid(row=0, column=0, padx=5)
        self.load_ct_dir_entry = Entry(load_dir_frame, width=70, font=self._BIG_FONT)
        self.load_ct_dir_entry.grid(row=0, column=1, pady=7)
        load_pet_dir_btn = Button(load_dir_frame, command=self.load_pet_dir_btn_callback, width=17, text="PET文件夹路径")
        load_pet_dir_btn.config(font=self._BIG_FONT)
        load_pet_dir_btn.grid(row=1, column=0, padx=5)
        self.load_pet_dir_entry = Entry(load_dir_frame, width=70, font=self._BIG_FONT)
        self.load_pet_dir_entry.grid(row=1, column=1, pady=7)
        load_dir_btn = Button(load_dir_frame, command=self.load_btn_callback, width=17, text="加载")
        load_dir_btn.config(font=self._BIG_FONT)
        load_dir_btn.grid(row=2, column=0, padx=5, pady=3)
        load_dir_label = Label(load_dir_frame, font=Font(size=15))
        load_dir_label.grid(row=2, column=1, sticky=W, )

        # 3.2 病人诊断面板
        diagnosis_frame = LabelFrame(bottom_right_frame, text="参考", font=self._MID_FONT)
        diagnosis_frame.grid(row=1, column=0)
        self.diagnosis_text = Text(diagnosis_frame, height=13, width=90, font=self._BIG_FONT, relief=FLAT)
        self.diagnosis_text.grid(row=0, column=0, padx=0, pady=0)
        diagnosis_save_btn = Button(diagnosis_frame, text="保存参考信息", command=self.save_remark_btn_callback)
        diagnosis_save_btn.config(height=1, font=self._BIG_FONT)
        diagnosis_save_btn.grid(row=1, column=0, sticky=EW)

        # 6. logo
        logo_label = Label(bottom_right_frame, text="Huiyan Jiang Lab. in Northeastern University", fg="gray")
        logo_label.config(font=self._BIG_FONT)
        logo_label.grid(row=2, column=0, sticky=EW, pady=10)

        # debug
        if self.cfg["debug"] is True:
            debug_mode(self)

        # 启动GUI
        self.root.mainloop()
