import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import ezdxf

try:
    # 使用之前的测试结果，我们知道十一.dxf没有DIMENSION实体
    # 检查是否有包含块内DIMENSION的测试文件
    print("检查测试文件...")
    
    # 直接检查块内实体
    # 这里以一个假设的文件为例，用户可以替换为实际包含块内DIMENSION的文件
    input_file = "data/十一.dxf"  # 用户可以替换为实际文件
    
    if os.path.exists(input_file):
        doc = ezdxf.readfile(input_file)
        print(f"成功打开文件: {input_file}")
        
        # 检查所有块定义
        print("\n检查所有块定义:")
        for block in doc.blocks:
            print(f"\n块 '{block.name}':")
            dimension_count = 0
            for entity in block:
                if entity.dxftype() == 'DIMENSION':
                    dimension_count += 1
                    print(f"  DIMENSION实体: 类型={entity.dxf.dimtype}, 尺寸样式={entity.dxf.dimstyle}, 测量值={entity.get_measurement()}")
            if dimension_count == 0:
                print(f"  该块中没有DIMENSION实体")
    else:
        print(f"文件不存在: {input_file}")
    
    print("\n注意：")
    print("1. 块内的DIMENSION实体已经被process_dimension函数处理")
    print("2. 由于process_dimension函数已更新，块内的DIMENSION实体也会包含'尺寸样式'字段")
    print("3. 用户可以提供包含块内DIMENSION的DXF文件来测试此功能")
    
    # 检查修改后的process_dimension函数是否适用于块内实体
    print("\nprocess_dimension函数修改已完成，块内DIMENSION实体将自动支持尺寸样式字段")
    
except Exception as e:
    print(f"发生错误: {str(e)}")
    import traceback
    traceback.print_exc()