import sqlite3 as sq3

# test_trueskill.py
from sukiaTrueSkill import Rating, match1v1

def show(name, r):
    print(f"  {name}: μ={r.mean:.2f}, σ={r.std:.2f}")

# 测试1: 势均力敌
print("=== 势均力敌，a 赢 ===")
a, b = Rating(), Rating()
print("Before:")
show("a", a)
show("b", b)
a, b = match1v1(a, b)
print("After:")
show("a", a)
show("b", b)

# 测试2: 强者赢弱者（不意外，小更新）
print("\n=== 强者赢弱者 ===")
strong = Rating(mean=35, sigma=4)
weak = Rating(mean=15, sigma=4)
print("Before:")
show("strong", strong)
show("weak", weak)
strong, weak = match1v1(strong, weak)
print("After:")
show("strong", strong)
show("weak", weak)

# 测试3: 弱者爆冷（大更新）
print("\n=== 弱者爆冷 ===")
strong = Rating(mean=35, sigma=4)
weak = Rating(mean=15, sigma=4)
print("Before:")
show("strong", strong)
show("weak", weak)
weak, strong = match1v1(weak, strong)  # weak 赢了
print("After:")
show("strong", strong)
show("weak", weak)

# 测试4: 连续比赛看收敛
print("\n=== 10 连胜 ===")
a, b = Rating(), Rating()
for i in range(10):
    a, b = match1v1(a, b)
    print(f"Round {i+1}: a={a.mean:.2f}±{a.std:.2f}, b={b.mean:.2f}±{b.std:.2f}")