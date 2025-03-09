为了设计一个测试用例来验证这个工具，我们需要一个Git仓库，其中包含至少两个提交，它们之间执行同一个脚本会产生不同的结果。以下是测试用例的设计步骤：

测试环境准备
创建一个新的Git仓库，或者使用一个现有的仓库。
准备一个简单的可执行脚本，比如一个Python脚本，它会根据某些条件返回不同的结果。
提交这个脚本到Git仓库。
修改脚本，使它在下一次提交时返回不同的结果。
提交修改后的脚本。
以下是具体的步骤和脚本示例：

步骤1: 创建Git仓库
mkdir test_repo
cd test_repo
git init
步骤2: 创建并提交一个脚本
创建一个名为test_script.py的Python脚本，内容如下：

# test_script.py
print("First version - True")
exit(0)  # 返回码0表示成功，即True
提交这个脚本到Git仓库：

git add test_script.py
git commit -m "Add test script that returns True"
步骤3: 修改脚本并提交
修改test_script.py，使其返回不同的结果：

# test_script.py
print("Second version - False")
exit(1)  # 返回码1表示失败，即False
提交这个修改：

git commit -am "Modify test script to return False"
步骤4: 获取两个提交的哈希值
获取第一个和第二个提交的哈希值：

git log --oneline
假设输出如下：

8a9f8a9 Modify test script to return False
e570c4f Add test script that returns True
步骤5: 运行测试用例
现在我们有两个提交，e570c4f（返回True）和8a9f8a9（返回False）。我们将使用这个工具来查找这两个提交之间的差异。

假设你的Python工具脚本名为find_commit_diff.py，运行以下命令：

python find_commit_diff.py ./test_repo e570c4f 8a9f8a9 ./test_script.py
预期结果
程序应该输出以下内容：

Found commits where the script result changes:
Commit 1: e570c4f
Output of the script on Commit 1:
First version - True

Commit 2: 8a9f8a9
Output of the script on Commit 2:
Second version - False
这个测试用例验证了工具能够正确地找到在两个提交之间脚本执行结果发生变化的点。如果工具输出与预期相符，那么测试用例就通过了。
