import ezdxf
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import logging

# 配置日志记录
logging.basicConfig(filename='dxf_csv_conversion.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


global_scale_factor = 5

# 定义默认颜色
def handle_color(color):
    if color == 'BYLAYER':
        return 256
    try:
        return int(color)
    except ValueError:
        return 256


# 设置线型函数
def handle_linetype_pattern(linetype_pattern_str, linetype, input_file, layer):
    linetype_pattern = []
    if linetype_pattern_str:
        parts = linetype_pattern_str.split(";")
        for part in parts:
            try:
                value = float(part.strip())
                linetype_pattern.append(value)
            except ValueError:
                if linetype != "Continuous":
                    messagebox.showwarning("警告",
                                           f"文件 {input_file} 中图层 {layer} 的线型图案字段 '{linetype_pattern_str}' 包含无效数据，将使用空列表代替。")
                    logging.warning(
                        f"文件 {input_file} 中图层 {layer} 的线型图案字段 '{linetype_pattern_str}' 包含无效数据，将使用空列表代替。")
                linetype_pattern = []
                break
    return linetype_pattern


# 创建图层函数
def create_layer(doc, layer, color, linetype, lineweight, linetype_description, linetype_pattern, input_file):
    if layer not in doc.layers:
        try:
            if linetype not in doc.linetypes:
                if linetype_pattern:
                    if len(linetype_pattern) % 2 != 0:
                        linetype_pattern.append(0)
                    doc.linetypes.add(
                        name=linetype,
                        pattern=linetype_pattern,
                        description=linetype_description
                    )
                elif linetype != "Continuous":
                    messagebox.showwarning("警告",
                                           f"文件 {input_file} 中图层 '{layer}' 使用了未知线型 '{linetype}'，将使用默认实线。")
                    logging.warning(f"文件 {input_file} 中图层 '{layer}' 使用了未知线型 '{linetype}'，将使用默认实线。")
                    linetype = "CONTINUOUS"
            doc.layers.new(name=layer, dxfattribs={
                "color": color,
                "linetype": linetype,
                "lineweight": lineweight
            })
        except ezdxf.DXFValueError:
            messagebox.showwarning("警告", f"文件 {input_file} 中图层 '{layer}' 无法创建，可能是无效的线型或线宽。将使用默认设置。")
            logging.warning(f"文件 {input_file} 中图层 '{layer}' 无法创建，可能是无效的线型或线宽。将使用默认设置。")
            if layer not in doc.layers:
                doc.layers.new(name=layer)


# 绘制直线函数
def handle_line(row, msp, layer, color, linetype, lineweight, input_file, line_num):
    try:
        start = (float(row["起点 X"]), float(row["起点 Y"]))
        end = (float(row["终点 X"]), float(row["终点 Y"]))
        msp.add_line(start, end,
                     dxfattribs={"layer": layer, "color": color, "linetype": linetype, "lineweight": lineweight})
    except ValueError:
        messagebox.showwarning("警告",
                               f"文件 {input_file} 第 {line_num} 行的 LINE 实体坐标字段包含无效数据，将略过此数据。")
        logging.warning(f"文件 {input_file} 第 {line_num} 行的 LINE 实体坐标字段包含无效数据，将略过此数据。")


# 绘制圆形函数
def handle_circle(row, msp, layer, color, linetype, lineweight, input_file, line_num):
    try:
        center = (float(row["圆心 X"]), float(row["圆心 Y"]))
        radius = float(row["半径"])
        msp.add_circle(center, radius,
                       dxfattribs={"layer": layer, "color": color, "linetype": linetype, "lineweight": lineweight})
    except ValueError:
        messagebox.showwarning("警告",
                               f"文件 {input_file} 第 {line_num} 行的 CIRCLE 实体坐标或半径字段包含无效数据，将略过此数据。")
        logging.warning(f"文件 {input_file} 第 {line_num} 行的 CIRCLE 实体坐标或半径字段包含无效数据，将略过此数据。")


# 绘制多段线函数
def handle_lwpolyline(row, msp, layer, color, linetype, lineweight, input_file, line_num):
    vertices = []
    points = row["顶点数据"].split("; ")
    if row["闭合"] == "是":
        closed = True
    else:
        closed = False
    for point in points:
        try:
            x, y, start_width, end_width, bulge = point.strip("()").split(", ")
            vertices.append(
                (float(x), float(y), float(start_width), float(end_width), float(bulge)))
        except ValueError:
            messagebox.showwarning("警告",
                                   f"文件 {input_file} 第 {line_num} 行的 LWPOLYLINE 实体顶点数据包含无效数据，将略过此数据。")
            logging.warning(
                f"文件 {input_file} 第 {line_num} 行的 LWPOLYLINE 实体顶点数据包含无效数据，将略过此数据。")
            vertices = []
            break
    if vertices:
        msp.add_lwpolyline(vertices,
                           dxfattribs={"layer": layer, "color": color, "linetype": linetype, "lineweight": lineweight,
                                       "closed": closed})


# 绘制尺寸函数
def handle_dimension(row, msp, layer, color, linetype, lineweight, input_file, line_num):
    dim_type = row["类型/名称"]
    dim_code = row["尺寸编码"]

    try:
        dim_angle = float(row["角度"])
    except ValueError:
        dim_angle = 0
    if dim_type == "UNKNOWN":
        messagebox.showwarning("警告", f"第 {line_num} 行的尺寸标注类型未知，尺寸编码为 {dim_code}，将略过此尺寸。")
        logging.warning(f"第 {line_num} 行的尺寸标注类型未知，尺寸编码为 {dim_code}，将略过此尺寸。")
        return
    if dim_type in ["LINEAR", "ALIGNED", "LINEAR_HORIZONTAL", "LINEAR_VERTICAL", "LINEAR_ROTATED"]:
        try:
            location = (float(row["位置 X"]), float(row["位置 Y"]))

            # 通过调整尺寸初始点和角度，来调整尺寸显示位置。
            if 90 <= dim_angle <= 120 or 270 <= dim_angle <= 300:
                if float(row["终点 Y"]) > float(row["起点 Y"]):
                    p1 = (float(row["起点 X"]), float(row["起点 Y"]))
                    p2 = (float(row["终点 X"]), float(row["终点 Y"]))
                else:
                    p2 = (float(row["起点 X"]), float(row["起点 Y"]))
                    p1 = (float(row["终点 X"]), float(row["终点 Y"]))
            elif float(row["终点 X"]) > float(row["起点 X"]):
                p1 = (float(row["起点 X"]), float(row["起点 Y"]))
                p2 = (float(row["终点 X"]), float(row["终点 Y"]))
            else:
                p2 = (float(row["起点 X"]), float(row["起点 Y"]))
                p1 = (float(row["终点 X"]), float(row["终点 Y"]))
            if 90 < dim_angle < 180:
                dim_angle += 180
            elif 180 <= dim_angle <= 270:
                dim_angle -= 180
            # 覆盖测量文本
            if row["覆盖值"]:
                dim_text = row["覆盖值"]
            else:
                dim_text = row["值"]

            dim = msp.add_linear_dim(
                base=location,
                p1=p1,
                p2=p2,
                text=dim_text,
                dimstyle="CUSTOM_DIMSTYLE",
                dxfattribs={"layer": layer, "color": color, "linetype": linetype, "lineweight": lineweight},
                angle=dim_angle
            )
            dim.render()
        except ValueError:
            messagebox.showwarning("警告",
                                   f"文件 {input_file} 第 {line_num} 行的 DIMENSION 实体线性尺寸坐标字段包含无效数据，将略过此数据。")
            logging.warning(
                f"文件 {input_file} 第 {line_num} 行的 DIMENSION 实体线性尺寸坐标字段包含无效数据，将略过此数据。")
    elif dim_type == 'ANGULAR':
        try:
            p1 = (float(row["起点 X"]), float(row["起点 Y"]))
            p2 = (float(row["终点 X"]), float(row["终点 Y"]))
            p3 = (float(row["圆心 X"]), float(row["圆心 Y"]))
            dim = msp.add_angular_dim3p(
                base=(0, 0),
                p1=p1,
                p2=p2,
                p3=p3,
                dimstyle="CUSTOM_DIMSTYLE",
                dxfattribs={"layer": layer, "color": color, "linetype": linetype, "lineweight": lineweight}
            )
            dim.render()
        except ValueError:
            messagebox.showwarning("警告",
                                   f"文件 {input_file} 第 {line_num} 行的 DIMENSION 实体角度尺寸坐标字段包含无效数据，将略过此数据。")
            logging.warning(
                f"文件 {input_file} 第 {line_num} 行的 DIMENSION 实体角度尺寸坐标字段包含无效数据，将略过此数据。")
    elif dim_type == 'DIAMETER':
        try:
            dim_value = float(row["值"])
            center = (float(row["圆心 X"]), float(row["圆心 Y"]))
            radius = dim_value / 2
            location = (float(row["位置 X"]), float(row["位置 Y"]))
            if row["覆盖值"]:
                dim_text = row["覆盖值"]
            else:
                dim_text = row["值"]
            dim = msp.add_diameter_dim(
                center=center,
                radius=radius,
                angle=dim_angle,
                # location=location,
                text=dim_text,
                dimstyle="CUSTOM_DIMSTYLE",
                dxfattribs={"layer": layer, "color": color, "linetype": linetype, "lineweight": lineweight},
                override={"dimtoh": 1, "dimtix": 0}
            )
            dim.render()
        except ValueError:
            messagebox.showwarning("警告",
                                   f"文件 {input_file} 第 {line_num} 行的 DIMENSION 实体直径尺寸坐标或值字段包含无效数据，将略过此数据。")
            logging.warning(
                f"文件 {input_file} 第 {line_num} 行的 DIMENSION 实体直径尺寸坐标或值字段包含无效数据，将略过此数据。")
    elif dim_type == 'RADIUS':
        try:
            dim_value = float(row["值"])
            center = (float(row["圆心 X"]), float(row["圆心 Y"]))
            radius = dim_value
            location = (float(row["位置 X"]), float(row["位置 Y"]))
            dim = msp.add_radius_dim(
                center=center,
                radius=radius,
                angle=dim_angle,
                dimstyle="CUSTOM_DIMSTYLE",
                # location=location,
                dxfattribs={"layer": layer, "color": color, "linetype": linetype, "lineweight": lineweight},
                override={"dimtoh": 1, "dimtix": 0}
            )
            dim.render()
        except ValueError:
            messagebox.showwarning("警告",
                                   f"文件 {input_file} 第 {line_num} 行的 DIMENSION 实体半径尺寸坐标或值字段包含无效数据，将略过此数据。")
            logging.warning(
                f"文件 {input_file} 第 {line_num} 行的 DIMENSION 实体半径尺寸坐标或值字段包含无效数据，将略过此数据。")


# 绘制圆弧函数
def handle_arc(row, msp, layer, color, linetype, lineweight, input_file, line_num):
    try:
        center = (float(row["圆心 X"]), float(row["圆心 Y"]))
        radius = float(row["半径"])
        start_angle = float(row["起始角度"])
        end_angle = float(row["终止角度"])
        msp.add_arc(center, radius, start_angle, end_angle,
                    dxfattribs={"layer": layer, "color": color, "linetype": linetype, "lineweight": lineweight})
    except ValueError:
        messagebox.showwarning("警告",
                               f"文件 {input_file} 第 {line_num} 行的 ARC 实体坐标、半径或角度字段包含无效数据，将略过此数据。")
        logging.warning(f"文件 {input_file} 第 {line_num} 行的 ARC 实体坐标、半径或角度字段包含无效数据，将略过此数据。")


# 绘制文本函数
def handle_text(row, msp, layer, color, input_file, entity_type, line_num):
    try:
        text_content = row["值"]
        text_location = (float(row["位置 X"]), float(row["位置 Y"]))
        text_height = float(row["高度"])
        text_rotation = float(row["角度"])
        if entity_type == 'TEXT':
            msp.add_text(
                text_content,
                dxfattribs={
                    "layer": layer,
                    "height": text_height,
                    "rotation": text_rotation,
                    "color": color,
                }
            ).set_pos(text_location)
        else:  # MTEXT
            msp.add_mtext(
                text_content,
                dxfattribs={
                    "layer": layer,
                    "char_height": text_height,
                    "rotation": text_rotation,
                    "color": color,
                    'style': 'CUSTOM_TEXTSTYLE'
                }
            ).set_location(text_location)
    except ValueError:
        messagebox.showwarning("警告",
                               f"文件 {input_file} 第 {line_num} 行的 {entity_type} 实体文本相关字段包含无效数据，将略过此数据。")
        logging.warning(
            f"文件 {input_file} 第 {line_num} 行的 {entity_type} 实体文本相关字段包含无效数据，将略过此数据。")


# 绘制剖面线函数
def handle_hatch(row, msp, layer, color, input_file, line_num):
    pattern_name = row["类型/名称"]
    boundary_vertices_str = row["顶点数据"]
    scale_str = row.get("缩放比例", "1.0")
    try:
        if pattern_name == "AR-CONC":
            scale = 0.1
        else:
            scale = float(scale_str)
    except ValueError:
        messagebox.showwarning("警告",
                               f"文件 {input_file} 第 {line_num} 行的 HATCH 实体缩放比例字段 '{scale_str}' 不是有效的数字，将使用默认值 1.0。")
        logging.warning(
            f"文件 {input_file} 第 {line_num} 行的 HATCH 实体缩放比例字段 '{scale_str}' 不是有效的数字，将使用默认值 1.0。")
        scale = 1.0
    if not boundary_vertices_str:
        return
    boundary_vertices = []
    vertex_strs = boundary_vertices_str.split("; ")
    for vertex_str in vertex_strs:
        try:
            # 处理三元数组数据，假设格式为 (x, y, bulge)
            parts = vertex_str.strip("()").split(", ")
            if len(parts) == 2:
                x, y = parts
                bulge = 0
            elif len(parts) == 3:
                x, y, bulge = parts
            else:
                raise ValueError
            vertex = (float(x), float(y), float(bulge))
            boundary_vertices.append(vertex)
        except ValueError:
            messagebox.showwarning("警告",
                                   f"文件 {input_file} 第 {line_num} 行的 HATCH 实体边界顶点数据包含无效数据，将略过此数据。")
            logging.warning(
                f"文件 {input_file} 第 {line_num} 行的 HATCH 实体边界顶点数据包含无效数据，将略过此数据。")
            boundary_vertices = []
            break
    if boundary_vertices:
        hatch = msp.add_hatch(dxfattribs={"layer": layer})
        # 这里假设 ezdxf 支持带 bulge 值的路径
        hatch.paths.add_polyline_path(boundary_vertices, is_closed=True)
        hatch.set_pattern_fill(pattern_name, scale=scale, color=color)


# 块添加实体函数
def block_add_virtual_entities(data, block, block_name, input_file):
    # 将模型空间设为块
    msp = block
    for line_num, row in enumerate(data, start=2):  # 从第 2 行开始计数
        line_num -= 1
        # 读取块内元素
        if row["块名"] and row["实体类型"] != 'INSERT':
            if row["块名"].split(": ")[1] == block_name:
                try:
                    entity_type = row["实体类型"]
                    layer = row["图层"]
                    color = handle_color(row["颜色"])
                    linetype = row["线型"]
                    lineweight = int(row["线宽"])
                    if entity_type == 'LINE':
                        handle_line(row, msp, layer, color, linetype, lineweight, input_file, line_num)
                    elif entity_type == 'CIRCLE':
                        handle_circle(row, msp, layer, color, linetype, lineweight, input_file, line_num)
                    elif entity_type == 'LWPOLYLINE':
                        handle_lwpolyline(row, msp, layer, color, linetype, lineweight, input_file, line_num)
                    elif entity_type == 'DIMENSION':
                        handle_dimension(row, msp, layer, color, linetype, lineweight, input_file, line_num)
                    elif entity_type == 'ARC':
                        handle_arc(row, msp, layer, color, linetype, lineweight, input_file, line_num)
                    elif entity_type in ['TEXT', 'MTEXT']:
                        handle_text(row, msp, layer, color, input_file, entity_type, line_num)
                    elif entity_type == 'HATCH':
                        handle_hatch(row, msp, layer, color, input_file, line_num)
                except Exception as e:
                    messagebox.showwarning("警告", f"文件 {input_file} 第 {line_num} 行发生未知错误: {str(e)}，将略过此数据。")
                    logging.warning(f"文件 {input_file} 第 {line_num} 行发生未知错误: {str(e)}，将略过此数据。")


# 绘制块函数
def handle_insert(data, row, msp, doc, layer, color, linetype, lineweight, input_file):
    # 读取块名
    block_name = row["块名"].split(": ")[1]
    # 创建块
    block = doc.blocks.new(name=block_name)
    # 块添加实体
    block_add_virtual_entities(data, block, block_name, input_file)
    # 根据块引用添加块
    block_location = (float(row["位置 X"]), float(row["位置 Y"]))
    try:
        block_rotation = float(row["角度"])
    except ValueError:
        block_rotation = 0
    msp.add_blockref(block_name, block_location, dxfattribs={"layer": layer, "color": color,
                                                             "linetype": linetype, "lineweight": lineweight,
                                                             'rotation': block_rotation})


# csv转dxf主函数
def csv_to_dxf(input_file, output_file):
    try:
        # 创建一个新的 DXF 文档
        doc = ezdxf.new("R2018")
        msp = doc.modelspace()
        # 创建自定义尺寸样式
        dimstyle = doc.dimstyles.new("CUSTOM_DIMSTYLE", dxfattribs={
            "dimtxt": 3.5,  # 尺寸文字高度
            "dimclrd": 3,  # 尺寸文字颜色
            "dimasz": 5,  # 箭头大小
            "dimtad": 1,  # 文字垂直位置
            "dimjust": 0,  # 文字水平位置
            "dimlwd": 0.25,  # 尺寸线线宽
            "dimexo": 0,  # 尺寸界线超出尺寸线的距离
            "dimscale": global_scale_factor,  # 全局比例因子
            "dimalt": 0,  # 禁用换算单位
            "dimadec": 3,  # 换算单位小数位数
            "dimdsep": ord('.')
        })

        layer_dict = {}

        with open(input_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)

        # 第一次遍历整个csv表格
        for line_num, row in enumerate(data, start=2):  # 从第 2 行开始计数
            line_num -= 1
            # 首先读取图层信息
            if row["实体类型"] == "图层":
                layer = row["图层"]
                color = handle_color(row["颜色"])
                linetype = row["线型"]
                lineweight = int(row["线宽"])
                linetype_description = row["线型描述"]
                linetype_pattern_str = row["线型图案"]
                linetype_pattern = handle_linetype_pattern(linetype_pattern_str, linetype, input_file, layer)
                create_layer(doc, layer, color, linetype, lineweight, linetype_description, linetype_pattern,
                             input_file)
                layer_dict[layer] = (color, linetype, lineweight)
            # 读取非块元素
            elif not row["块名"]:
                try:
                    entity_type = row["实体类型"]
                    layer = row["图层"]
                    color = handle_color(row["颜色"])
                    linetype = row["线型"]
                    lineweight = int(row["线宽"])

                    if entity_type == 'LINE':
                        handle_line(row, msp, layer, color, linetype, lineweight, input_file, line_num)
                    elif entity_type == 'CIRCLE':
                        handle_circle(row, msp, layer, color, linetype, lineweight, input_file, line_num)
                    elif entity_type == 'LWPOLYLINE':
                        handle_lwpolyline(row, msp, layer, color, linetype, lineweight, input_file, line_num)
                    elif entity_type == 'DIMENSION':
                        handle_dimension(row, msp, layer, color, linetype, lineweight, input_file, line_num)
                    elif entity_type == 'ARC':
                        handle_arc(row, msp, layer, color, linetype, lineweight, input_file, line_num)
                    elif entity_type in ['TEXT', 'MTEXT']:
                        handle_text(row, msp, layer, color, input_file, entity_type, line_num)
                    elif entity_type == 'HATCH':
                        handle_hatch(row, msp, layer, color, input_file, line_num)
                except Exception as e:
                    messagebox.showwarning("警告", f"文件 {input_file} 第 {line_num} 行发生未知错误: {str(e)}，将略过此数据。")
                    logging.warning(f"文件 {input_file} 第 {line_num} 行发生未知错误: {str(e)}，将略过此数据。")
            # 读取块元素
            elif row["实体类型"] == 'INSERT':
                try:
                    layer = row["图层"]
                    color = handle_color(row["颜色"])
                    linetype = row["线型"]
                    lineweight = int(row["线宽"])
                    handle_insert(data, row, msp, doc, layer, color, linetype, lineweight, input_file)

                except Exception as e:
                    messagebox.showwarning("警告", f"文件 {input_file} 第 {line_num} 行发生未知错误: {str(e)}，将略过此数据。")
                    logging.warning(f"文件 {input_file} 第 {line_num} 行发生未知错误: {str(e)}，将略过此数据。")

        # 保存 DXF 文件
        doc.saveas(output_file)
        messagebox.showinfo("成功", f"图纸生成成功！已保存到 {output_file}")
        logging.info(f"{input_file} 已成功转换为 {output_file} (CSV to DXF)")
    except FileNotFoundError:
        messagebox.showerror("错误", f"文件 {input_file} 未找到")
        logging.error(f"文件 {input_file} 未找到")
    except Exception as e:
        messagebox.showerror("错误", f"发生未知错误: {str(e)}")
        logging.error(f"发生未知错误: {str(e)}")

