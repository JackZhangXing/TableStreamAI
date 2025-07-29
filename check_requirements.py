import importlib.util
import importlib.metadata
from pathlib import Path
import sys
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet

def check_requirements(file_path='requirements.txt', encoding='utf-8'):
    missing_packages = []
    version_mismatches = []
    unparsable_entries = []

    req_file = Path(file_path)
    if not req_file.exists():
        print(f"错误：找不到 {file_path} 文件")
        return

    try:
        with req_file.open('r', encoding=encoding) as f:
            requirements = f.read().splitlines()
    except UnicodeDecodeError:
        print(f"错误：无法以 {encoding} 编码读取文件。尝试其他编码（如 'gbk', 'latin-1'）")
        return
    except Exception as e:
        print(f"读取文件时出错：{e}")
        return

    for line in requirements:
        line = line.strip()
        if not line or line.startswith(('#', '-')):
            continue  # 跳过注释和特殊指令

        try:
            req = Requirement(line)
            package_name = req.name

            # 检查包是否安装
            try:
                importlib.metadata.distribution(package_name)
                installed = True
            except importlib.metadata.PackageNotFoundError:
                installed = False

            if not installed:
                # 尝试标准导入（处理包名与导入名不同的情况）
                try:
                    importlib.util.find_spec(package_name) or __import__(package_name)
                except ImportError:
                    missing_packages.append(line)
                else:
                    print(f"警告：'{package_name}' 通过导入检查，但未在 metadata 中找到。可能名称不匹配。")
            else:
                # 检查版本
                installed_version = importlib.metadata.version(package_name)
                if req.specifier and not req.specifier.contains(installed_version):
                    version_mismatches.append(f"{package_name} 要求 {req.specifier}，但安装的是 {installed_version}")

        except Exception as e:
            unparsable_entries.append(f"{line} (错误: {str(e)})")

    if unparsable_entries:
        print("\n无法解析的依赖项:")
        for entry in unparsable_entries:
            print(f"- {entry}")

    if missing_packages:
        print("\n缺失的包:")
        for pkg in missing_packages:
            print(f"- {pkg}")

    if version_mismatches:
        print("\n版本不匹配:")
        for mismatch in version_mismatches:
            print(f"- {mismatch}")

    if not missing_packages and not version_mismatches and not unparsable_entries:
        print("所有依赖项都已正确安装！")

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'requirements.txt'
    encoding = sys.argv[2] if len(sys.argv) > 2 else 'utf-8'
    check_requirements(file_path, encoding)