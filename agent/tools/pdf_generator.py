# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
PDF 生成工具 - 用于生成恋爱相关的 PDF 文档
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDF_OUTPUT_DIR = os.path.join(BASE_DIR, "generated_pdfs")

# 确保输出目录存在
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)


def register_chinese_fonts():
    """注册中文字体 - 使用系统自带的字体"""
    try:
        # Windows 系统字体路径
        font_path = "C:/Windows/Fonts/msyh.ttc"  # 微软雅黑
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
            return True
    except Exception as e:
        print(f"警告: 无法注册中文字体 {e}")
    return False


def generate_date_plan_pdf(
    title: str,
    restaurant_info: dict,
    activity_schedule: list,
    gift_list: list,
    additional_notes: str = ""
) -> dict:
    """
    生成约会计划 PDF
    
    Args:
        title: PDF 标题 (例如: "七夕约会计划")
        restaurant_info: 餐厅信息字典 {"name": "餐厅名", "time": "预订时间", "address": "地址", "phone": "电话"}
        activity_schedule: 活动流程列表 [{"time": "14:00", "activity": "看电影", "location": "万达影城"}]
        gift_list: 礼物清单列表 [{"name": "玫瑰花", "price": "99元", "status": "已购买"}]
        additional_notes: 额外备注
    
    Returns:
        dict: {"success": bool, "file_path": str, "file_name": str, "message": str}
    """
    try:
        # 注册中文字体
        has_chinese_font = register_chinese_fonts()
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{title}_{timestamp}.pdf"
        file_path = os.path.join(PDF_OUTPUT_DIR, file_name)
        
        # 创建 PDF 文档
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        story = []
        
        # 设置样式
        styles = getSampleStyleSheet()
        
        # 标题样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName='ChineseFont' if has_chinese_font else 'Helvetica-Bold',
            fontSize=24,
            textColor=colors.HexColor('#E91E63'),
            alignment=TA_CENTER,
            spaceAfter=30,
        )
        
        # 副标题样式
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontName='ChineseFont' if has_chinese_font else 'Helvetica-Bold',
            fontSize=16,
            textColor=colors.HexColor('#FF4081'),
            spaceAfter=12,
        )
        
        # 正文样式
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontName='ChineseFont' if has_chinese_font else 'Helvetica',
            fontSize=11,
            leading=18,
        )
        
        # 添加标题
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # 添加生成时间
        date_text = f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}"
        story.append(Paragraph(date_text, body_style))
        story.append(Spacer(1, 1*cm))
        
        # 1. 餐厅预订信息
        story.append(Paragraph("🍽️ 餐厅预订信息", subtitle_style))
        restaurant_data = [
            ["餐厅名称", restaurant_info.get("name", "未指定")],
            ["预订时间", restaurant_info.get("time", "未指定")],
            ["餐厅地址", restaurant_info.get("address", "未指定")],
            ["联系电话", restaurant_info.get("phone", "未指定")],
        ]
        
        restaurant_table = Table(restaurant_data, colWidths=[4*cm, 12*cm])
        restaurant_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FFE0F0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont' if has_chinese_font else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#FFB6D9')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(restaurant_table)
        story.append(Spacer(1, 1*cm))
        
        # 2. 活动流程
        story.append(Paragraph("📅 活动流程安排", subtitle_style))
        activity_data = [["时间", "活动内容", "地点"]]
        for activity in activity_schedule:
            activity_data.append([
                activity.get("time", ""),
                activity.get("activity", ""),
                activity.get("location", "")
            ])
        
        activity_table = Table(activity_data, colWidths=[3*cm, 7*cm, 6*cm])
        activity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF4081')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont' if has_chinese_font else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#FFB6D9')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(activity_table)
        story.append(Spacer(1, 1*cm))
        
        # 3. 礼物清单
        story.append(Paragraph("🎁 礼物清单", subtitle_style))
        gift_data = [["礼物名称", "预算/价格", "状态"]]
        for gift in gift_list:
            gift_data.append([
                gift.get("name", ""),
                gift.get("price", ""),
                gift.get("status", "待购买")
            ])
        
        gift_table = Table(gift_data, colWidths=[6*cm, 5*cm, 5*cm])
        gift_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF4081')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont' if has_chinese_font else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#FFB6D9')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(gift_table)
        story.append(Spacer(1, 1*cm))
        
        # 4. 额外备注
        if additional_notes:
            story.append(Paragraph("📝 温馨提示", subtitle_style))
            story.append(Paragraph(additional_notes, body_style))
        
        # 生成 PDF
        doc.build(story)
        
        return {
            "success": True,
            "file_path": file_path,
            "file_name": file_name,
            "message": f"PDF 文档生成成功! 文件名: {file_name}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "file_path": "",
            "file_name": "",
            "message": f"PDF 生成失败: {str(e)}"
        }


def generate_pdf_from_text(title: str, content: str) -> dict:
    """
    从文本内容生成简单的 PDF
    
    Args:
        title: PDF 标题
        content: 文本内容
    
    Returns:
        dict: {"success": bool, "file_path": str, "file_name": str, "message": str}
    """
    try:
        has_chinese_font = register_chinese_fonts()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{title}_{timestamp}.pdf"
        file_path = os.path.join(PDF_OUTPUT_DIR, file_name)
        
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName='ChineseFont' if has_chinese_font else 'Helvetica-Bold',
            fontSize=20,
            textColor=colors.HexColor('#E91E63'),
            alignment=TA_CENTER,
            spaceAfter=20,
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontName='ChineseFont' if has_chinese_font else 'Helvetica',
            fontSize=11,
            leading=18,
        )
        
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 1*cm))
        
        # 处理多行文本
        for line in content.split('\n'):
            if line.strip():
                story.append(Paragraph(line, body_style))
                story.append(Spacer(1, 0.3*cm))
        
        doc.build(story)
        
        return {
            "success": True,
            "file_path": file_path,
            "file_name": file_name,
            "message": f"PDF 文档生成成功! 文件名: {file_name}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "file_path": "",
            "file_name": "",
            "message": f"PDF 生成失败: {str(e)}"
        }
