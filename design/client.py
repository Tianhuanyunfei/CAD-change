import tkinter as tk
import os
import json
from tkinter import filedialog, messagebox, ttk


class CADApp:
    def __init__(self, root):
        self.root = root
        self.root.title("阻尼器设计软件")
        self.root.geometry("300x500+20+20")  # 窗口大小和位置
        self.setup_ui() # 初始化UI

    def setup_ui(self):
        """设置主界面UI"""
        # 创建ttk样式
        style = ttk.Style()
        # 使用支持良好立体效果的主题
        style.theme_use('clam')
        style.configure('Rounded.TButton', 
                        borderwidth=3,
                        relief="raised",  # 凸起立体效果
                        padding=8,
                        background="#4a7ba6",  # 更亮的蓝色主题
                        foreground="white",
                        font=('Microsoft YaHei', 11, 'bold'),
                        borderradius=8,
                        lightcolor="#7ba3c5",  # 相应调整的高光颜色
                        darkcolor="#375a7f")  # 相应调整的阴影颜色
        style.map('Rounded.TButton',
                  background=[('active', '#375a7f')],
                  foreground=[('active', 'white')],
                  relief=[('active', 'sunken')],  # 按下时凹陷
                  lightcolor=[('active', '#4a7ba6')],
                  darkcolor=[('active', '#2c435c')])
        
        # 创建主框架
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 主功能区域（BRB和粘滞产品设计）
        main_functions_frame = tk.LabelFrame(main_frame, text="主功能", font=('SimHei', 12, 'bold'), highlightthickness=0, bd=0)
        main_functions_frame.pack(fill=tk.X, pady=20, ipady=20)

        # BRB产品设计按钮
        brb_btn = ttk.Button(main_functions_frame, text="BRB产品设计",
                            command=self.open_brb_design,
                            style='Rounded.TButton')
        brb_btn.pack(fill=tk.X, padx=10, pady=20)

        # 粘滞产品设计按钮
        vfd_btn = ttk.Button(main_functions_frame, text="粘滞产品设计",
                                command=self.product_design2,
                                style='Rounded.TButton')
        vfd_btn.pack(fill=tk.X, padx=10, pady=5)

        # 分隔线
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill=tk.X, pady=10)

        # 辅助功能区域（DXF/CSV转换和CSV编辑）
        auxiliary_functions_frame = tk.LabelFrame(main_frame, text="辅助功能", font=('SimHei', 12, 'bold'), highlightthickness=0, bd=0)
        auxiliary_functions_frame.pack(fill=tk.X, pady=10, expand=True)

        # DXF转CSV按钮
        dxf_to_csv_btn = ttk.Button(auxiliary_functions_frame, text="DXF 转 CSV",
                                   command=self.convert_dxf_to_csv,
                                   style='Rounded.TButton')
        dxf_to_csv_btn.pack(fill=tk.X, padx=10, pady=3)

        # CSV转DXF按钮
        csv_to_dxf_btn = ttk.Button(auxiliary_functions_frame, text="CSV 转 DXF",
                                   command=self.convert_csv_to_dxf,
                                   style='Rounded.TButton')
        csv_to_dxf_btn.pack(fill=tk.X, padx=10, pady=3)

        # 显示并编辑CSV文件按钮
        edit_csv_btn = ttk.Button(auxiliary_functions_frame, text="编辑 CSV 文件",
                                 command=self.show_and_edit_csv,
                                 style='Rounded.TButton')
        edit_csv_btn.pack(fill=tk.X, padx=10, pady=3)

    def convert_dxf_to_csv(self):
        """将DXF文件转换为CSV文件"""
        import dxf_to_csv
        input_file = filedialog.askopenfilename(filetypes=[("DXF 文件", "*.dxf")])
        if input_file:
            output_file = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV 文件", "*.csv")]
            )
            if output_file:
                try:
                    dxf_to_csv.dxf_to_csv(input_file, output_file)
                    messagebox.showinfo("成功", "DXF转CSV成功！")
                except Exception as e:
                    messagebox.showerror("错误", f"转换失败: {str(e)}")

    def convert_csv_to_dxf(self):
        """将CSV文件转换为DXF文件"""
        import csv_to_dxf
        input_file = filedialog.askopenfilename(filetypes=[("CSV 文件", "*.csv")])
        if input_file:
            output_file = filedialog.asksaveasfilename(
                defaultextension=".dxf",
                filetypes=[("DXF 文件", "*.dxf")]
            )
            if output_file:
                try:
                    csv_to_dxf.csv_to_dxf(input_file, output_file)
                    messagebox.showinfo("成功", "CSV转DXF成功！")
                except Exception as e:
                    messagebox.showerror("错误", f"转换失败: {str(e)}")

    def show_and_edit_csv(self):
        """显示并编辑CSV文件"""
        from edit_csv import show_and_edit_csv
        show_and_edit_csv(self.root)

    def open_brb_design(self):
        """打开BRB产品设计窗口"""
        from brb_drawing import brb_drawing
        design_window = tk.Toplevel(self.root)
        design_window.title("BRB产品设计")
        design_window.geometry("1000x800+450+50")
        design_window.resizable(True, True)

        # 设置窗口图标和样式
        if hasattr(self.root, 'iconbitmap'):
            try:
                # 使用BRB专用图标
                design_window.iconbitmap("BRB.ico")
            except:
                # 如果BRB.ico不存在，使用根窗口图标作为备选
                try:
                    design_window.iconbitmap(self.root.iconbitmap())
                except:
                    pass

        # 创建设计表单
        DesignForm(design_window)

    def product_design2(self):
        """打开粘滞产品设计窗口"""
        from vfd_drawing import vfd_drawing
        vfd_window = tk.Toplevel(self.root)
        vfd_window.title("粘滞产品设计")
        vfd_window.geometry("600x700")
        vfd_window.resizable(True, True)

        # 设置窗口图标和样式
        if hasattr(self.root, 'iconbitmap'):
            try:
                vfd_window.iconbitmap(self.root.iconbitmap())
            except:
                pass

        # 创建设计表单
        VfdDesignForm(vfd_window)


class DesignForm:
    """BRB产品设计表单类"""

    def __init__(self, parent):
        self.parent = parent

        # 创建主菜单
        self.create_menu()

        # 创建主框架
        main_frame = tk.Frame(parent, padx=1, pady=1, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建滚动区域 - 主内容区域不使用垂直滚动条
        canvas = tk.Canvas(main_frame)
        self.content_frame = tk.Frame(canvas, bg="cornsilk") # 内容框架

        # 修复内容框架宽度和高度扩展问题
        def on_canvas_configure(event):
            # 设置内容框架宽度和高度与canvas一致
            canvas.itemconfig(canvas_window, width=event.width, height=event.height)
        canvas.bind("<Configure>", on_canvas_configure)

        self.content_frame.bind( 
            "<Configure>", 
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        ) # 绑定配置事件，更新滚动区域

        canvas_window = canvas.create_window((0, 0), window=self.content_frame, anchor="nw", width=canvas.winfo_width()) # 创建窗口并设置初始宽度
        
        # 绑定鼠标滚轮事件
        def on_main_canvas_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", on_main_canvas_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)

        # 创建设计表单
        self.create_form()
        
    def _handle_mousewheel(self, event, canvas):
        """
        处理鼠标滚轮事件，只有当内容高度超过canvas可见高度时才执行滚动
        
        参数:
            event: 鼠标滚轮事件对象
            canvas: 要滚动的canvas对象
        """
        # 获取内容的总高度和canvas的可见高度
        content_height = canvas.bbox("all")[3] - canvas.bbox("all")[1]
        visible_height = canvas.winfo_height()
        
        # 只有当内容高度超过可见高度时才执行滚动
        if content_height > visible_height:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def create_form(self):
        """
        创建设计表单UI界面
        
        功能说明：
        - 构建BRB产品设计参数输入表单的完整界面
        - 创建包含标题、全局共享参数和多个参数表的界面布局
        - 支持根据不同设计力添加多个参数表，每个表都有独立的长度-数量表格
        - 初始化必要的界面组件和数据结构
        
        界面组成：
        1. 表单标题：显示"BRB产品设计参数"
        2. 全局共享参数：包含项目名称和模板选择
        3. 多个参数表区域：支持添加多个参数表，每个表对应不同的设计力和独立的长度-数量表格
        4. 操作按钮：添加参数表和生成图纸按钮
        """
        # 表单标题 - 显示应用程序名称
        title_label = tk.Label(self.content_frame, text="BRB产品设计",
                               font=("SimHei", 20, "bold"), bg="cornsilk")
        title_label.pack(pady=5)

        # 项目名称区域
        global_frame = tk.LabelFrame(self.content_frame, text="", font=('SimHei', 12), bg="cornsilk", highlightthickness=0, bd=0)
        global_frame.pack(fill=tk.X, pady=10)
        
        # 项目文件夹选择
        folder_frame = tk.Frame(global_frame, bg="cornsilk")
        folder_frame.pack(fill=tk.X, pady=3)
        tk.Label(folder_frame, text="项目文件夹:", width=10, anchor=tk.W, font=('SimHei', 15, "bold"), bg="cornsilk").pack(side=tk.LEFT, padx=5)
        self.project_folder_var = tk.StringVar()
        # 添加标志，跟踪用户是否手动选择了项目文件夹
        self.project_folder_manually_selected = False
        # 设置默认值为桌面路径
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.project_folder_var.set(desktop_path)
        folder_entry = tk.Entry(folder_frame, textvariable=self.project_folder_var, font=('SimHei', 15), bd=2, width=50)
        folder_entry.pack(side=tk.LEFT, padx=5)
        
        def select_folder():
            """选择项目文件夹"""
            folder_path = filedialog.askdirectory(title="选择项目文件夹")
            if folder_path:
                self.project_folder_var.set(folder_path)
                self.project_folder_manually_selected = True
        
        select_folder_btn = tk.Button(folder_frame, text="浏览", command=select_folder, font=('SimHei', 12), bg="#4CAF50", fg="white", bd=0, highlightthickness=0, relief="flat", borderwidth=0)
        select_folder_btn.pack(side=tk.LEFT, padx=5)
        
        # 项目名称输入
        project_frame = tk.Frame(global_frame, bg="cornsilk")
        project_frame.pack(fill=tk.X, pady=3)
        tk.Label(project_frame, text="项目名称:", width=10, anchor=tk.W, font=('SimHei', 15, "bold"), bg="cornsilk").pack(side=tk.LEFT, padx=5)
        self.project_name_var = tk.StringVar()
        self.project_name_entry = tk.Entry(project_frame, textvariable=self.project_name_var, font=('SimHei', 15), bd=2, width=60)
        self.project_name_entry.pack(side=tk.LEFT, padx=5)
        
        def update_project_folder(*args):
            """当项目名称变化时更新项目文件夹路径"""
            # 如果用户手动选择了项目文件夹，则不自动更新路径
            if self.project_folder_manually_selected:
                return
            
            project_name = self.project_name_var.get()
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            if project_name:
                # 创建以项目名称命名的文件夹路径
                project_folder_path = os.path.join(desktop_path, project_name)
                self.project_folder_var.set(project_folder_path)
            else:
                # 如果项目名称为空，恢复默认值为桌面路径
                self.project_folder_var.set(desktop_path)
        
        # 绑定项目名称变化事件
        self.project_name_var.trace("w", update_project_folder)
        
        # 添加填充，将BRB总数量推到右边
        tk.Frame(project_frame, bg="cornsilk").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # BRB总数量显示
        self.total_quantity_var = tk.StringVar(value="0件")
        tk.Label(project_frame, text="BRB总数量:", font=('SimHei', 12), bg="cornsilk").pack(side=tk.LEFT, padx=10)
        tk.Label(project_frame, textvariable=self.total_quantity_var, font=('SimHei', 12), bg="cornsilk").pack(side=tk.LEFT, padx=(5, 10))

        # 固定参数列表
        self.param_labels = ["截面宽度(mm)", "截面高度(mm)", "板材厚度(mm)", "焊缝高度(mm)", "方管宽度(mm)", "方管厚度(mm)", "芯板材料"]
        
        # 参数表横向滚动容器
        scrollable_frame = tk.Frame(self.content_frame, bg="cornsilk")  # 移除固定高度，让高度随窗口变化
        scrollable_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 添加水平滚动条
        h_scrollbar = tk.Scrollbar(scrollable_frame, orient=tk.HORIZONTAL, width=30)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 添加垂直滚动条（从main_frame移动过来）
        v_scrollbar = tk.Scrollbar(scrollable_frame, orient=tk.VERTICAL, width=30)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建画布来容纳参数表
        canvas = tk.Canvas(scrollable_frame, xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        h_scrollbar.config(command=canvas.xview)
        v_scrollbar.config(command=canvas.yview)
        
        # 绑定鼠标滚轮事件
        def on_mousewheel(event):
            self._handle_mousewheel(event, canvas)
        
        canvas.bind("<MouseWheel>", on_mousewheel)
        
        # 参数表容器 - 用于容纳多个参数表（横向排列）
        self.param_tables_container = tk.Frame(canvas, bg="bisque")
        canvas.create_window((0, 0), window=self.param_tables_container, anchor="nw")
        
        # 绑定配置事件以更新滚动区域
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            
        self.param_tables_container.bind("<Configure>", on_configure)
        
        # 将鼠标滚轮事件绑定到参数表容器，实现鼠标放在参数表上时也能触发滚动
        self.param_tables_container.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        # 初始化参数表列表，用于存储所有参数表的信息
        self.param_tables = []
        
        # 生成按钮区域
        btn_frame = tk.Frame(self.content_frame, bg="cornsilk")
        btn_frame.pack(fill=tk.X, pady=5)

        # 添加参数表按钮
        add_table_btn = tk.Button(btn_frame, text="添加参数表", command=self.add_param_table,
                                 font=("SimHei", 12 ,), bg="#4CAF50", fg="black",
                                 height=1, width=15, bd=0, highlightthickness=0, relief="flat", borderwidth=0)
        add_table_btn.pack(side=tk.LEFT, padx=10)

        # 移除全局的长度-数量表格，每个参数表现在有自己独立的长度-数量表格



        # 创建生成图纸按钮，点击时调用generate_drawing方法开始生成图纸
        generate_btn = tk.Button(btn_frame, text="生成图纸",
                                 command=self.generate_drawing,
                                 font=("SimHei", 12,),
                                 bg="#4CAF50", fg="black",
                                 height=2, width=18, bd=0, highlightthickness=0, relief="flat", borderwidth=0)
        generate_btn.pack(side=tk.RIGHT, padx=10)
        
        # 创建生成材料单按钮
        materials_btn = tk.Button(btn_frame, text="生成材料单",
                                 command=self.generate_materials,
                                 font=("SimHei", 12,),
                                 bg="#FF9800", fg="black",
                                 height=2, width=18, bd=0, highlightthickness=0, relief="flat", borderwidth=0)
        materials_btn.pack(side=tk.RIGHT, padx=10)
        
        # 创建提示信息标签区域
        self.message_frame = tk.Frame(self.content_frame, bg="cornsilk")
        self.message_frame.pack(fill=tk.X, pady=5)
        
        # 生成图纸提示
        self.drawing_message_label = tk.Label(self.message_frame, text="",
                                              font=("SimHei", 10),
                                              fg="green", bg="cornsilk")
        self.drawing_message_label.pack(side=tk.RIGHT, padx=10)
        
        # 生成材料单提示
        self.materials_message_label = tk.Label(self.message_frame, text="",
                                                font=("SimHei", 10),
                                                fg="green", bg="cornsilk")
        self.materials_message_label.pack(side=tk.RIGHT, padx=10)
        
        # 添加一个默认的参数表
        self.add_param_table()

    # 移除全局的add_row和remove_row方法，改为使用每个参数表的专用方法

    def add_param_table(self):
        """
        添加一个新的参数表，包含设计力输入、参数和独立的长度-数量表格
        """
        table_number = len(self.param_tables) + 1
        
        # 获取主画布引用
        # 从参数表容器的父级开始向上查找，直到找到主画布
        canvas = self.param_tables_container.master  # canvas是self.param_tables_container的父容器
        
        # 创建参数表框架（横向排列）
        table_frame = tk.LabelFrame(self.param_tables_container, 
                                   text=f"BRB {table_number}参数", 
                                   font=('SimHei', 15),
                                   width=200, height=400, bg="white", highlightthickness=0, bd=1.5, cursor="hand2")  # 调整宽度和高度，设置鼠标指针
        table_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y, expand=False)
        
        # 添加拖拽功能相关的变量和事件绑定
        table_frame.dragging = False
        table_frame.offset_x = 0
        
        # 绑定鼠标事件
        table_frame.bind("<Button-1>", self._on_table_press)
        table_frame.bind("<B1-Motion>", self._on_table_drag)
        table_frame.bind("<ButtonRelease-1>", self._on_table_release)
        
        # 为参数表的所有子组件绑定鼠标事件，确保拖拽在整个参数表区域都能工作
        def bind_all_children(widget):
            widget.bind("<Button-1>", self._on_table_press, add="+")
            widget.bind("<B1-Motion>", self._on_table_drag, add="+")
            widget.bind("<ButtonRelease-1>", self._on_table_release, add="+")
            for child in widget.winfo_children():
                bind_all_children(child)
        
        bind_all_children(table_frame)
        # 为参数表框架绑定鼠标滚轮事件
        table_frame.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        # 截面选择区域
        template_frame = tk.Frame(table_frame, bg="white")
        template_frame.pack(fill=tk.X, pady=5)
        # 为截面选择区域框架绑定鼠标滚轮事件
        template_frame.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        label = tk.Label(template_frame, text="选择截面:", width=15, anchor=tk.W, font=('SimHei', 12 ,), bg="white")
        label.pack(side=tk.LEFT, padx=5)
        # 为标签绑定鼠标滚轮事件
        label.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        # 初始化截面选择变量和下拉框组件
        template_var = tk.StringVar()
        template_combo = ttk.Combobox(template_frame, textvariable=template_var,
                                      width=8, font=('SimHei', 12),)
        # 设置截面选项并默认选择第一个
        template_combo['values'] = ('王一', '十一', '王工')
        template_combo.current(0)
        template_combo.pack(side=tk.LEFT, padx=5)
        # 为下拉框绑定鼠标滚轮事件
        template_combo.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        # 设计力输入行
        force_frame = tk.Frame(table_frame, bg="white")
        force_frame.pack(fill=tk.X, pady=5)
        # 为设计力输入行框架绑定鼠标滚轮事件
        force_frame.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        label = tk.Label(force_frame, text="屈服承载力(KN):", width=15, anchor=tk.W, font=('SimHei', 12), bg="white")
        label.pack(side=tk.LEFT, padx=5)
        # 为标签绑定鼠标滚轮事件
        label.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        force_entry = tk.Entry(force_frame, font=('SimHei', 12), width=10, bd=1.5)
        force_entry.pack(side=tk.LEFT, padx=5)
        # 为输入框绑定鼠标滚轮事件
        force_entry.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        # 创建参数区域
        params_frame = tk.Frame(table_frame, bg="white")
        params_frame.pack(fill=tk.X, pady=3)
        # 为参数区域框架绑定鼠标滚轮事件
        params_frame.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        # 初始化参数输入框字典
        param_entries = {}
        param_frames = {}
        
        # 为每个参数创建标签和输入框
        for label_text in self.param_labels:
            # 创建每一行的框架
            frame = tk.Frame(params_frame, bg="white")
            frame.pack(fill=tk.X, pady=2)
            # 为行框架绑定鼠标滚轮事件
            frame.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
            
            # 创建参数标签
            label = tk.Label(frame, text=f"{label_text}:", width=13, anchor=tk.W, font=('SimHei', 11), bg="white")                  
            label.pack(side=tk.LEFT, padx=5, pady=1)
            # 为标签绑定鼠标滚轮事件
            label.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
            
            # 创建参数输入框
            entry = tk.Entry(frame, font=('SimHei', 11), width=12, bd=1.5)
            # 为芯板材料输入框设置默认值Q235
            if label_text == "芯板材料":
                entry.insert(0, "Q235")
            entry.pack(side=tk.LEFT, padx=5)
            # 为输入框绑定鼠标滚轮事件
            entry.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
            
            # 存储输入框和框架
            param_entries[label_text] = entry
            param_frames[label_text] = frame
        
        # 添加独立的长度-数量表格区域
        table_label_frame = tk.LabelFrame(table_frame, text="长度-数量设置", font=('SimHei', 12), highlightthickness=0, bd=1.5,bg="white")
        table_label_frame.pack(fill=tk.X, pady=3)
        # 为长度-数量表格区域框架绑定鼠标滚轮事件
        table_label_frame.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        # 表格标题
        header_frame = tk.Frame(table_label_frame, bg="white")
        header_frame.pack(fill=tk.X, pady=5)
        # 为表格标题框架绑定鼠标滚轮事件
        header_frame.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        label = tk.Label(header_frame, text="长度(mm)", width=12, font=('SimHei', 12), bg="white")
        label.pack(side=tk.LEFT, padx=5)
        # 为标签绑定鼠标滚轮事件
        label.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        label = tk.Label(header_frame, text="数量", width=8, font=('SimHei', 12), bg="white")
        label.pack(side=tk.LEFT, padx=5)
        # 为标签绑定鼠标滚轮事件
        label.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        # 表格内容框架
        table_content_frame = tk.Frame(table_label_frame, bg="white")
        table_content_frame.pack(fill=tk.BOTH, expand=True)
        # 为表格内容框架绑定鼠标滚轮事件
        table_content_frame.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        # 初始化此参数表的长度-数量行列表
        length_quantity_rows = []
        
        # 添加行按钮到header_frame
        add_btn = tk.Button(header_frame, text="添加行", 
                           command=lambda tcf=table_content_frame, lqr=length_quantity_rows, c=canvas: 
                           self._add_length_quantity_row(tcf, lqr, c),
                           font= ("SimHei", 10), bg="white", fg="green",
                           bd=0, highlightthickness=0, relief="flat", borderwidth=0)
        add_btn.pack(side=tk.LEFT, padx=5)
        # 为添加行按钮绑定鼠标滚轮事件
        add_btn.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        # 添加默认的第一行
        self._add_length_quantity_row(table_content_frame, length_quantity_rows, canvas)
        

        
        # 添加删除按钮
        delete_frame = tk.Frame(table_frame, bg="white")
        delete_frame.pack(fill=tk.X, pady=3)
        delete_btn = tk.Button(delete_frame, text="删除此参数表", 
                             command=lambda tf=table_frame, tn=table_number: self.remove_param_table(tf, tn),
                             font= ("SimHei", 10 , ), bg="coral", fg="black",
                             bd=0, highlightthickness=0, relief="flat", borderwidth=0)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # 存储参数表信息
        table_info = {
            "frame": table_frame,
            "force_entry": force_entry,
            "template_var": template_var,
            "template_combo": template_combo,
            "param_entries": param_entries,
            "param_frames": param_frames,
            "table_number": table_number,
            "table_content_frame": table_content_frame,
            "length_quantity_rows": length_quantity_rows,
            "length_quantity_frame": table_content_frame,  # 存储长度-数量表格的父框架
            "canvas": canvas  # 存储主画布引用
        }
        
        self.param_tables.append(table_info)
        
        # 设置焦点到新添加的设计力输入框
        force_entry.focus_set()
        
        # 更新总数量统计
        self.calculate_total_quantity()
    
    def _add_length_quantity_row(self, parent_frame, rows_list, canvas):
        """
        为指定参数表添加长度-数量行
        
        参数：
        - parent_frame: 父框架，用于放置行元素
        - rows_list: 当前参数表的行列表，用于存储行信息
        - canvas: 主画布引用，用于绑定鼠标滚轮事件
        """
        row_frame = tk.Frame(parent_frame, bg="white")
        row_frame.pack(fill=tk.X, pady=2)
        # 为行框架绑定鼠标滚轮事件
        row_frame.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        length_entry = tk.Entry(row_frame, width=12, font=('SimHei', 12), bd=1.5)
        length_entry.pack(side=tk.LEFT, padx=5)
        # 为长度输入框绑定鼠标滚轮事件
        length_entry.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        quantity_entry = tk.Entry(row_frame, width=8, font=('SimHei', 12), bd=1.5)
        quantity_entry.pack(side=tk.LEFT, padx=5)
        # 为数量输入框绑定鼠标滚轮事件
        quantity_entry.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        # 为数量输入框添加事件监听，当内容变化时更新总数量
        quantity_entry.bind("<KeyRelease>", lambda event: self.calculate_total_quantity())
        
        delete_btn = tk.Button(row_frame, text="删除", 
                              command=lambda rf=row_frame, rl=rows_list, pf=parent_frame, c=canvas: 
                              self._remove_length_quantity_row(rf, rl, pf, c),
                              width=4, font= ("SimHei", 10 , "bold"), bg="white", fg="coral",
                              bd=0, highlightthickness=0, relief="flat", borderwidth=0)
        delete_btn.pack(side=tk.LEFT, padx=5)
        # 为删除按钮绑定鼠标滚轮事件
        delete_btn.bind("<MouseWheel>", lambda event, c=canvas: self._handle_mousewheel(event, c))
        
        rows_list.append((row_frame, length_entry, quantity_entry))
        
        # 设置焦点到新添加的长度输入框
        length_entry.focus_set()
        
        # 更新总数量统计
        self.calculate_total_quantity()
    
    def calculate_total_quantity(self):
        """
        计算所有参数表中长度-数量行的总数量
        """
        total_quantity = 0
        for table in self.param_tables:
            for row in table['length_quantity_rows']:
                _, _, quantity_entry = row
                quantity_value = quantity_entry.get().strip()
                if quantity_value and quantity_value.isdigit():
                    total_quantity += int(quantity_value)
        
        # 更新总数量显示
        self.total_quantity_var.set(str(total_quantity) + "件")
    
    def _remove_length_quantity_row(self, row_frame, rows_list, parent_frame, canvas):
        """
        删除指定参数表的长度-数量行
        
        参数：
        - row_frame: 要删除的行框架
        - rows_list: 当前参数表的行列表
        - parent_frame: 父框架，用于在需要时添加新行
        - canvas: 主画布引用，用于绑定鼠标滚轮事件
        """
        for i, (frame, _, _) in enumerate(rows_list):
            if frame == row_frame:
                del rows_list[i]
                frame.destroy()
                break
        
        # 如果没有行了，添加一个空行
        if not rows_list:
            self._add_length_quantity_row(parent_frame, rows_list, canvas)
        else:
            # 更新总数量统计
            self.calculate_total_quantity()
    
    def _on_table_press(self, event):
        """
        处理参数表的鼠标按下事件，记录拖拽开始的位置
        """
        # 查找参数表框架
        table_frame = event.widget
        while not hasattr(table_frame, "dragging") and table_frame.master:
            table_frame = table_frame.master
            
        if hasattr(table_frame, "dragging"):
            table_frame.dragging = True
            # 记录鼠标相对于参数表左侧的偏移量
            table_frame.offset_x = event.x_root - table_frame.winfo_rootx()
            # 提高拖拽时的z-index，使被拖拽的表显示在最前面
            table_frame.lift()
    
    def _on_table_drag(self, event):
        """
        处理参数表的鼠标拖拽事件，移动参数表框架
        """
        # 查找参数表框架
        table_frame = event.widget
        while not hasattr(table_frame, "dragging") and table_frame.master:
            table_frame = table_frame.master
            
        if hasattr(table_frame, "dragging") and table_frame.dragging:
            # 获取父容器相对于屏幕的位置
            parent_x = table_frame.master.winfo_rootx()
            
            # 计算鼠标相对于父容器的x位置
            new_x = event.x_root - parent_x - table_frame.offset_x
            
            # 确保x位置不小于0
            new_x = max(0, new_x)
            
            # 先移除pack布局，改用place布局进行拖拽
            if table_frame.winfo_ismapped():
                table_frame.pack_forget()
                
            # 设置参数表的新位置
            table_frame.place(x=new_x, y=0, anchor="nw")
    
    def _on_table_release(self, event):
        """
        处理参数表的鼠标释放事件，确定新的位置并更新参数表顺序
        """
        # 查找参数表框架
        table_frame = event.widget
        while not hasattr(table_frame, "dragging") and table_frame.master:
            table_frame = table_frame.master
            
        if hasattr(table_frame, "dragging") and table_frame.dragging:
            table_frame.dragging = False
            
            # 获取容器中所有参数表框架的位置和引用
            tables = []
            for i, table_info in enumerate(self.param_tables):
                tf = table_info["frame"]
                tables.append((tf.winfo_rootx(), tf))
            
            # 找到当前拖拽的表
            current_table = None
            for i, (x, tf) in enumerate(tables):
                if tf == table_frame:
                    current_table = (x, tf)
                    tables.pop(i)
                    break
            
            if current_table:
                # 获取当前拖拽表的最终x位置
                current_x = table_frame.winfo_rootx()
                
                # 确定新的插入位置
                insert_index = len(tables)
                for i, (x, tf) in enumerate(tables):
                    if current_x < x:
                        insert_index = i
                        break
                
                # 将拖拽的表插入到新位置
                tables.insert(insert_index, (current_x, table_frame))
                
                # 更新参数表在容器中的顺序
                for i, (x, tf) in enumerate(tables):
                    tf.pack_forget()  # 先移除
                    tf.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y, expand=False)  # 重新添加到新位置
                
                # 更新self.param_tables列表中的顺序
                new_param_tables = []
                for x, tf in tables:
                    for table_info in self.param_tables:
                        if table_info["frame"] == tf:
                            new_param_tables.append(table_info)
                            break
                
                self.param_tables = new_param_tables
                
                # 更新所有参数表的标题编号
                for i, table_info in enumerate(self.param_tables):
                    new_number = i + 1
                    table_info["table_number"] = new_number
                    table_info["frame"].config(text=f"BRB {new_number}参数")
    
    def remove_param_table(self, table_frame, table_number):
        """
        删除指定的参数表
        
        参数：
        - table_frame: 要删除的参数表框架
        - table_number: 参数表编号
        """
        # 确保至少保留一个参数表
        if len(self.param_tables) <= 1:
            messagebox.showwarning("警告", "至少需要保留一个参数表")
            return
            
        # 获取Canvas引用和当前滚动位置
        canvas = self.param_tables_container.master  # 获取Canvas引用
        current_xview = canvas.xview()  # 获取当前滚动位置比例
        canvas_width = canvas.bbox("all")[2]  # 获取当前画布总宽度
        # 计算当前绝对滚动位置（像素值）
        absolute_scroll_x = current_xview[0] * canvas_width
        
        # 从列表中移除参数表信息
        for i, table_info in enumerate(self.param_tables):
            if table_info["frame"] == table_frame:
                del self.param_tables[i]
                break
        
        # 销毁参数表框架
        table_frame.destroy()
        
        # 更新剩余参数表的标题
        for i, table_info in enumerate(self.param_tables):
            new_number = i + 1
            table_info["table_number"] = new_number
            table_info["frame"].config(text=f"BRB {new_number}参数")
        
        # 延迟恢复滚动位置，确保容器大小已经更新
        def restore_scroll_position():
            new_canvas_width = canvas.bbox("all")[2]  # 获取新的画布总宽度
            # 如果新宽度为0或小于等于可见宽度，不需要滚动
            if new_canvas_width <= canvas.winfo_width():
                return
            # 计算新的相对滚动比例
            new_xview = absolute_scroll_x / new_canvas_width
            # 确保比例在0-1之间
            new_xview = max(0, min(1, new_xview))
            # 恢复滚动位置
            canvas.xview_moveto(new_xview)
        
        # 更新总数量统计
        self.calculate_total_quantity()
        
        self.parent.after(100, restore_scroll_position)
    
    # 移除update_all_param_tables方法，因为不再需要动态更新参数类型
    
    def create_menu(self):
        """
        创建主菜单
        """
        # 创建菜单条
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        
        # 创建文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        # 增大"文件"两个字的字体大小
        menubar.add_cascade(label="文件", menu=file_menu)
        
        
        # 添加文件菜单的选项
        file_menu.add_command(label="新建", command=self.new_design,font=("楷体", 12))
        file_menu.add_command(label="打开", command=self.open_design,font=("楷体", 12))
        file_menu.add_command(label="保存", command=self.save_design,font=("楷体", 12))
    
    def new_design(self):
        """
        新建设计，清空所有表单数据
        """
        # 清空项目名称
        self.project_name_var.set("")
        
        # 移除所有参数表，只保留一个空的参数表
        while len(self.param_tables) > 1:
            # 获取第一个参数表的框架和编号
            table_info = self.param_tables[0]
            table_frame = table_info["frame"]
            table_number = table_info["table_number"]
            self.remove_param_table(table_frame, table_number)  # 移除第一个参数表
        
        # 清空剩余参数表的数据
        if self.param_tables:
            table_info = self.param_tables[0]
            # 清空设计力
            table_info["force_entry"].delete(0, tk.END)
            # 重置模板选择
            table_info["template_var"].set("王一")
            # 清空参数
            for label, entry in table_info["param_entries"].items():
                entry.delete(0, tk.END)
                # 为芯板材料输入框重新设置默认值Q235
                if label == "芯板材料":
                    entry.insert(0, "Q235")
            # 移除所有长度-数量行，只保留一行
            while len(table_info["length_quantity_rows"]) > 1:
                row_frame, _, _ = table_info["length_quantity_rows"][-1]
                row_frame.destroy()
                table_info["length_quantity_rows"].pop()
            # 清空剩余行的数据
            if table_info["length_quantity_rows"]:
                _, length_entry, quantity_entry = table_info["length_quantity_rows"][0]
                length_entry.delete(0, tk.END)
                quantity_entry.delete(0, tk.END)
        
        # 更新总数量统计
        self.calculate_total_quantity()
    
    def open_design(self):
        """
        打开设计，从文件中加载表单数据
        """
        # 选择文件
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")],
            title="打开设计"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    design_data = json.load(f)
                
                # 清空现有数据
                self.new_design()
                
                # 填充项目名称
                self.project_name_var.set(design_data.get("project_name", ""))
                
                # 处理参数表数据
                param_tables_data = design_data.get("param_tables", [])
                
                # 如果有多个参数表，添加新的参数表
                while len(self.param_tables) < len(param_tables_data):
                    self.add_param_table()
                
                # 填充每个参数表的数据
                for i, table_data in enumerate(param_tables_data):
                    if i < len(self.param_tables):
                        table_info = self.param_tables[i]
                        
                        # 填充设计力
                        table_info["force_entry"].insert(0, table_data.get("design_force", ""))
                        
                        # 填充模板选择
                        table_info["template_var"].set(table_data.get("template", "王一"))
                        
                        # 填充参数
                        for label, value in table_data.get("parameters", {}).items():
                            if label in table_info["param_entries"]:
                                entry = table_info["param_entries"][label]
                                entry.delete(0, tk.END)  # 在插入新值之前先清空输入框
                                entry.insert(0, value)
                        
                        # 填充长度-数量数据
                        length_quantity_data = table_data.get("length_quantity", [])
                        
                        # 获取当前参数表的相关组件
                        parent_frame = table_info["length_quantity_frame"]
                        rows_list = table_info["length_quantity_rows"]
                        canvas = table_info["canvas"]
                        
                        # 添加足够的行
                        while len(rows_list) < len(length_quantity_data):
                            self._add_length_quantity_row(parent_frame, rows_list, canvas)
                        
                        # 填充数据
                        for j, (length, quantity) in enumerate(length_quantity_data):
                            if j < len(rows_list):
                                _, length_entry, quantity_entry = rows_list[j]
                                length_entry.insert(0, str(length))
                                quantity_entry.insert(0, str(quantity))
                        
                        # 更新总数量统计
                        self.calculate_total_quantity()
                
                
                
            except Exception as e:
                messagebox.showerror("错误", f"加载设计文件失败: {str(e)}")
    
    def save_design(self):
        """
        保存设计，将表单数据保存到文件
        """
        # 获取表单数据
        data = self.get_form_data()
        
        # 验证数据
        if not data["project_name"]:
            messagebox.showerror("错误", "请输入项目名称")
            return
        
        if not data["param_tables"]:
            messagebox.showerror("错误", "请至少添加一个参数表")
            return
        
        # 获取项目文件夹路径
        project_folder = self.project_folder_var.get()
        
        # 直接保存到项目文件夹，不弹出选择对话框
        default_filename = f"{data['project_name']}_design.json"
        file_path = os.path.join(project_folder, default_filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            messagebox.showinfo("成功", f"设计文件保存成功！\n保存路径：{file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存设计文件失败: {str(e)}")
    
    def get_form_data(self):
        """
        获取表单数据
        
        返回值：
        - 包含全局参数和多个参数表数据的字典，每个参数表包含自己的长度-数量数据
        """
        data = {
            "project_name": self.project_name_var.get(),  # 全局项目名称
            "param_tables": []                          # 多个参数表数据，每个表包含自己的长度-数量数据
        }

        # 收集每个参数表的数据
        for table_info in self.param_tables:
            # 获取设计力
            force_value = table_info["force_entry"].get().strip()
            
            # 获取模板选择
            template_value = table_info["template_var"].get()
            
            # 收集参数表中的参数
            table_params = {label: entry.get() for label, entry in table_info["param_entries"].items()}
            
            # 收集此参数表的长度-数量数据
            length_quantity_data = []
            for _, length_entry, quantity_entry in table_info["length_quantity_rows"]:
                length = length_entry.get().strip()
                quantity = quantity_entry.get().strip()
                
                if length and quantity:
                    try:
                        length_quantity_data.append((int(length), int(quantity)))
                    except ValueError:
                        pass
            
            # 创建参数表数据对象，包含独立的长度-数量数据和模板选择
            table_data = {
                "table_number": table_info["table_number"],
                "design_force": force_value,
                "template": template_value,
                "parameters": table_params,
                "length_quantity": length_quantity_data
            }
            
            data["param_tables"].append(table_data)

        return data

    def generate_drawing(self):
        """生成图纸"""
        data = self.get_form_data()

        # 验证必要字段
        if not data["project_name"]:
            messagebox.showerror("错误", "请输入项目名称")
            return 
        
        # 验证是否有参数表
        if not data["param_tables"]:
            messagebox.showerror("错误", "请至少添加一个参数表")
            return
        
        # 准备数据表格，每个参数表对应一个数据项
        data_table = []
        
        # 处理每个参数表
        for table in data["param_tables"]:
            # 验证参数表是否填写了设计力
            if not table["design_force"]:
                messagebox.showerror("错误", f"请为参数表 {table['table_number']} 输入设计力")
                return
            
            # 验证参数表是否有长度-数量数据
            if not table["length_quantity"]:
                messagebox.showerror("错误", f"请为参数表 {table['table_number']} 添加至少一组长度-数量数据")
                return
            
            # 验证参数表中的必填参数
            for param_label in ["截面宽度(mm)", "截面高度(mm)", "板材厚度(mm)", "焊缝高度(mm)", "方管宽度(mm)", "方管厚度(mm)"]:
                if not table["parameters"].get(param_label, "").strip():
                    messagebox.showerror("错误", f"请为参数表 {table['table_number']} 填写 {param_label}")
                    return
            
            # 为每个参数表准备数据项
            table_item = {
                "template": table["template"],
                "project_name": data["project_name"],
                "width": table["parameters"]["截面宽度(mm)"],  # 截面宽度
                "height": table["parameters"]["截面高度(mm)"],  # 截面高度
                "thickness": table["parameters"]["板材厚度(mm)"],  # 板厚
                "force": table["design_force"],  # 设计力
                "tube_width": table["parameters"]["方管宽度(mm)"],  # 方管宽度
                "tube_thickness": table["parameters"]["方管厚度(mm)"],  # 方管厚度
                "weld": table["parameters"]["焊缝高度(mm)"],  # 焊缝
                "core_material": table["parameters"].get("芯板材料", "Q235"),  # 芯板材料，默认值Q235
                "length_quantity": table["length_quantity"]  # 此参数表的长度-数量数据
            }
            
            data_table.append(table_item)
        
        print(data_table)
        
        # 获取项目文件夹路径
        project_folder = self.project_folder_var.get()
        # 调用brb_drawing函数生成图纸
        from brb_drawing import brb_drawing
        brb_drawing(data_table, project_folder)
        # 更新图纸生成提示标签
        self.drawing_message_label.config(text="图纸生成成功")
        # 添加定时器，3秒后清空提示
        self.parent.after(3000, lambda: self.drawing_message_label.config(text=""))
        
    def generate_materials(self):
        """
        生成材料单
        """
        try:
            data = self.get_form_data()

            # 验证必要字段
            if not data["project_name"]:
                messagebox.showerror("错误", "请输入项目名称")
                return 
            
            # 验证是否有参数表
            if not data["param_tables"]:
                messagebox.showerror("错误", "请至少添加一个参数表")
                return
            
            # 转换参数表格式以适应brb_materials.py的要求
            param_tables = []
            for table in data["param_tables"]:
                # 转换长度-数量数据格式
                length_quantity = [
                    {"length": lq[0], "quantity": lq[1]} 
                    for lq in table["length_quantity"]
                ]
                
                param_table = {
                    "table_number": table["table_number"],
                    "design_force": table["design_force"],
                    "template_type": table["template"],
                    "params": table["parameters"],
                    "core_material": table["parameters"].get("芯板材料", "Q235"),  # 将芯板材料单独提取到顶层
                    "length_quantity": length_quantity
                }
                param_tables.append(param_table)
                print(param_table)
            
            # 调用brb_materials函数生成材料单
            from brb_materials import generate_materials_excel
            # 使用设定的项目文件夹作为保存路径
            project_folder = self.project_folder_var.get()
            excel_path = generate_materials_excel(data["project_name"], param_tables, project_folder=project_folder)
            
            if excel_path:
                # 更新材料单提示标签
                self.materials_message_label.config(text=f"材料单生成成功：{os.path.basename(excel_path)}")
                # 添加定时器，3秒后清空提示
                self.parent.after(3000, lambda: self.materials_message_label.config(text=""))
            else:
                # 更新材料单提示标签
                self.materials_message_label.config(text="材料单生成失败", fg="red")
                # 添加定时器，3秒后清空提示
                self.parent.after(3000, lambda: self.materials_message_label.config(text="", fg="green"))
        except Exception as e:
            messagebox.showerror("错误", f"材料单生成过程中发生错误：{str(e)}")

class VfdDesignForm:
    """粘滞产品设计表单类"""
    pass

def main():
    """主函数"""
    root = tk.Tk()
    try:
        root.iconbitmap("app.ico")  # 如果有图标文件
    except:
        pass
    app = CADApp(root)
    root.mainloop()

# 测试
if __name__ == "__main__":
    # 新增：设置工作目录为当前文件所在目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()