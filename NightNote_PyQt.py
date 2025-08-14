from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QAction, 
                            QFileDialog, QMessageBox, QInputDialog, QToolBar,
                            QStatusBar, QVBoxLayout, QWidget, QLabel, QSplitter, QStyle)
from PyQt5.QtGui import QIcon, QTextCursor, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, QSize
import platform
import re
import sys

MAINNAME = "NightNote"
VERSION = "250814"
AUTHOR = "DONGFANG Lingye"
EMAIL = "ly@lingye.online"

class NightNoteGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__mainname__ = MAINNAME
        self.__version__ = VERSION
        self.__author__ = AUTHOR
        self.__email__ = EMAIL
        # 缓冲区
        self.buffers = [""]
        self.buffer_files = [""]
        self.current_buffer = 0
        # 历史记录
        self.history = []
        self.redo_history = []
        self.MAX_HISTORY = 10
        
        self.initUI()
        self.update_title()
        self.update_status()
    
    def initUI(self):
        # 设置窗口属性
        self.setWindowTitle(f"{self.__mainname__} {self.__version__}")
        self.setGeometry(100, 100, 900, 650)
        # 检测系统主题
        self.is_dark_theme = self.detect_dark_theme()
        # 设置颜色方案
        if self.is_dark_theme:
            self.bg_color = "#2d2d2d"
            self.text_color = "#ffffff"
            self.toolbar_bg = "#3d3d3d"
            self.toolbar_text = "#ffffff"
            self.status_bg = "#3d3d3d"
            self.status_text = "#ffffff"
        else:
            self.bg_color = "#ffffff"
            self.text_color = "#000000"
            self.toolbar_bg = "#f0f0f0"
            self.toolbar_text = "#000000"
            self.status_bg = "#f0f0f0"
            self.status_text = "#000000"
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # 文本编辑区域
        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet(f"""
            QTextEdit {{
                font-family: Consolas;
                font-size: 12pt;
                background-color: {self.bg_color};
                color: {self.text_color};
            }}
        """)
        # 添加到布局
        main_layout.addWidget(self.text_edit)
        # 菜单栏
        self.create_menubar()
        # 工具栏
        self.create_toolbar()
        # 状态栏
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {self.status_bg};
                color: {self.status_text};
                border-top: 1px solid {'#505050' if self.is_dark_theme else '#d0d0d0'};
            }}
            QLabel {{
                color: {self.status_text};
            }}
        """)
        self.setStatusBar(self.status_bar)
        
        # 状态栏标签
        self.status_label = QLabel()
        self.buffer_label = QLabel()
        self.status_bar.addPermanentWidget(self.status_label, 1)
        self.status_bar.addPermanentWidget(self.buffer_label)
    
    def create_menubar(self):
        menubar = self.menuBar()
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        new_action = QAction('新建', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('打开...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('保存', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction('另存为...', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Alt+F4')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑')
        
        undo_action = QAction('撤销', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.undo_last)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('重做', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction('查找', self)
        find_action.setShortcut('Ctrl+F')
        find_action.triggered.connect(self.search_text)
        edit_menu.addAction(find_action)
        
        replace_action = QAction('替换', self)
        replace_action.setShortcut('Ctrl+H')
        replace_action.triggered.connect(self.replace_text)
        edit_menu.addAction(replace_action)
        # 缓冲区菜单
        buffer_menu = menubar.addMenu('缓冲区')
        
        new_buffer_action = QAction('新建缓冲区', self)
        new_buffer_action.setShortcut('Ctrl+B')
        new_buffer_action.triggered.connect(self.new_buffer)
        buffer_menu.addAction(new_buffer_action)
        
        switch_buffer_action = QAction('切换缓冲区', self)
        switch_buffer_action.setShortcut('Ctrl+Tab')
        switch_buffer_action.triggered.connect(self.switch_buffer)
        buffer_menu.addAction(switch_buffer_action)
        
        remove_buffer_action = QAction('删除缓冲区', self)
        remove_buffer_action.triggered.connect(self.remove_buffer)
        buffer_menu.addAction(remove_buffer_action)
        
        list_buffers_action = QAction('列出缓冲区', self)
        list_buffers_action.triggered.connect(self.list_buffers)
        buffer_menu.addAction(list_buffers_action)
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        help_action = QAction('帮助', self)
        help_action.setShortcut('F1')
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        debug_action = QAction('调试信息', self)
        debug_action.triggered.connect(self.show_debug)
        help_menu.addAction(debug_action)
    
    def detect_dark_theme(self):
        #检测是否使用深色主题
        palette = self.palette()
        text_color = palette.text().color()
        return text_color.lightness() > 128
    
    def create_toolbar(self):
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: {self.toolbar_bg};
                border: none;
                spacing: 5px;
                padding: 2px;
            }}
            QToolButton {{
                color: {self.toolbar_text};
                background-color: transparent;
                border: 1px solid transparent;
                padding: 4px;
                margin: 1px;
                font: 9pt;
            }}
            QToolButton:hover {{
                background-color: {'#505050' if self.is_dark_theme else '#e0e0e0'};
                border: 1px solid {'#606060' if self.is_dark_theme else '#d0d0d0'};
            }}
            QToolButton:pressed {{
                background-color: {'#404040' if self.is_dark_theme else '#d0d0d0'};
            }}
            QToolButton:!hover {{
                color: {self.toolbar_text};
            }}
        """)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        palette = toolbar.palette()
        palette.setColor(palette.ButtonText, QColor(self.toolbar_text))
        toolbar.setPalette(palette)

        actions = [
            ('新建', QApplication.style().standardIcon(QStyle.SP_FileIcon), self.new_file),
            ('打开', QApplication.style().standardIcon(QStyle.SP_DialogOpenButton), self.open_file),
            ('保存', QApplication.style().standardIcon(QStyle.SP_DialogSaveButton), self.save_file),
            ('撤销', QApplication.style().standardIcon(QStyle.SP_ArrowBack), self.undo_last),
            ('重做', QApplication.style().standardIcon(QStyle.SP_ArrowForward), self.redo),
            ('查找', QApplication.style().standardIcon(QStyle.SP_FileDialogContentsView), self.search_text),
            ('替换', QApplication.style().standardIcon(QStyle.SP_FileDialogDetailedView), self.replace_text)
        ]
        
        for text, icon, callback in actions:
            action = QAction(icon, text, self)
            action.triggered.connect(callback)
            toolbar.addAction(action)
    
    def update_title(self):
        filename = self.buffer_files[self.current_buffer]
        title = f"{self.__mainname__} {self.__version__}"
        if filename:
            title += f" - {filename}"
        self.setWindowTitle(title)
    
    def update_status(self):
        text = self.buffers[self.current_buffer]
        lines = len(text.split('\n')) if text else 0
        size = len(text.encode('utf-8')) if text else 0
        self.status_label.setText(f"{lines} lines | {size} bytes")
        self.buffer_label.setText(f"Buffer: {self.current_buffer+1}/{len(self.buffers)}")
    
    def save_state(self, operation):
        # 保存当前状态到历史记录
        if len(self.history) >= self.MAX_HISTORY:
            self.history.pop(0)
        self.history.append((self.current_buffer, self.buffers[self.current_buffer], 
                          self.buffer_files[self.current_buffer]))
        self.redo_history.clear()
    
    def new_file(self):
        self.save_state("新建文件")
        self.buffers[self.current_buffer] = ""
        self.buffer_files[self.current_buffer] = ""
        self.text_edit.clear()
        self.update_title()
        self.update_status()
    
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "打开文件")
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.save_state(f"打开文件 {filename}")
                self.buffers[self.current_buffer] = content
                self.buffer_files[self.current_buffer] = filename
                self.text_edit.setPlainText(content)
                self.update_title()
                self.update_status()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开文件: {str(e)}")
    
    def save_file(self):
        if not self.buffer_files[self.current_buffer]:
            self.save_as()
            return
        
        try:
            content = self.text_edit.toPlainText()
            with open(self.buffer_files[self.current_buffer], 'w', encoding='utf-8') as f:
                f.write(content)
            self.save_state(f"保存文件 {self.buffer_files[self.current_buffer]}")
            self.buffers[self.current_buffer] = content
            self.status_label.setText("文件保存成功")
            self.update_status()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法保存文件: {str(e)}")
    
    def save_as(self):
        filename, _ = QFileDialog.getSaveFileName(self, "另存为")
        if filename:
            try:
                content = self.text_edit.toPlainText()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.save_state(f"另存为 {filename}")
                self.buffers[self.current_buffer] = content
                self.buffer_files[self.current_buffer] = filename
                self.update_title()
                self.update_status()
                self.status_label.setText("文件保存成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法保存文件: {str(e)}")
    
    def undo_last(self):
        if not self.history:
            QMessageBox.information(self, "撤销", "没有可撤销的操作")
            return
        
        buf_idx, buf_content, buf_file = self.history.pop()
        self.redo_history.append((self.current_buffer, self.buffers[self.current_buffer], 
                                self.buffer_files[self.current_buffer]))
        self.current_buffer = buf_idx
        self.buffers[buf_idx] = buf_content
        self.buffer_files[buf_idx] = buf_file
        self.text_edit.setPlainText(buf_content)
        self.update_title()
        self.update_status()
        QMessageBox.information(self, "撤销", f"已撤销操作，恢复缓冲区 {buf_idx}")
    
    def redo(self):
        if not self.redo_history:
            QMessageBox.information(self, "重做", "没有可重做的操作")
            return
        
        buf_idx, buf_content, buf_file = self.redo_history.pop()
        self.history.append((self.current_buffer, self.buffers[self.current_buffer], 
                           self.buffer_files[self.current_buffer]))
        self.current_buffer = buf_idx
        self.buffers[buf_idx] = buf_content
        self.buffer_files[buf_idx] = buf_file
        self.text_edit.setPlainText(buf_content)
        self.update_title()
        self.update_status()
        QMessageBox.information(self, "重做", f"已重做操作，恢复缓冲区 {buf_idx}")
    
    def search_text(self):
        pattern, ok = QInputDialog.getText(self, "查找", "输入要查找的内容:")
        if ok and pattern:
            content = self.text_edit.toPlainText()
            try:
                regex = re.compile(pattern)
                matches = [m for m in regex.finditer(content)]
                
                if not matches:
                    QMessageBox.information(self, "查找", "未找到匹配内容")
                else:
                    # 高亮显示第一个匹配项
                    first_match = matches[0]
                    cursor = self.text_edit.textCursor()
                    cursor.setPosition(first_match.start())
                    cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 
                                      first_match.end() - first_match.start())
                    
                    # 设置高亮格式
                    fmt = QTextCharFormat()
                    fmt.setBackground(QColor("yellow"))
                    cursor.mergeCharFormat(fmt)
                    
                    self.text_edit.setTextCursor(cursor)
                    self.text_edit.setFocus()
                    
                    QMessageBox.information(self, "查找", f"找到 {len(matches)} 处匹配")
            except re.error:
                QMessageBox.critical(self, "错误", "无效的正则表达式")
    
    def replace_text(self):
        pattern, ok = QInputDialog.getText(self, "替换", "输入要查找的内容:")
        if not ok or not pattern:
            return
            
        replacement, ok = QInputDialog.getText(self, "替换", f"将 '{pattern}' 替换为:")
        if not ok:
            return
            
        content = self.text_edit.toPlainText()
        try:
            regex = re.compile(pattern)
            new_content, count = regex.subn(replacement, content)
            
            if count > 0:
                self.save_state(f"替换 '{pattern}' 为 '{replacement}'")
                self.buffers[self.current_buffer] = new_content
                self.text_edit.setPlainText(new_content)
                # 清除所有高亮
                cursor = self.text_edit.textCursor()
                cursor.select(QTextCursor.Document)
                fmt = QTextCharFormat()
                fmt.setBackground(QColor(Qt.transparent))
                cursor.mergeCharFormat(fmt)
                self.status_label.setText(f"替换了 {count} 处")
            else:
                self.status_label.setText("未找到匹配内容")
        except re.error:
            QMessageBox.critical(self, "错误", "无效的正则表达式")
    
    def new_buffer(self):
        self.save_state("新建缓冲区")
        self.buffers.append("")
        self.buffer_files.append("")
        self.current_buffer = len(self.buffers) - 1
        self.text_edit.clear()
        self.update_title()
        self.update_status()
        QMessageBox.information(self, "缓冲区", f"已创建新缓冲区 {self.current_buffer}")
    
    def switch_buffer(self):
        buf_num, ok = QInputDialog.getInt(self, "切换缓冲区", 
                                        "输入缓冲区编号:", 
                                        min=0, max=len(self.buffers)-1)
        if ok:
            self.save_state(f"切换到缓冲区 {buf_num}")
            self.current_buffer = buf_num
            self.text_edit.setPlainText(self.buffers[buf_num])
            self.update_title()
            self.update_status()
    
    def remove_buffer(self):
        if len(self.buffers) == 1:
            QMessageBox.critical(self, "错误", "必须保留至少一个缓冲区")
            return
            
        buf_num, ok = QInputDialog.getInt(self, "删除缓冲区", 
                                         "输入要删除的缓冲区编号:", 
                                         min=0, max=len(self.buffers)-1)
        if ok:
            self.save_state(f"删除缓冲区 {buf_num}")
            self.buffers.pop(buf_num)
            self.buffer_files.pop(buf_num)
            
            if self.current_buffer == buf_num:
                self.current_buffer = 0
            elif self.current_buffer > buf_num:
                self.current_buffer -= 1
                
            self.text_edit.setPlainText(self.buffers[self.current_buffer])
            self.update_title()
            self.update_status()
            QMessageBox.information(self, "删除", f"已删除缓冲区 {buf_num}")
    
    def list_buffers(self):
        info = "缓冲区列表:\n"
        for idx, (buf, fname) in enumerate(zip(self.buffers, self.buffer_files)):
            size = len(buf.encode('utf-8'))
            lines = len(buf.split('\n'))
            mark = " <-- 当前" if idx == self.current_buffer else ""
            info += f"[{idx}] {lines} 行, {size} 字节, '{fname}'{mark}\n"
        QMessageBox.information(self, "缓冲区列表", info)
    
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
        QMessageBox.information(self, "帮助", help_text)
    
    def show_about(self):
        about_text = f"""{self.__mainname__} 版本 {self.__version__}

一个简单的文本编辑器，支持多缓冲区管理。

{self.__author__}
{self.__email__}"""
        QMessageBox.information(self, "关于", about_text)
    
    def show_debug(self):
        debug_text = f"""
    {self.__version__}
    {platform.system()}
    {platform.version()}
    {platform.platform()}
    {platform.python_version()}

当前缓冲区: {self.current_buffer}
缓冲区数量: {len(self.buffers)}"""
        QMessageBox.information(self, "调试信息", debug_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建并显示主窗口
    window = NightNoteGUI()
    window.show()
    
    sys.exit(app.exec_())
