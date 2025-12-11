# imgElo - 你的个人审美炼丹炉 

**imgElo** 是一个基于 Python 和 Gradio 的本地化图像美学评分工具。

它不让你打分（1-10分），而是让你做选择题（A/B）。通过无数次 **1v1 竞技 (Elo Rating)**，系统会精准地计算出你眼中每一张图片的“段位”。它是构建高质量、个性化 Stable Diffusion 训练集的神器。

## ✨ 核心特性

* **⚖️ 科学的 Elo 算法**：抛弃主观打分，使用竞技排名逻辑，解决“审美漂移”问题。
* **🎯 主动学习策略**：系统会自动计算分数的“稳定性”。已定型的图片会退居幕后，系统会优先推送那些“争议很大”或“未定级”的图片让你评判。
* **🎹 键盘流操作**：支持 `←` 左选、`→` 右选，手指不离键盘，体验如切菜般丝滑。
* **↩️ 后悔药机制**：内置有限步数的撤销功能，手滑点错随时回滚。
* **🚀 极简架构**：基于 Gradio + SQLite，无需安装复杂数据库，即开即用。
* **🚀 基于TrueSkill的评分系统**：可以在10次比赛内快速鉴定出某张图片的准确水平

## 🛠️ 安装指南

确保你的电脑上安装了 Python 3.8+。

1.  **克隆或下载本项目**
    ```bash
    git clone [https://github.com/yourname/imgElo.git](https://github.com/yourname/imgElo.git)
    cd imgElo
    ```

2.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```
    *(注：核心依赖仅需 `gradio`)*

## 📖 使用说明

### 1. 准备图片
打开 `config.py` 文件，修改 `IMAGE_DIR` 变量，指向你存放图片的文件夹路径。
```python
# config.py
IMAGE_DIR = r"C:\My_Datasets\Best_Waifu_Images"
````

### 2\. 启动程序

运行以下命令启动 Web 界面：

```bash
python main.py
```

程序启动后，会自动扫描文件夹并将新图片加入数据库（初始分 1200）。

### 3\. 开始“炼丹”

打开浏览器访问终端显示的地址（通常是 `http://127.0.0.1:7860`）。

  * **操作方式**：
      * 觉得左边好看：按 **`←` (左箭头)** 或点击左侧按钮。
      * 觉得右边好看：按 **`→` (右箭头)** 或点击右侧按钮。
      * 撤销上一步：点击页面下方的 **Undo** 按钮。
  * **注意**：每次投票后，**左右两张图都会刷新**，确保你每次面对的都是全新的对比。

## 📂 数据结构

所有数据存储在 `data/elo.db` SQLite 数据库中。

  * **images 表**：存储图片路径、当前 Elo 分数、比赛场次、稳定性指数。
  * **matches 表**：存储最近 N 场（可配置）的对战记录，用于撤销操作。

## 🤝 贡献与扩展

如果你想导出高分图片用于训练 LoRA：
可以编写简单的 Python 脚本读取 `elo.db`：

```python
import sqlite3
import shutil

conn = sqlite3.connect('data/elo.db')
# 导出前 100 名的高分图
top_images = conn.execute("SELECT file_path FROM images ORDER BY score DESC LIMIT 100").fetchall()
for img in top_images:
    shutil.copy(img[0], "output/best_images/")
```

## 📄 License

MIT License
