import os
import sys
import subprocess

def find_venv():
    venv_path = os.environ.get('PADDLEOCR_VENV')
    if venv_path and os.path.exists(os.path.join(venv_path, 'Scripts', 'python.exe')):
        return venv_path
    
    default_venv = 'D:\\Software\\PaddleOCR_gpu\\venv'
    if os.path.exists(os.path.join(default_venv, 'Scripts', 'python.exe')):
        return default_venv
    
    return None

def is_in_correct_venv():
    venv_path = find_venv()
    if not venv_path:
        return False
    
    current_python = sys.executable
    expected_python = os.path.join(venv_path, 'Scripts', 'python.exe')
    
    return current_python.lower() == expected_python.lower()

def check_ffmpeg(project_dir):
    ffmpeg_path = os.path.join(project_dir, 'bin', 'ffmpeg.exe')
    ffprobe_path = os.path.join(project_dir, 'bin', 'ffprobe.exe')
    
    results = []
    results.append(('ffmpeg.exe', ffmpeg_path, os.path.exists(ffmpeg_path)))
    results.append(('ffprobe.exe', ffprobe_path, os.path.exists(ffprobe_path)))
    
    return all(r[2] for r in results), results

def show_env_error():
    print('=' * 70, file=sys.stderr)
    print('                    环境检测失败', file=sys.stderr)
    print('=' * 70, file=sys.stderr)
    print('', file=sys.stderr)
    print('【问题原因】', file=sys.stderr)
    print('  无法找到 PaddleOCR GPU 虚拟环境', file=sys.stderr)
    print('', file=sys.stderr)
    print('【搜索过的路径】', file=sys.stderr)
    
    paths = [
        ('环境变量 PADDLEOCR_VENV', os.environ.get('PADDLEOCR_VENV', '(未设置)')),
        ('默认路径', 'D:\\Software\\PaddleOCR_gpu\\venv'),
    ]
    
    for name, path in paths:
        exists = '✓ 存在' if os.path.exists(path) else '✗ 不存在'
        print(f'  {name}: {path} [{exists}]', file=sys.stderr)
    
    print('', file=sys.stderr)
    print('【缺失的关键文件】', file=sys.stderr)
    print('  需要找到: venv\\Scripts\\python.exe', file=sys.stderr)
    print('  需要安装的依赖: PyQt5, paddleocr, paddlepaddle-gpu', file=sys.stderr)
    print('', file=sys.stderr)
    print('【解决方案】', file=sys.stderr)
    print('  方法1: 设置环境变量', file=sys.stderr)
    print('    $env:PADDLEOCR_VENV = "你的虚拟环境路径"', file=sys.stderr)
    print('', file=sys.stderr)
    print('  方法2: 重新安装 PaddleOCR GPU 环境', file=sys.stderr)
    print('    参考文档: docs/外部依赖说明.md', file=sys.stderr)
    print('', file=sys.stderr)
    print('=' * 70, file=sys.stderr)

def show_ffmpeg_error(results):
    print('=' * 70, file=sys.stderr)
    print('                   FFmpeg 检测失败', file=sys.stderr)
    print('=' * 70, file=sys.stderr)
    print('', file=sys.stderr)
    print('【问题原因】', file=sys.stderr)
    print('  缺少 FFmpeg 工具，无法进行视频处理', file=sys.stderr)
    print('', file=sys.stderr)
    print('【检测结果】', file=sys.stderr)
    
    for name, path, exists in results:
        status = '✓ 存在' if exists else '✗ 缺失'
        print(f'  {name}: {path} [{status}]', file=sys.stderr)
    
    print('', file=sys.stderr)
    print('【解决方案】', file=sys.stderr)
    print('  1. 下载 FFmpeg: https://ffmpeg.org/download.html', file=sys.stderr)
    print('  2. 解压后将 ffmpeg.exe 和 ffprobe.exe 放入:', file=sys.stderr)
    print('     D:\\Users\\liket\\Desktop\\AVT\\AVT_Subtitle_Processor\\bin\\', file=sys.stderr)
    print('', file=sys.stderr)
    print('=' * 70, file=sys.stderr)

def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    print('【启动检查】正在检测运行环境...')
    
    ffmpeg_ok, ffmpeg_results = check_ffmpeg(project_dir)
    if not ffmpeg_ok:
        show_ffmpeg_error(ffmpeg_results)
        input('\n按 Enter 键退出...')
        sys.exit(1)
    
    print('  ✓ FFmpeg 工具检测通过')
    
    if is_in_correct_venv():
        print('  ✓ 虚拟环境检测通过')
        sys.path.insert(0, project_dir)
        from main import main as app_main
        sys.exit(app_main())
    else:
        venv_path = find_venv()
        if not venv_path:
            show_env_error()
            input('\n按 Enter 键退出...')
            sys.exit(1)
        
        print('  ✓ 虚拟环境检测通过')
        venv_python = os.path.join(venv_path, 'Scripts', 'python.exe')
        print(f'【启动应用】使用虚拟环境: {venv_python}')
        
        result = subprocess.run([venv_python, 'main.py'], cwd=project_dir)
        sys.exit(result.returncode)

if __name__ == '__main__':
    main()