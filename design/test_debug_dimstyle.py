import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import ezdxf

try:
    # 直接使用ezdxf读取dxf文件，检查尺寸样式
    input_file = "data/十一.dxf"
    doc = ezdxf.readfile(input_file)
    msp = doc.modelspace()
    
    print(f"成功打开DXF文件: {input_file}")
    print(f"文件中实体数量: {len(msp)}")
    
    # 查找DIMENSION实体
    print("\n查找DIMENSION实体...")
    found_dimensions = False
    for entity in msp:
        if entity.dxftype() == 'DIMENSION':
            found_dimensions = True
            print(f"找到DIMENSION实体，类型: {entity.dxf.dimtype}, 尺寸样式: {entity.dxf.dimstyle}")
            break
    
    if not found_dimensions:
        print("未找到DIMENSION实体")
        
    # 检查所有DIMENSION实体
    print("\n所有DIMENSION实体:")
    dimension_count = 0
    for entity in msp:
        if entity.dxftype() == 'DIMENSION':
            dimension_count += 1
            print(f"DIMENSION {dimension_count}: 类型={entity.dxf.dimtype}, 样式={entity.dxf.dimstyle}, 测量值={entity.get_measurement()}")
            
    print(f"\n总共找到 {dimension_count} 个DIMENSION实体")
    
    # 检查dimstyles表
    print("\nDXF文件中的dimstyles:")
    for dimstyle_name in doc.dimstyles:
        print(f"  - {dimstyle_name}")
        
except Exception as e:
    print(f"发生错误: {str(e)}")
    import traceback
    traceback.print_exc()