# coding=utf-8
import tkinter
from tkinter import *
from tkinter.filedialog import askdirectory
import cv2
import numpy as np
import os
import time
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import natsort
import shutil


def detect_file():
	# 读取文件目录，生成需要检测的文件名列表
	# 完成列表中的文件类型筛选
	# 输出含有二维码的图片的所有路径
	file_path = get_file_path()
	cycle_range = int(get_cycle_range())
	path_screen = []
	dirs = []
	# 获取所有文件的路径
	names = natsort.natsorted(os.listdir(file_path), alg=natsort.ns.PATH)
	print(names)
	for n in names:
		a = file_path + "\\" + n
		dirs.append(a)
	print(dirs)
	# 从所有文件的路径中筛选符合要求的文件路径
	for d in dirs:
		print(os.path.splitext(d)[1])
		if os.path.splitext(d)[1] in (".jpg", ".JPG", ".PNG", ".png", ".raw", ".RAW",
									  ".jpeg", ".JPEG", ".tif", ".TIF", ".gif", ".GIF"):  # 需要筛选的文件后缀名
			path_screen.append(d)  # 返回所有符合要求的文件路径
		else:
			print("程序没有找到图片文件！")
	print(path_screen)
	# 根据每组照片的数量，将指定的一部分含有二维码的图片路径存到一个列表中
	dirs_detect_file = []
	for i in path_screen:
		if path_screen.index(i) % cycle_range == 0:
			dirs_detect_file.append(i)
	print(str("待检测文件个数:") + '%.f' % len(dirs_detect_file))
	text.insert(END, str("待检测文件个数:") + '%.f' % len(dirs_detect_file) + '\n')
	return dirs_detect_file, path_screen


def detect_image(dirs_detect_file, cycle_range, file_path, path_screen):
	# 实例化微信二维码识别方法
	detect_obj = cv2.wechat_qrcode_WeChatQRCode('detect.prototxt', 'detect.caffemodel', 'sr.prototxt', 'sr.caffemodel')
	text.insert(END, "开始检测......" + '\n')
	start = time.time()  # 开始计时
	i = 0
	while i < len(dirs_detect_file):
		img = cv2.imdecode(np.fromfile(dirs_detect_file[i], dtype=np.uint8), cv2.IMREAD_COLOR)
		number, points = detect_obj.detectAndDecode(img)
		
		if number:  # success
			folder_path = file_path + r"\\" + number[0]
			exists = os.path.exists(folder_path)
			if not exists:
				os.makedirs(folder_path)
			else:
				pass
			# 文件移动到新的文件夹
			for n in range(0, cycle_range):
				old_file_path = path_screen[i * cycle_range + n]
				shutil.move(old_file_path, folder_path)
			text.insert(END, number[0] + ",分组成功!" + '\n')
			text.see("end")
			i = i + 1
		else:  # fail
			folder_path = file_path + "\未识别"
			exists = os.path.exists(folder_path)
			if not exists:
				os.makedirs(folder_path)
			else:
				pass
			# 文件移动到新的文件夹
			for n in range(0, cycle_range):
				old_file_path = path_screen[i * cycle_range + n]
				shutil.move(old_file_path, folder_path)
			text.insert(END, "未识别，分组失败!" + '\n')
			text.see("end")
			i = i + 1
	end = time.time()  # 终止计时
	text.insert(END, str('检测时间:') + '%.2f' % (end - start) + str("s") + '\n')
	speed = (end - start) / len(dirs_detect_file)
	text.insert(END, str('单组平均耗时：') + '%.2f' % speed + str("s") + '\n')
	text.insert(END, "照片分组结束！" + '\n')
	text.see("end")


def app():
	dirs_detect_file, path_screen = detect_file()
	cycle_range = get_cycle_range()
	file_path = get_file_path()
	detect_image(dirs_detect_file, cycle_range, file_path, path_screen)


def multprocess_it(func):
	# 创建进程
	t = threading.Thread(target=func)
	t.setDaemon(True)
	t.start()


def select_path():
	path_ = askdirectory()
	# 使用askdirectory()方法返回文件夹的路径
	if path_ == "":
		path.get()
	# 当打开文件路径选择框后点击"取消" 输入框会清空路径，所以使用get()方法再获取一次路径
	else:
		path_ = path_.replace("/", "\\")  # 实际在代码中执行的路径为“\“ 所以替换一下
		path.set(path_)


def open_path():
	# 打开指定的文件目录
	dirtion = os.path.dirname(path.get() + "\\")
	os.system('start ' + dirtion)


def get_file_path():
	file_path = E1.get()
	# print(file_path)
	return file_path


def get_cycle_range():
	cycle_range = spinbox2.get()
	# print(cycle_range)
	return int(cycle_range)


def close_window():
	root.destroy()


root = ttk.Window()
# 主界面
root.title("GroupIMG 2")
root.geometry("560x360+600+400")
root.resizable(False, False)
menu = tkinter.Menu(root, tearoff=False)

about_menu = tkinter.Menu(menu, tearoff=False)
menu.add_cascade(label="关于", menu=about_menu)
about_menu.add_command(label='关于软件: 1、本软件只能对二维码照片分组\n 2、不识别含有中文的二维码')
about_menu.add_command(label='鸣谢: 感谢QiHebiotech对本人工作的支持')
about_menu.add_command(label='作者: aaashuai')

about_menu2 = tkinter.Menu(menu, tearoff=False)
menu.add_cascade(label="软件更新记录", menu=about_menu2)
about_menu2.add_command(label='2022.6更新-支持对服务器上的照片进行分组')
about_menu2.add_command(label='2022.7更新-多线程，支持实时显示进度，优化照片分组算法，优化界面')
about_menu2.add_command(label='2022.9更新：解决频繁未识别的BUG')

root.config(menu=menu)

# 功能按键
path = StringVar()
path.set(os.path.abspath("."))
L1 = ttk.Label(root, text="请选择文件夹:")
L1.grid(row=1, column=0, sticky='w')
E1 = ttk.Entry(root, textvariable=path, bootstyle='success')
E1.grid(row=1, column=1, columnspan=2, ipadx=100)
B1 = tkinter.Button(root, text="选择", command=select_path)
B1.grid(row=1, column=3, ipadx=34, sticky='e')
B2 = tkinter.Button(root, text="打开文件位置", command=open_path)
B2.grid(row=2, column=3, ipadx=10, sticky='e')
L2 = tkinter.Label(root, text="每组照片数量:")
L2.grid(row=3, column=0, sticky='snw')
spinbox2 = ttk.Spinbox(root, from_=1, to=20, increment=1, width=5)
spinbox2.insert(0, "3")
spinbox2.grid(row=3, column=1, padx=5, pady=2, sticky="nsw")
# 获取每组照片的数量
B4 = tkinter.Button(root, text="开始", command=lambda: multprocess_it(app))
B4.grid(row=3, column=2, ipadx=34, pady=10, sticky='e')
B5 = tkinter.Button(root, text="退出", command=close_window)
B5.grid(row=3, column=3, ipadx=34, pady=10, sticky='e')
L3 = tkinter.Label(root, text="运行状态:")
L3.grid(row=4, column=0, sticky='w')
text = Text(root, width=75, height=12)
text.grid(row=7, column=0, columnspan=4, padx=1, pady=1, sticky='sne')
# 将滚动条填充


EventScrollBar = tkinter.Scrollbar(root, command=text.yview, orient="vertical")
EventScrollBar.grid(row=7, column=4, sticky="ns")
text.configure(yscrollcommand=EventScrollBar.set)

root.mainloop()
