import csv
import tkinter as tk
from tkinter import messagebox
import logging
from csv_to_dxf import csv_to_dxf


# 数字格式化，去除末尾0
def format_number(num):
    formatted = "{:.3f}".format(num).rstrip('0').rstrip('.') if isinstance(num, (int, float)) else str(num)
    return formatted


# 结构图 移动
def x_move(line, x, csv_vfd_P_data):
    # 获取列名
    header = csv_vfd_P_data[0]
    # 生成列名和索引的映射字典
    column_index_map = {col_name: header.index(col_name) for col_name in header}

    if csv_vfd_P_data[line][column_index_map['起点 X']]:  # 如果有起点 x
        start_x = float(csv_vfd_P_data[line][column_index_map['起点 X']])
        end_x = float(csv_vfd_P_data[line][column_index_map['终点 X']])
        # 先计算新值，再格式化
        new_start_x = start_x + x
        new_end_x = end_x + x
        csv_vfd_P_data[line][column_index_map['起点 X']] = format_number(new_start_x)
        csv_vfd_P_data[line][column_index_map['终点 X']] = format_number(new_end_x)
    if csv_vfd_P_data[line][column_index_map['圆心 X']]:  # 如果没有起点 x，但有圆心 x
        circle_x = float(csv_vfd_P_data[line][column_index_map['圆心 X']])
        new_circle_x = circle_x + x
        csv_vfd_P_data[line][column_index_map['圆心 X']] = format_number(new_circle_x)
    if csv_vfd_P_data[line][column_index_map['类型/名称']] == 'LINEAR':
        location_x = float(csv_vfd_P_data[line][column_index_map['位置 X']])
        new_location_x = location_x + x
        csv_vfd_P_data[line][column_index_map['位置 X']] = format_number(new_location_x)
    if csv_vfd_P_data[line][column_index_map['实体类型']] == 'INSERT':
        location_x = float(csv_vfd_P_data[line][column_index_map['位置 X']])
        new_location_x = location_x + x
        csv_vfd_P_data[line][column_index_map['位置 X']] = format_number(new_location_x)


# 结构图 延长
def x_extend(line, point, x, csv_vfd_P_data):
    # 获取列名
    header = csv_vfd_P_data[0]
    # 生成列名和索引的映射字典
    column_index_map = {col_name: header.index(col_name) for col_name in header}

    point_x = float(csv_vfd_P_data[line][column_index_map[point]])
    new_point_x = point_x + x
    csv_vfd_P_data[line][column_index_map[point]] = format_number(new_point_x)

# 结构图数据更新
def update_csv_data(csv_vfd_P_data, project_name, force, design_displacement, quantity, δpiston_width,
                                                 δdt1, δdt2, δdt3, δdt4, δdt5):
    try:
        # 以活塞中心为原点

        # 活塞轮廓移动距离
        x1 = δpiston_width / 2
        # 前盖移动距离  -（活塞/2 + 前腔变化）
        x2 = -(δpiston_width / 2 + δdt2)
        # 前吊耳移动距离  -（活塞/2 + 前腔变化 + 前吊耳距离变化）
        x3 = -(δpiston_width / 2 + δdt2 + δdt1)
        # 导向套处+后缸筒 移动距离  活塞/2 + 后腔变化
        x4 = δpiston_width / 2 + δdt3
        # 轴后端移动距离  活塞/2 + 后腔变化 + 轴后端变化
        x5 = δpiston_width / 2 + δdt3 + δdt4
        # 后盖+后吊耳 移动距离  活塞/2 + 后腔变化 + 轴后端变化 + 轴到后吊耳距离
        x6 = δpiston_width / 2 + δdt3 + δdt4 + δdt5


        # 移动
    # 活塞轮廓移动距离
        for i in [19, 20, 91, 92]:
            x_move_x1 = x_move(i, -x1, csv_vfd_P_data)
        for i in [21, 22, 101]:
            x_move__x1 = x_move(i, x1, csv_vfd_P_data)

        for i in [23, 24, 25, 26, 27, 28, 29, 30,  # 直线
            90,  # 尺寸
            183]:
            x_move_x2 = x_move(i, x2, csv_vfd_P_data)

        for i in [
            31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44,  # 直线
            84,  # 中心线
            86, 88, 89,   # 尺寸
            102, 108,
        ]:
            x_move_x3 = x_move(i, x3, csv_vfd_P_data)

        for i in [
            45, 46, 47, 48, 49, 50, 51, 52, 53, 54  # 直线
        ]:
            x_move_x4 = x_move(i, x4, csv_vfd_P_data)  # 线条移动

        for i in [
            55, 56, 57, 58   # 直线
        ]:
            x_move_x5 = x_move(i, x5, csv_vfd_P_data)

        for i in [
            59, 60, 61, 62, 63, 64, 65, 66, 67, 68,   # 直线
            85,  # 中心线
            87, 93,   # 尺寸
            114, 120
            ]:
            x_move_x6 = x_move(i, x6, csv_vfd_P_data)

        for i in [192, 193, 194, 195, 196]:
            x_move__δdt1 = x_move(i, -δdt1  , csv_vfd_P_data)


        END_POINTS = [
            81, 82,
            94,
        ]
        START_POINTS = [
             69, 70, 71, 72, 73, 74,   # 直线
             95,
        ]
        all_points = END_POINTS + START_POINTS
        for j in all_points:  # 直接遍历有效数字，无需连续范围
            if j in END_POINTS:
                point = '终点 X'
            else:
                point = '起点 X'
            x_extend_x2 = x_extend(j, point, x2, csv_vfd_P_data) # 端点延伸

        # 延伸
        END_POINTS = []
        START_POINTS = [
            81, 82,
            83,  # 中心线
            94, 99, 100  # 尺寸线
             ]
        all_points = END_POINTS + START_POINTS
        for j in all_points:  # 直接遍历有效数字，无需连续范围
            if j in END_POINTS:
                point = '终点 X'
            else:
                point = '起点 X'
            x_extend_x3 = x_extend(j, point, x3, csv_vfd_P_data)  # 端点延伸

        END_POINTS = [
            69, 70, 71, 72, 73, 74,   # 直线
            95,
        ]
        START_POINTS = [
            75, 76, 77, 78, 79, 80,  # 直线
            96, 97
        ]
        all_points = END_POINTS + START_POINTS
        for j in all_points:  # 直接遍历有效数字，无需连续范围
            if j in END_POINTS:
                point = '终点 X'
            else:
                point = '起点 X'
            x_extend_x4 = x_extend(j, point, x4, csv_vfd_P_data)  # 端点延伸

        END_POINTS = [
            75, 76,   # 直线
            97, 99
        ]
        START_POINTS = [
            98,
        ]
        all_points = END_POINTS + START_POINTS
        for j in all_points:  # 直接遍历有效数字，无需连续范围
            if j in END_POINTS:
                point = '终点 X'
            else:
                point = '起点 X'
            x_extend_x5 = x_extend(j, point, x5, csv_vfd_P_data)  # 端点延伸

        END_POINTS = [
            77, 78, 79, 80,   # 直线
            83,   # 中心线
            96, 98, 100
        ]
        START_POINTS = []
        all_points = END_POINTS + START_POINTS
        for j in all_points:  # 直接遍历有效数字，无需连续范围
            if j in END_POINTS:
                point = '终点 X'
            else:
                point = '起点 X'
            x_extend_x6 = x_extend(j, point, x6, csv_vfd_P_data)  # 端点延伸

        END_POINTS = []
        START_POINTS = [188, 189, 190, 191]
        all_points = END_POINTS + START_POINTS
        for j in all_points:  # 直接遍历有效数字，无需连续范围
            if j in END_POINTS:
                point = '终点 X'
            else:
                point = '起点 X'
            x_extend__δdt1 = x_extend(j, point, -δdt1, csv_vfd_P_data)  # 端点延伸


        # 标题栏更改
        # 获取列名
        header = csv_vfd_P_data[0]
        # 生成列名和索引的映射字典
        column_index_map = {col_name: header.index(col_name) for col_name in header}

        csv_vfd_P_data[182][column_index_map['值']] = f'\W0.7;\T1.1;{quantity}'

        csv_vfd_P_data[179][column_index_map['值']] = calculate_dynamic_width(
            project_name,
            max_width=160
        )

        product_model = f'VFD-{force}-{design_displacement}'
        csv_vfd_P_data[181][column_index_map['值']] = calculate_dynamic_width(
            product_model,
            max_width=92
        )


    except (IndexError, ValueError) as e:
        logging.error(f"修改 CSV 数据时出现错误: {str(e)}")
        messagebox.showerror("错误", "修改CSV数据时出现错误，请检查数据格式。")
        raise  # 重新抛出异常，让上层调用者处理

    return csv_vfd_P_data

# 限制字符总长
def calculate_dynamic_width(text, max_width=300, base_width_cn=23.7, base_width_en=11.85):

    # 计算不同类型字符的数量
    cn_count = 0  # 中文字符数量
    en_count = 0  # 英文字符数量（包括数字和符号）

    for char in text:
        # 判断是否为中文字符（Unicode范围：0x4E00-0x9FFF）
        if 0x4E00 <= ord(char) <= 0x9FFF:
            cn_count += 1
        else:
            en_count += 1

    # 计算总字符数量
    total_count = cn_count + en_count

    # 估算1倍率下的总宽度
    estimated_total_length = (cn_count * base_width_cn) + (en_count * base_width_en)

    # 计算动态宽度倍率
    if total_count > 0 and estimated_total_length > 0:
        dynamic_multiplier = max_width / estimated_total_length
        # 限制倍率范围
        dynamic_multiplier = max(0.3, min(dynamic_multiplier, 1.0))
    else:
        dynamic_multiplier = 0.7  # 默认倍率

    # 构建并返回最终字符串
    return f'\W{dynamic_multiplier:.2f};\T1.1;{text}'

# 主函数，绘制vfd图纸
def vfd_drawing(data_table):
    """根据数据表格生成图纸"""
    # 确保数据表格是列表类型
    if not isinstance(data_table, list):
        data_table = [data_table]

    # 读取数据包
    for row in data_table:
        try:
            # 从数据行中获取各参数值，使用get方法并设置默认值
            project_name = row.get("project_name", "")  # 项目名称
            force = int(row.get("force"))  # 阻尼力
            design_displacement = int(row.get("design_displacement"))  # 设计位移
            quantity = int(row.get("quantity"))  # 数量
            cylinder_diameter = int(row.get("cylinder_diameter"))  # 缸筒内径
            axis_diameter = int(row.get("axis_diameter"))  # 轴径
            dt1 = int(row.get("dt1"))  # 前吊耳 到 前盖 距离
            dt2 = int(row.get("dt2"))  # 前腔距离
            dt3 = int(row.get("dt3"))  # 后腔距离
            piston_width = int(row.get("piston_width"))  # 活塞宽度
            dt4 = int(row.get("dt4"))  # 轴后端伸出距离
            dt5 = int(row.get("dt5"))  # 轴 到 后盖 距离
        except Exception as e:
            logging.error(f"处理数据行时出错: {str(e)}")
            messagebox.showerror("错误", f"错误数据: {str(e)}，请确保为正确的值类型")

    # 生成产品图
    # 打开VFD-型号表，读取数据
    with open('data/vfd/VFD-型号表.csv', 'r', encoding='utf-8') as VFD_style:
        csv_reader = csv.DictReader(VFD_style)
        csv_VFD_style_data = list(csv_reader)

    # 遍历型号表数据，根据缸径和轴径，确定其他零件的尺寸和数据文件
    found = False
    for line_num, row in enumerate(csv_VFD_style_data, start=2):
        try:
            # 将CSV中的字符串值转换为整数进行比较
            csv_cylinder_diameter = int(row["缸径"])
            csv_axis_diameter = int(row["轴径"])

            # 比较整数类型
            if csv_cylinder_diameter == cylinder_diameter and csv_axis_diameter == axis_diameter:
                print(f"找到匹配项在第 {line_num} 行")
                print(f"缸径: {csv_cylinder_diameter}")
                print(f"轴径: {csv_axis_diameter}")
                print(f"产品结构图数据: {row['产品结构图数据']}")
                found = True
                δdt1 = dt1 - int(row["ex_dt1"])  # 前吊耳距离变化
                δdt2 = dt2 - int(row["ex_dt2"])  # 前腔变化
                δdt3 = dt3 - int(row["ex_dt3"])  # 后腔变化
                δdt4 = dt4 - int(row["ex_dt4"])  # 活塞杆后端变化
                δdt5 = dt5 - int(row["ex_dt5"])  # 活塞杆到后吊耳距离变化
                δpiston_width = piston_width - int(row["ex_piston_width"])  # 活塞变化
                # 可以在这里添加进一步的处理逻辑
                # 读取产品图数据
                with open(row['产品结构图数据'], 'r', encoding='utf-8') as vfd_P:
                    csv_reader = csv.reader(vfd_P)
                    csv_vfd_P_data = list(csv_reader)

                # 根据参数更改结构图数据
                csv_vfd_P_data = update_csv_data(csv_vfd_P_data, project_name, force, design_displacement, quantity, δpiston_width,
                                                 δdt1, δdt2, δdt3, δdt4, δdt5)

                # 调用 csv_to_dxf 函数进行转换，输出 DXF 文件名称为产品型号输入的参数
                input_file = f'{project_name} VFD-{force}-{design_displacement}.csv'
                with open(input_file, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows(csv_vfd_P_data)

                output_dxf_file = f'{project_name} VFD-{force}-{design_displacement}.dxf'

                # 调用 csv_to_dxf，传递文件路径
                csv_to_dxf(input_file, output_dxf_file)

                break  # 找到匹配项后跳出循环

        except (KeyError, ValueError) as e:
            logging.warning(f"处理第 {line_num} 行时出错: {str(e)}")
            continue

    if not found:
        messagebox.showerror("错误", f"未找到匹配的缸径({cylinder_diameter})和轴径({axis_diameter})组合")


# 测试
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    data_table = [{
        "project_name": "这是一个超级长的项目名称",
        "force": 400,  # 阻尼力
        "design_displacement": 30,  # 设计位移
        "quantity": 10,  # 数量
        "cylinder_diameter": 140,  # 缸筒内径
        "axis_diameter": 50,  # 轴径
        "dt1": 130,  # 前吊耳 到 前盖 距离
        "dt2": 100,  # 前腔距离
        "dt3": 100,  # 后腔距离
        "piston_width": 50,  # 活塞宽度
        "dt4": 95,  # 轴后端伸出距离
        "dt5": 115  # 轴 到 后盖 距离
    }]

    # 调用函数
    vfd_drawing(data_table)