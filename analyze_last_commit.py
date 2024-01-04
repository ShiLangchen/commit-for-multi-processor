import git
import subprocess
import os
import json
import shutil

# https://gitee.com/hribz/ArchReviewer.git

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


def run_ArchReviewer():
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
    source_folder = os.path.join(work_dir, "source")

    if not commit.parents:
        # 在没有父提交的情况下直接获取当前提交的所有文件列表
        changed_files = [item.path for item in commit.tree.traverse() if item.type == 'blob']
        # changed_files = [item.a_path for item in
        #                  commit.diff(commit.parents[0] if commit.parents else None).iter_change_type('M')]

    else:
        # 获取当前提交和父提交之间的差异，找出该次提交修改和新增的文件列表
        diff = commit.diff(commit.parents[0].tree)
        modified_files = [item.a_path for item in diff.iter_change_type('M')]
        added_files = [item.a_path for item in diff.iter_change_type('D')]
        changed_files = modified_files + added_files

    # print("All file has changed in this commit")
    # for file in changed_files:
    #     print(file)

    for file in changed_files:
        try:
            # 使用GitPython检查文件是否存在于当前提交中
            # if file not in commit.tree:
            #     raise FileNotFoundError
            # 使用git show命令获取文件内容并复制到/source文件夹下
            output = subprocess.check_output(['git', 'show', f'{commit.hexsha}:{file}'], cwd=repo_path)
            dest_path = os.path.join(source_folder, file)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            print(f"Copying file {file} successfully")
            with open(dest_path, 'wb') as dest_file:
                dest_file.write(output)
        except subprocess.CalledProcessError as e:
            print(f"Error copying file {file}: {e}")
        # except FileNotFoundError:
        #     print(f"Skipping file {file} as it does not exist in this commit.")

    # 运行ArchReviewer并获取结果
    result = run_ArchReviewer()

    # 列出文件夹中的所有文件和文件夹
    files_in_folder = os.listdir(source_folder)

    # 输出文件列表
    print("Files in source_folder:")
    for file in files_in_folder:
        print(file)

    # 清空/source文件夹
    shutil.rmtree(source_folder)
    os.makedirs(source_folder)

    return result


# 输入git仓库地址
git_url = input("请输入Git仓库地址：")
# 克隆仓库到本地
destination_folder = "repo_folder"  # 修改为你想要保存的文件夹名
# 清空文件夹
if os.path.exists(destination_folder):
    shutil.rmtree(destination_folder)

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
    shutil.rmtree(src_folder)
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
        # all_results[str(commit)] = result
        # 检查结果是否为空
        if result:
            all_results[str(commit)] = result

    # 将结果保存到一个JSON文件中
    with open('all_arch_info_results.json', 'w') as outfile:
        json.dump(all_results, outfile, indent=4)
else:
    print("无法克隆仓库")
