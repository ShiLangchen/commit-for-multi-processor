import git
import subprocess
import os
import json
import shutil

# 记录分析结果目录(不应该将repo_folder作为该目录，
# 否则git仓库原来的source文件夹可能被覆盖掉)
work_dir = os.path.abspath('.') + '/test'
# 分析工具所在目录
arch_reviewer_dir = '/root/ArchReviewer'

def clone_repo(repo_url, destination):
    try:
        git.Repo.clone_from(repo_url, destination)
        return True
    except git.exc.GitCommandError as e:
        print(f"Error cloning repository: {e}")
        return False


def run_ArchReviewer(repo_path):
    # arch_reviewer_command = "ArchReviewer --kind=archinfo --list=" + os.path.abspath('input.txt')
    # result_file = os.path.join(repo_path, "json__ArchReviewer", "arch_info_result.json")
    arch_reviewer_command = "ArchReviewer --kind=archinfo --list=" + os.path.abspath('input.txt')
    result_file = os.path.join(work_dir, "_ArchReviewer", "arch_info_result.json")
    print(result_file)

    try:
        subprocess.run(arch_reviewer_command.split(), cwd=arch_reviewer_dir)
        if os.path.exists(result_file):
            with open(result_file, 'r') as file:
                return json.load(file)
            os.remove(result_file)
    except FileNotFoundError:
        print("ArchReviewer not found")

def handle_commit(repo_path, commit):
    changed_files = [item.a_path for item in commit.diff(commit.parents[0] if commit.parents else None).iter_change_type('M')]
    source_folder = os.path.join(repo_path, "source")

    for file in changed_files:
        # try:
        #     src_path = commit.tree[file].data_stream.path
        #     dest_path = os.path.join(source_folder, file)
        #     os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        #     shutil.copy(src_path, dest_path)
        # except KeyError:
        #     print(f"File {file} was deleted in this commit, skipping copying.")
        try:
            # 使用git show命令获取文件内容并复制到/source文件夹下
            output = subprocess.check_output(['git', 'show', f'{commit.hexsha}:{file}'], cwd=repo_path)
            dest_path = os.path.join(source_folder, file)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, 'wb') as dest_file:
                dest_file.write(output)
        except subprocess.CalledProcessError as e:
            print(f"Error copying file {file}: {e}")


    result = run_ArchReviewer(repo_path)

    shutil.rmtree(source_folder)
    os.makedirs(source_folder)

    return result


# 输入git仓库地址
git_url = input("请输入Git仓库地址：")
# 克隆仓库到本地
destination_folder = "repo_folder"  # 修改为你想要保存的文件夹名
# 清空文件夹
# if os.path.exists(destination_folder):
#     shutil.rmtree(destination_folder)

if clone_repo(git_url, destination_folder):
    print("仓库成功克隆到本地")

    # 新建workdir文件夹和记录workdir路径的文件input.txt
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
        print("work dir created")
    with open('input.txt', 'w') as f:
        f.write(work_dir)

    # 创建/source文件夹用于存放文件
    src_folder = os.path.join(work_dir, "source")
    # shutil.rmtree(src_folder)
    # os.makedirs(src_folder, exist_ok=True)
    os.makedirs(src_folder)

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
