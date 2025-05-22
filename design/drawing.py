import csv
import tkinter as tk
from tkinter import messagebox
import logging
from csv_to_dxf import csv_to_dxf


def generate_drawing(data_table):
    """根据数据表格生成图纸"""

    # 确保数据表格是列表类型
    if not isinstance(data_table, list):
        data_table = [data_table]

    for row in data_table:
        try:
            # 从数据行中获取各参数值，使用get方法并设置默认值
            selected_template = row.get("template")  # 模版类型
            input_param = row.get("project_name", "")  # 项目名称
            width = row.get("width")  # 截面宽度
            height = row.get("height")  # 截面高度
            thick = row.get("thickness")  # 板厚
            force = row.get("force")  # 力
            tube_width = row.get("tube_width")  # 方管宽度
            weld = row.get("weld")  # 焊缝
            table = row.get("length_quantity", [])  # 长度-数量表格

            # 验证必要参数是否存在
            required_params = {
                "template": selected_template,
                "project_name": input_param,
                "width": width,
                "height": height,
                "thickness": thick,
                "force": force,
                "tube_width": tube_width,
                "weld": weld
            }

            for param_name, param_value in required_params.items():
                if param_value is None:
                    messagebox.showwarning("参数缺失", f"缺少必要参数: {param_name}")
                    continue  # 跳过当前数据行，处理下一行

            try:
                width = float(width)
                height = float(height)
                thick = float(thick)
                force = float(force)
                tube_width = float(tube_width)
                weld = float(weld)
            except ValueError:
                messagebox.showwarning("输入错误", "数值字段必须为有效数字（如 123 或 123.45）！")
                continue

            # 模板与CSV文件映射
            template_files = {
                '王工': 'data\\王工.csv',
                '十一': 'data\\十一.csv',
                '王一': 'data\\王一.csv'
            }

            # 模板与更新函数映射
            update_functions = {
                '王工': update_common_data,
                '十一': update_common_data,
                '王一': update_common_data
            }

            # 模板与配置数据映射
            template_configs = {
                '王工': {
                    'length_desc_row': 81,
                    'end_face_start_row': 149,
                    'energy_absorbing_start_row': 185,
                    'connecting_plate_start_row': 201,
                    'baffle_start_row': 216,
                    'weld_row': 110,
                    'baffle_weld_row': 246,
                    'title_row': 292,
                    'model_row': 294,
                    'plate_type': 1
                },
                '十一': {
                    'length_desc_row': 75,
                    'end_face_start_row': 129,
                    'energy_absorbing_start_row': 157,
                    'connecting_plate_start_row': 170,
                    'baffle_start_row': 181,
                    'weld_row': 103,
                    'baffle_weld_row': 200,
                    'title_row': 247,
                    'model_row': 249,
                    'plate_type': 1
                },
                '王一': {
                    'length_desc_row': 77,
                    'end_face_start_row': 163,
                    'energy_absorbing_start_row': 193,
                    'connecting_plate1_start_row': 309,
                    'connecting_plate2_start_row': 206,
                    'baffle_start_row': 221,
                    'weld_row': 124,
                    'baffle_weld_row': 250,
                    'title_row': 297,
                    'model_row': 299,
                    'plate_type': 2
                }
            }

            if selected_template not in template_files:
                messagebox.showerror("错误", f"未知的模板类型: {selected_template}")
                continue

            csv_file = template_files[selected_template]

            try:
                with open(csv_file, 'r', encoding='utf-8') as file:
                    csv_reader = csv.reader(file)
                    # 将 csv_reader 转换为列表
                    csv_data = list(csv_reader)

                # 输入参数并更新数据
                config = template_configs[selected_template]
                update_function = update_functions[selected_template]
                csv_data = update_function(csv_data, input_param, width, height, thick, force, tube_width, weld, table,
                                           config)

                # 将修改后的数据写回到 CSV 文件
                with open(csv_file, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows(csv_data)

                # 调用 csv_to_dxf 函数进行转换，输出 DXF 文件名称为产品型号输入的参数
                output_dxf_file = f'{input_param} BRB-{format_number(force)}-L.dxf'
                csv_to_dxf(csv_file, output_dxf_file)
                """logging.info(f"图纸生成成功: {output_dxf_file}")
                messagebox.showinfo("成功", f"图纸生成成功！文件已保存为: {output_dxf_file}")"""

            except FileNotFoundError:
                logging.error(f"文件不存在: {csv_file}")
                messagebox.showerror("错误", f"文件不存在: {csv_file}")
            except Exception as e:
                logging.error(f"处理文件时出错: {str(e)}")
                messagebox.showerror("错误", f"处理文件时出错: {str(e)}")

        except Exception as e:
            logging.error(f"处理数据行时出错: {str(e)}")
            messagebox.showerror("错误", f"处理数据行时出错: {str(e)}")


def format_number(num):
    """格式化数字，去除多余的零和小数点"""
    formatted = "{:.3f}".format(num).rstrip('0').rstrip('.') if isinstance(num, (int, float)) else str(num)
    return formatted


def update_common_data(csv_data, input_param, width, height, thick, force, tube_width, weld, table, config):
    """通用的CSV数据更新函数"""
    try:
        # 获取列名
        header = csv_data[0]
        """
        header = [
            '实体类型', '图层', '颜色', '线型', '线宽', '线型描述', '线型图案',
            '类型/名称', '块名', '值', '覆盖值', '位置 X', '位置 Y', '起点 X', '起点 Y', '终点 X', '终点 Y',
            '圆心 X', '圆心 Y', '半径', '顶点数据', '闭合', '高度', '角度', '尺寸编码',
            '起始角度', '终止角度', '缩放比例'
        ]
        """
        # 生成列名和索引的映射字典
        column_index_map = {col_name: header.index(col_name) for col_name in header}

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
        csv_data[config['length_desc_row']][column_index_map['值']] = f'\W0.7;\T1.1;{result_str}\P共计{product_quantity}件'

        # 端面设置（合并重复代码）
        face_start_row = config['end_face_start_row']
        csv_data[face_start_row][column_index_map['覆盖值']] = format_number(thick)
        csv_data[face_start_row + 1][column_index_map['覆盖值']] = format_number(width)
        csv_data[face_start_row + 2][column_index_map['覆盖值']] = format_number(thick)
        csv_data[face_start_row + 3][column_index_map['覆盖值']] = format_number(height - thick - thick)
        csv_data[face_start_row + 4][column_index_map['覆盖值']] = format_number(thick)
        csv_data[face_start_row + 5][column_index_map['覆盖值']] = format_number(thick)
        csv_data[face_start_row + 6][column_index_map['覆盖值']] = format_number(tube_width)
        csv_data[face_start_row + 7][column_index_map['覆盖值']] = format_number(tube_width)

        # 端面焊缝
        csv_data[config['weld_row']][column_index_map['值']] = f'\T1.1;{format_number(weld)}'

        # 耗能面设置
        energy_start_row = config['energy_absorbing_start_row']
        if config['plate_type'] == 1:
            csv_data[energy_start_row][column_index_map['覆盖值']] = format_number(thick)
            csv_data[energy_start_row + 1][column_index_map['覆盖值']] = format_number(thick)
            csv_data[energy_start_row + 2][column_index_map['覆盖值']] = format_number(thick)
            csv_data[energy_start_row + 3][column_index_map['覆盖值']] = format_number(height)
            csv_data[energy_start_row + 4][column_index_map['覆盖值']] = format_number(width)
        else:
            csv_data[energy_start_row][column_index_map['覆盖值']] = format_number(thick)
            csv_data[energy_start_row + 1][column_index_map['覆盖值']] = format_number(height - thick - thick)

        # 连接板设置
        if config['plate_type'] == 2:
            # 两种连接板的情况
            # 板1，尺寸
            csv_data[config['connecting_plate1_start_row']][column_index_map['覆盖值']] = format_number(width)
            # 板1，数量
            csv_data[config['connecting_plate1_start_row'] - 2][column_index_map[
                '值']] = f'\W0.7;\T1.1;连接板1 H={format_number(thick)}-{format_number(product_quantity * 4)}件'

            # 板2，尺寸
            csv_data[config['connecting_plate2_start_row']][column_index_map['覆盖值']] = format_number(
                (width - thick) / 2)
            # 板2，数量
            csv_data[config['connecting_plate2_start_row'] - 2][column_index_map[
                '值']] = f'\W0.7;\T1.1;连接板2 H={format_number(thick)}-{format_number(product_quantity * 4)}件'
        else:
            # 一种连接板的情况
            # 连接板，尺寸
            csv_data[config['connecting_plate_start_row']][column_index_map['覆盖值']] = format_number((width - thick) / 2)
            # 连接板，数量
            csv_data[config['connecting_plate_start_row'] - 2][column_index_map[
                '值']] = f'\W0.7;\T1.1;连接板 H={format_number(thick)}-{format_number(product_quantity * 4)}件'

        # 挡板
        baffle_start_row = config['baffle_start_row']
        csv_data[baffle_start_row][column_index_map['覆盖值']] = format_number(width + 5)
        csv_data[baffle_start_row + 1][column_index_map['覆盖值']] = format_number(thick + 5)
        csv_data[baffle_start_row + 2][column_index_map['覆盖值']] = format_number(thick + 5)
        csv_data[baffle_start_row + 3][column_index_map['覆盖值']] = format_number(thick + 5)
        csv_data[baffle_start_row + 4][column_index_map['覆盖值']] = format_number(thick + 5)
        csv_data[baffle_start_row + 5][column_index_map['覆盖值']] = format_number(height - thick - thick - 5)
        csv_data[baffle_start_row - 5][column_index_map['覆盖值']] = format_number(tube_width + 20)
        csv_data[baffle_start_row - 2][column_index_map['覆盖值']] = format_number(tube_width + 20)

        # 挡板焊缝
        csv_data[config['baffle_weld_row']][column_index_map['值']] = f'\T1.1;C{format_number(weld)}'
        # 挡板数量
        csv_data[baffle_start_row - 4][
            column_index_map['值']] = f'\W0.7;\T1.1;挡板H=6-{format_number(product_quantity * 2)}件'

        # 标题栏，项目名称
        csv_data[config['title_row']][column_index_map['值']] = f'\W0.5;\T1.1;{input_param}'
        # 标题栏，产品型号
        csv_data[config['model_row']][column_index_map['值']] = f'\W0.7;\T1.1;YSX-BRB-{force}-L'

    except (IndexError, ValueError) as e:
        logging.error(f"修改 CSV 数据时出现错误: {str(e)}")
        messagebox.showerror("错误", "修改CSV数据时出现错误，请检查数据格式。")
        raise  # 重新抛出异常，让上层调用者处理

    return csv_data

# 测试
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    """
        根据数据表格生成图纸
    """

    data_table = [{
        "template": "王一",
        "project_name": "项目名称",
        "width": 160,  # 截面宽度
        "height": 160,  # 截面高度
        "thickness": 12,  # 板厚
        "force": 2000,  # 力
        "tube_width": 250,  # 方管宽度
        "weld": 6,  # 焊缝
        "length_quantity": [(5000, 2), (6000, 3)]  # 添加长度-数量表格
    }]
    print(data_table)

    # 调用函数
    generate_drawing(data_table)