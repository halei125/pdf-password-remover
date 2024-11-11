import os
import pikepdf
import logging
import coloredlogs
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from threading import Thread
import queue

class PDFPasswordRemoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Password Remover")
        self.root.geometry("800x600")
        
        # 版本信息
        self.VERSION = "1.0"
        self.AUTHOR = "Halei125"
        
        # 初始化队列
        self.log_queue = queue.Queue()
        
        # 设置日志
        self.setup_logging()
        
        # 创建GUI元素
        self.create_widgets()
        
        # 开始处理日志队列
        self.process_log_queue()
        
    def setup_logging(self):
        class QueueHandler(logging.Handler):
            def __init__(self, queue):
                super().__init__()
                self.queue = queue

            def emit(self, record):
                msg = self.format(record)
                self.queue.put(msg)

        self.logger = logging.getLogger('PDFPasswordRemover')
        self.logger.setLevel(logging.DEBUG)
        
        queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
        queue_handler.setFormatter(formatter)
        self.logger.addHandler(queue_handler)
        
        file_handler = logging.FileHandler('pdf_password_remover.log', encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 密码输入框
        ttk.Label(main_frame, text="PDF密码:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.password_var = tk.StringVar(value="0")
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 选择类型（文件/文件夹）
        self.select_type_var = tk.StringVar(value="file")
        select_type_frame = ttk.Frame(main_frame)
        select_type_frame.grid(row=1, column=0, columnspan=3, pady=5)
        ttk.Radiobutton(select_type_frame, text="选择文件", variable=self.select_type_var, 
                       value="file", command=self.update_select_button).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(select_type_frame, text="选择文件夹", variable=self.select_type_var, 
                       value="folder", command=self.update_select_button).pack(side=tk.LEFT, padx=5)
        
        # 选择路径框架
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        self.path_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.path_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.select_button = ttk.Button(path_frame, text="选择文件", command=self.choose_path)
        self.select_button.pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        
        # 开始按钮
        self.start_button = ttk.Button(main_frame, text="开始处理", command=self.start_processing)
        self.start_button.grid(row=4, column=0, columnspan=3, pady=10)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(main_frame, height=20, width=80)
        self.log_text.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10, padx=5)
        
        # 版本信息框架
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 版本信息标签
        version_label = ttk.Label(info_frame, text=f"Version: {self.VERSION}", font=("Arial", 9))
        version_label.pack(side=tk.LEFT, padx=5)
        
        # 作者信息标签
        author_label = ttk.Label(info_frame, text=f"{self.AUTHOR}", font=("Arial", 9))
        author_label.pack(side=tk.RIGHT, padx=5)
        
        # 配置列权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)

    def update_select_button(self):
        """更新选择按钮文本"""
        text = "选择文件夹" if self.select_type_var.get() == "folder" else "选择文件"
        self.select_button.configure(text=text)
        self.path_var.set("")  # 清空已选择的路径
        
    def choose_path(self):
        """选择文件或文件夹"""
        if self.select_type_var.get() == "folder":
            path = filedialog.askdirectory()
        else:
            path = filedialog.askopenfilename(filetypes=[("PDF文件", "*.pdf")])
        
        if path:
            self.path_var.set(path)
            
    def process_log_queue(self):
        while True:
            try:
                msg = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, msg + '\n')
                self.log_text.see(tk.END)
                self.log_queue.task_done()
            except queue.Empty:
                break
        self.root.after(100, self.process_log_queue)
            
    def start_processing(self):
        if not self.path_var.get():
            self.logger.error("请选择PDF文件或文件夹！")
            return
            
        self.start_button.state(['disabled'])
        self.progress_var.set(0)
        thread = Thread(target=self.process_pdfs, daemon=True)
        thread.start()
        
    def process_pdf_file(self, filepath):
        """处理单个PDF文件"""
        file = os.path.basename(filepath)
        self.logger.info(f"正在处理: {file}")
        
        try:
            # 尝试打开PDF检查是否加密
            pdf = pikepdf.open(filepath)
            self.logger.info(f"{file} 未加密")
            pdf.close()
        except pikepdf._qpdf.PasswordError:
            # 尝试使用密码解密
            try:
                pdf = pikepdf.open(filepath, password=self.password_var.get(), allow_overwriting_input=True)
                pdf.save(filepath)
                pdf.close()
                self.logger.info(f"成功移除 {file} 的密码")
            except pikepdf._qpdf.PasswordError:
                self.logger.error(f"{file} 密码错误")
            except Exception as e:
                self.logger.error(f"{file} 处理失败: {str(e)}")
        except Exception as e:
            self.logger.error(f"{file} 处理失败: {str(e)}")
        
    def process_pdfs(self):
        try:
            path = self.path_var.get()
            pdf_files = []
            
            # 根据选择类型获取PDF文件列表
            if self.select_type_var.get() == "folder":
                # 只处理当前文件夹中的PDF文件（不包括子文件夹）
                for file in os.listdir(path):
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(path, file))
            else:
                # 处理单个PDF文件
                if path.lower().endswith('.pdf'):
                    pdf_files.append(path)
            
            total_files = len(pdf_files)
            if total_files == 0:
                self.logger.warning("未找到PDF文件！")
                return
                
            # 处理文件
            for i, filepath in enumerate(pdf_files, 1):
                self.process_pdf_file(filepath)
                progress = (i / total_files) * 100
                self.progress_var.set(progress)
                
        except Exception as e:
            self.logger.error(f"处理过程出错: {str(e)}")
        finally:
            self.root.after(0, lambda: self.start_button.state(['!disabled']))
            self.logger.info("处理完成")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFPasswordRemoverGUI(root)
    root.mainloop()