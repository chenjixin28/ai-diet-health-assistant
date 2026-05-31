import pymysql
from datetime import datetime, timedelta

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='', database='ai_diet_health', charset='utf8mb4')
cur = conn.cursor()

cur.execute("SELECT id, username FROM users WHERE username='123'")
row = cur.fetchone()

if not row:
    print("用户 123 不存在")
    conn.close()
    exit()

user_id = row[0]
print(f"找到用户: id={user_id}, username={row[1]}")

foods = ["米饭", "鸡胸肉", "青菜", "苹果", "鸡蛋", "面条"]

for i in range(3):
    day = datetime.now() - timedelta(days=i+1)
    food = foods[i]
    cur.execute(
        "INSERT INTO food_records (user_id, food_name, meal_type, calories, protein, fat, carbohydrates, serving_size, recorded_at, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (user_id, food, "lunch", 300, 15, 10, 30, "约200g", day.strftime("%Y-%m-%d 12:00:00"), day.strftime("%Y-%m-%d 12:00:00"))
    )
    print(f"  已添加: {day.strftime('%Y-%m-%d')} {food}")

conn.commit()
conn.close()
print("完成!")
