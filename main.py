from backend import RatingDB

# 初始化数据库
db = RatingDB('my_images.db')

# 扫描文件夹建表
stats = db.init_from_folder(r'\\192.168.2.25\hardDrive\imgEloTest')
print(f"新增 {stats['new']} 张，更新 {stats['updated']} 张")

# 抽取一对图片
img_high_var, img_low_var = db.sample_pair()
print(f"图片1: {img_high_var.path}")
print(f"图片2: {img_low_var.path}")

# 用户选择后更新（假设 img_high_var 赢了）
db.update(winner=img_high_var, loser=img_low_var)

# 查看排名
for img in db.get_ranking():
    print(f"{img.rating.mean:.1f} ± {img.rating.std:.1f}  {img.path}")

# 删除
db.delete(img_high_var.hash)

db.close()