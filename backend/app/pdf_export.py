"""
PDF导出功能
使用 reportlab 生成PDF文档，支持中文字体和图片插入
"""
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
import logging
import os
import requests
import tempfile
from typing import Dict, Any, List, Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)

# 中文字体配置
CHINESE_FONT_NAME = 'WQY'  # 文泉驿字体
_chinese_font_loaded = False


def safe_float(value: Any, default: float = 0.0) -> float:
    """安全地将值转换为浮点数"""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            cleaned = value.replace('¥', '').replace('元', '').replace(',', '').replace(' ', '')
            return float(cleaned)
        except (ValueError, AttributeError):
            return default
    return default


def safe_str(value: Any, default: str = '') -> str:
    """安全地将值转换为字符串"""
    if value is None:
        return default
    try:
        return str(value)
    except:
        return default


def escape_html(text: str) -> str:
    """转义HTML特殊字符"""
    if not text:
        return ''
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))


def register_chinese_font():
    """注册中文字体（文泉驿字体 - 开源免费）"""
    global _chinese_font_loaded
    
    if _chinese_font_loaded:
        return
    
    font_paths = [
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # 文泉驿微米黑
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',    # 文泉驿正黑
        '/usr/share/fonts/truetype/arphic/uming.ttc',      # 文鼎字体（备用）
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', # DejaVu Sans（备用，支持部分中文）
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(CHINESE_FONT_NAME, font_path))
                logger.info(f"成功注册中文字体: {font_path}")
                _chinese_font_loaded = True
                return
            except Exception as e:
                logger.warning(f"注册字体失败 {font_path}: {e}")
                continue
    
    # 如果都没有找到，使用默认字体（会有警告）
    logger.warning("未找到中文字体，PDF中的中文可能无法正确显示")
    _chinese_font_loaded = False


def download_image(image_url: str, timeout: int = 5) -> Optional[BytesIO]:
    """
    从URL下载图片
    
    Args:
        image_url: 图片URL
        timeout: 超时时间（秒）
    
    Returns:
        BytesIO对象，如果下载失败返回None
    """
    try:
        response = requests.get(image_url, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # 检查Content-Type
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            logger.warning(f"URL不是图片: {image_url} (Content-Type: {content_type})")
            return None
        
        image_data = BytesIO(response.content)
        return image_data
    except Exception as e:
        logger.warning(f"下载图片失败 {image_url}: {e}")
        return None


def create_chinese_paragraph(text: str, style: ParagraphStyle, max_width: float = 170*mm) -> Paragraph:
    """
    创建支持中文的段落
    
    Args:
        text: 文本内容
        style: 段落样式
        max_width: 最大宽度
    """
    # 转义HTML特殊字符
    text = escape_html(safe_str(text))
    # 替换换行符
    text = text.replace('\n', '<br/>')
    
    # 如果中文字体已加载，使用中文样式
    if _chinese_font_loaded:
        # 创建支持中文的样式副本
        chinese_style = ParagraphStyle(
            style.name + '_Chinese',
            parent=style,
            fontName=CHINESE_FONT_NAME,
        )
        return Paragraph(text, chinese_style)
    else:
        return Paragraph(text, style)


def generate_pdf(itinerary_data: Dict[str, Any], destination: str, days: int) -> BytesIO:
    """生成行程PDF文档
    
    Args:
        itinerary_data: 行程数据字典
        destination: 目的地
        days: 天数
    
    Returns:
        BytesIO: PDF文件流
    
    Raises:
        Exception: PDF生成过程中的任何错误
    """
    try:
        # 注册中文字体
        register_chinese_font()
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # 创建支持中文的样式
        if _chinese_font_loaded:
            font_name = CHINESE_FONT_NAME
        else:
            font_name = 'Helvetica'
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName=font_name
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12,
            fontName=font_name
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            fontName=font_name,
            leading=14
        )
        
        # 标题
        title = create_chinese_paragraph(f"{destination} {days}天旅行行程", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # 预算概览
        if 'overview' in itinerary_data and itinerary_data['overview']:
            overview = itinerary_data['overview']
            story.append(create_chinese_paragraph("预算概览", heading_style))
            
            total_budget = safe_float(overview.get('totalBudget'))
            if total_budget > 0:
                budget_text = f"总预算: ¥{total_budget:,.2f}"
                story.append(create_chinese_paragraph(budget_text, normal_style))
                story.append(Spacer(1, 10))
            
            breakdown = overview.get('breakdown') or overview.get('budgetBreakdown')
            if breakdown:
                breakdown_data = [['类别', '金额', '占比']]
                total = safe_float(overview.get('totalBudget', 0))
                
                for item in breakdown:
                    amount = safe_float(item.get('amount', 0))
                    percentage = (amount / total * 100) if total > 0 else 0
                    breakdown_data.append([
                        item.get('category', ''),
                        f"¥{amount:,.2f}",
                        f"{percentage:.1f}%"
                    ])
                
                breakdown_table = Table(breakdown_data, colWidths=[80*mm, 50*mm, 30*mm])
                table_style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e7ff')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), font_name),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 1), (-1, -1), font_name),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                ])
                breakdown_table.setStyle(table_style)
                story.append(breakdown_table)
            
            story.append(Spacer(1, 20))
            story.append(PageBreak())
        
        # 每日行程
        if 'dailyPlans' in itinerary_data and itinerary_data['dailyPlans']:
            for day_idx, day_plan in enumerate(itinerary_data['dailyPlans'], 1):
                day_title = f"第{day_idx}天: {day_plan.get('title', f'第{day_idx}天')}"
                story.append(create_chinese_paragraph(day_title, heading_style))
                
                if 'activities' in day_plan and day_plan['activities']:
                    for activity in day_plan['activities']:
                        activity_items = []
                        
                        # 活动标题和时间
                        activity_title = f"{activity.get('time', '')} - {activity.get('title', '')}"
                        activity_items.append(create_chinese_paragraph(activity_title, styles['Heading3']))
                        
                        # 活动图片（最多2张）
                        images = activity.get('images', [])
                        if images:
                            image_row = []
                            for img_url in images[:2]:  # 最多显示2张图片
                                img_data = download_image(img_url)
                                if img_data:
                                    try:
                                        # 图片宽度设置为页面宽度的一半减去间距
                                        img_width = (A4[0] - 40*mm) / 2 - 5*mm
                                        img_height = img_width * 0.75  # 保持4:3比例
                                        img = Image(img_data, width=img_width, height=img_height)
                                        image_row.append(img)
                                    except Exception as e:
                                        logger.warning(f"插入图片失败 {img_url}: {e}")
                            
                            if image_row:
                                # 如果只有一张图片，居中显示
                                if len(image_row) == 1:
                                    activity_items.append(Spacer(1, 5))
                                    activity_items.append(image_row[0])
                                else:
                                    # 两张图片并排
                                    img_table = Table([[image_row[0], image_row[1]]], colWidths=[(A4[0] - 40*mm) / 2 - 5*mm] * 2)
                                    img_table.setStyle(TableStyle([
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                    ]))
                                    activity_items.append(Spacer(1, 5))
                                    activity_items.append(img_table)
                                activity_items.append(Spacer(1, 8))
                        
                        # 活动描述
                        if activity.get('description'):
                            desc_text = safe_str(activity.get('description', ''))
                            activity_items.append(create_chinese_paragraph(desc_text, normal_style))
                            activity_items.append(Spacer(1, 5))
                        
                        # 活动信息（地址、费用等）
                        info_items = []
                        if activity.get('address'):
                            info_items.append(f"地址: {activity['address']}")
                        if activity.get('duration'):
                            info_items.append(f"时长: {activity['duration']}")
                        cost_value = activity.get('cost')
                        if cost_value is not None:
                            cost_float = safe_float(cost_value)
                            info_items.append(f"费用: ¥{cost_float:,.2f}")
                        
                        if info_items:
                            info_text = " | ".join(info_items)
                            activity_items.append(create_chinese_paragraph(info_text, normal_style))
                            activity_items.append(Spacer(1, 5))
                        
                        if activity.get('reason'):
                            reason_text = safe_str(activity.get('reason', ''))
                            italic_style = ParagraphStyle(
                                'CustomItalic',
                                parent=normal_style,
                                fontName=font_name,
                                textColor=colors.HexColor('#666666')
                            )
                            activity_items.append(create_chinese_paragraph(f"推荐理由: {reason_text}", italic_style))
                        
                        # 将活动内容组合在一起，避免分页
                        story.append(KeepTogether(activity_items))
                        story.append(Spacer(1, 12))
                
                story.append(Spacer(1, 20))
                if day_idx < len(itinerary_data['dailyPlans']):
                    story.append(PageBreak())
        
        # 隐藏宝石推荐
        if 'hiddenGems' in itinerary_data and itinerary_data['hiddenGems']:
            story.append(create_chinese_paragraph("隐藏宝石推荐", heading_style))
            for gem in itinerary_data['hiddenGems']:
                story.append(create_chinese_paragraph(gem.get('title', ''), styles['Heading3']))
                if gem.get('description'):
                    desc_text = safe_str(gem.get('description', ''))
                    story.append(create_chinese_paragraph(desc_text, normal_style))
                story.append(Spacer(1, 12))
            story.append(Spacer(1, 20))
        
        # 实用建议
        tips = itinerary_data.get('tips') or itinerary_data.get('practicalTips')
        if tips:
            story.append(create_chinese_paragraph("实用旅行建议", heading_style))
            
            if tips.get('transportation'):
                story.append(create_chinese_paragraph("交通建议", styles['Heading3']))
                transport_text = safe_str(tips.get('transportation', ''))
                story.append(create_chinese_paragraph(transport_text, normal_style))
                story.append(Spacer(1, 12))
            
            packing = tips.get('packingList') or tips.get('packing')
            if packing:
                story.append(create_chinese_paragraph("打包清单", styles['Heading3']))
                if isinstance(packing, list):
                    packing_text = '<br/>'.join([f"• {item}" for item in packing])
                else:
                    packing_text = safe_str(packing).replace('\n', '<br/>')
                story.append(create_chinese_paragraph(packing_text, normal_style))
                story.append(Spacer(1, 12))
            
            if tips.get('weather'):
                story.append(create_chinese_paragraph("天气信息", styles['Heading3']))
                weather_text = safe_str(tips.get('weather', ''))
                story.append(create_chinese_paragraph(weather_text, normal_style))
                story.append(Spacer(1, 12))
            
            if tips.get('seasonalNotes'):
                story.append(create_chinese_paragraph("季节注意事项", styles['Heading3']))
                seasonal_text = safe_str(tips.get('seasonalNotes', ''))
                story.append(create_chinese_paragraph(seasonal_text, normal_style))
                story.append(Spacer(1, 12))
        
        # 构建PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    except Exception as e:
        logger.error(f"PDF生成过程中出错: {str(e)}", exc_info=True)
        raise
