import csv
import json
from typing import List, Dict

def generate_summaries_from_references(client, model: str, reference_csv: str, summary_csv: str):
    """
    Generate content summaries based on reference materials
    """
    print(f"📖 Reading references from {reference_csv}...")
    
    # Read reference materials
    with open(reference_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        references = list(reader)
    
    # Group references by title
    references_by_title = {}
    for ref in references:
        title = ref['title']
        if title not in references_by_title:
            references_by_title[title] = []
        references_by_title[title].append(ref)
    
    summaries = []
    
    for title, title_references in references_by_title.items():
        print(f"📝 Generating summary for: {title}")
        
        # Build reference information
        ref_info = ""
        for i, ref in enumerate(title_references, 1):
            ref_info += f"""
{i}. Type: {ref['reference_type']}
   Keywords: {ref['search_keywords']}
   Expected Information: {ref['expected_info']}
   Usage Purpose: {ref['usage_purpose']}
"""
        
        # Build prompt - 简化JSON格式要求
        prompt = f"""
You are a professional content strategist. Based on the following title and reference information, generate a detailed content summary.

Title: {title}

Reference Information:
{ref_info}

Please generate a content summary and return ONLY a valid JSON object with these exact fields:
{{
  "core_concepts": "Brief core concept definitions (max 200 chars)",
  "main_points": "Key points separated by semicolons (max 300 chars)",
  "key_data": "Important data and statistics (max 200 chars)",
  "case_studies": "Relevant case studies (max 200 chars)",
  "trends": "Industry trends (max 200 chars)",
  "challenges_solutions": "Main challenges and solutions (max 200 chars)"
}}

IMPORTANT: Return ONLY the JSON object, no markdown formatting, no explanations.
"""
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional content strategist. Always return valid JSON only, no markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 降低温度以获得更一致的输出
                max_tokens=1500
            )
            
            # 获取并清理响应内容
            summary_content = response.choices[0].message.content.strip()
            
            # 移除可能的markdown代码块标记
            if summary_content.startswith('```json'):
                summary_content = summary_content[7:]
            if summary_content.startswith('```'):
                summary_content = summary_content[3:]
            if summary_content.endswith('```'):
                summary_content = summary_content[:-3]
            summary_content = summary_content.strip()
            
            # 尝试解析JSON
            try:
                summary_data = json.loads(summary_content)
                
                # 确保所有字段都存在并且是字符串
                summary_entry = {
                    'title': title,
                    'core_concepts': str(summary_data.get('core_concepts', '')).replace('\n', ' ').replace('\r', ' ')[:200],
                    'main_points': str(summary_data.get('main_points', '')).replace('\n', ' ').replace('\r', ' ')[:300],
                    'key_data': str(summary_data.get('key_data', '')).replace('\n', ' ').replace('\r', ' ')[:200],
                    'case_studies': str(summary_data.get('case_studies', '')).replace('\n', ' ').replace('\r', ' ')[:200],
                    'trends': str(summary_data.get('trends', '')).replace('\n', ' ').replace('\r', ' ')[:200],
                    'challenges_solutions': str(summary_data.get('challenges_solutions', '')).replace('\n', ' ').replace('\r', ' ')[:200],
                    'raw_content': summary_content[:500] + '...' if len(summary_content) > 500 else summary_content
                }
                
                print(f"✅ Successfully parsed summary for: {title}")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed for '{title}': {e}")
                print(f"Raw content: {summary_content[:200]}...")
                
                # 创建备用条目
                summary_entry = {
                    'title': title,
                    'core_concepts': 'Content summary available in raw_content',
                    'main_points': 'Please check raw_content for details',
                    'key_data': '',
                    'case_studies': '',
                    'trends': '',
                    'challenges_solutions': '',
                    'raw_content': summary_content
                }
            
            summaries.append(summary_entry)
            
        except Exception as e:
            print(f"❌ Error generating summary for '{title}': {e}")
            summaries.append({
                'title': title,
                'core_concepts': f'Error: {str(e)}',
                'main_points': '',
                'key_data': '',
                'case_studies': '',
                'trends': '',
                'challenges_solutions': '',
                'raw_content': f'Error occurred: {str(e)}'
            })
    
    # 保存摘要到CSV
    print(f"💾 Saving summaries to {summary_csv}...")
    with open(summary_csv, 'w', newline='', encoding='utf-8') as f:
        if summaries:
            fieldnames = ['title', 'core_concepts', 'main_points', 'key_data', 'case_studies', 'trends', 'challenges_solutions', 'raw_content']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summaries)
    
    print(f"✅ Generated {len(summaries)} summary entries")
    return summaries