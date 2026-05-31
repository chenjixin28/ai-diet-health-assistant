"""播种12套食谱到数据库"""
import sys
sys.path.insert(0, ".")

from app.database import SessionLocal, init_db
from app.models.meal_plan import MealPlan

PLANS = [
    # ========== 减脂 (lose_fat) ==========
    ("lose_fat", "水煮蛋2个 + 无糖豆浆1杯 + 小份凉拌黄瓜", "清蒸鸡胸肉 + 清炒西兰花 + 半拳杂粮饭", "巴沙鱼柳 + 白灼生菜 + 玉米半根", "小番茄10颗", 1400),
    ("lose_fat", "无糖酸奶 + 原味坚果一小把 + 蓝莓", "瘦牛肉片炒菌菇 + 凉拌油麦菜 + 红薯1小块", "虾仁滑蛋（少油）+ 清炒冬瓜", "黄瓜1根", 1350),
    ("lose_fat", "全麦面包2片 + 煎蛋（少油）+ 黑咖啡", "卤牛肉（无酱汁）+ 蒜蓉娃娃菜 + 燕麦饭半碗", "去皮卤鸡腿 + 凉拌海带丝", "青苹果半个", 1450),
    ("lose_fat", "鸡蛋羹 + 凉拌木耳", "水煮虾 + 清炒茼蒿 + 山药小段", "豆腐炖白菜 + 少量瘦猪肉片", "原味无糖酸奶", 1380),

    # ========== 增肌 (build_muscle) ==========
    ("build_muscle", "全麦面包3片 + 鸡蛋3个 + 纯牛奶1杯 + 香蕉1根", "香煎鸡胸肉 + 清炒芦笋 + 一拳杂粮饭", "红烧瘦排骨（少糖少酱）+ 炒菠菜 + 红薯1个", "水煮蛋1个 + 原味坚果", 2400),
    ("build_muscle", "燕麦粥（纯燕麦）+ 鸡蛋2个 + 无糖花生酱少量", "牛排（少油煎）+ 彩椒西兰花 + 糙米饭1拳", "蒜蓉大虾 + 凉拌秋葵 + 玉米1根", "低脂牛奶 + 蛋白棒（无糖款）", 2500),
    ("build_muscle", "鸡蛋卷 + 无糖豆浆 + 全麦馒头半个", "瘦猪肉炒芹菜 + 水煮蛋1个 + 荞麦面1份", "嫩豆腐炖鱼肉 + 清炒芥蓝 + 紫薯1个", "鸡蛋白2个", 2350),
    ("build_muscle", "希腊无糖酸奶 + 燕麦 + 少量奇亚籽", "去皮鸭肉 + 杂蔬小炒 + 杂粮饭1拳", "牛肉丸清汤（纯肉丸）+ 生菜 + 山药", "牛油果半个", 2450),

    # ========== 控糖 (control_sugar) ==========
    ("control_sugar", "水煮蛋2个 + 无糖豆浆 + 凉拌苦瓜", "白灼虾 + 清炒荷兰豆 + 杂豆饭（少量）", "鸡胸肉炒木耳 + 蒜蓉菜心 + 蒸山药", "圣女果、柚子少量", 1300),
    ("control_sugar", "无糖酸奶 + 坚果 + 草莓", "瘦牛肉 + 大份绿叶菜 + 荞麦饭半拳", "嫩豆腐 + 菌菇汤 + 凉拌黄瓜", "原味黄瓜、芹菜条", 1280),
    ("control_sugar", "蒸鸡蛋 + 全麦饼干2片（无糖）+ 黑咖啡", "清蒸鲈鱼 + 清炒西葫芦 + 红薯小块", "去皮鸡腿肉 + 凉拌三丝（胡萝卜/木耳/生菜）", "猕猴桃1个", 1320),
    ("control_sugar", "纯燕麦（清水/无糖奶冲泡）+ 鸡蛋1个", "瘦猪肉炖萝卜 + 油麦菜 + 玉米半根", "虾仁豆腐羹 + 清炒茼蒿", "原味无糖豆浆", 1350),
]

def seed():
    init_db()
    db = SessionLocal()

    existing = db.query(MealPlan).count()
    if existing > 0:
        print(f"已有 {existing} 条食谱，跳过播种")
        db.close()
        return

    for goal_type, breakfast, lunch, dinner, snack, cal in PLANS:
        plan = MealPlan(
            goal_type=goal_type,
            breakfast=breakfast,
            lunch=lunch,
            dinner=dinner,
            snack=snack,
            total_calories=cal,
        )
        db.add(plan)

    db.commit()
    print(f"已插入 {len(PLANS)} 套食谱")
    for goal in ["lose_fat", "build_muscle", "control_sugar"]:
        c = db.query(MealPlan).filter(MealPlan.goal_type == goal).count()
        print(f"  {goal}: {c} 套")
    db.close()

if __name__ == "__main__":
    seed()
