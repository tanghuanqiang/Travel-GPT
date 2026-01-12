"""
PDF导出功能
使用 reportlab 生成PDF文档
"""
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# 尝试注册中文字体（如果可用）
try:
    # 这些字体路径可能需要根据系统调整
    # Windows: C:/Windows/Fonts/simsun.ttc 或 simhei.ttf
    # Linux: /usr/share/fonts/truetype/arphic/uming.ttc
    # macOS: /System/Library/Fonts/PingFang.ttc
    pass  # 暂时使用默认字体，后续可以根据需要添加中文字体支持
except Exception as e:
    logger.warning(f"无法注册中文字体: {e}")


def generate_pdf(itinerary_data: Dict[str, Any], destination: str, days: int) -> BytesIO:
    """生成行程PDF文档
    
    Args:
        itinerary_data: 行程数据字典
        destination: 目的地
        days: 天数
    
    Returns:
        BytesIO: PDF文件流
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # 构建PDF内容
    story = []
    styles = getSampleStyleSheet()
    
    # 自定义样式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # 标题
    title = Paragraph(f"{destination} {days}天旅行行程", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # 预算概览
    if 'overview' in itinerary_data and itinerary_data['overview']:
        overview = itinerary_data['overview']
        story.append(Paragraph("预算概览", heading_style))
        
        if 'totalBudget' in overview and overview['totalBudget']:
            story.append(Paragraph(f"总预算: ¥{overview['totalBudget']:,.2f}", styles['Normal']))
            story.append(Spacer(1, 10))
        
        breakdown = overview.get('breakdown') or overview.get('budgetBreakdown')
        if breakdown:
            breakdown_data = [['类别', '金额', '占比']]
            total = overview.get('totalBudget', 0)
            
            for item in breakdown:
                amount = item.get('amount', 0)
                percentage = (amount / total * 100) if total > 0 else 0
                breakdown_data.append([
                    item.get('category', ''),
                    f"¥{amount:,.2f}",
                    f"{percentage:.1f}%"
                ])
            
            breakdown_table = Table(breakdown_data, colWidths=[80*mm, 50*mm, 30*mm])
            breakdown_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e7ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(breakdown_table)
        
        story.append(Spacer(1, 20))
        story.append(PageBreak())
    
    # 每日行程
    if 'dailyPlans' in itinerary_data and itinerary_data['dailyPlans']:
        for day_idx, day_plan in enumerate(itinerary_data['dailyPlans'], 1):
            story.append(Paragraph(f"第{day_idx}天: {day_plan.get('title', f'第{day_idx}天')}", heading_style))
            
            if 'activities' in day_plan and day_plan['activities']:
                for activity in day_plan['activities']:
                    # 活动标题和时间
                    activity_title = f"{activity.get('time', '')} - {activity.get('title', '')}"
                    story.append(Paragraph(activity_title, styles['Heading3']))
                    
                    # 活动描述
                    if activity.get('description'):
                        desc_text = activity.get('description', '').replace('\n', '<br/>')
                        story.append(Paragraph(desc_text, styles['Normal']))
                    
                    # 活动信息（地址、费用等）
                    info_items = []
                    if activity.get('address'):
                        info_items.append(f"地址: {activity['address']}")
                    if activity.get('duration'):
                        info_items.append(f"时长: {activity['duration']}")
                    if activity.get('cost') is not None:
                        info_items.append(f"费用: ¥{activity['cost']:,.2f}")
                    
                    if info_items:
                        info_text = " | ".join(info_items)
                        story.append(Paragraph(info_text, styles['Normal']))
                    
                    if activity.get('reason'):
                        story.append(Paragraph(f"推荐理由: {activity['reason']}", styles['Italic']))
                    
                    story.append(Spacer(1, 12))
            
            story.append(Spacer(1, 20))
            if day_idx < len(itinerary_data['dailyPlans']):
                story.append(PageBreak())
    
    # 隐藏宝石推荐
    if 'hiddenGems' in itinerary_data and itinerary_data['hiddenGems']:
        story.append(Paragraph("隐藏宝石推荐", heading_style))
        for gem in itinerary_data['hiddenGems']:
            story.append(Paragraph(gem.get('title', ''), styles['Heading3']))
            if gem.get('description'):
                desc_text = gem.get('description', '').replace('\n', '<br/>')
                story.append(Paragraph(desc_text, styles['Normal']))
            story.append(Spacer(1, 12))
        story.append(Spacer(1, 20))
    
    # 实用建议
    if 'tips' in itinerary_data and itinerary_data['tips']:
        story.append(Paragraph("实用旅行建议", heading_style))
        tips = itinerary_data['tips']
        
        if tips.get('transportation'):
            story.append(Paragraph("交通建议", styles['Heading3']))
            story.append(Paragraph(tips['transportation'].replace('\n', '<br/>'), styles['Normal']))
            story.append(Spacer(1, 12))
        
        if tips.get('packing'):
            story.append(Paragraph("打包清单", styles['Heading3']))
            story.append(Paragraph(tips['packing'].replace('\n', '<br/>'), styles['Normal']))
            story.append(Spacer(1, 12))
        
        if tips.get('weather'):
            story.append(Paragraph("天气信息", styles['Heading3']))
            story.append(Paragraph(tips['weather'].replace('\n', '<br/>'), styles['Normal']))
            story.append(Spacer(1, 12))
    
    # 构建PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer
