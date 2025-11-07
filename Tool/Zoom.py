import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageTk, ImageFont
import os
import platform

class TextMagnifier:
    def __init__(self, root):
        self.root = root
        self.root.title("Chinese Characters and English Words Magnifier")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Set fonts
        self.setup_fonts()
        
        # Create interface
        self.create_widgets()
        
    def setup_fonts(self):
        """Set available Chinese fonts"""
        self.available_fonts = []
        
        # Font paths for different systems
        font_paths = []
        system = platform.system()
        
        if system == "Windows":
            font_paths = [
                "C:/Windows/Fonts/simhei.ttf",  # Heiti
                "C:/Windows/Fonts/simsun.ttc",  # Simsun
                "C:/Windows/Fonts/msyh.ttc",    # Microsoft YaHei
                "C:/Windows/Fonts/simkai.ttf",  # KaiTi
            ]
        elif system == "Darwin":  # macOS
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/STHeiti Light.ttc",
                "/System/Library/Fonts/STHeiti Medium.ttc",
            ]
        else:  # Linux
            font_paths = [
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            ]
        
        # Test font availability
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    # Test if font can be loaded
                    test_font = ImageFont.truetype(font_path, 20)
                    self.available_fonts.append(font_path)
                    print(f"Found available font: {font_path}")
                except:
                    continue
        
        # Use PIL default font if no system fonts found
        if not self.available_fonts:
            print("No system fonts found, using default font")
            self.default_font = ImageFont.load_default()
        else:
            self.default_font = None
        
        # Current font index
        self.current_font_index = 0
        self.current_font_size = 100
    
    def get_current_font(self, size):
        """Get current font"""
        if self.available_fonts:
            try:
                return ImageFont.truetype(self.available_fonts[self.current_font_index], size)
            except:
                pass
        return ImageFont.load_default()
    
    def create_widgets(self):
        """Create interface components"""
        # Title
        title_label = tk.Label(self.root, text="Chinese Characters and English Words Magnifier", 
                              font=("Arial", 18, "bold"), 
                              bg='#f0f0f0', fg='#333333')
        title_label.pack(pady=15)
        
        # Input area frame
        input_frame = tk.Frame(self.root, bg='#f0f0f0')
        input_frame.pack(pady=10, fill='x', padx=20)
        
        # Input label
        input_label = tk.Label(input_frame, text="Enter Text:", 
                              font=("Arial", 12), bg='#f0f0f0')
        input_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        # Input field
        self.text_var = tk.StringVar()
        self.text_entry = tk.Entry(input_frame, textvariable=self.text_var, 
                                  font=("Arial", 14), width=50)
        self.text_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.text_entry.bind('<Return>', self.magnify_text)
        
        input_frame.columnconfigure(1, weight=1)
        
        # Control panel
        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(pady=10, fill='x', padx=20)
        
        # Font size adjustment
        size_label = tk.Label(control_frame, text="Font Size:", 
                             font=("Arial", 10), bg='#f0f0f0')
        size_label.grid(row=0, column=0, padx=5, sticky='w')
        
        self.size_var = tk.IntVar(value=self.current_font_size)
        size_scale = tk.Scale(control_frame, from_=50, to=300, 
                             orient=tk.HORIZONTAL,
                             variable=self.size_var,
                             command=self.update_display,
                             length=200, font=("Arial", 8))
        size_scale.grid(row=0, column=1, padx=5, sticky='w')
        
        # Font selection (if multiple fonts available)
        if len(self.available_fonts) > 1:
            font_label = tk.Label(control_frame, text="Select Font:", 
                                 font=("Arial", 10), bg='#f0f0f0')
            font_label.grid(row=0, column=2, padx=(20,5), sticky='w')
            
            font_names = [os.path.basename(f) for f in self.available_fonts]
            self.font_var = tk.StringVar(value=font_names[0])
            font_combo = ttk.Combobox(control_frame, textvariable=self.font_var, 
                                     values=font_names, state="readonly",
                                     width=15)
            font_combo.grid(row=0, column=3, padx=5, sticky='w')
            font_combo.bind('<<ComboboxSelected>>', self.change_font)
        
        # Button frame
        button_frame = tk.Frame(control_frame, bg='#f0f0f0')
        button_frame.grid(row=0, column=4, padx=(20,0), sticky='e')
        
        # Magnify button
        magnify_btn = tk.Button(button_frame, text="Magnify", 
                               font=("Arial", 10), 
                               command=self.magnify_text,
                               bg='#4CAF50', fg='white',
                               width=10, height=1)
        magnify_btn.pack(side='left', padx=5)
        
        # Clear button
        clear_btn = tk.Button(button_frame, text="Clear", 
                             font=("Arial", 10), 
                             command=self.clear_text,
                             bg='#f44336', fg='white',
                             width=8, height=1)
        clear_btn.pack(side='left', padx=5)
        
        control_frame.columnconfigure(4, weight=1)
        
        # Display area
        display_frame = tk.Frame(self.root, bg='white', relief='sunken', bd=2)
        display_frame.pack(pady=15, padx=20, fill='both', expand=True)
        
        # Create text display label (using Tkinter Label directly, supports large fonts)
        self.display_label = tk.Label(display_frame, text="", 
                                     bg='white', fg='black',
                                     font=("Arial", self.current_font_size),
                                     wraplength=800)
        self.display_label.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Status information
        self.status_var = tk.StringVar()
        status_label = tk.Label(self.root, textvariable=self.status_var,
                               font=("Arial", 9), bg='#f0f0f0', fg='#666666')
        status_label.pack(pady=5)
        
        # Update status information
        self.update_status()
        
        # Hint text
        hint_label = tk.Label(self.root, 
                             text="Tip: Enter Chinese characters or English words and click 'Magnify' or press Enter",
                             font=("Arial", 10), bg='#f0f0f0', fg='#666666')
        hint_label.pack(pady=5)
        
        # Example text button
        example_btn = tk.Button(self.root, text="Insert Example", 
                               font=("Arial", 9),
                               command=self.insert_example,
                               bg='#2196F3', fg='white')
        example_btn.pack(pady=5)
        
        # Set focus to input field
        self.text_entry.focus()
    
    def update_status(self):
        """Update status information"""
        font_count = len(self.available_fonts)
        if font_count > 0:
            current_font = os.path.basename(self.available_fonts[self.current_font_index])
            self.status_var.set(f"Found {font_count} fonts | Current font: {current_font} | Font size: {self.current_font_size}")
        else:
            self.status_var.set(f"Using default font | Font size: {self.current_font_size}")
    
    def change_font(self, event=None):
        """Change font"""
        selected_font = self.font_var.get()
        for i, font_path in enumerate(self.available_fonts):
            if os.path.basename(font_path) == selected_font:
                self.current_font_index = i
                break
        self.update_display()
        self.update_status()
    
    def magnify_text(self, event=None):
        """Magnify and display text"""
        text = self.text_var.get().strip()
        
        if not text:
            messagebox.showwarning("Tip", "Please enter text to magnify")
            return
        
        # Use Tkinter Label directly to display large font text
        font_size = self.size_var.get()
        self.current_font_size = font_size
        
        # Create font (using system-supported fonts)
        font_spec = ("Arial", font_size)
        
        # Try to use Chinese fonts
        if self.available_fonts:
            try:
                # Get font name (without extension)
                font_name = os.path.basename(self.available_fonts[self.current_font_index]).split('.')[0]
                font_spec = (font_name, font_size)
            except:
                pass
        
        # Update display
        self.display_label.config(text=text, font=font_spec)
        self.update_status()
    
    def update_display(self, value=None):
        """Update display (slider callback)"""
        if self.text_var.get().strip():
            self.magnify_text()
    
    def clear_text(self):
        """Clear text"""
        self.text_var.set("")
        self.display_label.config(text="")
        self.text_entry.focus()
    
    def insert_example(self):
        """Insert example text"""
        examples = [
            "Hello 你好 World!",
            "Chinese Characters 汉字", 
            "Magnification 放大效果",
            "Python Programming 编程",
            "Test Chinese Display 测试中文显示",
            "This is a test 这是一个测试"
        ]
        import random
        example = random.choice(examples)
        self.text_var.set(example)
        self.magnify_text()
        self.text_entry.focus()

def main():
    # Create main window
    root = tk.Tk()
    
    # Create application
    app = TextMagnifier(root)
    
    # Run main loop
    root.mainloop()

if __name__ == "__main__":
    main()