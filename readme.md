# ImgElo

Rank your image collection by clicking the better one. TrueSkill handles the rest.

基于 TrueSkill 算法的图片对比排序工具。

## 快速开始

```bash
# 安装所需依赖
pip install -r requirements.txt

# 首次运行，扫描文件夹
python UI.py --folder "你的图片文件夹路径" --db images.db

# 之后直接用
python UI.py --db images.db
```

支持网络路径：
```bash
python UI.py --folder "\\192.168.x.xx\hardDrive\photos"
```

## 操作方式

- **鼠标点击**：点击你认为更好的图片
- **方向键**：← 选左边 / → 选右边
- **ESC**：退出

## 文件结构

```
sukiaTrueSkill.py   # TrueSkill 算法核心
backend.py          # 数据库封装
UI.py               # 主界面入口
sound/              # 音效资源
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| --db | 数据库路径 | images.db |
| --folder | 首次运行时扫描的文件夹 | - |
| --height | 图片显示高度 | 800 |

## 工作原理

1. 每次展示两张图片，一张来自高不确定性区（需要更多数据），一张来自低不确定性区（已校准的参照）
2. 用户选择后，TrueSkill 算法更新双方评分
3. 多次对比后，图片评分收敛到稳定排名

## License

MIT