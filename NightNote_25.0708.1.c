#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINES 10000
#define MAX_BUFFERS 8
#define MAX_LINE_LEN 1024
#define MAX_FILENAME 256

const char* MAINNAME = "NightNote";
const char* VERSION = "25.0708.1";
const char* AUTHOR = "DONGFANG Lingye";
const char* EMAIL = "ly@lingye.online";

char buffers[MAX_BUFFERS][MAX_LINES][MAX_LINE_LEN];
int buffer_line_counts[MAX_BUFFERS] = {0};
char buffer_files[MAX_BUFFERS][MAX_FILENAME] = {""};
int current_buffer = 0;

void print_help() {
    printf("%s version %s by %s <%s>\n", MAINNAME, VERSION, AUTHOR, EMAIL);
    printf(
        "Command list:\n"
        "p               Print all lines\n"
        "i [n]           Insert after line n (end with '.')\n"
        "a               Append at end (end with '.')\n"
        "d [n]           Delete line n\n"
        "w [filename]    Write buffer to file\n"
        "o [filename]    Open file and load to buffer\n"
        "u l             List buffers\n"
        "u c             Clear buffer\n"
        "u s [n]         Switch buffer (0~N)\n"
        "u r [n]         Remove buffer n\n"
        "q               Quit\n"
        "h               Show this help\n"
        "b               Debug info\n"
        "v               Show about info\n"
    );
}

void show_buffer_size() {
    int lines = buffer_line_counts[current_buffer];
    int total_bytes = 0;
    for (int i = 0; i < lines; ++i) {
        total_bytes += strlen(buffers[current_buffer][i]) + 1;
    }
    printf("buffer %d %d lines %d bytes\n", current_buffer, lines, total_bytes);
}

void p() {
    show_buffer_size();
    int lines = buffer_line_counts[current_buffer];
    for (int i = 0; i < lines; ++i) {
        printf("%d: %s\n", i + 1, buffers[current_buffer][i]);
    }
}

void insert(int n) {
    show_buffer_size();
    int lines = buffer_line_counts[current_buffer];
    if (n < 0 || n > lines) {
        printf("Line number out of range\n");
        return;
    }
    if (lines >= MAX_LINES) {
        printf("Buffer is full, cannot insert more lines.\n");
        return;
    }
    char temp[MAX_LINE_LEN];
    int insert_count = 0;
    int max_insert = MAX_LINES - lines; // 剩余可插入行数
    char insert_lines[MAX_LINE_LEN][MAX_LINE_LEN]; // 每次插入不可能超过MAX_LINE_LEN行
    while (insert_count < max_insert) {
        if (!fgets(temp, sizeof(temp), stdin)) break;
        temp[strcspn(temp, "\n")] = 0;
        if (strcmp(temp, ".") == 0) break;
        strncpy(insert_lines[insert_count++], temp, MAX_LINE_LEN - 1);
        insert_lines[insert_count-1][MAX_LINE_LEN-1] = '\0';
    }
    if (insert_count == 0) return;
    // 移动原有行
    for (int i = lines - 1; i >= n; --i) {
        strncpy(buffers[current_buffer][i + insert_count], buffers[current_buffer][i], MAX_LINE_LEN - 1);
        buffers[current_buffer][i + insert_count][MAX_LINE_LEN-1] = '\0';
    }
    // 插入新行
    for (int i = 0; i < insert_count; ++i) {
        strncpy(buffers[current_buffer][n + i], insert_lines[i], MAX_LINE_LEN - 1);
        buffers[current_buffer][n + i][MAX_LINE_LEN-1] = '\0';
    }
    buffer_line_counts[current_buffer] += insert_count;
    show_buffer_size();
}

void append() {
    show_buffer_size();
    int lines = buffer_line_counts[current_buffer];
    char temp[MAX_LINE_LEN];
    while (1) {
        if (!fgets(temp, sizeof(temp), stdin)) break;
        temp[strcspn(temp, "\n")] = 0;
        if (strcmp(temp, ".") == 0) break;
        strncpy(buffers[current_buffer][lines++], temp, MAX_LINE_LEN);
    }
    buffer_line_counts[current_buffer] = lines;
    show_buffer_size();
}

void delete(int n) {
    int lines = buffer_line_counts[current_buffer];
    if (n < 1 || n > lines) {
        printf("E:Line number out of range\n");
        return;
    }
    for (int i = n - 1; i < lines - 1; ++i) {
        strncpy(buffers[current_buffer][i], buffers[current_buffer][i + 1], MAX_LINE_LEN);
    }
    buffer_line_counts[current_buffer]--;
    printf("Deleted line %d\n", n);
    show_buffer_size();
}

void write(const char* filename) {
    FILE* f = fopen(filename, "w");
    if (!f) {
        printf("E:Failed to save: %s\n", filename);
        show_buffer_size();
        return;
    }
    int lines = buffer_line_counts[current_buffer];
    for (int i = 0; i < lines; ++i) {
        fprintf(f, "%s\n", buffers[current_buffer][i]);
    }
    fclose(f);
    strncpy(buffer_files[current_buffer], filename, MAX_FILENAME);
    printf("OK %s\n", filename);
    show_buffer_size();
}

void select_file(const char* filename) {
    FILE* f = fopen(filename, "r");
    if (!f) {
        printf("E:File not found\n");
        buffer_line_counts[current_buffer] = 0;
        buffer_files[current_buffer][0] = '\0';
        show_buffer_size();
        return;
    }
    int count = 0;
    char temp[MAX_LINE_LEN];
    while (fgets(temp, sizeof(temp), f) && count < MAX_LINES) {
        temp[strcspn(temp, "\n")] = 0;
        strncpy(buffers[current_buffer][count++], temp, MAX_LINE_LEN);
    }
    fclose(f);
    buffer_line_counts[current_buffer] = count;
    strncpy(buffer_files[current_buffer], filename, MAX_FILENAME);
    printf("%s OK\n", filename);
    show_buffer_size();
}

void clear_buffer() {
    buffer_line_counts[current_buffer] = 0;
    printf("OK\n");
    show_buffer_size();
}

void debug() {
    printf("DEBUG INFO\n");
    printf("%s\n", VERSION);
    printf("OS: Linux (C version, no platform details)\n");
    show_buffer_size();
}

void about() {
    printf("%s version %s by %s <%s>\n", MAINNAME, VERSION, AUTHOR, EMAIL);
    printf("A simple line editor, similar to Linux's ed editor.\n");
    printf("Type 'h' for help.\n");
    printf("Type 'q' to quit.\n");
}

void switch_buffer(int n) {
    if (n < 0 || n >= MAX_BUFFERS) {
        printf("E:Buffer number must be >= 0 and < %d\n", MAX_BUFFERS);
        return;
    }
    current_buffer = n;
    show_buffer_size();
}

void list_buffers() {
    printf("Buffers info:\n");
    for (int i = 0; i < MAX_BUFFERS; ++i) {
        int lines = buffer_line_counts[i];
        int total_bytes = 0;
        for (int j = 0; j < lines; ++j) {
            total_bytes += strlen(buffers[i][j]) + 1;
        }
        printf("[%d] %d lines, %d bytes, '%s'%s\n", i, lines, total_bytes, buffer_files[i], (i == current_buffer) ? "    <--" : "");
    }
}

void remove_buffer(int n) {
    if (n < 0 || n >= MAX_BUFFERS) {
        printf("E:Buffer number out of range\n");
        return;
    }
    if (MAX_BUFFERS == 1) {
        printf("E:At least one buffer must remain\n");
        return;
    }
    // 这里只是清空，不真正移除
    buffer_line_counts[n] = 0;
    buffer_files[n][0] = '\0';
    if (current_buffer == n) {
        current_buffer = 0;
        printf("OK:switch to buffer 0\n");
    }
    printf("Buffer %d removed.\n", n);
}

int main() {
    printf("%s %s\n", MAINNAME, VERSION);
    char cmd[256];
    while (1) {
        printf("]");
        if (!fgets(cmd, sizeof(cmd), stdin)) break;
        cmd[strcspn(cmd, "\n")] = 0;
        if (strcmp(cmd, "p") == 0) {
            p();
        } else if (strncmp(cmd, "i ", 2) == 0) {
            int n = atoi(cmd + 2);
            insert(n);
        } else if (strcmp(cmd, "a") == 0) {
            append();
        } else if (strncmp(cmd, "d ", 2) == 0) {
            int n = atoi(cmd + 2);
            delete(n);
        } else if (strncmp(cmd, "w ", 2) == 0) {
            write(cmd + 2);
        } else if (strncmp(cmd, "o ", 2) == 0) {
            select_file(cmd + 2);
        } else if (strcmp(cmd, "c") == 0) {
            clear_buffer();
        } else if (strncmp(cmd, "s ", 2) == 0) {
            int n = atoi(cmd + 2);
            switch_buffer(n);
        } else if (strncmp(cmd, "r ", 2) == 0) {
            int n = atoi(cmd + 2);
            remove_buffer(n);
        } else if (strncmp(cmd, "u ", 2) == 0) {
            if (strcmp(cmd + 2, "c") == 0) {
                clear_buffer();
            } else if (strcmp(cmd + 2, "l") == 0) {
                list_buffers();
            } else if (strncmp(cmd + 2, "s ", 2) == 0) {
                int n = atoi(cmd + 4);
                switch_buffer(n);
            } else if (strncmp(cmd + 2, "r ", 2) == 0) {
                int n = atoi(cmd + 4);
                remove_buffer(n);
            } else {
                printf("u c  Clear buffer | u s [n]  Switch buffer | u r [n]  Remove buffer n\n");
            }
        } else if (strcmp(cmd, "l") == 0) {
            list_buffers();
        } else if (strcmp(cmd, "q") == 0) {
            printf("Bye!\n");
            break;
        } else if (strcmp(cmd, "h") == 0) {
            print_help();
        } else if (strcmp(cmd, "b") == 0) {
            debug();
        } else if (strcmp(cmd, "v") == 0) {
            about();
        } else {
            printf("E:Unknown command, enter h for help.\n");
            show_buffer_size();
        }
    }
    return 0;
}