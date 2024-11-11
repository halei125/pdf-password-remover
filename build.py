import os
import sys
import subprocess

def install_requirements():
    """安装所需依赖"""
    requirements = [
        'pikepdf',
        'coloredlogs',
        'pyinstaller'
    ]
    print("正在安装依赖...")
    for package in requirements:
        print(f"安装 {package}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def build_exe():
    """使用PyInstaller编译程序"""
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(current_dir, 'main.py')
    
    # 检查主程序文件是否存在
    if not os.path.exists(main_py):
        raise FileNotFoundError(f"找不到主程序文件: {main_py}")
    
    print(f"主程序文件路径: {main_py}")
    
    command = [
        'pyinstaller',
        '--noconfirm',  # 覆盖输出目录
        '--clean',      # 清理临时文件
        '--windowed',   # Windows下不显示控制台
        '--onefile',    # 打包成单个文件
        '--name=PDF Password Remover',  # 可执行文件名称
        '--hidden-import=pikepdf',
        '--hidden-import=coloredlogs',
        main_py  # 使用完整路径
    ]
    
    # 如果存在图标文件，添加图标
    icon_path = os.path.join(current_dir, 'app.ico')
    if os.path.exists(icon_path):
        command.extend(['--icon', icon_path])
    
    print("开始编译...")
    print("编译命令:", ' '.join(command))
    
    # 切换到当前目录
    os.chdir(current_dir)
    
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        print(f"编译失败: {e}")
        raise
    
def main():
    """主函数"""
    try:
        print("=== PDF密码移除工具编译脚本 ===")
        print("当前工作目录:", os.getcwd())
        
        # 安装依赖
        install_requirements()
        
        # 编译程序
        print("\n开始编译程序...")
        build_exe()
        
        print("\n构建完成！")
        print("可执行文件位于 dist 目录中")
        
    except Exception as e:
        print(f"\n错误: {e}")
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()