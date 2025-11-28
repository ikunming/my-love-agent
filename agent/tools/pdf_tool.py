# Copyright 2025 Google LLC
# ... (版权头保持不变) ...

"""
PDF 生成工具 - Google ADK Tool 包装器
"""

from .pdf_generator import generate_date_plan_pdf

import json


# 注意：这里移除了函数参数中的所有默认值 (= "")

def create_date_plan_pdf(
        title: str,
        restaurant_name: str,
        restaurant_time: str,
        restaurant_address: str,
        restaurant_phone: str,
        activity_schedule_json: str,
        gift_list_json: str,
        additional_notes: str
) -> str:
    """
    生成约会计划 PDF 文档

    使用场景:
    - 当用户要求生成约会计划、节日计划(如七夕、情人节)等 PDF 文档时使用
    - 必须为所有参数提供值，如果某个字段没有信息，请传入空字符串 "" 或空 JSON 列表 "[]"

    Args:
        title: PDF 标题,例如 "七夕约会计划"
        restaurant_name: 餐厅名称 (如果没有，请传入空字符串)
        restaurant_time: 预订时间 (如果没有，请传入空字符串)
        restaurant_address: 餐厅地址 (如果没有，请传入空字符串)
        restaurant_phone: 餐厅电话 (如果没有，请传入空字符串)
        activity_schedule_json: 活动流程 JSON 字符串 (如果没有，请传入 "[]")
        gift_list_json: 礼物清单 JSON 字符串 (如果没有，请传入 "[]")
        additional_notes: 额外备注信息 (如果没有，请传入空字符串)

    Returns:
        str: 生成结果的 JSON 字符串
    """
    try:
        # 容错处理：虽然要求模型必填，但为了防止代码崩溃，还是做一下 None 判断
        r_name = restaurant_name if restaurant_name else ""
        r_time = restaurant_time if restaurant_time else ""
        r_addr = restaurant_address if restaurant_address else ""
        r_phone = restaurant_phone if restaurant_phone else ""

        # 解析 JSON 参数
        # 针对模型可能传入 "null" 字符串或 None 的情况进行防御
        if not activity_schedule_json or activity_schedule_json == "null":
            activity_schedule = []
        else:
            try:
                activity_schedule = json.loads(activity_schedule_json)
            except:
                activity_schedule = []

        if not gift_list_json or gift_list_json == "null":
            gift_list = []
        else:
            try:
                gift_list = json.loads(gift_list_json)
            except:
                gift_list = []

        # 构建餐厅信息
        restaurant_info = {
            "name": r_name,
            "time": r_time,
            "address": r_addr,
            "phone": r_phone
        }

        # 生成 PDF
        result = generate_date_plan_pdf(
            title=title,
            restaurant_info=restaurant_info,
            activity_schedule=activity_schedule,
            gift_list=gift_list,
            additional_notes=additional_notes if additional_notes else ""
        )

        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "success": False,
            "file_path": "",
            "file_name": "",
            "message": f"工具调用失败: {str(e)}"
        }, ensure_ascii=False)
