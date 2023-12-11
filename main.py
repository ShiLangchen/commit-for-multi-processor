#首先，确保你已经安装了gitpython库，可以使用以下命令进行安装：
# pip install gitpython

import git
import subprocess
import os
import json

def clone_repo(repo_url, destination):
    try:
        git.Repo.clone_from(repo_url, destination)
        return True
    except git.exc.GitCommandError as e:
        print(f"Error cloning repository: {e}")
        return False

def run_analysis_exe(files_to_analyze, repo_path):
    exe_path = os.path.join(repo_path, "analysis.exe")
    results = {}
    if os.path.exists(exe_path):
        try:
            for file in files_to_analyze:
                file_path = os.path.join(repo_path, file)
                if os.path.exists(file_path):
                    result = subprocess.run([exe_path, file_path], cwd=repo_path, capture_output=True, text=True)
                    results[file] = json.loads(result.stdout)
                else:
                    print(f"File {file} does not exist in the repository")
        except FileNotFoundError:
            print("analysis.exe not found")
    else:
        print("analysis.exe does not exist in the repository")
    return results


def get_changed_files_in_commit(repo, commit):
    diff_index = commit.diff(commit.parents[0] if commit.parents else None)
    # 返回该文件相对根目录的路径/绝对路径
    return [item.a_path for item in diff_index.iter_change_type('M')]


# 输入git仓库地址
git_url = input("请输入Git仓库地址：")

# 克隆仓库到本地
destination_folder = "repo_folder"  # 修改为你想要保存的文件夹名
if clone_repo(git_url, destination_folder):
    print("仓库成功克隆到本地")

    # 找到commit内的全部文件，对每个文件执行
    repo = git.Repo(destination_folder) #打开本地仓库
    commits = list(repo.iter_commits()) #获取提交信息

    all_results = {}

    for commit in commits:
        # 获取commit涉及的文件列表
        changed_files = get_changed_files_in_commit(repo, commit)
        # 运行分析程序
        commit_result = run_analysis_exe(changed_files, destination_folder)

        # 以json文件返回分析结果给后端
        # 合并结果到总结果中
        for file, result in commit_result.items():
            if file not in all_results:
                all_results[file] = []
            # all_results[file].append(result)
            all_results[file].append({f"commit_{commit.hexsha}": result})

#     # 保存结果到JSON文件
#     with open('analysis_results.json', 'w') as outfile:
#         json.dump(all_results, outfile, indent=4)
# else:
#     print("无法克隆仓库")

    # 保存每个文件的JSON结果到单独的文件
    for file, results_list in all_results.items():
        file_results_path = f"{file}_results.json"
        with open(file_results_path, 'w') as outfile:
            json.dump(results_list, outfile, indent=4)
else:
    print("无法克隆仓库")


