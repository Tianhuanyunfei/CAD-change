#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证dimstyle信息是否被正确写入到CSV文件的末尾
"""

import os
import sys
import csv
import tempfile
from dxf_to_csv import dxf_to_csv

def test_dimstyle_position(dxf_file_path):
    """
    测试dimstyle信息是否被正确写入到CSV文件的末尾
    
    Args:
        dxf_file_path (str): DXF文件路径
        
    Returns:
        bool: 测试是否通过
    """
    # 创建临时CSV文件
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, encoding='utf-8') as temp_csv:
        output_csv_path = temp_csv.name
    
    try:
        # 调用转换函数
        print(f"正在转换: {dxf_file_path} -> {output_csv_path}")
        dxf_to_csv(dxf_file_path, output_csv_path)
        print("转换完成")
        
        # 读取CSV文件并检查dimstyle位置
        dimstyle_rows = []
        all_rows = []
        
        print("\n读取CSV文件内容...")
        with open(output_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                all_rows.append(row)
                if row.get('实体类型') == 'dimstyle':
                    dimstyle_rows.append(row)
        
        if not dimstyle_rows:
            print("\n❌ 测试失败: CSV文件中没有找到dimstyle信息")
            return False
        
        print(f"\n找到 {len(dimstyle_rows)} 个dimstyle定义")
        
        # 检查dimstyle是否在文件末尾
        has_non_dimstyle_after = False
        in_dimstyle_section = False
        
        for i, row in enumerate(all_rows):
            if row.get('实体类型') == 'dimstyle':
                in_dimstyle_section = True
            elif in_dimstyle_section and row.get('实体类型') != 'dimstyle':
                has_non_dimstyle_after = True
                print(f"\n❌ 测试失败: 在dimstyle定义之后发现非dimstyle行 (行 {i+2})")
                break
        
        if not has_non_dimstyle_after:
            print("\n✅ 测试通过: 所有dimstyle定义都在CSV文件的末尾")
            print("\ndimstyle定义详情:")
            for i, dimstyle_row in enumerate(dimstyle_rows):
                dimstyle_name = dimstyle_row.get('类型/名称', '未知名称')
                dimstyle_value = dimstyle_row.get('值', '无值')
                print(f"  {i+1}. 名称: {dimstyle_name}, 值: {dimstyle_value[:50]}...")
            return True
        else:
            return False
            
    finally:
        # 清理临时文件
        if os.path.exists(output_csv_path):
            os.unlink(output_csv_path)
            print(f"\n清理临时文件: {output_csv_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python test_dimstyle_position.py <dxf文件路径>")
        sys.exit(1)
    
    dxf_file = sys.argv[1]
    if not os.path.exists(dxf_file):
        print(f"错误: DXF文件 '{dxf_file}' 不存在")
        sys.exit(1)
    
    success = test_dimstyle_position(dxf_file)
    sys.exit(0 if success else 1)
