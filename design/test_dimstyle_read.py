import dxf_to_csv

# 测试读取dxf文件中的尺寸样式
try:
    input_file = "design/data/十一 copy.dxf"
    output_file = "test_dimstyle_output.csv"
    dxf_to_csv.dxf_to_csv(input_file, output_file)
    print(f"测试完成，输出文件: {output_file}")
    # 读取输出文件，验证尺寸样式字段
    import csv
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        print(f"CSV表头字段: {reader.fieldnames}")
        # 查找包含DIMENSION的行
        print("\nDIMENSION实体及其尺寸样式:")
        found_dimensions = False
        for row in reader:
            if row['实体类型'] == 'DIMENSION':
                found_dimensions = True
                print(f"类型: {row['类型/名称']}, 尺寸样式: {row['尺寸样式']}, 值: {row['值']}")
        if not found_dimensions:
            print("未找到DIMENSION实体")
except Exception as e:
    print(f"测试失败: {str(e)}")
    import traceback
    traceback.print_exc()