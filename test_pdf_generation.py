"""
PDF 生成功能测试脚本
"""

import csv
csv.field_size_limit(100 * 1024 * 1024)

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.tools.pdf_generator import generate_date_plan_pdf
import json

def test_pdf_generation():
    """测试 PDF 生成功能"""
    
    print("🧪 开始测试 PDF 生成功能...\n")
    
    # 测试数据
    title = "七夕约会计划"
    
    restaurant_info = {
        "name": "浪漫西餐厅",
        "time": "2025年8月22日 晚上7:00",
        "address": "市中心广场3楼",
        "phone": "010-12345678"
    }
    
    activity_schedule = [
        {"time": "14:00", "activity": "看电影《浪漫爱情故事》", "location": "万达影城"},
        {"time": "17:00", "activity": "公园散步", "location": "中央公园"},
        {"time": "19:00", "activity": "浪漫晚餐", "location": "浪漫西餐厅"},
        {"time": "21:00", "activity": "江边夜景", "location": "滨江大道"}
    ]
    
    gift_list = [
        {"name": "99朵玫瑰花", "price": "299元", "status": "已购买"},
        {"name": "巧克力礼盒", "price": "150元", "status": "已购买"},
        {"name": "施华洛世奇项链", "price": "999元", "status": "待购买"},
        {"name": "香水", "price": "500元", "status": "待购买"}
    ]
    
    additional_notes = """
    温馨提示:
    1. 提前30分钟到达餐厅,确认预订信息
    2. 记得带上相机,记录美好时刻
    3. 准备好浪漫的表白词
    4. 注意天气预报,准备雨伞
    5. 保持手机电量充足
    """
    
    # 生成 PDF
    print("📝 生成 PDF 文档...")
    result = generate_date_plan_pdf(
        title=title,
        restaurant_info=restaurant_info,
        activity_schedule=activity_schedule,
        gift_list=gift_list,
        additional_notes=additional_notes
    )
    
    # 打印结果
    print("\n" + "="*60)
    print("📊 生成结果:")
    print("="*60)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("="*60)
    
    if result["success"]:
        print(f"\n✅ 测试成功!")
        print(f"📄 PDF 文件已生成: {result['file_name']}")
        print(f"📂 文件路径: {result['file_path']}")
        print(f"\n💡 下载链接: http://localhost:8000/api/download_pdf/{result['file_name']}")
    else:
        print(f"\n❌ 测试失败: {result['message']}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_pdf_generation()
