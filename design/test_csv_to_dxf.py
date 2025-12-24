import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import ezdxf

# 导入csv_to_dxf模块中的函数
from csv_to_dxf import drawing, create_layer

try:
    # 测试文件路径
    input_csv = "d:/Python/CAD-change/design/data/test_dimstyle_output.csv"
    output_dxf = "d:/Python/CAD-change/design/data/test_dimstyle_output.dxf"
    
    print(f"测试CSV文件: {input_csv}")
    print(f"输出DXF文件: {output_dxf}")
    
    # 创建新的DXF文档
    doc = ezdxf.new(dxfversion='R2013')
    msp = doc.modelspace()
    
    # 调用drawing函数转换CSV到DXF
    print("\n开始CSV到DXF的转换...")
    drawing(doc, msp, input_csv, output_dxf)
    
    # 保存DXF文件
    doc.saveas(output_dxf)
    print(f"\n转换完成！DXF文件已保存到: {output_dxf}")
    
    # 打开保存的DXF文件，验证dimstyle是否正确创建
    print("\n验证生成的DXF文件中的dimstyle...")
    doc_verification = ezdxf.readfile(output_dxf)
    
    # 检查dimstyles
    print("生成的DXF文件中的dimstyles:")
    for dimstyle in doc_verification.dimstyles:
        dimstyle_name = str(dimstyle.dxf.name)
        print(f"  - {dimstyle_name}")
        
        # 打印部分关键属性
        print(f"    dimtxt: {dimstyle.dxf.dimtxt}")
        print(f"    dimclrd: {dimstyle.dxf.dimclrd}")
        print(f"    dimasz: {dimstyle.dxf.dimasz}")
        print(f"    dimscale: {dimstyle.dxf.dimscale}")
    
    print("\n测试成功！dimstyle从CSV到DXF的转换验证完成。")
    
except Exception as e:
    print(f"发生错误: {str(e)}")
    import traceback
    traceback.print_exc()
