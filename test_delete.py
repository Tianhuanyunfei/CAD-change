import requests
import os
import tempfile

# 创建一个临时文件用于测试
temp_file_path = ''
try:
    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as temp_file:
        temp_file.write(b'Test DXF content')
        temp_file_path = temp_file.name
    
    print(f"Created temporary file: {temp_file_path}")
    
    # 测试删除API
    delete_url = 'http://localhost:8000/api/download/delete'
    delete_data = {'filePath': temp_file_path}
    
    print(f"Testing delete API with file: {temp_file_path}")
    response = requests.post(delete_url, json=delete_data)
    
    print(f"Delete API response status: {response.status_code}")
    print(f"Delete API response content: {response.text}")
    
    # 检查文件是否被删除
    if not os.path.exists(temp_file_path):
        print("✓ File was successfully deleted")
    else:
        print("✗ File still exists")
        
    # 测试无效路径的情况
    invalid_path = 'C:\\Windows\\System32\\cmd.exe'
    delete_data_invalid = {'filePath': invalid_path}
    response_invalid = requests.post(delete_url, json=delete_data_invalid)
    print(f"\nTesting delete API with invalid path: {invalid_path}")
    print(f"Delete API response status: {response_invalid.status_code}")
    print(f"Delete API response content: {response_invalid.text}")
    
finally:
    # 确保临时文件被删除
    if temp_file_path and os.path.exists(temp_file_path):
        os.remove(temp_file_path)
        print(f"\nCleaned up temporary file: {temp_file_path}")