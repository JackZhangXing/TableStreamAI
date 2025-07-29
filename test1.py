# main.py 顶部添加
import tool
print(f"tool 模块路径: {tool.__file__}")  # 验证路径是否正确

# 尝试导入子模块
try:
    from tool.context_locals import app, local
    print("context_locals 导入成功!")
except ImportError as e:
    print(f"导入失败: {e}")
    # 显示所有可用子模块
    print(f"tool 包内容: {dir(tool)}")

