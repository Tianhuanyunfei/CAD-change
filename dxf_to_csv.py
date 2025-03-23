import ezdxf
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import math

# 配置日志记录
logging.basicConfig(filename='dxf_csv_conversion.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 定义尺寸标注类型映射，添加半径尺寸编码映射
DIMTYPE_MAPPING = {
    0: "UNKNOWN",
    1: "LINEAR",
    2: "ALIGNED",
    3: "ANGULAR",
    4: "DIAMETER",
    5: "RADIUS",
    6: "ANGULAR_3P",
    7: "ORDINATE",
    8: "LINEAR_HORIZONTAL",
    9: "LINEAR_VERTICAL",
    10: "LINEAR_ROTATED",
    32: "LINEAR",
    160: "LINEAR",
    163: "DIAMETER",
    35: "DIAMETER",
    164: "RADIUS",
    36: "RADIUS"
}

# 手动定义一些常见线型的图案信息
COMMON_LINETYPE_PATTERNS = {
    "点画线": [21, 12, 2, 5, 2],  # 示例图案，可根据实际调整
    "虚线": [2.0, 1.0, 1.0]  # 示例图案，可根据实际调整
}


def get_linetype_pattern(doc, linetype):
    linetype_obj = doc.linetypes.get(linetype)
    pattern = []
    if linetype_obj:
        try:
            pattern = linetype_obj.dxf.dash_lengths
        except AttributeError:
            if linetype in COMMON_LINETYPE_PATTERNS:
                pattern = COMMON_LINETYPE_PATTERNS[linetype]
            elif linetype == "Continuous":
                pattern = []
            else:
                messagebox.showwarning("警告", f"无法获取线型 {linetype} 的图案信息，将使用空列表代替。")
                logging.warning(f"无法获取线型 {linetype} 的图案信息，将使用空列表代替。")
    return pattern


def write_layer_info(doc, writer):
    for layer in doc.layers:
        linetype = layer.dxf.linetype
        pattern = get_linetype_pattern(doc, linetype)
        linetype_obj = doc.linetypes.get(linetype)
        description = linetype_obj.dxf.description if linetype_obj else ""
        row = {
            "实体类型": "LAYER_INFO",
            "图层": layer.dxf.name,
            "颜色": layer.dxf.color,
            "线型": linetype,
            "线宽": layer.dxf.lineweight,
            "线型描述": description,
            "线型图案": ";".join(map(str, pattern)),
            "起点 X": "", "起点 Y": "",
            "终点 X": "", "终点 Y": "",
            "半径": "", "圆心 X": "", "圆心 Y": "",
            "起始角度": "", "终止角度": "",
            "顶点数据": "",
            "顶点凸起值": "",
            "尺寸标注类型": "", "尺寸值": "",
            "尺寸编码": "",
            "location_X": "", "location_Y": "",
            "尺寸起点_X": "", "尺寸起点_Y": "",
            "尺寸终点_X": "", "尺寸终点_Y": "",
            "尺寸角度": "",
            "defpoint_X": "", "defpoint_Y": "",
            "defpoint2_X": "", "defpoint2_Y": "",
            "defpoint3_X": "", "defpoint3_Y": "",
            "defpoint4_X": "", "defpoint4_Y": "",
            "defpoint5_X": "", "defpoint5_Y": "",
            "文本内容": "", "文本位置 X": "", "文本位置 Y": "", "文本高度": "", "文本旋转角度": "",
            "填充图案名称": "", "填充边界顶点数据": "",
            "填充缩放比例": ""
        }
        writer.writerow(row)


def process_line(entity, row):
    start = entity.dxf.start
    end = entity.dxf.end
    row.update({
        "起点 X": "{:.3f}".format(start[0]),
        "起点 Y": "{:.3f}".format(start[1]),
        "终点 X": "{:.3f}".format(end[0]),
        "终点 Y": "{:.3f}".format(end[1])
    })
    return row


def process_circle(entity, row):
    center = entity.dxf.center
    radius = entity.dxf.radius
    row.update({
        "半径": "{:.3f}".format(radius),
        "圆心 X": "{:.3f}".format(center[0]),
        "圆心 Y": "{:.3f}".format(center[1])
    })
    return row


def process_lwpolyline(entity, row):
    vertices = []
    bulges = []
    for point in entity.get_points(format='xyseb'):
        x, y, start_width, end_width, bulge = point
        vertices.append(
            f"({'{:.3f}'.format(x)}, {'{:.3f}'.format(y)}, {'{:.3f}'.format(start_width)}, {'{:.3f}'.format(end_width)})")
        bulges.append("{:.3f}".format(bulge))
    if entity.closed:
        first_vertex = vertices[0]
        last_vertex = vertices[-1]
        if first_vertex != last_vertex:
            vertices.append(first_vertex)
    row["顶点数据"] = "; ".join(vertices)
    row["顶点凸起值"] = "; ".join(bulges)
    return row


def process_insert(entity, row):
    row["顶点数据"] = f"块名: {entity.dxf.name}"
    return row


def process_dimension(entity, row):
    dimtype_code = entity.dxf.dimtype
    row["尺寸编码"] = str(dimtype_code)
    row["尺寸标注类型"] = DIMTYPE_MAPPING.get(dimtype_code, "UNKNOWN")
    try:
        dim_value = entity.get_measurement()
        row["尺寸值"] = "{:.3f}".format(dim_value)
    except Exception as e:
        row["尺寸值"] = "未知"
        logging.error(f"获取尺寸标注 {entity.dxf.handle} 的尺寸值时出错: {str(e)}")
    defpoint = entity.dxf.defpoint
    defpoint2 = entity.dxf.defpoint2
    defpoint3 = entity.dxf.defpoint3
    try:
        defpoint4 = entity.dxf.defpoint4
    except AttributeError:
        defpoint4 = (0, 0)
    try:
        defpoint5 = entity.dxf.defpoint5
    except AttributeError:
        defpoint5 = (0, 0)
    row["defpoint_X"] = "{:.3f}".format(defpoint[0])
    row["defpoint_Y"] = "{:.3f}".format(defpoint[1])
    row["defpoint2_X"] = "{:.3f}".format(defpoint2[0])
    row["defpoint2_Y"] = "{:.3f}".format(defpoint2[1])
    row["defpoint3_X"] = "{:.3f}".format(defpoint3[0])
    row["defpoint3_Y"] = "{:.3f}".format(defpoint3[1])
    row["defpoint4_X"] = "{:.3f}".format(defpoint4[0])
    row["defpoint4_Y"] = "{:.3f}".format(defpoint4[1])
    row["defpoint5_X"] = "{:.3f}".format(defpoint5[0])
    row["defpoint5_Y"] = "{:.3f}".format(defpoint5[1])
    if row["尺寸标注类型"] in ["LINEAR", "ALIGNED", "LINEAR_HORIZONTAL", "LINEAR_VERTICAL", "LINEAR_ROTATED"]:
        row["location_X"] = "{:.3f}".format(defpoint[0])
        row["location_Y"] = "{:.3f}".format(defpoint[1])
        row["尺寸起点_X"] = "{:.3f}".format(defpoint2[0])
        row["尺寸起点_Y"] = "{:.3f}".format(defpoint2[1])
        row["尺寸终点_X"] = "{:.3f}".format(defpoint3[0])
        row["尺寸终点_Y"] = "{:.3f}".format(defpoint3[1])
        row["尺寸角度"] = "{:.3f}".format(entity.dxf.angle)
    elif row["尺寸标注类型"] == "DIAMETER":
        try:
            center_x = (defpoint[0] + defpoint4[0]) / 2
            center_y = (defpoint[1] + defpoint4[1]) / 2
            row["圆心 X"] = "{:.3f}".format(center_x)
            row["圆心 Y"] = "{:.3f}".format(center_y)
            row["尺寸值"] = "{:.3f}".format(dim_value)
            dx = defpoint4[0] - defpoint[0]
            dy = defpoint4[1] - defpoint[1]
            angle = math.degrees(math.atan2(dy, dx))
            row["尺寸角度"] = "{:.3f}".format(angle)
        except Exception as e:
            logging.error(f"获取直径尺寸标注 {entity.dxf.handle} 的圆心信息或角度信息时出错: {str(e)}")
    elif row["尺寸标注类型"] == "RADIUS":
        try:
            center_x = defpoint[0]
            center_y = defpoint[1]
            row["圆心 X"] = "{:.3f}".format(center_x)
            row["圆心 Y"] = "{:.3f}".format(center_y)
            row["尺寸值"] = "{:.3f}".format(dim_value)
            dx = defpoint4[0] - defpoint[0]
            dy = defpoint4[1] - defpoint[1]
            angle = math.degrees(math.atan2(dy, dx))
            row["尺寸角度"] = "{:.3f}".format(angle)
        except Exception as e:
            logging.error(f"获取半径尺寸标注 {entity.dxf.handle} 的圆心信息或角度信息时出错: {str(e)}")
    if row["尺寸标注类型"] == "UNKNOWN":
        logging.warning(f"发现未知尺寸类型，尺寸编码为 {dimtype_code}，实体句柄为 {entity.dxf.handle}")
    return row


def process_arc(entity, row):
    center = entity.dxf.center
    radius = entity.dxf.radius
    start_angle = entity.dxf.start_angle
    end_angle = entity.dxf.end_angle
    row.update({
        "半径": "{:.3f}".format(radius),
        "圆心 X": "{:.3f}".format(center[0]),
        "圆心 Y": "{:.3f}".format(center[1]),
        "起始角度": "{:.3f}".format(start_angle),
        "终止角度": "{:.3f}".format(end_angle)
    })
    return row


def process_text(entity, row):
    if entity.dxftype() == 'TEXT':
        text_content = entity.dxf.text
        text_location = entity.dxf.insert
        text_height = entity.dxf.height
        text_rotation = entity.dxf.rotation
    else:  # MTEXT
        text_content = entity.text
        text_location = entity.dxf.insert
        text_height = entity.dxf.char_height
        text_rotation = entity.dxf.rotation
    row.update({
        "文本内容": text_content,
        "文本位置 X": "{:.3f}".format(text_location[0]),
        "文本位置 Y": "{:.3f}".format(text_location[1]),
        "文本高度": "{:.3f}".format(text_height),
        "文本旋转角度": "{:.3f}".format(text_rotation)
    })
    return row


def process_hatch(entity, row):
    pattern_name = entity.dxf.pattern_name
    boundary_vertices = []
    bulge_values = []

    def add_vertex(x, y, bulge=0):
        boundary_vertices.append(f"({x:.3f}, {y:.3f}, {bulge:.3f})")


    for path in entity.paths:
        if hasattr(path, 'vertices'):
            for vertex in path.vertices:
                if len(vertex) == 3:
                    x, y, bulge = vertex
                else:
                    x, y = vertex
                    bulge = 0
                add_vertex(x, y, bulge)
        elif hasattr(path, 'edges'):
            for edge in path.edges:
                if hasattr(edge, 'start') and hasattr(edge, 'end'):
                    start = edge.start
                    end = edge.end
                    if len(start) == 3:
                        start_x, start_y, start_bulge = start
                    else:
                        start_x, start_y = start
                        start_bulge = 0
                    if len(end) == 3:
                        end_x, end_y, end_bulge = end
                    else:
                        end_x, end_y = end
                        end_bulge = 0
                    add_vertex(start_x, start_y, start_bulge)
                    add_vertex(end_x, end_y, end_bulge)
                elif hasattr(edge, 'center') and hasattr(edge, 'radius') and hasattr(edge, 'start_angle') and hasattr(
                        edge, 'end_angle'):
                    center = edge.center
                    radius = edge.radius
                    start_angle = edge.start_angle
                    end_angle = edge.end_angle
                    start_x = center[0] + radius * math.cos(math.radians(start_angle))
                    start_y = center[1] + radius * math.sin(math.radians(start_angle))
                    end_x = center[0] + radius * math.cos(math.radians(end_angle))
                    end_y = center[1] + radius * math.sin(math.radians(end_angle))
                    # 根据圆弧的起止角度计算凸起值
                    delta_angle = math.radians(end_angle - start_angle)
                    bulge = math.tan(delta_angle / 4)
                    add_vertex(start_x, start_y, bulge)
                    add_vertex(end_x, end_y)

    row["填充图案名称"] = pattern_name
    row["填充边界顶点数据"] = "; ".join(boundary_vertices)
    try:
        row["填充缩放比例"] = "{:.3f}".format(entity.dxf.pattern_scale)
    except AttributeError:
        row["填充缩放比例"] = "未知"
        logging.warning(f"无法获取 HATCH 实体 {entity.dxf.handle} 的填充缩放比例，将使用 '未知' 代替。")
    return row


def dxf_to_csv(input_file, output_file):
    try:
        doc = ezdxf.readfile(input_file)
        msp = doc.modelspace()
        headers = [
            "实体类型", "图层", "颜色", "线型", "线宽",
            "线型描述", "线型图案",
            "起点 X", "起点 Y",
            "终点 X", "终点 Y",
            "半径", "圆心 X", "圆心 Y",
            "起始角度", "终止角度",
            "顶点数据",
            "顶点凸起值",
            "尺寸标注类型", "尺寸值",
            "尺寸编码",
            "location_X", "location_Y",
            "尺寸起点_X", "尺寸起点_Y",
            "尺寸终点_X", "尺寸终点_Y",
            "尺寸角度",
            "defpoint_X", "defpoint_Y",
            "defpoint2_X", "defpoint2_Y",
            "defpoint3_X", "defpoint3_Y",
            "defpoint4_X", "defpoint4_Y",
            "defpoint5_X", "defpoint5_Y",
            "文本内容", "文本位置 X", "文本位置 Y", "文本高度", "文本旋转角度",
            "填充图案名称", "填充边界顶点数据",
            "填充缩放比例"
        ]

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            write_layer_info(doc, writer)

            for entity in msp:
                layer = entity.dxf.layer
                row = {
                    "实体类型": entity.dxftype(),
                    "图层": layer,
                    "颜色": entity.dxf.color,
                    "线型": entity.dxf.linetype,
                    "线宽": entity.dxf.lineweight,
                    "线型描述": "",
                    "线型图案": "",
                    "起点 X": "", "起点 Y": "",
                    "终点 X": "", "终点 Y": "",
                    "半径": "", "圆心 X": "", "圆心 Y": "",
                    "起始角度": "", "终止角度": "",
                    "顶点数据": "",
                    "顶点凸起值": "",
                    "尺寸标注类型": "", "尺寸值": "",
                    "尺寸编码": "",
                    "location_X": "", "location_Y": "",
                    "尺寸起点_X": "", "尺寸起点_Y": "",
                    "尺寸终点_X": "", "尺寸终点_Y": "",
                    "尺寸角度": "",
                    "defpoint_X": "", "defpoint_Y": "",
                    "defpoint2_X": "", "defpoint2_Y": "",
                    "defpoint3_X": "", "defpoint3_Y": "",
                    "defpoint4_X": "", "defpoint4_Y": "",
                    "defpoint5_X": "", "defpoint5_Y": "",
                    "文本内容": "", "文本位置 X": "", "文本位置 Y": "", "文本高度": "", "文本旋转角度": "",
                    "填充图案名称": "", "填充边界顶点数据": "",
                    "填充缩放比例": ""
                }
                if entity.dxftype() == 'LINE':
                    row = process_line(entity, row)
                elif entity.dxftype() == 'CIRCLE':
                    row = process_circle(entity, row)
                elif entity.dxftype() == 'LWPOLYLINE':
                    row = process_lwpolyline(entity, row)
                elif entity.dxftype() == 'INSERT':
                    row = process_insert(entity, row)
                elif entity.dxftype() == 'DIMENSION':
                    row = process_dimension(entity, row)
                elif entity.dxftype() == 'ARC':
                    row = process_arc(entity, row)
                elif entity.dxftype() in ['TEXT', 'MTEXT']:
                    row = process_text(entity, row)
                elif entity.dxftype() == 'HATCH':
                    row = process_hatch(entity, row)

                writer.writerow(row)
        messagebox.showinfo("成功", f"转换完成！已保存到 {output_file}")
        logging.info(f"{input_file} 已成功转换为 {output_file} (DXF to CSV)")
    except IOError:
        messagebox.showerror("错误", f"文件 {input_file} 未找到或不是有效的 DXF 文件")
        logging.error(f"文件 {input_file} 未找到或不是有效的 DXF 文件")
    except ezdxf.DXFStructureError:
        messagebox.showerror("错误", f"文件 {input_file} 是无效或损坏的 DXF 文件")
        logging.error(f"文件 {input_file} 是无效或损坏的 DXF 文件")

