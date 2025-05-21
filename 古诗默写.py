import os
import random
import re
import tkinter as tk
from tkinter import messagebox

class MemorizationApp:
    def __init__(self, master, file_path):
        self.master = master
        self.file_path = os.path.abspath(file_path)  # 转为绝对路径便于调试
        self.new_file_path = os.path.join(os.path.dirname(self.file_path), "sentences_new.txt")
        self.true_path = os.path.join(os.path.dirname(self.file_path), "true.txt")
        self.false_path = os.path.join(os.path.dirname(self.file_path), "false.txt")
        self.original_sentences = []
        self.current_index = -1
        self.mask_mode = 'back'  # 默认遮挡后半句

        self.initialize_files()
        self.load_and_process_data()

        # 新增变量：统计总句数和剩余句数
        self.total_count = len(self.original_sentences)
        self.remaining_count = self.total_count

        self.setup_ui()
        self.update_count_label()
        self.next_sentence()

    def initialize_files(self):
        """初始化 true.txt、false.txt，并复制 sentences.txt 为 sentences_new.txt"""
        for path in [self.true_path, self.false_path]:
            if not os.path.exists(path):
                open(path, 'w').close()

        # 如果 sentences_new.txt 不存在，则从 sentences.txt 复制一份
        if not os.path.exists(self.new_file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8-sig') as src:
                    content = src.read()
                with open(self.new_file_path, 'w', encoding='utf-8') as dst:
                    dst.write(content)
            except Exception as e:
                messagebox.showerror("文件错误", f"无法创建 sentences_new.txt：{str(e)}")
                self.master.destroy()

    def load_and_process_data(self):
        """加载题库文件并过滤无效内容"""
        exclude_pattern = re.compile(r"[《》0-9()·]")

        if not os.path.isfile(self.file_path):
            messagebox.showerror("错误", f"题库文件不存在：{self.file_path}")
            self.master.destroy()
            return

        try:
            with open(self.file_path, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if line and not exclude_pattern.search(line):
                        self.original_sentences.append(line)

            if not self.original_sentences:
                messagebox.showwarning("警告", "题库文件内容为空或格式不正确")
                self.master.destroy()

        except Exception as e:
            messagebox.showerror("错误", f"读取题库失败：{str(e)}\n请确认文件是否被占用或编码是否正确。")
            self.master.destroy()

    def setup_ui(self):
        """设置 GUI 界面"""
        self.master.title("默写刷题工具")

        main_frame = tk.Frame(self.master)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # 显示剩余句子数量的标签
        self.count_label = tk.Label(
            main_frame,
            text="",
            font=('宋体', 14),
            fg='blue'
        )
        self.count_label.pack(pady=5)

        self.label = tk.Label(
            main_frame,
            text="",
            font=('宋体', 16),
            wraplength=600,
            bg='#F0F0F0',
            padx=20,
            pady=20
        )
        self.label.pack(expand=True, fill=tk.BOTH)

        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=20)

        btn_config = {
            'font': ('宋体', 12),
            'width': 10,
            'height': 1,
            'relief': tk.GROOVE
        }

        self.show_btn = tk.Button(btn_frame, text="查看答案", command=self.show_original, bg='#E0E0E0', **btn_config)
        self.unknown_btn = tk.Button(btn_frame, text="不会", command=self.unknow, bg='#FF9999', **btn_config)
        self.know_btn = tk.Button(btn_frame, text="会", command=self.know, bg='#90EE90', **btn_config)

        self.mask_var = tk.BooleanVar(value=False)
        self.mask_check = tk.Checkbutton(
            btn_frame,
            text="遮挡前半句",
            variable=self.mask_var,
            font=('宋体', 12),
            bg='#E0E0E0',
            command=self.update_mask_mode
        )

        self.show_btn.pack(side=tk.LEFT, padx=10)
        self.unknown_btn.pack(side=tk.LEFT, padx=10)
        self.know_btn.pack(side=tk.LEFT, padx=10)
        self.mask_check.pack(side=tk.LEFT, padx=10)

    def update_mask_mode(self):
        """根据 Checkbutton 状态更新遮挡模式"""
        self.mask_mode = 'front' if self.mask_var.get() else 'back'

    def next_sentence(self):
        """显示下一个句子（根据遮挡模式生成遮挡内容）"""
        if not self.original_sentences:
            self.label.config(text="没有更多句子了！")
            self.show_btn.config(state=tk.DISABLED)
            self.unknown_btn.config(state=tk.DISABLED)
            self.know_btn.config(state=tk.DISABLED)
            return

        self.current_index = random.randint(0, len(self.original_sentences) - 1)
        sentence = self.original_sentences[self.current_index]
        processed = self.process_sentence(sentence)
        self.label.config(text=processed)

    def process_sentence(self, sentence):
        """根据遮挡模式动态生成遮挡内容"""
        punctuations = "，。？；！、"
        punctuation_pos = -1

        for i, c in enumerate(sentence):
            if c in punctuations:
                punctuation_pos = i
                break

        if punctuation_pos == -1:
            return '_' * len(sentence)

        if self.mask_mode == 'front':
            before = sentence[:punctuation_pos]
            after = sentence[punctuation_pos:]
            return '_' * len(before) + after
        else:
            before = sentence[:punctuation_pos + 1]
            after = sentence[punctuation_pos + 1:]
            return before + '_' * len(after)

    def show_original(self):
        """显示原句"""
        if self.current_index == -1:
            return
        self.label.config(text=self.original_sentences[self.current_index])

    def know(self):
        """标记为“会”，写入 true.txt 并移除当前句子，同时从 sentences_new.txt 删除"""
        if self.current_index == -1:
            return
        sentence = self.original_sentences[self.current_index]
        self._append_to_file(self.true_path, sentence)
        self._remove_from_new_file(sentence)
        self._remove_current_sentence()

    def unknow(self):
        """标记为“不会”，写入 false.txt 并移除当前句子，同时从 sentences_new.txt 删除"""
        if self.current_index == -1:
            return
        sentence = self.original_sentences[self.current_index]
        self._append_to_file(self.false_path, sentence)
        self._remove_from_new_file(sentence)
        self._remove_current_sentence()

    def _append_to_file(self, path, content):
        """将内容追加写入指定文件"""
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content + '\n')

    def _remove_current_sentence(self):
        """移除当前句子，并更新剩余数量"""
        del self.original_sentences[self.current_index]
        self.current_index = -1
        self.remaining_count -= 1
        self.update_count_label()
        self.next_sentence()

    def _remove_from_new_file(self, sentence):
        """从 sentences_new.txt 中删除当前句子"""
        try:
            with open(self.new_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(self.new_file_path, 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.strip() != sentence.strip():
                        f.write(line)
        except Exception as e:
            messagebox.showerror("文件错误", f"无法从 sentences_new.txt 中删除句子：{str(e)}")

    def update_count_label(self):
        """更新剩余句子数量的显示"""
        self.count_label.config(text=f"剩余句子：{self.remaining_count} / {self.total_count}")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.geometry("800x600")
        root.resizable(False, False)

        file_path = "sentences.txt"

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"找不到题库文件：{file_path}")

        app = MemorizationApp(root, file_path)
        root.mainloop()

    except Exception as e:
        import tkinter.messagebox as mbox
        mbox.showerror("启动错误", f"程序启动失败：\n{str(e)}\n\n请检查以下内容：\n1. 文件 'sentences.txt' 是否存在\n2. 是否缺少必要依赖\n3. Python 环境是否正确")