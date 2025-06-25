import os
import csv
import random
import re
import glob
import os  # 添加缺少的os模块导入
from difflib import SequenceMatcher
import traceback
import requests
from urllib.parse import urlparse
import time


def generate_article_content(client, model_name, outline, title, selected_images=None):
    """Generate high-quality article content"""

    # Build detailed article generation prompt
    prompt = f"""
You are a professional SEO content writing expert. Please generate a high-quality SEO-optimized article based on the following outline and title.

**Article Title**: {title}
**Article Outline**: {outline}

**Writing Requirements**:
1. **Article Structure**:
   - Use clear Markdown formatting
   - # for main title
   - ## for main sections
   - ### for subsections
   - Do NOT include table of contents

2. **Content Quality**:
   - Target word count: 2500-3500 words
   - Content must be original, valuable, and in-depth
   - Avoid repetition and filler content
   - Each paragraph must contain substantial content
   - Provide specific examples and practical advice

3. **SEO Optimization**:
   - Naturally integrate relevant keywords
   - Use semantically related vocabulary
   - Create valuable content links
   - Include practical FAQ section

4. **Format Requirements**:
   - Use **bold** to emphasize key points
   - Use *italic* for definitions
   - Use > for important quotes or callouts
   - Use - or * for lists
   - Use ```code blocks``` for technical content
   - Use tables for comparison data

5. **Article Structure Template**:
**Important Reminders**:
- Ensure each section has substantial content, don't repeat to fill word count
- Content should be logical and coherent
- Provide practical value, not empty theory
- Language should be professional but accessible
- Do NOT include any table of contents or navigation sections

Please begin writing:
"""

    try:
        # 尝试生成文章内容
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000,
            presence_penalty=0.1,  # 添加presence_penalty以减少重复
            frequency_penalty=0.1  # 添加frequency_penalty以增加用词多样性
        )

        # 检查响应是否有效
        if not response or not response.choices:
            print("Error: Empty response from API")
            return None

        # 提取并清理文章内容
        article_content = response.choices[0].message.content.strip()
        if not article_content:
            print("Error: Empty article content")
            return None

        # 检查文章内容长度
        if len(article_content.split()) < 100:  # 内容过短可能表示生成不完整
            print("Error: Article content too short")
            return None

        return article_content

    except Exception as e:
        print(f"Error generating article: {str(e)}")
        # 记录详细错误信息
        print(f"Detailed error: {traceback.format_exc()}")
        return None


def fix_format_issues(content):
    """Fix formatting issues"""
    if not content:
        return content

    # Fix heading format
    content = re.sub(r'^#{4,}', '###', content, flags=re.MULTILINE)

    # Ensure headings have blank lines before and after
    content = re.sub(r'\n(#{1,3}\s+[^\n]+)\n', r'\n\n\1\n\n', content)

    # Fix list format
    content = re.sub(r'\n([*-]\s+)', r'\n\n\1', content)

    # Remove excessive blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content.strip()


def search_local_images(keywords, image_dir="pixabay_ai_images", max_images=3):
    """Search for local images based on keywords"""
    if not os.path.exists(image_dir):
        return []

    # Clean and split keywords
    clean_keywords = []
    for keyword in keywords:
        # Remove special characters, convert to lowercase
        clean_keyword = re.sub(r'[^a-zA-Z0-9\s]', '', keyword.lower())
        clean_keywords.extend(clean_keyword.split())

    # Get all image files
    image_files = glob.glob(f"{image_dir}/*.webp")

    # Calculate match scores
    matches = []
    for image_file in image_files:
        filename = os.path.basename(image_file).lower()
        score = 0

        for keyword in clean_keywords:
            if keyword in filename:
                score += len(keyword) * 2  # Higher score for exact matches
            else:
                # Use similarity matching
                similarity = SequenceMatcher(None, keyword, filename).ratio()
                if similarity > 0.3:
                    score += similarity

        if score > 0:
            matches.append((image_file, score))

    # Sort by score and return top N
    matches.sort(key=lambda x: x[1], reverse=True)
    return [match[0] for match in matches[:max_images]]


def insert_images_from_local(content, keywords, image_dir="pixabay_ai_images", github_username="xiaotiancaixmy", repo_name="seo-article-gen", branch="main"):
    """Insert GitHub-hosted images into article"""
    if not content:
        return content
    
    # 检查内容中是否已经有图片，避免重复插入
    if '![' in content and 'github.com' in content:
        print("📷 图片已存在，跳过重复插入")
        return content

    # Search for relevant images
    selected_images = search_local_images(keywords, image_dir, max_images=3)

    if not selected_images:
        print("⚠️ 未找到匹配的图片文件")
        return content

    lines = content.split('\n')
    new_lines = []
    image_index = 0
    inserted_after_title = False

    for i, line in enumerate(lines):
        new_lines.append(line)

        # Insert first image after H1 title (only once)
        if line.startswith('# ') and not inserted_after_title and image_index < len(selected_images):
            image_path = selected_images[image_index]
            image_name = os.path.basename(image_path)
            github_url = f"https://raw.githubusercontent.com/{github_username}/{repo_name}/{branch}/pixabay_ai_images/{image_name}"
            alt_text = f"Illustration about {keywords[0] if keywords else 'topic'}"
            new_lines.append('')
            new_lines.append(f'![{alt_text}]({github_url})')
            new_lines.append('')
            image_index += 1
            inserted_after_title = True
            print(f"📷 已插入标题后图片: {image_name}")

        # Insert images after main H2 headings
        elif line.startswith('## ') and image_index < len(selected_images):
            # Skip table of contents, FAQ, conclusion sections
            if not any(skip_word in line.lower() for skip_word in ['contents', 'table of contents', 'faq', 'conclusion', 'summary']):
                image_path = selected_images[image_index]
                image_name = os.path.basename(image_path)
                github_url = f"https://raw.githubusercontent.com/{github_username}/{repo_name}/{branch}/pixabay_ai_images/{image_name}"
                section_title = line.replace('## ', '').strip()
                alt_text = f"Image related to {section_title}"
                new_lines.append('')
                new_lines.append(f'![{alt_text}]({github_url})')
                new_lines.append('')
                image_index += 1
                print(f"📷 已插入章节图片: {image_name} for {section_title}")

    print(f"📷 总共插入了 {image_index} 张图片")
    return '\n'.join(new_lines)


def count_words(text):
    """Count words in both English and Chinese"""
    if not text:
        return 0

    # Remove Markdown formatting
    clean_text = re.sub(r'[#*`>\-\[\]\(\)]', '', text)
    clean_text = re.sub(r'!\[.*?\]\(.*?\)', '', clean_text)  # Remove images

    # Count Chinese characters
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', clean_text))

    # Count English words
    english_words = len(re.findall(r'\b[a-zA-Z]+\b', clean_text))

    return chinese_chars + english_words


def check_format_and_grammar(content):
    """Check format and basic grammar"""
    issues = []

    if not content:
        return ["Content is empty"]

    # Check for main title
    if not re.search(r'^# ', content, re.MULTILINE):
        issues.append("Missing main title (# )")

    # Check for section headings
    if not re.search(r'^## ', content, re.MULTILINE):
        issues.append("Missing section headings (## )")

    # Check word count
    word_count = count_words(content)
    if word_count < 2000:
        issues.append(f"Insufficient word count: {word_count} < 2000")
    elif word_count > 4000:
        issues.append(f"Excessive word count: {word_count} > 4000")

    return issues


def save_article(content, output_dir, filename):
    """Save article to file"""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath


def validate_and_fix_links(content, client, model_name):
    """验证并修复文章中的外部链接"""
    import re
    
    # 提取所有外部链接
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    links = re.findall(link_pattern, content)
    
    fixed_content = content
    
    for link_text, url in links:
        # 跳过图片链接和内部链接
        if url.startswith('http') and not 'github.com' in url and not 'pixabay.com' in url:
            if not is_valid_url(url):
                print(f"⚠️ 发现无效链接: {url}")
                # 根据链接文本和上下文重新搜索有效链接
                new_url = find_alternative_link(link_text, client, model_name)
                if new_url:
                    fixed_content = fixed_content.replace(f'[{link_text}]({url})', f'[{link_text}]({new_url})')
                    print(f"✅ 已替换为: {new_url}")
                else:
                    # 如果找不到替代链接，移除该链接但保留文本
                    fixed_content = fixed_content.replace(f'[{link_text}]({url})', link_text)
                    print(f"❌ 已移除无效链接，保留文本: {link_text}")
    
    return fixed_content

def is_valid_url(url, timeout=10):
    """检查URL是否有效"""
    try:
        # 基本URL格式检查
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # 发送HEAD请求检查可访问性
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code < 400
    
    except Exception as e:
        print(f"URL验证失败 {url}: {e}")
        return False

def find_alternative_link(link_text, client, model_name):
    """根据链接文本找到替代的有效链接"""
    try:
        prompt = f"""
请为以下内容找到一个真实有效的相关网站链接：

链接描述：{link_text}

要求：
1. 必须是真实存在的网站
2. 内容与描述相关
3. 优先选择权威网站（如官方网站、知名媒体、学术机构等）
4. 只返回URL，不要其他内容
5. 如果找不到合适的链接，返回"NONE"

示例：
- 如果是"OpenAI官方网站"，返回：https://openai.com
- 如果是"arXiv论文"，返回：https://arxiv.org
- 如果是"GitHub"，返回：https://github.com

请返回URL：
"""
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=100
        )
        
        suggested_url = response.choices[0].message.content.strip()
        
        # 验证建议的URL
        if suggested_url != "NONE" and is_valid_url(suggested_url):
            return suggested_url
        
    except Exception as e:
        print(f"查找替代链接失败: {e}")
    
    return None


def check_format_and_grammar(content):
    """Check format and basic grammar"""
    issues = []

    if not content:
        return ["Content is empty"]

    # Check for main title
    if not re.search(r'^# ', content, re.MULTILINE):
        issues.append("Missing main title (# )")

    # Check for section headings
    if not re.search(r'^## ', content, re.MULTILINE):
        issues.append("Missing section headings (## )")

    # Check word count
    word_count = count_words(content)
    if word_count < 2000:
        issues.append(f"Insufficient word count: {word_count} < 2000")
    elif word_count > 4000:
        issues.append(f"Excessive word count: {word_count} > 4000")

    return issues


def save_article(content, output_dir, filename):
    """Save article to file"""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath


def generate_article_from_outline(client, model_name, outline, title, keywords=None, output_dir="output/articles"):
    """Generate complete article from outline"""
    print(f"Starting article generation: {title}")
    print(f"📝 关键词: {keywords}")

    # Generate article content
    content = generate_article_content(client, model_name, outline, title)

    if not content:
        print("❌ Article generation failed")
        return None

    # Fix formatting issues
    content = fix_format_issues(content)

    # Insert relevant images (确保有关键词时才插入)
    if keywords and len(keywords) > 0:
        print("📷 开始插入图片...")
        content = insert_images_from_local(content, keywords)
    else:
        print("⚠️ 没有关键词，跳过图片插入")
    
    # 验证和修复外部链接
    print("🔍 验证文章中的外部链接...")
    content = validate_and_fix_links(content, client, model_name)

    # Check content quality
    issues = check_format_and_grammar(content)

    if issues:
        print(f"⚠️ Issues found: {', '.join(issues)}")

        # If word count is insufficient, try to optimize rather than simply rewrite
        if any("Insufficient word count" in issue for issue in issues):
            print("Optimizing content length...")

            optimize_prompt = f"""
Please optimize the following article to make it more detailed and complete, but do not repeat existing content.

Current article:
{content}

Optimization requirements:
1. Add more practical details and examples to existing sections
2. Expand each point with deeper explanations
3. Add more real-world application scenarios
4. Ensure content is valuable, don't repeat just to fill word count
5. Maintain original structure and logic
6. Target word count: 2500-3500 words
7. make sure H3 details need to have at least 100 words for each.
8. DO NOT remove or modify existing images

Please return the optimized complete article:
"""

            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": optimize_prompt}],
                    temperature=0.6,
                    max_tokens=4000
                )
                optimized_content = response.choices[0].message.content.strip()

                if optimized_content:
                    content = fix_format_issues(optimized_content)
                    # 不要重复插入图片，因为优化后的内容应该保留原有图片
                    print("✅ Content optimization completed")

            except Exception as e:
                print(f"Error during optimization: {e}")

    # Final check
    final_word_count = count_words(content)
    print(f"📊 Final word count: {final_word_count}")

    # Save article
    timestamp = random.randint(1000, 9999)
    filename = f"article_{timestamp}.md"
    filepath = save_article(content, output_dir, filename)

    print(f"✅ Article saved: {filepath}")
    return filepath


def generate_articles_from_outlines(client, model_name, input_file, output_dir, metadata_file=None):
    """Batch generate articles from outline file"""
    with open(input_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        outlines = [row[0] for row in reader]

    # Try to read keywords (if available)
    keywords_list = []
    keyword_file = "data/keyword.csv"
    if os.path.exists(keyword_file):
        with open(keyword_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            keywords_list = [row[0].split(',') if row else [] for row in reader]

    # Try to read titles (if available)
    titles_list = []
    title_file = "data/title.csv"
    if os.path.exists(title_file):
        with open(title_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            titles_list = [row[0] if row else f"Article {i+1}" for i, row in enumerate(reader)]

    generated_files = []

    for i, outline in enumerate(outlines):
        title = titles_list[i] if i < len(titles_list) else f"Article {i+1}"
        keywords = keywords_list[i] if i < len(keywords_list) else []

        filepath = generate_article_from_outline(
            client, model_name, outline, title, keywords, output_dir
        )

        if filepath:
            generated_files.append(filepath)

        print(f"Progress: {i+1}/{len(outlines)}")
        print("-" * 50)

    print(f"\n🎉 Batch generation completed! Generated {len(generated_files)} articles")
    print(f"Articles saved in: {output_dir}")

    return generated_files