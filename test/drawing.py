import csv
import tkinter as tk
from tkinter import messagebox
import logging
from csv_to_dxf import csv_to_dxf


def generate_drawing(template_var, param_entry, width_entry, height_entry, thickness_entry,
                     force_entry, tube_width_entry, weld_entry, table):
    # 获取各参数值
    selected_template = template_var.get()  # 模版类型
    input_param = param_entry.get()  # 项目名称
    width = width_entry.get()  # 截面宽度
    height = height_entry.get()  # 截面高度
    thick = thickness_entry.get()  # 板厚
    force = force_entry.get()  # 力
    tube_width = tube_width_entry.get()  # 方管宽度
    weld = weld_entry.get()  # 焊缝

    # 判断是否为数值，并改为整数类型
    try:
        width = int(width)
        height = int(height)
        thick = int(thick)
        force = int(force)
        tube_width = int(tube_width)
        weld = int(weld)
    except ValueError:
        messagebox.showwarning("输入的值不是有效的数字，请检查。")

    if selected_template == '王工':
        csv_file = 'data\王工.csv'
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                # 将 csv_reader 转换为列表
                csv_data = list(csv_reader)

            # 输入参数并更新数据
            csv_data = update_csv_data_1(csv_data, input_param, width, height, thick, force, tube_width, weld, table)

            # 将修改后的数据写回到 CSV 文件
            with open(csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(csv_data)

            # 调用 csv_to_dxf 函数进行转换，输出 DXF 文件名称为产品型号输入的参数
            output_dxf_file = f'{input_param} BRB-{force}-L.dxf'
            csv_to_dxf(csv_file, output_dxf_file)

        except FileNotFoundError:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("错误", "文件不存在，请检查。")
            return
    elif selected_template == '十一':
        csv_file = 'data\十一.csv'
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                # 将 csv_reader 转换为列表
                csv_data = list(csv_reader)

            # 输入参数并更新数据
            csv_data = update_csv_data_2(csv_data, input_param, width, height, thick, force, tube_width, weld, table)

            # 将修改后的数据写回到 CSV 文件
            with open(csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(csv_data)

            # 调用 csv_to_dxf 函数进行转换，输出 DXF 文件名称为产品型号输入的参数
            output_dxf_file = f'{input_param} BRB-{force}-L.dxf'
            csv_to_dxf(csv_file, output_dxf_file)

        except FileNotFoundError:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("错误", "文件不存在，请检查。")
            return
    elif selected_template == '王一':
        csv_file = 'data\王一.csv'
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                # 将 csv_reader 转换为列表
                csv_data = list(csv_reader)

            # 输入参数并更新数据
            csv_data = update_csv_data_3(csv_data, input_param, width, height, thick, force, tube_width, weld, table)

            # 将修改后的数据写回到 CSV 文件
            with open(csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(csv_data)

            # 调用 csv_to_dxf 函数进行转换，输出 DXF 文件名称为产品型号输入的参数
            output_dxf_file = f'{input_param} BRB-{force}-L.dxf'
            csv_to_dxf(csv_file, output_dxf_file)

        except FileNotFoundError:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("错误", "文件不存在，请检查。")
            return

def format_number(num):
    formatted = "{:.3f}".format(num).rstrip('0').rstrip('.') if isinstance(num, (int, float)) else str(num)
    return formatted


def update_csv_data_1(csv_data, input_param, width, height, thick, force, tube_width, weld, table):
    try:
        # 获取列名
        header = csv_data[0]
        # 定义列名列表
        column_names = [
            '实体类型', '图层', '颜色', '线型', '线宽', '线型描述', '线型图案',
            '类型/名称', '块名', '值', '覆盖值', '位置 X', '位置 Y', '起点 X', '起点 Y', '终点 X', '终点 Y',
            '圆心 X', '圆心 Y', '半径', '顶点数据', '闭合', '高度', '角度', '尺寸编码',
            '起始角度', '终止角度', '缩放比例'
        ]
        # 生成列名和索引的映射字典
        column_index_map = {col_name: header.index(col_name) for col_name in column_names}

        # 直接更新指定行和列的数据

        # 主视图，长度数量说明
        result_str = ''
        product_quantity = 0
        count = 0
        total_count = len(table)
        for index, (length, quantity) in enumerate(table):
            result_str += f'L={length}-{quantity}件, '
            product_quantity += quantity
            count += 1
            if count % 4 == 0 and index < total_count - 1:
                result_str += '\P'
        result_str = result_str.rstrip(' ， ')
        csv_data[81][column_index_map['值']] = f'\W0.7;\T1.1;{result_str}\P共计{product_quantity}件'

        # 端面
        csv_data[149][column_index_map['覆盖值']] = format_number(thick)
        csv_data[150][column_index_map['覆盖值']] = format_number(width)
        csv_data[151][column_index_map['覆盖值']] = format_number(thick)
        csv_data[152][column_index_map['覆盖值']] = format_number(height-thick-thick)
        csv_data[153][column_index_map['覆盖值']] = format_number(thick)
        csv_data[154][column_index_map['覆盖值']] = format_number(thick)
        csv_data[155][column_index_map['覆盖值']] = format_number(tube_width)
        csv_data[156][column_index_map['覆盖值']] = format_number(tube_width)
        # 端面,焊缝
        csv_data[110][column_index_map['值']] = f'\T1.1;{format_number(weld)}'

        # 耗能面
        csv_data[185][column_index_map['覆盖值']] = format_number(thick)
        csv_data[186][column_index_map['覆盖值']] = format_number(thick)
        csv_data[187][column_index_map['覆盖值']] = format_number(thick)
        csv_data[188][column_index_map['覆盖值']] = format_number(height)
        csv_data[189][column_index_map['覆盖值']] = format_number(width)

        # 连接板，尺寸
        csv_data[201][column_index_map['覆盖值']] = format_number((width-thick)/2)
        # 连接板，数量
        csv_data[199][column_index_map['值']] = f'\W0.7;\T1.1;连接板 H={format_number(thick)}-{format_number(product_quantity * 4)}件'


        # 挡板，尺寸
        csv_data[216][column_index_map['覆盖值']] = format_number(width+5)
        csv_data[217][column_index_map['覆盖值']] = format_number(thick + 5)
        csv_data[218][column_index_map['覆盖值']] = format_number(thick + 5)
        csv_data[219][column_index_map['覆盖值']] = format_number(thick + 5)
        csv_data[222][column_index_map['覆盖值']] = format_number(thick + 5)
        csv_data[223][column_index_map['覆盖值']] = format_number(height-thick-thick-5)
        csv_data[206][column_index_map['覆盖值']] = format_number(tube_width + 20)
        csv_data[209][column_index_map['覆盖值']] = format_number(tube_width + 20)
        # 挡板，焊缝
        csv_data[246][column_index_map['值']] = f'\T1.1;C{format_number(weld)}'
        # 挡板，数量
        csv_data[207][column_index_map['值']] = f'\W0.7;\T1.1;挡板H=6-{format_number(product_quantity * 2)}件'

        # 标题栏，项目名称
        csv_data[292][column_index_map['值']] = f'\W0.5;\T1.1;{input_param}'
        # 标题栏，产品型号
        csv_data[294][column_index_map['值']] = f'\W0.7;\T1.1;YSX-BRB-{force}-L'

    except (IndexError, ValueError):
        print("修改 CSV 数据时出现错误，请检查数据格式、行数和列名。")
    return csv_data
def update_csv_data_2(csv_data, input_param, width, height, thick, force, tube_width, weld, table):
    try:
        # 获取列名
        header = csv_data[0]
        # 定义列名列表
        column_names = [
            '实体类型', '图层', '颜色', '线型', '线宽', '线型描述', '线型图案',
            '类型/名称', '块名', '值', '覆盖值', '位置 X', '位置 Y', '起点 X', '起点 Y', '终点 X', '终点 Y',
            '圆心 X', '圆心 Y', '半径', '顶点数据', '闭合', '高度', '角度', '尺寸编码',
            '起始角度', '终止角度', '缩放比例'
        ]
        # 生成列名和索引的映射字典
        column_index_map = {col_name: header.index(col_name) for col_name in column_names}

        # 直接更新指定行和列的数据

        # 主视图，长度数量说明
        result_str = ''
        product_quantity = 0
        count = 0
        total_count = len(table)
        for index, (length, quantity) in enumerate(table):
            result_str += f'L={length}-{quantity}件, '
            product_quantity += quantity
            count += 1
            if count % 4 == 0 and index < total_count - 1:
                result_str += '\P'
        result_str = result_str.rstrip(' ， ')
        csv_data[75][column_index_map['值']] = f'\W0.7;\T1.1;{result_str}\P共计{product_quantity}件'

        # 端面
        csv_data[129][column_index_map['覆盖值']] = format_number(thick)
        csv_data[130][column_index_map['覆盖值']] = format_number(width)
        csv_data[131][column_index_map['覆盖值']] = format_number(height)
        csv_data[132][column_index_map['覆盖值']] = format_number(thick)
        csv_data[133][column_index_map['覆盖值']] = format_number(tube_width)
        csv_data[134][column_index_map['覆盖值']] = format_number(tube_width)
        # 端面,焊缝
        csv_data[103][column_index_map['值']] = f'\T1.1;{format_number(weld)}'

        # 耗能面
        csv_data[157][column_index_map['覆盖值']] = format_number(thick)
        csv_data[158][column_index_map['覆盖值']] = format_number(height)

        # 连接板，尺寸
        csv_data[170][column_index_map['覆盖值']] = format_number((width - thick) / 2)
        # 连接板，数量
        csv_data[168][
            column_index_map['值']] = f'\W0.7;\T1.1;连接板 H={format_number(thick)}-{format_number(product_quantity * 4)}件'

        # 挡板，尺寸
        csv_data[181][column_index_map['覆盖值']] = format_number(width + 5)
        csv_data[182][column_index_map['覆盖值']] = format_number(thick + 5)
        csv_data[185][column_index_map['覆盖值']] = format_number(thick + 5)
        csv_data[186][column_index_map['覆盖值']] = format_number(height + 5)
        csv_data[175][column_index_map['覆盖值']] = format_number(tube_width + 20)
        csv_data[178][column_index_map['覆盖值']] = format_number(tube_width + 20)
        # 挡板，焊缝
        csv_data[200][column_index_map['值']] = f'\T1.1;C{format_number(weld)}'
        # 挡板，数量
        csv_data[176][column_index_map['值']] = f'\W0.7;\T1.1;挡板H=6-{format_number(product_quantity * 2)}件'

        # 标题栏，项目名称
        csv_data[247][column_index_map['值']] = f'\W0.5;\T1.1;{input_param}'
        # 标题栏，产品型号
        csv_data[249][column_index_map['值']] = f'\W0.7;\T1.1;YSX-BRB-{force}-L'


    except (IndexError, ValueError):
        print("修改 CSV 数据时出现错误，请检查数据格式、行数和列名。")
    return csv_data
def update_csv_data_3(csv_data, input_param, width, height, thick, force, tube_width, weld, table):
    try:
        # 获取列名
        header = csv_data[0]
        # 定义列名列表
        column_names = [
            '实体类型', '图层', '颜色', '线型', '线宽', '线型描述', '线型图案',
            '类型/名称', '块名', '值', '覆盖值', '位置 X', '位置 Y', '起点 X', '起点 Y', '终点 X', '终点 Y',
            '圆心 X', '圆心 Y', '半径', '顶点数据', '闭合', '高度', '角度', '尺寸编码',
            '起始角度', '终止角度', '缩放比例'
        ]
        # 生成列名和索引的映射字典
        column_index_map = {col_name: header.index(col_name) for col_name in column_names}

        # 直接更新指定行和列的数据

        # 主视图，长度数量说明
        result_str = ''
        product_quantity = 0
        count = 0
        total_count = len(table)
        for index, (length, quantity) in enumerate(table):
            result_str += f'L={length}-{quantity}件, '
            product_quantity += quantity
            count += 1
            if count % 4 == 0 and index < total_count - 1:
                result_str += '\P'
        result_str = result_str.rstrip(' ， ')
        csv_data[77][column_index_map['值']] = f'\W0.7;\T1.1;{result_str}\P共计{product_quantity}件'

        # 端面
        csv_data[163][column_index_map['覆盖值']] = format_number(thick)
        csv_data[164][column_index_map['覆盖值']] = format_number(width)
        csv_data[165][column_index_map['覆盖值']] = format_number(thick)
        csv_data[166][column_index_map['覆盖值']] = format_number(height-thick-thick)
        csv_data[167][column_index_map['覆盖值']] = format_number(thick)
        csv_data[168][column_index_map['覆盖值']] = format_number(thick)
        csv_data[169][column_index_map['覆盖值']] = format_number(tube_width)
        csv_data[170][column_index_map['覆盖值']] = format_number(tube_width)
        # 端面,焊缝
        csv_data[124][column_index_map['值']] = f'\T1.1;{format_number(weld)}'

        # 耗能面
        csv_data[193][column_index_map['覆盖值']] = format_number(thick)
        csv_data[194][column_index_map['覆盖值']] = format_number(height-thick-thick)

        # 板1，尺寸
        csv_data[309][column_index_map['覆盖值']] = format_number(width)
        # 板1，数量
        csv_data[307][column_index_map['值']] = f'\W0.7;\T1.1;连接板1 H={format_number(thick)}-{format_number(product_quantity * 4)}件'

        # 板2，尺寸
        csv_data[206][column_index_map['覆盖值']] = format_number((width - thick) / 2)
        # 连接板，数量
        csv_data[204][column_index_map['值']] = f'\W0.7;\T1.1;连接板2 H={format_number(thick)}-{format_number(product_quantity * 4)}件'

        # 挡板，尺寸
        csv_data[221][column_index_map['覆盖值']] = format_number(width + 5)
        csv_data[222][column_index_map['覆盖值']] = format_number(thick + 5)
        csv_data[223][column_index_map['覆盖值']] = format_number(thick + 5)
        csv_data[224][column_index_map['覆盖值']] = format_number(thick + 5)
        csv_data[227][column_index_map['覆盖值']] = format_number(thick + 5)
        csv_data[228][column_index_map['覆盖值']] = format_number(height-thick-thick-5)
        csv_data[211][column_index_map['覆盖值']] = format_number(tube_width + 20)
        csv_data[214][column_index_map['覆盖值']] = format_number(tube_width + 20)
        # 挡板，焊缝
        csv_data[250][column_index_map['值']] = f'\T1.1;C{format_number(weld)}'
        # 挡板，数量
        csv_data[212][column_index_map['值']] = f'\W0.7;\T1.1;挡板H=6-{format_number(product_quantity * 2)}件'

        # 标题栏，项目名称
        csv_data[297][column_index_map['值']] = f'\W0.5;\T1.1;{input_param}'
        # 标题栏，产品型号
        csv_data[299][column_index_map['值']] = f'\W0.7;\T1.1;YSX-BRB-{force}-L'

    except (IndexError, ValueError):
        print("修改 CSV 数据时出现错误，请检查数据格式、行数和列名。")
    return csv_data