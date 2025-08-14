import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
import platform
import re

class NightNoteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NightNote GUI")
        
        # 程序信息
        self.__mainname__ = "NightNote GUI"
        self.__version__ = "25.0708.1"
        self.__author__ = "DONGFANG Lingye"
        self.__email__ = "ly@lingye.online"
        
        # 多缓冲区支持
        self.buffers = [""]
        self.buffer_files = [""]
        self.current_buffer = 0
        
        # 历史记录
        self.history = []
        self.redo_history = []
        self.MAX_HISTORY = 10
        
        # 样式配置
        self.setup_styles()
        
        # 创建UI
        self.create_menu()
        self.create_toolbar()
        self.create_text_area()
        self.create_status_bar()
        
        # 初始状态
        self.update_title()
        self.update_status()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')  # 使用现代主题
        
        # 自定义样式
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', padding=6)
        style.configure('Toolbar.TFrame', background='#e0e0e0')
        style.configure('Status.TFrame', background='#e0e0e0')
        style.configure('Status.TLabel', background='#e0e0e0', font=('Arial', 9))
        
        # 文本区域样式
        self.text_bg = '#ffffff'
        self.text_fg = '#000000'
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="打开...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="保存", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="另存为...", command=self.save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit, accelerator="Alt+F4")
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="撤销", command=self.undo_last, accelerator="Ctrl+Z")
        edit_menu.add_command(label="重做", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="查找", command=self.search_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="替换", command=self.replace_text, accelerator="Ctrl+H")
        menubar.add_cascade(label="编辑", menu=edit_menu)
        
        # 缓冲区菜单
        buffer_menu = tk.Menu(menubar, tearoff=0)
        buffer_menu.add_command(label="新建缓冲区", command=self.new_buffer, accelerator="Ctrl+B")
        buffer_menu.add_command(label="切换缓冲区", command=self.switch_buffer, accelerator="Ctrl+Tab")
        buffer_menu.add_command(label="删除缓冲区", command=self.remove_buffer)
        buffer_menu.add_command(label="列出缓冲区", command=self.list_buffers)
        menubar.add_cascade(label="缓冲区", menu=buffer_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="帮助", command=self.show_help, accelerator="F1")
        help_menu.add_command(label="关于", command=self.show_about)
        help_menu.add_command(label="调试信息", command=self.show_debug)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root, style='Toolbar.TFrame')
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        
        # 工具栏按钮图标
        icons = [
            ("新建", self.new_file),
            ("打开", self.open_file),
            ("保存", self.save_file),
            ("撤销", self.undo_last),
            ("重做", self.redo),
            ("查找", self.search_text),
            ("替换", self.replace_text)
        ]
        
        for text, command in icons:
            btn = ttk.Button(toolbar, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=2, pady=2)
    
    def create_text_area(self):
        self.text_frame = ttk.Frame(self.root)
        self.text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 使用ScrolledText实现滚动条
        self.text = ScrolledText(self.text_frame, wrap=tk.WORD, undo=True,
                               font=('Consolas', 11), bg=self.text_bg, fg=self.text_fg,
                               insertbackground='black', selectbackground='#4a98e9')
        self.text.pack(fill=tk.BOTH, expand=True)
        
        # 绑定快捷键
        self.text.bind("<Control-n>", lambda e: self.new_file())
        self.text.bind("<Control-o>", lambda e: self.open_file())
        self.text.bind("<Control-s>", lambda e: self.save_file())
        self.text.bind("<Control-Shift-S>", lambda e: self.save_as())
        self.text.bind("<Control-z>", lambda e: self.undo_last())
        self.text.bind("<Control-y>", lambda e: self.redo())
        self.text.bind("<Control-f>", lambda e: self.search_text())
        self.text.bind("<Control-h>", lambda e: self.replace_text())
        self.text.bind("<Control-b>", lambda e: self.new_buffer())
        self.text.bind("<Control-Tab>", lambda e: self.switch_buffer())
        self.text.bind("<F1>", lambda e: self.show_help())
    
    def create_status_bar(self):
        status_frame = ttk.Frame(self.root, style='Status.TFrame')
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=2)
        
        self.status_var = tk.StringVar()
        self.status = ttk.Label(status_frame, textvariable=self.status_var, 
                              style='Status.TLabel')
        self.status.pack(side=tk.LEFT, padx=5)
        
        # 添加缓冲区指示器
        self.buffer_var = tk.StringVar()
        ttk.Label(status_frame, textvariable=self.buffer_var, 
                 style='Status.TLabel').pack(side=tk.RIGHT, padx=5)
    
    def update_title(self):
        filename = self.buffer_files[self.current_buffer]
        title = f"{self.__mainname__} {self.__version__}"
        if filename:
            title += f" - {filename}"
        self.root.title(title)
    
    def update_status(self):
        text = self.buffers[self.current_buffer]
        lines = len(text.split('\n')) if text else 0
        size = len(text.encode('utf-8')) if text else 0
        self.status_var.set(f"行数: {lines} | 大小: {size} 字节")
        self.buffer_var.set(f"缓冲区: {self.current_buffer}/{len(self.buffers)-1}")
    
    def save_state(self, operation):
        """保存当前状态到历史记录"""
        if len(self.history) >= self.MAX_HISTORY:
            self.history.pop(0)
        self.history.append((self.current_buffer, self.buffers[self.current_buffer], 
                          self.buffer_files[self.current_buffer]))
        self.redo_history.clear()
    
    # 以下是各个功能的实现 (保持不变)
    def new_file(self):
        self.save_state("新建文件")
        self.buffers[self.current_buffer] = ""
        self.buffer_files[self.current_buffer] = ""
        self.text.delete(1.0, tk.END)
        self.update_title()
        self.update_status()
    
    def open_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                self.save_state(f"打开文件 {filename}")
                self.buffers[self.current_buffer] = content
                self.buffer_files[self.current_buffer] = filename
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, content)
                self.update_title()
                self.update_status()
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件: {str(e)}")
    
    def save_file(self):
        if not self.buffer_files[self.current_buffer]:
            self.save_as()
            return
        
        try:
            content = self.text.get(1.0, tk.END)
            with open(self.buffer_files[self.current_buffer], 'w') as f:
                f.write(content)
            self.save_state(f"保存文件 {self.buffer_files[self.current_buffer]}")
            self.buffers[self.current_buffer] = content
            messagebox.showinfo("保存", "文件保存成功")
            self.update_status()
        except Exception as e:
            messagebox.showerror("错误", f"无法保存文件: {str(e)}")
    
    def save_as(self):
        filename = filedialog.asksaveasfilename()
        if filename:
            try:
                content = self.text.get(1.0, tk.END)
                with open(filename, 'w') as f:
                    f.write(content)
                self.save_state(f"另存为 {filename}")
                self.buffers[self.current_buffer] = content
                self.buffer_files[self.current_buffer] = filename
                self.update_title()
                self.update_status()
                messagebox.showinfo("保存", "文件保存成功")
            except Exception as e:
                messagebox.showerror("错误", f"无法保存文件: {str(e)}")
    
    def undo_last(self):
        if not self.history:
            messagebox.showinfo("撤销", "没有可撤销的操作")
            return
        
        buf_idx, buf_content, buf_file = self.history.pop()
        self.redo_history.append((self.current_buffer, self.buffers[self.current_buffer], 
                                self.buffer_files[self.current_buffer]))
        self.current_buffer = buf_idx
        self.buffers[buf_idx] = buf_content
        self.buffer_files[buf_idx] = buf_file
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, buf_content)
        self.update_title()
        self.update_status()
        messagebox.showinfo("撤销", f"已撤销操作，恢复缓冲区 {buf_idx}")
    
    def redo(self):
        if not self.redo_history:
            messagebox.showinfo("重做", "没有可重做的操作")
            return
        
        buf_idx, buf_content, buf_file = self.redo_history.pop()
        self.history.append((self.current_buffer, self.buffers[self.current_buffer], 
                           self.buffer_files[self.current_buffer]))
        self.current_buffer = buf_idx
        self.buffers[buf_idx] = buf_content
        self.buffer_files[buf_idx] = buf_file
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, buf_content)
        self.update_title()
        self.update_status()
        messagebox.showinfo("重做", f"已重做操作，恢复缓冲区 {buf_idx}")
    
    def search_text(self):
        pattern = simpledialog.askstring("查找", "输入要查找的内容:")
        if pattern:
            content = self.text.get(1.0, tk.END)
            try:
                regex = re.compile(pattern)
                matches = [m for m in regex.finditer(content)]
                
                if not matches:
                    messagebox.showinfo("查找", "未找到匹配内容")
                else:
                    # 高亮显示第一个匹配项
                    first_match = matches[0]
                    start = f"1.0 + {first_match.start()} chars"
                    end = f"1.0 + {first_match.end()} chars"
                    self.text.tag_add("search", start, end)
                    self.text.tag_config("search", background="yellow")
                    self.text.see(start)
                    messagebox.showinfo("查找", f"找到 {len(matches)} 处匹配")
            except re.error:
                messagebox.showerror("错误", "无效的正则表达式")
    
    def replace_text(self):
        pattern = simpledialog.askstring("替换", "输入要查找的内容:")
        if not pattern:
            return
            
        replacement = simpledialog.askstring("替换", f"将 '{pattern}' 替换为:")
        if replacement is None:
            return
            
        content = self.text.get(1.0, tk.END)
        try:
            regex = re.compile(pattern)
            new_content, count = regex.subn(replacement, content)
            
            if count > 0:
                self.save_state(f"替换 '{pattern}' 为 '{replacement}'")
                self.buffers[self.current_buffer] = new_content
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, new_content)
                messagebox.showinfo("替换", f"替换了 {count} 处")
            else:
                messagebox.showinfo("替换", "未找到匹配内容")
        except re.error:
            messagebox.showerror("错误", "无效的正则表达式")
    
    def new_buffer(self):
        self.save_state("新建缓冲区")
        self.buffers.append("")
        self.buffer_files.append("")
        self.current_buffer = len(self.buffers) - 1
        self.text.delete(1.0, tk.END)
        self.update_title()
        self.update_status()
        messagebox.showinfo("缓冲区", f"已创建新缓冲区 {self.current_buffer}")
    
    def switch_buffer(self):
        buf_num = simpledialog.askinteger("切换缓冲区", 
                                         f"输入缓冲区编号 (0-{len(self.buffers)-1}):")
        if buf_num is not None and 0 <= buf_num < len(self.buffers):
            self.save_state(f"切换到缓冲区 {buf_num}")
            self.current_buffer = buf_num
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, self.buffers[buf_num])
            self.update_title()
            self.update_status()
        elif buf_num is not None:
            messagebox.showerror("错误", "无效的缓冲区编号")
    
    def remove_buffer(self):
        if len(self.buffers) == 1:
            messagebox.showerror("错误", "必须保留至少一个缓冲区")
            return
            
        buf_num = simpledialog.askinteger("删除缓冲区", 
                                         f"输入要删除的缓冲区编号 (0-{len(self.buffers)-1}):")
        if buf_num is not None and 0 <= buf_num < len(self.buffers):
            self.save_state(f"删除缓冲区 {buf_num}")
            self.buffers.pop(buf_num)
            self.buffer_files.pop(buf_num)
            
            if self.current_buffer == buf_num:
                self.current_buffer = 0
            elif self.current_buffer > buf_num:
                self.current_buffer -= 1
                
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, self.buffers[self.current_buffer])
            self.update_title()
            self.update_status()
            messagebox.showinfo("删除", f"已删除缓冲区 {buf_num}")
        elif buf_num is not None:
            messagebox.showerror("错误", "无效的缓冲区编号")
    
    def list_buffers(self):
        info = "缓冲区列表:\n"
        for idx, (buf, fname) in enumerate(zip(self.buffers, self.buffer_files)):
            size = len(buf.encode('utf-8'))
            lines = len(buf.split('\n'))
            mark = " <-- 当前" if idx == self.current_buffer else ""
            info += f"[{idx}] {lines} 行, {size} 字节, '{fname}'{mark}\n"
        messagebox.showinfo("缓冲区列表", info)
    
    def show_help(self):
        help_text = f"""{self.__mainname__} 版本 {self.__version__} 作者 {self.__author__} <{self.__email__}>

功能说明:
1. 文件操作: 新建、打开、保存文件
2. 编辑功能: 撤销、重做、查找、替换
3. 多缓冲区管理: 可创建、切换、删除多个缓冲区
4. 支持正则表达式查找替换

快捷键:
Ctrl+N: 新建文件
Ctrl+O: 打开文件
Ctrl+S: 保存文件
Ctrl+Shift+S: 另存为
Ctrl+Z: 撤销
Ctrl+Y: 重做
Ctrl+F: 查找
Ctrl+H: 替换
Ctrl+B: 新建缓冲区
Ctrl+Tab: 切换缓冲区
F1: 帮助"""
        messagebox.showinfo("帮助", help_text)
    
    def show_about(self):
        about_text = f"""{self.__mainname__} 版本 {self.__version__}

一个简单的文本编辑器，支持多缓冲区管理。

作者: {self.__author__}
邮箱: {self.__email__}"""
        messagebox.showinfo("关于", about_text)
    
    def show_debug(self):
        debug_text = f"""调试信息
版本: {self.__version__}
操作系统: {platform.system()}
系统版本: {platform.version()}
平台: {platform.platform()}
Python版本: {platform.python_version()}

当前缓冲区: {self.current_buffer}
缓冲区数量: {len(self.buffers)}"""
        messagebox.showinfo("调试信息", debug_text)

if __name__ == "__main__":
    root = tk.Tk()
    
    # 设置窗口图标和初始大小
    try:
        root.iconbitmap('note.ico')  # 如果有图标文件
    except:
        pass
        
    root.geometry("900x650")
    app = NightNoteGUI(root)
    root.mainloop()
