import sys
import os

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将当前文件所在目录添加到Python路径
sys.path.insert(0, current_dir)

# 设置工作目录为当前文件所在目录
os.chdir(current_dir)

# 导入client模块
from client import main

# 运行客户端
if __name__ == "__main__":
    main()