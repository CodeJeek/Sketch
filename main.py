from tkinter import filedialog
from tkinter import messagebox
import json
import sys
import os

from ttkbootstrap import *
from PIL import Image, ImageTk
import numpy as np


class Application():
    def __init__(self):
        self.get_data()
        self.flag = False

        self.root = Window(
            title="CodeJeek - 图片素描生成器",
            themename=self.data["theme"],
            iconphoto=r"resources\images\icons\icon.png",
            size=(1000, 600),
            resizable=(0, 0)
        )
        self.root.place_window_center()

        self.menu_bar = Frame(self.root)
        self.logo = Label(self.menu_bar, text="CodeJeek - 图片素描生成器", foreground="#7090FF", font=("微软雅黑", 18))

        self.file_bar = Frame(self.menu_bar)
        self.file_path = StringVar()
        self.file_info = Label(self.file_bar, text="图片路径:", font=("微软雅黑", 10))
        self.file_enter = Entry(self.file_bar, textvariable=self.file_path, width=30)
        self.file_button = Button(self.file_bar, text="选择路径", style="outline", command=self.get_path)
        self.depth = StringVar()
        self.depth_info = Label(self.file_bar, text="选择绘画深度:", font=("微软雅黑", 10))
        self.depth_box = Spinbox(self.file_bar, from_=0, to=100, increment=1, textvariable=self.depth, width=26)

        self.func_bar = Frame(self.menu_bar)
        self.start_button = Button(self.func_bar, text="开始转换", width=30, style="warning", command=self.start)
        self.save_button = Button(self.func_bar, text="保存图片", width=30, command=self.save)

        self.options_bar = Frame(self.menu_bar)
        self.options_image = PhotoImage(file=r"resources\images\icons\options.png")
        self.icon = self.options_image.subsample(20, 20)
        self.options_button = ttk.Button(self.options_bar, style=("success", "outline"), image=self.icon, command=self.options)
        self.version = Label(self.options_bar, text="Version: 1.0.0")

        self.error_info = Label(self.root, text="转换失败", style="danger", font=("微软雅黑", 18))

    def gui_arrang(self):
        self.menu_bar.pack(fill="y", side="left")
        self.logo.pack(pady=50)

        self.file_bar.pack(pady=30)
        self.file_info.grid(padx=10, pady=5, sticky=W)
        self.file_enter.grid(padx=10, sticky=W)
        self.file_button.grid(row=1, column=1, padx=10)
        self.depth_info.grid(padx=10, pady=10, sticky=W)
        self.depth_box.grid(row=2, columnspan=2, padx=10, pady=10, sticky=E)

        self.func_bar.pack(pady=70, anchor=S)
        self.start_button.grid(columnspan=2, padx=10, pady=5)
        self.save_button.grid(columnspan=2, padx=10, pady=5)

        self.options_bar.pack(fill="x", side="bottom", anchor=S)
        self.options_button.pack(side="left")
        self.version.pack(padx=10, side="right")


        self.depth.set(30)

        self.root.mainloop()

    def get_data(self):
        self.data_path = "data.json"
        if not os.path.exists(self.data_path):
            self.data = {"theme": "darkly"}

            with open(self.data_path, "w", encoding="utf-8") as data_path:
                json.dump(self.data, data_path)
        else:
            with open(self.data_path, "r", encoding="utf-8") as data_path:
                self.data = json.load(data_path)

    def get_path(self):
        self.photo_path = filedialog.askopenfilename(filetypes=[("JPG", ".jpg"), ("PNG", ".png"), ("All", ".*")])
        self.file_path.set(self.photo_path)

    def start(self):
        def resize(w, h, w_box, h_box, pil_image):
            f1 = 1.0 * w_box / w
            f2 = 1.0 * h_box / h
            factor = min([f1, f2])
            width = int(w * factor)
            height = int(h * factor)
            return pil_image.resize((width, height))

        self.flag = False

        try:
            self.error_info.pack_forget()
            self.image_bar.pack_forget()
        except Exception:
            pass

        try:
            file_path = str(self.file_path.get())
            depth = int(self.depth.get())
            picture_grad = np.gradient(np.asarray(Image.open(file_path).convert("L")).astype("int"))
            grad_x, grad_y = picture_grad[0] * depth / 100., picture_grad[1] * depth / 100.
            base = np.sqrt(grad_x ** 2 + grad_y ** 2 + 1.)
            _x, _y, _z = grad_x / base, grad_y / base, 1. / base
            sce_z, sce_x = np.pi / 2.1, np.pi / 3

            dx, dy, dz = np.cos(sce_z) * np.cos(sce_x), np.cos(sce_z) * np.sin(sce_x), np.sin(sce_z)
            normalized = 255 * (dx * _x + dy * _y + dz * _z).clip(0, 255)
            self.result_image = Image.fromarray(normalized.astype("uint8"))
            w, h = self.result_image.size
            self.realsize_image = resize(w, h, 660, 600, self.result_image)

            self.image = ImageTk.PhotoImage(self.realsize_image)
            self.image_bar = Label(self.root, image=self.image)
            self.image_bar.pack(fill="both")

            self.flag = True
        except Exception:
            self.error_info.pack(anchor="center", expand=True)

    def save(self):
        if self.flag:
            result_path = filedialog.asksaveasfilename(defaultextension="jpg", filetypes=[("JPG", '.jpg'), ("PNG", ".png")])

            try:
                self.result_image.save(result_path)
            except ValueError:
                pass
        else:
            messagebox.showwarning("警告", "你还没有转换图片!")

    def options(self):
        self.options_root = Toplevel(
            title="设置",
            resizable=(0, 0)
            )
        self.options_root.place_window_center()

        theme_list = [
            "cosmo", "flatly", "journal", "literal", "lumen", "minty", "pulse", "sandstone", "united", "yeti",
            "cyborg", "darkly", "solar", "superhero"
            ]
        self.theme = StringVar()
        self.theme_info = Label(self.options_root, text="选择主题:", font=("微软雅黑", 10))
        self.theme_info.grid(padx=4, pady=4)
        self.theme_box = Combobox(self.options_root, textvariable=self.theme, values=theme_list)
        self.theme_box.grid(row=0, column=1, padx=4, pady=4)
        self.theme.set(self.data["theme"])
        self.theme_box.config(state="readonly")

        self.sure_button = Button(self.options_root, text="确 定", style="success", command=self.chose)
        self.sure_button.grid(padx=4, pady=4)
        self.cancel_button = Button(self.options_root, text="取 消", style=("secondary", "outline"), command=self.options_root.destroy)
        self.cancel_button.grid(row=1, column=1, padx=4, pady=4, sticky=E)

    def chose(self):
        self.data["theme"] = str(self.theme.get())
        with open(self.data_path, "w", encoding="utf-8") as data_path:
            json.dump(self.data, data_path)

        py = sys.executable
        os.execl(py, py, *sys.argv)


def main():
    app = Application()
    app.gui_arrang()

if __name__ == "__main__":
    main()

