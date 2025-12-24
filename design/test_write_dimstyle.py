import sys
import os
import csv

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import ezdxf
import json
import logging
import tkinter.messagebox as messagebox

# 设置日志
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# 从dxf_to_csv.py导入函数
from dxf_to_csv import write_dimstyle_info

try:
    # 打开测试DXF文件
    input_file = "d:/Python/CAD-change/design/data/十一.dxf"
    output_file = "d:/Python/CAD-change/design/data/test_dimstyle_output.csv"
    
    print(f"测试DXF文件: {input_file}")
    print(f"输出CSV文件: {output_file}")
    
    # 读取DXF文件
    doc = ezdxf.readfile(input_file)
    print(f"成功打开DXF文件，模型空间有 {len(doc.modelspace())} 个实体")
    
    # 准备CSV字段名
    fieldnames = [
        '实体类型', '图层', '颜色', '线型', '线宽', '线型描述', '线型图案',
        '类型/名称', '块名', '值', '覆盖值', '位置 X', '位置 Y', '起点 X', '起点 Y', '终点 X', '终点 Y',
        '圆心 X', '圆心 Y', '半径', '顶点数据', '闭合', '高度', '角度', '尺寸编码',
        '起始角度', '终止角度', '缩放比例', '尺寸样式'
    ]
    
    # 写入CSV文件
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # 测试write_dimstyle_info函数
        print("\n开始写入dimstyle信息...")
        write_dimstyle_info(doc, writer)
        print("写入dimstyle信息完成")
    
    print(f"\n测试完成！输出文件: {output_file}")
    
    # 读取并显示输出文件内容
    print("\n输出文件内容:")
    with open(output_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row)
            
except Exception as e:
    print(f"发生错误: {str(e)}")
    import traceback
    traceback.print_exc()
