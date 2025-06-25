import csv
import json
from typing import List, Dict

def generate_references_from_titles(client, model: str, title_csv: str, reference_csv: str):
    """
    Generate relevant reference materials based on titles
    """
    print(f"📚 Reading titles from {title_csv}...")
    
    # Read titles
    with open(title_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        titles = list(reader)
    
    references = []
    
    for title_row in titles:
        title = title_row['title']
        print(f"🔍 Generating references for: {title}")
        
        # Build prompt
        prompt = f"""
You are a professional research assistant. Please generate 5-8 relevant reference material suggestions for the following title:

Title: {title}

Please provide the following types of reference materials:
1. Authoritative websites and official documentation
2. Academic research and reports
3. Industry statistics and data
4. Expert opinions and case studies
5. Related news and trend analysis

For each reference material, please provide:
- Material type (Official Documentation/Academic Research/Statistical Data/Expert Opinion/News Trends)
- Suggested search keywords
- Expected information type
- Purpose of use in the article

Please return in JSON format as follows:
{{
  "references": [
    {{
      "type": "Material Type",
      "search_keywords": "Search Keywords",
      "expected_info": "Expected Information Type",
      "usage_purpose": "Purpose of Use"
    }}
  ]
}}
"""
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional research assistant who specializes in providing high-quality reference material suggestions for content creation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            reference_content = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                reference_data = json.loads(reference_content)
                reference_list = reference_data.get('references', [])
            except json.JSONDecodeError:
                # If JSON parsing fails, create a basic reference entry
                reference_list = [{
                    "type": "General Material",
                    "search_keywords": title,
                    "expected_info": "Related background information and data",
                    "usage_purpose": "Support article content"
                }]
            
            # Add title information to each reference
            for ref in reference_list:
                references.append({
                    'title': title,
                    'reference_type': ref.get('type', ''),
                    'search_keywords': ref.get('search_keywords', ''),
                    'expected_info': ref.get('expected_info', ''),
                    'usage_purpose': ref.get('usage_purpose', ''),
                    'raw_content': reference_content
                })
                
        except Exception as e:
            print(f"❌ Error generating references for '{title}': {e}")
            # Add a default reference entry
            references.append({
                'title': title,
                'reference_type': 'Basic Material',
                'search_keywords': title,
                'expected_info': 'Related information',
                'usage_purpose': 'Content support',
                'raw_content': f'Error: {str(e)}'
            })
    
    # Save references
    print(f"💾 Saving references to {reference_csv}...")
    with open(reference_csv, 'w', newline='', encoding='utf-8') as f:
        if references:
            fieldnames = ['title', 'reference_type', 'search_keywords', 'expected_info', 'usage_purpose', 'raw_content']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(references)
    
    print(f"✅ Generated {len(references)} reference entries")
    return references