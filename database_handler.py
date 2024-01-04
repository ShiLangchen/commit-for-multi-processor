import sqlite3
import json

def save_json_to_db(json_file):
    # 连接数据库
    conn = sqlite3.connect('commits.db')
    cursor = conn.cursor()

    # 创建数据库表
    cursor.execute('''CREATE TABLE IF NOT EXISTS CommitResults (
                        commit_id TEXT PRIMARY KEY,
                        result JSON
                    )''')

    # 读取 JSON 文件并将数据存入数据库
    with open(json_file, 'r') as infile:
        data = json.load(infile)

        for commit_id, result in data.items():
            cursor.execute('INSERT INTO CommitResults (commit_id, result) VALUES (?, ?)',
                           (commit_id, json.dumps(result)))

    # 提交更改并关闭连接
    conn.commit()
    conn.close()

if __name__ == "__main__":
    json_file_path = 'all_arch_info_results.json'
    save_json_to_db(json_file_path)