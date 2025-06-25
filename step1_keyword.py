import csv
from datetime import datetime
import random
import time
import hashlib

def generate_keywords(client, model_name, output_file, num_keywords=2, knowledge_scope="technology", topic=None):
    # 使用多重随机化策略确保每次结果不同
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    microsecond_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    
    # 组合多个随机源
    time_seed = int(time.time() * 1000000) % 100000  # 微秒级时间戳
    random_seed = random.randint(1, 100000)  # 扩大随机范围
    hash_seed = int(hashlib.md5(microsecond_time.encode()).hexdigest()[:8], 16) % 100000
    
    # 组合种子确保唯一性
    combined_seed = (time_seed + random_seed + hash_seed) % 100000
    
    # 根据知识范围调整AI类别
    if "AI" in knowledge_scope or "人工智能" in knowledge_scope:
        categories = """
    1. AI Assistants (e.g. ChatGPT, Claude, Gemini)
    2. AI Note-taking Tools (e.g. Notion AI, Mem.ai)
    3. General AI Tools and Applications"""
    elif "科技" in knowledge_scope or "技术" in knowledge_scope:
        categories = """
    1. Emerging Technologies (e.g. Blockchain, IoT, AR/VR)
    2. Software Development Tools and Frameworks
    3. Tech Industry Trends and Innovations"""
    elif "商业" in knowledge_scope or "营销" in knowledge_scope:
        categories = """
    1. Digital Marketing and Social Media
    2. E-commerce and Online Business
    3. Business Intelligence and Analytics"""
    elif "教育" in knowledge_scope or "学习" in knowledge_scope:
        categories = """
    1. Online Learning Platforms and EdTech
    2. Educational Technology and Tools
    3. Skills Development and Training"""
    else:
        # 自定义范围，使用用户输入的范围
        categories = f"""
    1. {knowledge_scope} - Core Topics and Trends
    2. {knowledge_scope} - Tools and Applications
    3. {knowledge_scope} - Industry Developments"""
    
    # 添加更多随机化元素到prompt中
    random_perspectives = [
        "from a startup founder's perspective",
        "from a tech investor's viewpoint", 
        "from an early adopter's angle",
        "from an industry analyst's view",
        "from a developer's standpoint",
        "from a business strategist's perspective"
    ]
    
    random_timeframes = [
        "emerging in the last 48 hours",
        "trending in the past week",
        "gaining momentum recently",
        "showing viral growth patterns",
        "experiencing sudden popularity spikes"
    ]
    
    selected_perspective = random.choice(random_perspectives)
    selected_timeframe = random.choice(random_timeframes)
    
    # 修改prompt，要求生成可分割的关键词
    # 在prompt中添加主题相关内容
    topic_context = f"\nSpecific topic focus: {topic}" if topic else ""
    
    prompt = f"""
    As a trend analyst specializing in {knowledge_scope}, identify the {num_keywords} most trending and popular keywords from X (Twitter) & reddit & medium discussions at {current_time}.{topic_context}
    
    Analyze {selected_perspective} and focus on topics {selected_timeframe}.
    
    Focus on these categories related to {knowledge_scope}:
    {categories}
    
    Requirements:
    - Return EXACTLY {num_keywords} keywords from different categories above
    - Keywords must be currently trending and relevant to {knowledge_scope}
    {f"- All keywords should be related to or inspired by: {topic}" if topic else ""}
    - Consider topics with high search volume and viral discussions (unique seed: {combined_seed})
    - Focus on emerging topics and developments in {knowledge_scope}
    - Look for sudden spikes in discussion and engagement
    - Consider global trends across different regions
    - Prioritize fresh and currently active discussions
    - Ensure completely different results each time (randomization key: {hash_seed})
    - Avoid previously common keywords, seek novel trending terms
    - IMPORTANT: Output keywords as comma-separated values for better processing
    
    Format: Output each keyword set as comma-separated values on one line.
    Example: artificial intelligence, machine learning, technology
    
    Just output the {num_keywords} keyword sets directly, one per line, without any additional text or explanations.
    Do not include any headers, bullet points, or section markers.
    """
    
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,  # 保持最大随机性
        seed=combined_seed  # 使用组合种子
    )
    
    # 处理关键词，确保每个关键词单独保存
    raw_keywords = [k.strip('- ') for k in response.choices[0].message.content.strip().split('\n') 
                  if k.strip() and not k.startswith('#') and not k.startswith('##')][:num_keywords]
    
    processed_keywords = []
    for keyword_line in raw_keywords:
        if keyword_line:
            # 如果包含逗号，按逗号分割成多个关键词
            if ',' in keyword_line:
                # 按逗号分割并清理每个关键词
                split_keywords = [k.strip().lower() for k in keyword_line.split(',') if k.strip()]
                processed_keywords.extend(split_keywords)
            else:
                # 单个关键词直接添加
                processed_keywords.append(keyword_line.strip().lower())
    
    # 保存到CSV文件
    import csv
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Keyword'])
        for keyword in processed_keywords:
            if keyword:  # 只写入非空关键词
                writer.writerow([keyword])
    
    print(f"✅ 已保存{len(processed_keywords)}个关键词到{output_file} (种子: {combined_seed})")
    print(f"📝 生成的关键词: {processed_keywords}")