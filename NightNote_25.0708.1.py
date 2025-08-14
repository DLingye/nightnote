
import platform
__mainname__ = "NightNote"
__version__ = "25.0708.1"
__author__ = "DONGFANG Lingye"
__email__ = "ly@lingye.online"

# 历史记录相关
history = []
redo_history = []
operation_history = []
MAX_HISTORY = 10
def print_help():
    print(f"{__mainname__} version {__version__} by {__author__} <{__email__}>")
    print('''
        Command list:
        p               Print all lines
        i [n]           Insert after line n (end with '.')
        a               Append at end (end with '.')
        d [n]           Delete line n
        w [filename]    Write buffer to file
        o [filename]    Open file and load to buffer
        s [pattern]     Search for pattern (regex supported)
        r [pattern] [replacement] Replace pattern (regex supported)
        u l             List buffers
        u c             Clear buffer
        u s [n]         Switch buffer (0~N)
        u r [n]         Remove buffer n
        u z             Undo last operation
        u y             Redo last undo
        u h             List operation history
        q               Quit
        h               Show this help
        b               Debug info (OS version, Python version, etc.)
        v               Show about info
        ''')
lines = []  # 用于存储文本的每一行
buffers = [[]]  # 多个缓冲区，初始一个
buffer_files = [""]  # 记录每个缓冲区对应的文件名（如有）
current_buffer = 0  # 当前缓冲区编号

def get_lines():
    return buffers[current_buffer]

def set_lines(new_lines):
    buffers[current_buffer] = new_lines

def save_state(operation):
    """保存当前状态到历史记录"""
    if len(history) >= MAX_HISTORY:
        history.pop(0)
    history.append((current_buffer, buffers[current_buffer][:], buffer_files[current_buffer]))
    operation_history.append((operation, current_buffer))
    redo_history.clear()

def set_buffer_file(filename):
    while len(buffer_files) <= current_buffer:
        buffer_files.append("")
    buffer_files[current_buffer] = filename

def get_buffer_file(idx):
    if idx < len(buffer_files):
        return buffer_files[idx]
    return ""
    
def show_buffer_size():
    lines = get_lines()
    total_bytes = sum(len(line.encode('utf-8')) + 1 for line in lines)
    print(f"buffer {current_buffer} {len(lines)} lines {total_bytes} bytes")

def select_file(filename):
    if not filename:
        print("E:Please specify a filename")
        return
        
    try:
        with open(filename, "r") as f:
            set_lines([line.rstrip('\n') for line in f])
        set_buffer_file(filename)
        print(f"File '{filename}' loaded successfully")
    except FileNotFoundError:
        print(f"E:File '{filename}' not found")
        set_lines([])
        set_buffer_file("")
    except PermissionError:
        print(f"E:Permission denied when accessing '{filename}'")
        set_lines([])
        set_buffer_file("")
    except Exception as e:
        print(f"E:Failed to open file '{filename}': {str(e)}")
        set_lines([])
        set_buffer_file("")
    show_buffer_size()

def p():
    show_buffer_size()
    lines = get_lines()
    for idx, line in enumerate(lines, 1):
        print(f"{idx}: {line}")

def insert(n):
    show_buffer_size()
    lines = get_lines()
    if n < 0 or n > len(lines):
        print(f"E:Line number must be between 0 and {len(lines)}")
        return
        
    print(f"Inserting after line {n}. Enter lines (end with '.'):")
    insert_lines = []
    while True:
        try:
            text = input()
            if text == ".":
                break
            insert_lines.append(text)
        except EOFError:
            print("\nE:Input interrupted, insertion cancelled")
            return
            
    if insert_lines:
        save_state(f"insert after line {n}")
        lines[n:n] = insert_lines
        set_lines(lines)
        print(f"Inserted {len(insert_lines)} lines after line {n}")
    show_buffer_size()

def append():
    show_buffer_size()
    lines = get_lines()
    print("Appending to end. Enter lines (end with '.'):")
    append_lines = []
    while True:
        try:
            text = input()
            if text == ".":
                break
            append_lines.append(text)
        except EOFError:
            print("\nE:Input interrupted, append cancelled")
            return
            
    if append_lines:
        save_state("append")
        lines.extend(append_lines)
        set_lines(lines)
        print(f"Appended {len(append_lines)} lines")
    show_buffer_size()

def delete(n):
    lines = get_lines()
    if n < 1 or n > len(lines):
        print(f"E:Line number must be between 1 and {len(lines)}")
        return
        
    save_state(f"delete line {n}")
    deleted_line = lines.pop(n-1)
    set_lines(lines)
    print(f"Deleted line {n}: {deleted_line[:50]}{'...' if len(deleted_line) > 50 else ''}")
    show_buffer_size()

def write(filename):
    if not filename:
        print("E:Please specify a filename")
        return
        
    lines = get_lines()
    if not lines:
        print("E:Buffer is empty, nothing to save")
        return
        
    try:
        with open(filename, "w") as f:
            for line in lines:
                f.write(line + "\n")
        save_state(f"write to file {filename}")
        set_buffer_file(filename)
        print(f"Successfully saved {len(lines)} lines to '{filename}'")
    except PermissionError:
        print(f"E:Permission denied when writing to '{filename}'")
    except Exception as e:
        print(f"E:Failed to save to '{filename}': {str(e)}")
    show_buffer_size()

def clear_buffer():
    save_state("clear buffer")
    set_lines([])
    print("OK")
    show_buffer_size()

def debug():
    #操作系统版本
    print("DEBUG INFO")
    print(__version__)
    print("OS:", platform.system())
    print("OS Version:", platform.version())
    print("Platform:", platform.platform())
    #py版本
    print("Python Version:", platform.python_version())
    show_buffer_size()

def about():
    print(f"{__mainname__} version {__version__} by {__author__} <{__email__}>")
    print("A simple line editor, similar to Linux's ed editor.")
    print("Type 'h' for help.")
    print("Type 'q' to quit.")

def switch_buffer(n):
    global current_buffer
    if n < 0:
        print("E:Buffer number must be >= 0")
        return
    while n >= len(buffers):
        buffers.append([])
    while n >= len(buffer_files):
        buffer_files.append("")
    current_buffer = n
    show_buffer_size()

def list_buffers():
    print("Buffers info:")
    for idx, buf in enumerate(buffers):
        fname = get_buffer_file(idx)
        total_bytes = sum(len(line.encode('utf-8')) + 1 for line in buf)
        mark = "    <--" if idx == current_buffer else ""
        print(f"[{idx}] {len(buf)} lines, {total_bytes} bytes, '{fname}' {mark}")

def remove_buffer(n):
    global current_buffer
    if n < 0 or n >= len(buffers):
        print("E:Buffer number out of range")
        return
    if len(buffers) == 1:
        print("E:At least one buffer must remain")
        return
    buffers.pop(n)
    buffer_files.pop(n)
    if current_buffer == n:
        current_buffer = 0
        print("OK:switch to buffer 0")
    elif current_buffer > n:
        current_buffer -= 1
    print(f"Buffer {n} removed.")

def search(pattern):
    import re
    try:
        regex = re.compile(pattern)
    except re.error:
        print("E:Invalid regular expression")
        return
    
    lines = get_lines()
    matches = []
    for idx, line in enumerate(lines, 1):
        if regex.search(line):
            matches.append((idx, line))
    
    if not matches:
        print("No matches found")
    else:
        print(f"Found {len(matches)} matches:")
        for idx, line in matches:
            print(f"{idx}: {line}")

def replace(pattern, replacement):
    import re
    try:
        regex = re.compile(pattern)
    except re.error:
        print("E:Invalid regular expression")
        return
    
    lines = get_lines()
    changed = 0
    for i in range(len(lines)):
        new_line, count = regex.subn(replacement, lines[i])
        if count > 0:
            lines[i] = new_line
            changed += count
    
    if changed > 0:
        save_state(f"replace '{pattern}' with '{replacement}'")
        set_lines(lines)
        print(f"Replaced {changed} occurrences")
    else:
        print("No matches found")

def undo_last():
    """撤销上一次操作"""
    if not history:
        print("E:No more undo history available")
        return
        
    global current_buffer
    buf_idx, buf_content, buf_file = history.pop()
    redo_history.append((current_buffer, buffers[current_buffer][:], buffer_files[current_buffer]))
    current_buffer = buf_idx
    buffers[buf_idx] = buf_content
    buffer_files[buf_idx] = buf_file
    print(f"Undo successful, restored buffer {buf_idx} with {len(buf_content)} lines")
    show_buffer_size()

def redo():
    """重做上一次撤销的操作"""
    if not redo_history:
        print("E:No more redo history available")
        return
        
    global current_buffer
    buf_idx, buf_content, buf_file = redo_history.pop()
    history.append((current_buffer, buffers[current_buffer][:], buffer_files[current_buffer]))
    current_buffer = buf_idx
    buffers[buf_idx] = buf_content
    buffer_files[buf_idx] = buf_file
    print(f"Redo successful, restored buffer {buf_idx} with {len(buf_content)} lines")
    show_buffer_size()

def list_history():
    """列出操作历史"""
    if not operation_history:
        print("No operation history")
        return
        
    print("Operation history (newest first):")
    for idx, (op, buf_idx) in enumerate(reversed(operation_history[-10:]), 1):
        print(f"{idx}. {op} (buffer {buf_idx})")

def main():
    print(f"{__mainname__} {__version__}")
    while True:
        cmd = input("]").strip()
        if cmd == "p":
            p()
        elif cmd.startswith("s ") and len(cmd) > 2:
            search(cmd[2:])
        elif cmd.startswith("r ") and len(cmd.split()) >= 3:
            parts = cmd[2:].split(maxsplit=1)
            if len(parts) == 2:
                replace(parts[0], parts[1])
            else:
                print("r pattern replacement  Replace pattern with replacement")
        elif cmd.startswith("i "):
            try:
                n = int(cmd.split()[1])
                insert(n)
            except:
                print("i n  Insert after line n (end with '.')")
                
        elif cmd == "a":
            append()
        elif cmd.startswith("d "):
            try:
                n = int(cmd.split()[1])
                delete(n)
            except:
                print("d n  Delete line n")
                
        elif cmd.startswith("w "):
            filename = cmd[2:].strip()
            write(filename)
            
        elif cmd.startswith("o "):
            filename = cmd[2:].strip()
            if filename:
                select_file(filename)
            else:
                print("o filename   Open file and load to buffer")
                
        elif cmd == "c":
            clear_buffer()
        
        elif cmd.startswith("s "):
            try:
                n = int(cmd.split()[1])
                switch_buffer(n)
            except:
                print("s n  Switch buffer (0~N)")
        elif cmd.startswith("r "):
            try:
                n = int(cmd.split()[1])
                remove_buffer(n)
            except:
                print("r n  Remove buffer n")
                
        elif cmd.startswith("u "):
            args = cmd.split()
            if len(args) == 2 and args[1] == "c":
                clear_buffer()
            elif len(args) == 2 and args[1] == "l":
                list_buffers()
            elif len(args) == 2 and args[1] == "z":
                undo_last()
            elif len(args) == 2 and args[1] == "y":
                redo()
            elif len(args) == 2 and args[1] == "h":
                list_history()
            elif len(args) == 3 and args[1] == "s":
                try:
                    n = int(args[2])
                    switch_buffer(n)
                except:
                    print("u s [n]  Switch buffer (0~N)")
            elif len(args) == 3 and args[1] == "r":
                try:
                    n = int(args[2])
                    remove_buffer(n)
                except:
                    print("u r n  Remove buffer n")
            else:
                print("u c  Clear buffer | u s [n]  Switch buffer | u r [n]  Remove buffer n | u z Undo | u y Redo | u h History")
                
        elif cmd == "l":
            list_buffers()
        elif cmd == "q":
            print("Bye!")
            break
        elif cmd == "h":
            print_help()
        elif cmd == "b":
            debug()
        elif cmd == "v":
            about()
        elif cmd == "c":
            clear_buffer()
        else:
            print("E:Unknown command, enter h for help.")
            show_buffer_size()

if __name__ == "__main__":
    main()