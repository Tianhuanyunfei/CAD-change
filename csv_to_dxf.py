import ezdxf
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import logging

# 配置日志记录
logging.basicConfig(filename='dxf_csv_conversion.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def handle_color(color):
    if color == 'BYLAYER':
        return 256
    try:
        return int(color)
    except ValueError:
        return 256


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


def handle_line(row, msp, layer, color, input_file):
    try:
        start = (float(row["起点 X"]), float(row["起点 Y"]))
        end = (float(row["终点 X"]), float(row["终点 Y"]))
        msp.add_line(start, end, dxfattribs={"layer": layer, "color": color})
    except ValueError:
        messagebox.showwarning("警告",
                               f"文件 {input_file} 第 {row.line_num} 行的 LINE 实体坐标字段包含无效数据，将略过此数据。")
        logging.warning(f"文件 {input_file} 第 {row.line_num} 行的 LINE 实体坐标字段包含无效数据，将略过此数据。")


def handle_circle(row, msp, layer, color, input_file):
    try:
        center = (float(row["圆心 X"]), float(row["圆心 Y"]))
        radius = float(row["半径"])
        msp.add_circle(center, radius, dxfattribs={"layer": layer, "color": color})
    except ValueError:
        messagebox.showwarning("警告",
                               f"文件 {input_file} 第 {row.line_num} 行的 CIRCLE 实体坐标或半径字段包含无效数据，将略过此数据。")
        logging.warning(f"文件 {input_file} 第 {row.line_num} 行的 CIRCLE 实体坐标或半径字段包含无效数据，将略过此数据。")


def handle_lwpolyline(row, msp, layer, color, input_file):
    vertices = []
    bulges = []
    points = row["顶点数据"].split("; ")
    bulge_values = row["顶点凸起值"].split("; ")
    if len(points) != len(bulge_values) + 1:
        min_len = min(len(points), len(bulge_values) + 1)
        points = points[:min_len]
        bulge_values = bulge_values[:min_len - 1]
    for point, bulge in zip(points[:-1], bulge_values):
        try:
            x, y, start_width, end_width = point.strip("()").split(", ")
            vertices.append(
                (float(x), float(y), float(start_width), float(end_width), float(bulge)))
        except ValueError:
            messagebox.showwarning("警告",
                                   f"文件 {input_file} 第 {row.line_num} 行的 LWPOLYLINE 实体顶点数据或凸起值包含无效数据，将略过此数据。")
            logging.warning(
                f"文件 {input_file} 第 {row.line_num} 行的 LWPOLYLINE 实体顶点数据或凸起值包含无效数据，将略过此数据。")
            vertices = []
            break
    if vertices:
        x, y, start_width, end_width = points[-1].strip("()").split(", ")
        vertices.append((float(x), float(y), float(start_width), float(end_width), 0))
    if vertices:
        msp.add_lwpolyline(vertices, dxfattribs={"layer": layer, "color": color})


def handle_insert(row, msp, layer, color):
    block_name = row["顶点数据"].split(": ")[1]
    msp.add_blockref(block_name, (0, 0), dxfattribs={"layer": layer, "color": color})


def handle_dimension(row, msp, layer, color, input_file):
    dim_type = row["尺寸标注类型"]
    try:
        dim_value = float(row["尺寸值"])
    except ValueError:
        messagebox.showwarning("警告",
                               f"文件 {input_file} 第 {row.line_num} 行的 DIMENSION 实体尺寸值字段包含无效数据，将略过此数据。")
        logging.warning(f"文件 {input_file} 第 {row.line_num} 行的 DIMENSION 实体尺寸值字段包含无效数据，将略过此数据。")
        return
    dim_code = row["尺寸编码"]
    try:
        dim_angle = float(row["尺寸角度"])
    except ValueError:
        messagebox.showwarning("警告",
                               f"文件 {input_file} 第 {row.line_num} 行的 DIMENSION 实体角度字段包含无效数据，将使用默认值 0。")
        logging.warning(f"文件 {input_file} 第 {row.line_num} 行的 DIMENSION 实体角度字段包含无效数据，将使用默认值 0。")
        dim_angle = 0
    if dim_type == "UNKNOWN":
        messagebox.showwarning("警告", f"第 {row.line_num} 行的尺寸标注类型未知，尺寸编码为 {dim_code}，将略过此尺寸。")
        logging.warning(f"第 {row.line_num} 行的尺寸标注类型未知，尺寸编码为 {dim_code}，将略过此尺寸。")
        return
    if dim_type in ["LINEAR", "ALIGNED", "LINEAR_HORIZONTAL", "LINEAR_VERTICAL",
                    "LINEAR_ROTATED"]:
        try:
            location = (float(row["location_X"]), float(row["location_Y"]))
            p1 = (float(row["尺寸起点_X"]), float(row["尺寸起点_Y"]))
            p2 = (float(row["尺寸终点_X"]), float(row["尺寸终点_Y"]))
            dim = msp.add_linear_dim(
                base=location,
                p1=p1,
                p2=p2,
                dimstyle="CUSTOM_DIMSTYLE",
                dxfattribs={"layer": layer, "color": color},
                angle=dim_angle
            )
            dim.render()
        except ValueError:
            messagebox.showwarning("警告",
                                   f"文件 {input_file} 第 {row.line_num} 行的 DIMENSION 实体线性尺寸坐标字段包含无效数据，将略过此数据。")
            logging.warning(
                f"文件 {input_file} 第 {row.line_num} 行的 DIMENSION 实体线性尺寸坐标字段包含无效数据，将略过此数据。")
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
                dxfattribs={"layer": layer, "color": color}
            )
            dim.render()
        except ValueError:
            messagebox.showwarning("警告",
                                   f"文件 {input_file} 第 {row.line_num} 行的 DIMENSION 实体角度尺寸坐标字段包含无效数据，将略过此数据。")
            logging.warning(
                f"文件 {input_file} 第 {row.line_num} 行的 DIMENSION 实体角度尺寸坐标字段包含无效数据，将略过此数据。")
    elif dim_type == 'DIAMETER':
        try:
            center = (float(row["圆心 X"]), float(row["圆心 Y"]))
            radius = dim_value / 2
            dim = msp.add_diameter_dim(
                center=center,
                radius=radius,
                angle=dim_angle,
                dimstyle="CUSTOM_DIMSTYLE",
                dxfattribs={"layer": layer, "color": color}
            )
            dim.render()
        except ValueError:
            messagebox.showwarning("警告",
                                   f"文件 {input_file} 第 {row.line_num} 行的 DIMENSION 实体直径尺寸坐标或值字段包含无效数据，将略过此数据。")
            logging.warning(
                f"文件 {input_file} 第 {row.line_num} 行的 DIMENSION 实体直径尺寸坐标或值字段包含无效数据，将略过此数据。")
    elif dim_type == 'RADIUS':
        try:
            center = (float(row["圆心 X"]), float(row["圆心 Y"]))
            radius = dim_value
            dim = msp.add_radius_dim(
                center=center,
                radius=radius,
                angle=dim_angle,
                dimstyle="CUSTOM_DIMSTYLE",
                dxfattribs={"layer": layer, "color": color}
            )
            dim.render()
        except ValueError:
            messagebox.showwarning("警告",
                                   f"文件 {input_file} 第 {row.line_num} 行的 DIMENSION 实体半径尺寸坐标或值字段包含无效数据，将略过此数据。")
            logging.warning(
                f"文件 {input_file} 第 {row.line_num} 行的 DIMENSION 实体半径尺寸坐标或值字段包含无效数据，将略过此数据。")


def handle_arc(row, msp, layer, color, input_file):
    try:
        center = (float(row["圆心 X"]), float(row["圆心 Y"]))
        radius = float(row["半径"])
        start_angle = float(row["起始角度"])
        end_angle = float(row["终止角度"])
        msp.add_arc(center, radius, start_angle, end_angle, dxfattribs={"layer": layer, "color": color})
    except ValueError:
        messagebox.showwarning("警告",
                               f"文件 {input_file} 第 {row.line_num} 行的 ARC 实体坐标、半径或角度字段包含无效数据，将略过此数据。")
        logging.warning(f"文件 {input_file} 第 {row.line_num} 行的 ARC 实体坐标、半径或角度字段包含无效数据，将略过此数据。")


def handle_text(row, msp, layer, color, input_file, entity_type):
    try:
        text_content = row["文本内容"]
        text_location = (float(row["文本位置 X"]), float(row["文本位置 Y"]))
        text_height = float(row["文本高度"])
        text_rotation = float(row["文本旋转角度"])
        if entity_type == 'TEXT':
            msp.add_text(
                text_content,
                dxfattribs={
                    "layer": layer,
                    "height": text_height,
                    "rotation": text_rotation,
                    "color": color
                }
            ).set_pos(text_location)
        else:  # MTEXT
            msp.add_mtext(
                text_content,
                dxfattribs={
                    "layer": layer,
                    "char_height": text_height,
                    "rotation": text_rotation,
                    "color": color
                }
            ).set_location(text_location)
    except ValueError:
        messagebox.showwarning("警告",
                               f"文件 {input_file} 第 {row.line_num} 行的 {entity_type} 实体文本相关字段包含无效数据，将略过此数据。")
        logging.warning(
            f"文件 {input_file} 第 {row.line_num} 行的 {entity_type} 实体文本相关字段包含无效数据，将略过此数据。")


def handle_hatch(row, msp, layer, color, input_file):
    pattern_name = row["填充图案名称"]
    boundary_vertices_str = row["填充边界顶点数据"]
    scale_str = row.get("填充缩放比例", "1.0")
    try:
        scale = float(scale_str)
    except ValueError:
        messagebox.showwarning("警告",
                               f"文件 {input_file} 第 {row.line_num} 行的 HATCH 实体缩放比例字段 '{scale_str}' 不是有效的数字，将使用默认值 1.0。")
        logging.warning(
            f"文件 {input_file} 第 {row.line_num} 行的 HATCH 实体缩放比例字段 '{scale_str}' 不是有效的数字，将使用默认值 1.0。")
        scale = 1.0
    if not boundary_vertices_str:
        return
    boundary_vertices = []
    vertex_strs = boundary_vertices_str.split("; ")
    for vertex_str in vertex_strs:
        try:
            # 处理三元数组数据，假设格式为 (x, y, bulge)
            x, y, bulge = vertex_str.strip("()").split(", ")
            vertex = (float(x), float(y), float(bulge))
            boundary_vertices.append(vertex)
        except ValueError:
            messagebox.showwarning("警告",
                                   f"文件 {input_file} 第 {row.line_num} 行的 HATCH 实体边界顶点数据包含无效数据，将略过此数据。")
            logging.warning(
                f"文件 {input_file} 第 {row.line_num} 行的 HATCH 实体边界顶点数据包含无效数据，将略过此数据。")
            boundary_vertices = []
            break
    if boundary_vertices:
        hatch = msp.add_hatch(dxfattribs={"layer": layer})
        # 这里假设 ezdxf 支持带 bulge 值的路径
        hatch.paths.add_polyline_path(boundary_vertices, is_closed=True)
        hatch.set_pattern_fill(pattern_name, scale=scale, color=color)


def csv_to_dxf(input_file, output_file):
    try:
        # 创建一个新的 DXF 文档
        doc = ezdxf.new("R2010")
        msp = doc.modelspace()
        # 创建自定义尺寸样式
        dimstyle = doc.dimstyles.new("CUSTOM_DIMSTYLE", dxfattribs={
            "dimtxt": 3.5,
            "dimclrd": 2,
            "dimasz": 2.5
        })

        layer_dict = {}

        with open(input_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["实体类型"] == "LAYER_INFO":
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
                else:
                    try:
                        entity_type = row["实体类型"]
                        layer = row["图层"]
                        color = handle_color(row["颜色"])
                        linetype = row["线型"]
                        lineweight = int(row["线宽"])

                        if entity_type == 'LINE':
                            handle_line(row, msp, layer, color, input_file)
                        elif entity_type == 'CIRCLE':
                            handle_circle(row, msp, layer, color, input_file)
                        elif entity_type == 'LWPOLYLINE':
                            handle_lwpolyline(row, msp, layer, color, input_file)
                        elif entity_type == 'INSERT':
                            handle_insert(row, msp, layer, color)
                        elif entity_type == 'DIMENSION':
                            handle_dimension(row, msp, layer, color, input_file)
                        elif entity_type == 'ARC':
                            handle_arc(row, msp, layer, color, input_file)
                        elif entity_type in ['TEXT', 'MTEXT']:
                            handle_text(row, msp, layer, color, input_file, entity_type)
                        elif entity_type == 'HATCH':
                            handle_hatch(row, msp, layer, color, input_file)

                    except Exception as e:
                        messagebox.showwarning("警告", f"文件 {input_file} 第 {row.line_num} 行发生未知错误: {str(e)}，将略过此数据。")
                        logging.warning(f"文件 {input_file} 第 {row.line_num} 行发生未知错误: {str(e)}，将略过此数据。")

        # 保存 DXF 文件
        doc.saveas(output_file)
        messagebox.showinfo("成功", f"转换完成！已保存到 {output_file}")
        logging.info(f"{input_file} 已成功转换为 {output_file} (CSV to DXF)")
    except FileNotFoundError:
        messagebox.showerror("错误", f"文件 {input_file} 未找到")
        logging.error(f"文件 {input_file} 未找到")
    except Exception as e:
        messagebox.showerror("错误", f"发生未知错误: {str(e)}")
        logging.error(f"发生未知错误: {str(e)}")
