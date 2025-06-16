import csv
from datetime import datetime
import random

def generate_keywords_via_openrouter(client, model_name, output_file):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    random_seed = random.randint(1, 1000)
    
    prompt = f"""
    As an AI trend analyst, identify the 2 most trending and popular keywords from X (Twitter) discussions at {current_time}. Focus on these AI categories:
    1. AI Assistants (e.g. ChatGPT, Claude, Gemini)
    2. AI Note-taking Tools (e.g. Notion AI, Mem.ai)
    3. General AI Tools and Applications
    
    Requirements:
    - Return EXACTLY 2 keywords from different categories above
    - Keywords must be currently trending on X
    - Consider topics with high search volume and viral discussions (seed: {random_seed})
    - Focus on emerging AI products and features gaining attention
    - Look for sudden spikes in discussion and engagement
    - Consider global trends across different regions
    - Prioritize fresh and currently active discussions
    
    Just output the 2 keywords directly, one per line, without any additional text or explanations.
    Do not include any headers, bullet points, or section markers.
    """
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9  # 增加随机性
    )
    keywords = [k.strip('- ') for k in response.choices[0].message.content.strip().split('\n') 
              if k.strip() and not k.startswith('#') and not k.startswith('##')][:2]  # 限制只取前2个关键词
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['keyword'])
        for keyword in keywords:
            if keyword:  # 只写入非空关键词
                writer.writerow([keyword.lower()])
    print("✅ Saved keywords to", output_file)