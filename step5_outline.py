import csv
from typing import List, Dict

def generate_outlines_from_titles_and_references(client, model: str, title_csv: str, reference_csv: str, summary_csv: str, outline_csv: str):
    """
    Generate article outlines based on titles, reference materials, and summaries
    """
    print(f"📋 Reading titles from {title_csv}...")
    print(f"📚 Reading references from {reference_csv}...")
    print(f"📝 Reading summaries from {summary_csv}...")
    
    # Read titles
    with open(title_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        titles = list(reader)
    
    # Read reference materials
    references_by_title = {}
    try:
        with open(reference_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for ref in reader:
                title = ref['title']
                if title not in references_by_title:
                    references_by_title[title] = []
                references_by_title[title].append(ref)
    except FileNotFoundError:
        print("⚠️ Reference file not found, proceeding without references")
    
    # Read summaries
    summaries_by_title = {}
    try:
        with open(summary_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for summary in reader:
                summaries_by_title[summary['title']] = summary
    except FileNotFoundError:
        print("⚠️ Summary file not found, proceeding without summaries")
    
    outlines = []
    
    for title_row in titles:
        title = title_row['title']
        print(f"🧱 Generating outline for: {title}")
        
        # Get related reference materials
        title_references = references_by_title.get(title, [])
        ref_info = ""
        if title_references:
            ref_info = "\nReference Information:\n"
            for i, ref in enumerate(title_references, 1):
                ref_info += f"{i}. {ref['reference_type']}: {ref['search_keywords']} - {ref['usage_purpose']}\n"
        
        # Get related summary
        title_summary = summaries_by_title.get(title, {})
        summary_info = ""
        if title_summary:
            summary_info = f"""
Content Summary:
- Core Concepts: {title_summary.get('core_concepts', '')}
- Main Points: {title_summary.get('main_points', '')}
- Key Data: {title_summary.get('key_data', '')}
- Case Studies: {title_summary.get('case_studies', '')}
- Industry Trends: {title_summary.get('trends', '')}
- Challenges & Solutions: {title_summary.get('challenges_solutions', '')}
"""
        
        # Build enhanced prompt
        prompt = f"""
You are a professional SEO content strategist. Please create a detailed article outline for the following title.

Title: {title}
{ref_info}
{summary_info}

Please create an outline that meets the following requirements:

**SEO Optimization Requirements:**
• Follow Google EEAT principles (Expertise, Authoritativeness, Trustworthiness)
• Include natural distribution of target keywords
• Clear structure for search engine understanding
• Include internal and external link opportunities

**Content Structure Requirements:**
• Begin with a concise lead section defining the topic
• Use descriptive subheadings (H2, H3) that include relevant keywords
• Include sections for background, current applications, benefits, challenges
• Add a comprehensive FAQ section
• Conclude with actionable insights and future outlook

**Technical Requirements:**
• Article length: 2500-3500 words
• Include 5-8 main sections
• Each section contains 2-4 subsections
• Clearly mark keyword placement positions
• Suggest internal links and authoritative external links

Please generate a detailed outline based on the provided reference materials and summary information. If reference materials are available, please indicate how to use these materials in relevant sections.
"""
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional SEO content strategist who excels at creating structured, SEO-friendly article outlines. You will make full use of the provided reference materials and summary information to create high-quality content outlines."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            outline_content = response.choices[0].message.content.strip()
            
            outlines.append({
                'title': title,
                'outline': outline_content,
                'reference_count': len(title_references),
                'has_summary': bool(title_summary)
            })
            
        except Exception as e:
            print(f"❌ Error generating outline for '{title}': {e}")
            outlines.append({
                'title': title,
                'outline': f'Error generating outline: {str(e)}',
                'reference_count': 0,
                'has_summary': False
            })
    
    # Save outlines
    print(f"💾 Saving outlines to {outline_csv}...")
    with open(outline_csv, 'w', newline='', encoding='utf-8') as f:
        if outlines:
            fieldnames = ['title', 'outline', 'reference_count', 'has_summary']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(outlines)
    
    print(f"✅ Generated {len(outlines)} outline entries")
    return outlines