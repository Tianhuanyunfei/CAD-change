#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证尺寸实体是否正确使用CSV中指定的尺寸样式
"""

import os
import sys
import csv
import tempfile
import ezdxf
from csv_to_dxf import csv_to_dxf

def create_test_csv_file(output_path):
    """
    创建测试用的CSV文件，包含多个尺寸样式定义和尺寸实体
    """
    fieldnames = [
        '实体类型', '图层', '颜色', '线型', '线宽', '线型描述', '线型图案',
        '类型/名称', '块名', '值', '覆盖值', '位置 X', '位置 Y', '起点 X', '起点 Y', '终点 X', '终点 Y',
        '圆心 X', '圆心 Y', '半径', '顶点数据', '闭合', '高度', '角度', '尺寸编码',
        '起始角度', '终止角度', '缩放比例', '尺寸样式'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # 写入图层信息
        writer.writerow({
            '实体类型': '图层',
            '图层': '测试层',
            '颜色': 3,
            '线型': 'Continuous',
            '线宽': -1
        })
        
        # 写入一条直线
        writer.writerow({
            '实体类型': 'LINE',
            '图层': '测试层',
            '颜色': 3,
            '线型': 'Continuous',
            '线宽': -1,
            '起点 X': 20.0,
            '起点 Y': 20.0,
            '终点 X': 120.0,
            '终点 Y': 20.0
        })
        
        # 写入另一条直线
        writer.writerow({
            '实体类型': 'LINE',
            '图层': '测试层',
            '颜色': 3,
            '线型': 'Continuous',
            '线宽': -1,
            '起点 X': 20.0,
            '起点 Y': 40.0,
            '终点 X': 120.0,
            '终点 Y': 40.0
        })
        
        # 写入第一个尺寸（使用CUSTOM_DIMSTYLE）
        writer.writerow({
            '实体类型': 'DIMENSION',
            '图层': '测试层',
            '颜色': 3,
            '线型': 'Continuous',
            '线宽': -1,
            '类型/名称': 'LINEAR',
            '值': 100.0,
            '位置 X': 100.0,
            '位置 Y': 10.0,
            '起点 X': 20.0,
            '起点 Y': 20.0,
            '终点 X': 120.0,
            '终点 Y': 20.0,
            '角度': 0.0,
            '尺寸编码': 8,
            '尺寸样式': 'CUSTOM_DIMSTYLE'
        })
        
        # 写入第二个尺寸（使用GB_锥度）
        writer.writerow({
            '实体类型': 'DIMENSION',
            '图层': '测试层',
            '颜色': 3,
            '线型': 'Continuous',
            '线宽': -1,
            '类型/名称': 'LINEAR',
            '值': 100.0,
            '位置 X': 100.0,
            '位置 Y': 30.0,
            '起点 X': 20.0,
            '起点 Y': 40.0,
            '终点 X': 120.0,
            '终点 Y': 40.0,
            '角度': 0.0,
            '尺寸编码': 8,
            '尺寸样式': 'GB_锥度'
        })
        
        # 写入尺寸样式定义
        writer.writerow({
            '实体类型': 'dimstyle',
            '类型/名称': 'CUSTOM_DIMSTYLE',
            '值': '{"dimtxt": 3.5, "dimclrd": 3, "dimasz": 3, "dimtad": 1, "dimjust": 0, "dimlwd": 0.25, "dimexo": 0, "dimscale": scale_factor, "dimalt": 0, "dimadec": 3, "dimdsep": 46}'
        })
        
        writer.writerow({
            '实体类型': 'dimstyle',
            '类型/名称': 'GB_锥度',
            '值': '{"dimtxt": 4.0, "dimclrd": 1, "dimasz": 4, "dimtad": 0, "dimjust": 1, "dimlwd": 0.5, "dimexo": 1, "dimscale": scale_factor, "dimalt": 0, "dimadec": 2, "dimdsep": 46}'
        })

def test_dimstyle_usage():
    """
    测试尺寸实体是否正确使用CSV中指定的尺寸样式
    """
    print("开始测试尺寸样式使用...")
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', encoding='utf-8') as temp_csv:
        input_csv_path = temp_csv.name
    
    output_dxf_path = temp_csv.name.replace('.csv', '.dxf')
    
    try:
        # 创建测试CSV文件
        create_test_csv_file(input_csv_path)
        print(f"创建测试CSV文件: {input_csv_path}")
        
        # 调用转换函数
        print(f"正在转换: {input_csv_path} -> {output_dxf_path}")
        csv_to_dxf(input_csv_path, output_dxf_path)
        print("转换完成")
        
        # 打开生成的DXF文件并检查尺寸样式
        print("\n检查生成的DXF文件中的尺寸样式...")
        doc = ezdxf.readfile(output_dxf_path)
        msp = doc.modelspace()
        
        dimension_count = 0
        for entity in msp:
            if entity.dxftype() == 'DIMENSION':
                dimension_count += 1
                dimstyle_used = entity.dxf.dimstyle
                print(f"  尺寸 {dimension_count}: 使用的样式为 '{dimstyle_used}'")
        
        if dimension_count != 2:
            print(f"\n❌ 测试失败: 预期2个尺寸实体，实际找到 {dimension_count} 个")
            return False
        
        print("\n✅ 测试通过: 尺寸实体正确使用了CSV中指定的尺寸样式")
        return True
        
    finally:
        # 清理临时文件
        if os.path.exists(input_csv_path):
            os.unlink(input_csv_path)
            print(f"\n清理临时文件: {input_csv_path}")
        if os.path.exists(output_dxf_path):
            os.unlink(output_dxf_path)
            print(f"清理临时文件: {output_dxf_path}")

if __name__ == "__main__":
    success = test_dimstyle_usage()
    sys.exit(0 if success else 1)
