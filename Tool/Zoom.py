import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageTk, ImageFont
import os
import platform
import threading
import subprocess # 用于系统级朗读兜底

# 尝试导入 pyttsx3，如果失败也不影响程序运行
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

class TextMagnifier:
    def __init__(self, root):
        self.root = root
        self.root.title("Chinese Characters and English Words Magnifier")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # 状态标记
        self.is_speaking = False

        # 初始化字体和界面
        self.setup_fonts()
        self.create_widgets()
        self.text_entry.focus_set() 
        
        self.update_status()

    # ------------------ 核心修复：独立的朗读线程 ------------------

    def speak_text(self):
        """用户点击 Speak 按钮时的入口"""
        text = self.text_var.get().strip()
        if not text:
            messagebox.showwarning("提示", "请输入要朗读的文本")
            return
            
        if self.is_speaking:
            # 如果正在朗读，强制忽略（防止重叠导致崩溃）
            print("正在朗读中，请稍候...")
            return

        # 启动一个全新的线程来处理这次朗读
        # 注意：这里不使用任何全局的 engine 对象，防止状态锁死
        t = threading.Thread(target=self._speak_worker_one_off, args=(text,))
        t.daemon = True
        t.start()

    def _speak_worker_one_off(self, text):
        """
        一次性朗读工作线程。
        策略：初始化 -> 朗读 -> 销毁。绝不重用。
        """
        self._set_speaking_state(True)
        
        try:
            # 1. 优先尝试使用 pyttsx3 (如果库存在)
            if PYTTSX3_AVAILABLE:
                success = self._try_pyttsx3_once(text)
                if success:
                    return # 成功则退出

            # 2. 如果 pyttsx3 失败或不可用，使用系统级兜底方案
            print("pyttsx3 失败或未安装，尝试系统原生朗读...")
            self._try_system_tts_once(text)

        except Exception as e:
            print(f"朗读发生未知错误: {e}")
        finally:
            self._set_speaking_state(False)

    def _try_pyttsx3_once(self, text):
        """尝试使用 pyttsx3 朗读一次。返回是否成功。"""
        engine = None
        try:
            # 每次都创建一个全新的引擎实例
            engine = pyttsx3.init()
            
            # 简单的语音选择逻辑
            voices = engine.getProperty('voices')
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
            
            chosen_voice = None
            for v in voices:
                if has_chinese:
                    if 'chinese' in v.name.lower() or 'zh' in v.id.lower():
                        chosen_voice = v.id
                        break
                else:
                    if 'english' in v.name.lower() or 'en' in v.id.lower():
                        chosen_voice = v.id
                        break
            
            if chosen_voice:
                engine.setProperty('voice', chosen_voice)

            engine.say(text)
            engine.runAndWait() # 阻塞当前线程直到说完
            return True
            
        except Exception as e:
            print(f"pyttsx3 内部错误: {e}")
            return False
        finally:
            if engine:
                try:
                    engine.stop()
                    del engine # 显式删除引用
                except:
                    pass

    def _try_system_tts_once(self, text):
        """
        系统级兜底方案。
        直接调用操作系统命令，完全绕过 Python 库的线程问题。
        """
        sys_name = platform.system()
        
        try:
            if sys_name == "Windows":
                # Windows PowerShell 朗读命令
                # 这里会尝试创建一个临时的 .NET 语音对象
                # 注意：这需要 PowerShell，且可能比 pyttsx3 启动慢 1-2 秒，但绝对稳定
                ps_command = f"Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak('{text}');"
                subprocess.run(["powershell", "-Command", ps_command], check=True)
                
            elif sys_name == "Darwin": # macOS
                # macOS 自带 say 命令
                subprocess.run(["say", text], check=True)
                
            else: # Linux
                # Linux 尝试 espeak 或 spd-say
                try:
                    subprocess.run(["espeak", text], check=True)
                except:
                    subprocess.run(["spd-say", text], check=True)
                    
        except Exception as e:
            print(f"系统原生朗读失败: {e}")

    def _set_speaking_state(self, is_speaking):
        """安全地在主线程更新 UI 状态"""
        def _update():
            self.is_speaking = is_speaking
            self.update_status()
        self.root.after(0, _update)

    # ------------------ 以下为原有 UI 逻辑 (保持不变) ------------------

    def setup_fonts(self):
        self.available_fonts = []
        font_paths = []
        system = platform.system()
        if system == "Windows":
            font_paths = ["C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simsun.ttc", "C:/Windows/Fonts/simkai.ttf"]
        elif system == "Darwin":
            font_paths = ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Light.ttc", "/System/Library/Fonts/STHeiti Medium.ttc"]
        else:
            font_paths = ["/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    ImageFont.truetype(font_path, 20)
                    self.available_fonts.append(font_path)
                except: continue
        
        if not self.available_fonts:
            self.default_font = ImageFont.load_default()
        else:
            self.default_font = None
        self.current_font_index = 0
        self.current_font_size = 100

    def create_widgets(self):
        title_label = tk.Label(self.root, text="Chinese Characters and English Words Magnifier", font=("Arial", 18, "bold"), bg='#f0f0f0', fg='#333333')
        title_label.pack(pady=15)
        
        input_frame = tk.Frame(self.root, bg='#f0f0f0')
        input_frame.pack(pady=10, fill='x', padx=20)
        
        input_label = tk.Label(input_frame, text="Enter Text:", font=("Arial", 12), bg='#f0f0f0')
        input_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.text_var = tk.StringVar()
        self.text_entry = ttk.Entry(input_frame, textvariable=self.text_var, font=("Arial", 14), width=50)
        self.text_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.text_entry.bind('<Return>', self.magnify_text)
        input_frame.columnconfigure(1, weight=1)
        
        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(pady=10, fill='x', padx=20)
        
        size_label = tk.Label(control_frame, text="Font Size:", font=("Arial", 10), bg='#f0f0f0')
        size_label.grid(row=0, column=0, padx=5, sticky='w')
        
        self.size_var = tk.IntVar(value=self.current_font_size)
        size_scale = tk.Scale(control_frame, from_=50, to=300, orient=tk.HORIZONTAL, variable=self.size_var, command=self.update_display, length=200, font=("Arial", 8))
        size_scale.grid(row=0, column=1, padx=5, sticky='w')
        
        if len(self.available_fonts) > 1:
            font_label = tk.Label(control_frame, text="Select Font:", font=("Arial", 10), bg='#f0f0f0')
            font_label.grid(row=0, column=2, padx=(20,5), sticky='w')
            font_names = [os.path.basename(f) for f in self.available_fonts]
            self.font_var = tk.StringVar(value=font_names[0])
            font_combo = ttk.Combobox(control_frame, textvariable=self.font_var, values=font_names, state="readonly", width=15)
            font_combo.grid(row=0, column=3, padx=5, sticky='w')
            font_combo.bind('<<ComboboxSelected>>', self.change_font)
        
        button_frame = tk.Frame(control_frame, bg='#f0f0f0')
        button_frame.grid(row=0, column=5, padx=(20,0), sticky='e') 
        
        speak_btn = tk.Button(button_frame, text="Speak", font=("Arial", 10), command=self.speak_text, bg='#9C27B0', fg='white', width=8, height=1)
        speak_btn.pack(side='left', padx=5)

        magnify_btn = tk.Button(button_frame, text="Magnify", font=("Arial", 10), command=self.magnify_text, bg='#4CAF50', fg='white', width=10, height=1)
        magnify_btn.pack(side='left', padx=5)
        
        clear_btn = tk.Button(button_frame, text="Clear", font=("Arial", 10), command=self.clear_text, bg='#f44336', fg='white', width=8, height=1)
        clear_btn.pack(side='left', padx=5)
        
        control_frame.columnconfigure(5, weight=1) 
        
        display_frame = tk.Frame(self.root, bg='white', relief='sunken', bd=2)
        display_frame.pack(pady=15, padx=20, fill='both', expand=True)
        
        self.display_label = tk.Label(display_frame, text="", bg='white', fg='black', font=("Arial", self.current_font_size), wraplength=800)
        self.display_label.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.status_var = tk.StringVar()
        status_label = tk.Label(self.root, textvariable=self.status_var, font=("Arial", 9), bg='#f0f0f0', fg='#666666')
        status_label.pack(pady=5)
        
        hint_label = tk.Label(self.root, text="提示: 输入中文或英文，点击 'Magnify' 或按 Enter 放大显示。点击 'Speak' 进行朗读。", font=("Arial", 10), bg='#f0f0f0', fg='#666666')
        hint_label.pack(pady=5)
        
        example_btn = tk.Button(self.root, text="Insert Example", font=("Arial", 9), command=self.insert_example, bg='#2196F3', fg='white')
        example_btn.pack(pady=5)

    def update_status(self):
        font_count = len(self.available_fonts)
        status_text = "朗读中..." if self.is_speaking else "就绪"
        if font_count > 0:
            current_font = os.path.basename(self.available_fonts[self.current_font_index])
            self.status_var.set(f"找到 {font_count} 个字体 | 当前字体: {current_font} | 字体大小: {self.current_font_size} | 状态: {status_text}")
        else:
            self.status_var.set(f"使用默认字体 | 字体大小: {self.current_font_size} | 状态: {status_text}")
    
    def change_font(self, event=None):
        selected_font = self.font_var.get()
        for i, font_path in enumerate(self.available_fonts):
            if os.path.basename(font_path) == selected_font:
                self.current_font_index = i
                break
        self.update_display()
        self.update_status()
    
    def magnify_text(self, event=None):
        text = self.text_var.get().strip()
        if not text: return
        font_size = self.size_var.get()
        self.current_font_size = font_size
        font_spec = ("Arial", font_size)
        if self.available_fonts:
            try:
                font_name = os.path.basename(self.available_fonts[self.current_font_index]).split('.')[0]
                font_spec = (font_name, font_size)
            except: pass
        self.display_label.config(text=text, font=font_spec)
        self.update_status()
    
    def update_display(self, value=None):
        if self.text_var.get().strip(): self.magnify_text()
    
    def clear_text(self):
        self.text_var.set("")
        self.display_label.config(text="")
        self.text_entry.focus()
    
    def insert_example(self):
        examples = ["Hello 你好 World!", "Chinese Characters 汉字", "Magnification 放大效果", "Python Programming 编程"]
        import random
        self.text_var.set(random.choice(examples))
        self.magnify_text()
        self.text_entry.focus()

def main():
    root = tk.Tk()
    app = TextMagnifier(root)
    root.mainloop()

if __name__ == "__main__":
    main()