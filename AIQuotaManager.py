import tkinter as tk
from tkinter import messagebox
from win10toast import ToastNotifier
from threading import Timer
import datetime
import json
import os

# 默认配置
DEFAULT_CONFIG = {
    "ChatGPT": {"type": "countdown", "reset_minutes": 180},  # 默认ChatGPT重置时间为180分钟
}

CONFIG_FILE = 'config.json'

# 读取配置文件
def load_config():
    if not os.path.exists(CONFIG_FILE):
        # 如果文件不存在，创建默认的配置文件
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        messagebox.showinfo("创建配置文件", "未找到配置文件，已创建默认 'config.json'。请编辑以设置您希望的重置时间。")
        return DEFAULT_CONFIG
    else:
        # 文件存在则读取配置
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)

# 保存配置到config文件
def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# 平台类，记录平台名称和计时/定时模式
class AIPlatform:
    def __init__(self, name, reset_type, reset_minutes=None, reset_time=None):
        self.name = name
        self.reset_type = reset_type  # "countdown" 或 "daily"
        self.reset_minutes = reset_minutes  # 用于倒计时的分钟
        self.reset_time = reset_time  # 用于定时的"HH:MM"时间格式
        self.is_available = True  # 模型是否可用，初始为True

# Windows消息通知
def send_windows_notification(platform_name):
    notifier = ToastNotifier()
    notifier.show_toast(f"{platform_name} 的重置时间已到", 
                        f"您可以再次使用 {platform_name}。", duration=10)

# 定时任务，自动重置提醒
def schedule_reset(platform, app):
    platform.is_available = False  # 设置为不可用
    app.update_reset_time(platform)  # 更新平台状态

    if platform.reset_type == "countdown":
        now = datetime.datetime.now()
        reset_time = now + datetime.timedelta(minutes=platform.reset_minutes)
        delay = (reset_time - now).total_seconds()

        def reset_platform():
            platform.is_available = True  # 重置后设为可用
            app.update_reset_time(platform)  # 更新平台状态
            send_windows_notification(platform.name)

        Timer(delay, reset_platform).start()

    elif platform.reset_type == "daily":
        now = datetime.datetime.now()
        reset_hour, reset_minute = map(int, platform.reset_time.split(":"))
        reset_time = now.replace(hour=reset_hour, minute=reset_minute, second=0, microsecond=0)
        
        # 如果当前时间已经过了今天的重置时间，调整到明天
        if reset_time <= now:
            reset_time += datetime.timedelta(days=1)

        delay = (reset_time - now).total_seconds()

        def reset_platform():
            platform.is_available = True
            app.update_reset_time(platform)
            send_windows_notification(platform.name)
            # 继续安排下一天的重置
            schedule_reset(platform, app)

        Timer(delay, reset_platform).start()

# GUI界面
class Application(tk.Tk):
    def __init__(self, config):
        super().__init__()
        self.config = config  # 用于存储用户自定义的平台信息
        self.platforms = []  # 动态存储平台对象
        self.title("AI 配额管理器v1.0")
        self.configure(bg='white')  # 背景设为白色，简洁风格
        self.resizable(False, False)  # 禁止调整窗口大小
        # 捕捉窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # 初始化已保存的平台
        for name, details in self.config.items():
            platform = AIPlatform(name, details["type"], details.get("reset_minutes"), details.get("reset_time"))
            self.platforms.append(platform)
        
        self.create_widgets()
        
    # 关闭窗口事件处理
    def on_closing(self):
        if messagebox.askokcancel("退出", "关闭程序会导致弹窗提醒失效，建议最小化，确定要退出程序吗?"):
            self.destroy()  # 关闭窗口

    # 创建界面组件
    def create_widgets(self):
        # 清除旧组件
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="平台配额管理器", font=("Helvetica", 16), bg='white').grid(row=0, columnspan=6, pady=10)

        # 创建已有的平台列表
        for i, platform in enumerate(self.platforms):
            # 根据平台状态设置背景颜色
            bg_color = '#28A745' if platform.is_available else '#DC3545'
            tk.Label(self, text=f"{platform.name}:", bg=bg_color, font=("Helvetica", 12), width=20).grid(row=i+1, column=0, padx=10, pady=5, sticky='w')
            if platform.reset_type == "countdown":
                tk.Label(self, text=f"每 {platform.reset_minutes} 分钟", bg='white', font=("Helvetica", 12)).grid(row=i+1, column=1, padx=10, pady=5)
            else:
                tk.Label(self, text=f"每天 {platform.reset_time}", bg='white', font=("Helvetica", 12)).grid(row=i+1, column=1, padx=10, pady=5)

            # 开始计时按钮
            tk.Button(self, text="闲者模式", command=lambda p=platform: self.set_reset_time(p), bg='#007BFF', fg='white').grid(row=i+1, column=2, padx=5, pady=5)
            # 编辑按钮
            tk.Button(self, text="编辑", command=lambda p=platform: self.open_edit_window(p), bg='#17A2B8', fg='white').grid(row=i+1, column=3, padx=5, pady=5)
            # 删除按钮
            tk.Button(self, text="删除", command=lambda p=platform: self.delete_platform(p), bg='#DC3545', fg='white').grid(row=i+1, column=4, padx=5, pady=5)

        # 分隔线
        separator = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN, bg='white')
        separator.grid(row=len(self.platforms)+1, columnspan=6, sticky="ew", pady=10)

        # 添加新平台部分

        # 表头：平台名称
        tk.Label(self, text="平台名称:", font=("Helvetica", 12), bg='white').grid(row=len(self.platforms)+2, column=0, padx=10, pady=5, sticky='w')
        # 平台名称输入框
        self.new_platform_name = tk.Entry(self, width=20)
        self.new_platform_name.grid(row=len(self.platforms)+2, column=1, padx=10)

        # 表头：重置方式选择
        tk.Label(self, text="重置方式:", font=("Helvetica", 12), bg='white').grid(row=len(self.platforms)+2, column=2, padx=10)

        # 重置方式选择菜单
        self.reset_type = tk.StringVar()
        self.reset_type.set("countdown")  # 默认选择倒计时
        reset_type_menu = tk.OptionMenu(self, self.reset_type, "countdown", "daily", command=self.update_reset_options)
        reset_type_menu.grid(row=len(self.platforms)+2, column=3)

        # 容器：根据重置方式显示的时间选择器
        self.time_input_frame = tk.Frame(self, bg='white')
        self.time_input_frame.grid(row=len(self.platforms)+3, column=0, columnspan=6, pady=5)

        # 默认显示倒计时的小时和分钟选择器
        self.update_reset_options("countdown")

        tk.Button(self, text="添加平台", command=self.add_platform, bg='#28A745', fg='white').grid(row=len(self.platforms)+4, column=0, columnspan=6, pady=10)

    # 更新倒计时/定时输入框
    def update_reset_options(self, reset_type):
        for widget in self.time_input_frame.winfo_children():
            widget.destroy()

        if reset_type == "countdown":
            # 倒计时选择：小时和分钟
            tk.Label(self.time_input_frame, text="每多少小时后重置:", bg='white').grid(row=0, column=0, sticky='e')
            self.new_hours = tk.IntVar()
            hours_menu = tk.OptionMenu(self.time_input_frame, self.new_hours, *range(0, 24))
            hours_menu.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(self.time_input_frame, text="每多少分钟后重置:", bg='white').grid(row=0, column=2, sticky='e')
            self.new_minutes = tk.IntVar()
            minutes_menu = tk.OptionMenu(self.time_input_frame, self.new_minutes, *range(0, 60))
            minutes_menu.grid(row=0, column=3, padx=5, pady=5)

        elif reset_type == "daily":
            # 定时选择：每天固定时间重置
            tk.Label(self.time_input_frame, text="每天固定时间 (HH:MM) 重置:", bg='white').grid(row=0, column=0, sticky='e')
            self.new_reset_time = tk.Entry(self.time_input_frame, width=10)
            self.new_reset_time.insert(0, "00:00")  # 默认值为00:00
            self.new_reset_time.grid(row=0, column=1, padx=5, pady=5)

    # 添加新平台
    def add_platform(self):
        name = self.new_platform_name.get()
        reset_type = self.reset_type.get()

        if not name:
            messagebox.showerror("输入错误", "平台名称不能为空")
            return

        if reset_type == "countdown":
            reset_minutes = self.new_hours.get() * 60 + self.new_minutes.get()
            if reset_minutes <= 0:
                messagebox.showerror("输入错误", "倒计时时间必须大于零")
                return
            platform = AIPlatform(name, reset_type, reset_minutes=reset_minutes)
        elif reset_type == "daily":
            reset_time = self.new_reset_time.get()
            try:
                hour, minute = map(int, reset_time.split(":"))
                if not (0 <= hour < 24 and 0 <= minute < 60):
                    raise ValueError
            except ValueError:
                messagebox.showerror("输入错误", "请设置有效的重置时间 (HH:MM)")
                return
            platform = AIPlatform(name, reset_type, reset_time=reset_time)

        self.platforms.append(platform)
        self.config[name] = {
            "type": reset_type,
            "reset_minutes": platform.reset_minutes,
            "reset_time": platform.reset_time
        }
        save_config(self.config)
        self.create_widgets()

    # 开始计时按钮动作
    def set_reset_time(self, platform):
        schedule_reset(platform, self)

    # 更新平台状态
    def update_reset_time(self, platform):
        self.create_widgets()

    # 编辑平台
    def open_edit_window(self, platform):
        edit_window = tk.Toplevel(self)
        edit_window.title(f"编辑 {platform.name}")
        edit_window.geometry("300x250")
        edit_window.grab_set()  # 阻止用户与主窗口互动
        edit_window.resizable(False, False)  # 禁止调整窗口大小

        tk.Label(edit_window, text="平台名称:").pack(pady=5)
        platform_name_entry = tk.Entry(edit_window)
        platform_name_entry.insert(0, platform.name)
        platform_name_entry.pack(pady=5)

        tk.Label(edit_window, text="重置方式:").pack(pady=5)
        reset_type_var = tk.StringVar()
        reset_type_var.set(platform.reset_type)
        reset_type_menu = tk.OptionMenu(edit_window, reset_type_var, "countdown", "daily")
        reset_type_menu.config(state="disabled")  # 禁用下拉菜单
        reset_type_menu.pack(pady=5)

        time_input_frame = tk.Frame(edit_window)
        time_input_frame.pack(pady=5)

        if platform.reset_type == "countdown":
            tk.Label(time_input_frame, text="重置小时:").pack(side=tk.LEFT, padx=5)
            edit_hours = tk.IntVar(value=platform.reset_minutes // 60)
            hours_menu = tk.OptionMenu(time_input_frame, edit_hours, *range(0, 24))
            hours_menu.pack(side=tk.LEFT)

            tk.Label(time_input_frame, text="重置分钟:").pack(side=tk.LEFT, padx=5)
            edit_minutes = tk.IntVar(value=platform.reset_minutes % 60)
            minutes_menu = tk.OptionMenu(time_input_frame, edit_minutes, *range(0, 60))
            minutes_menu.pack(side=tk.LEFT)

        elif platform.reset_type == "daily":
            tk.Label(time_input_frame, text="重置时间 (HH:MM):").pack(side=tk.LEFT, padx=5)
            edit_reset_time = tk.Entry(time_input_frame, width=10)
            edit_reset_time.insert(0, platform.reset_time)
            edit_reset_time.pack(side=tk.LEFT, padx=5)

        # 保存修改后的平台信息
        def save_changes():
            new_name = platform_name_entry.get()
            new_reset_type = reset_type_var.get()

            if not new_name:
                messagebox.showerror("输入错误", "平台名称不能为空")
                return

            if new_reset_type == "countdown":
                new_minutes = edit_hours.get() * 60 + edit_minutes.get()
                if new_minutes <= 0:
                    messagebox.showerror("输入错误", "倒计时时间必须大于零")
                    return
                platform.reset_minutes = new_minutes
                platform.reset_type = "countdown"
                platform.reset_time = None
            elif new_reset_type == "daily":
                new_reset_time = edit_reset_time.get()
                try:
                    hour, minute = map(int, new_reset_time.split(":"))
                    if not (0 <= hour < 24 and 0 <= minute < 60):
                        raise ValueError
                except ValueError:
                    messagebox.showerror("输入错误", "请设置有效的重置时间 (HH:MM)")
                    return
                platform.reset_time = new_reset_time
                platform.reset_type = "daily"
                platform.reset_minutes = None

            del self.config[platform.name]  # 删除旧名称的配置
            platform.name = new_name
            self.config[new_name] = {
                "type": platform.reset_type,
                "reset_minutes": platform.reset_minutes,
                "reset_time": platform.reset_time
            }
            save_config(self.config)
            self.create_widgets()
            edit_window.destroy()

        tk.Button(edit_window, text="保存", command=save_changes, bg='#28A745', fg='white').pack(pady=10)

    # 删除平台
    def delete_platform(self, platform):
        if messagebox.askokcancel("删除平台", f"确定要删除 {platform.name} 吗？"):
            self.platforms.remove(platform)
            del self.config[platform.name]
            save_config(self.config)
            self.create_widgets()

# 主程序
if __name__ == "__main__":
    config = load_config()  # 加载配置文件

    app = Application(config)
    app.mainloop()
