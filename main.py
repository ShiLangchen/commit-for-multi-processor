#首先，确保你已经安装了gitpython库，可以使用以下命令进行安装：
# pip install gitpython

import git
import subprocess
import os

def clone_repo(repo_url, destination):
    try:
        git.Repo.clone_from(repo_url, destination)
        return True
    except git.exc.GitCommandError as e:
        print(f"Error cloning repository: {e}")
        return False

def run_fenxi_exe(repo_path):
    exe_path = os.path.join(repo_path, "fenxi.exe")
    if os.path.exists(exe_path):
        try:
            subprocess.run([exe_path], cwd=repo_path)
            return True
        except FileNotFoundError:
            print("fenxi.exe not found")
            return False
    else:
        print("fenxi.exe does not exist in the repository")
        return False

# 输入git仓库地址
git_url = input("请输入Git仓库地址：")

# 克隆仓库到本地
destination_folder = "repo_folder"  # 修改为你想要保存的文件夹名
if clone_repo(git_url, destination_folder):
    print("仓库成功克隆到本地")
    # 运行fenxi.exe
    if run_fenxi_exe(destination_folder):
        print("fenxi.exe成功运行")
    else:
        print("无法运行fenxi.exe")
else:
    print("无法克隆仓库")


