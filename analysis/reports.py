import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class ReportGenerator:
    """报告生成器 - 支持 PDF/Excel/Markdown 格式的生产报告"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_analysis_report(self, analysis_result: str, data: pd.DataFrame, title: str = "项目数据分析报告") -> str:
        """生成 Markdown + HTML 格式的分析报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"{title.replace(' ', '_')}_{timestamp}.md"
        
        report_content = f"""# {title}

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 分析结果
{analysis_result}

## 数据摘要
{data.describe().to_string() if not data.empty else '无可用数据'}

## 关键发现
- 待补充具体洞察...

**报告由 AI Agent 自动生成**
"""
        report_path.write_text(report_content, encoding="utf-8")
        return str(report_path)
    
    def export_to_excel(self, data: pd.DataFrame, filename: str):
        """导出Excel报告"""
        path = self.output_dir / f"{filename}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        data.to_excel(path, index=False)
        return str(path)
