import git
import subprocess
import os
import json
import shutil


def clone_repo(repo_url, destination):
    try:
        git.Repo.clone_from(repo_url, destination)
        return True
    except git.exc.GitCommandError as e:
        print(f"Error cloning repository: {e}")
        return False


def run_ArchReviewer(repo_path):
    arch_reviewer_command = "ArchReviewer --kind=archinfo"
    result_file = os.path.join(repo_path, "json__ArchReviewer", "arch_info_result.json")

    try:
        subprocess.run(arch_reviewer_command.split(), cwd=repo_path)
        if os.path.exists(result_file):
            with open(result_file, 'r') as file:
                return json.load(file)
            os.remove(result_file)
    except FileNotFoundError:
        print("ArchReviewer not found")


def handle_commit(repo_path, commit):
    changed_files = [item.a_path for item in
                     commit.diff(commit.parents[0] if commit.parents else None).iter_change_type('M')]
    source_folder = os.path.join(repo_path, "source")

    # 将commit涉及到的文件复制到/source文件夹下
    for file in changed_files:
        src_path = os.path.join(repo_path, file)
        dest_path = os.path.join(source_folder, file)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy(src_path, dest_path)

    # 运行ArchReviewer并获取结果
    result = run_ArchReviewer(repo_path)

    # 清空/source文件夹
    shutil.rmtree(source_folder)
    os.makedirs(source_folder)

    return result


# 输入git仓库地址
git_url = input("请输入Git仓库地址：")

# 克隆仓库到本地
destination_folder = "repo_folder"  # 修改为你想要保存的文件夹名
if clone_repo(git_url, destination_folder):
    print("仓库成功克隆到本地")
    # 打开克隆的仓库
    repo = git.Repo(destination_folder)
    # 获取所有commits
    commits = list(repo.iter_commits())

    all_results = {}
    for commit in commits:
        # 处理每个commit
        result = handle_commit(destination_folder, commit)
        # 存储结果
        all_results[str(commit)] = result

    # 将结果保存到一个JSON文件中
    with open('all_arch_info_results.json', 'w') as outfile:
        json.dump(all_results, outfile, indent=4)
else:
    print("无法克隆仓库")
