import os, csv
import random

def generate_articles_from_outlines(client, model_name, input_file, output_dir, metadata_file):
    with open(input_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        outlines = [row[0] for row in reader]

    os.makedirs(output_dir, exist_ok=True)
    article_file = os.path.join(output_dir, "articles.md")
    
    # 清空文件，准备写入
    with open(article_file, 'w', encoding='utf-8') as md_file:
        md_file.write("")
        
    for i, outline in enumerate(outlines):
        random_seed = random.randint(1, 1000)
        prompt = f"""
        Generate a comprehensive SEO-optimized article in Markdown format following the provided outline. The article should be >2,000 words, written in a third-person, educational tone.

        Follow this outline: {outline}

        Markdown Formatting Requirements:
        1. Use proper heading levels:
           - # for H1 (title)
           - ## for H2 (main sections)
           - ### for H3 (subsections)

        2. Use Markdown features for better readability:
           - Bullet points with *
           - Numbered lists where appropriate
           - **Bold** for emphasis
           - _Italic_ for definitions or key terms
           - > for important quotes or callouts
           - `code` for technical terms
           - --- for section breaks

        3. Structure each section with:
           - Clear headings
           - Well-organized paragraphs
           - Bullet points for lists
           - Examples in blockquotes
           - Citations where appropriate

        4. Include a table of contents at the start:
           ```markdown
           ## Table of Contents
           - [Introduction](#introduction)
           - [Understanding User Pain Points](#understanding-user-pain-points)
           - [Core Features](#core-features)
           - [Advanced Features](#advanced-features)
           - [Privacy & Security](#privacy-and-security)
           - [Practical Tips & FAQ](#practical-tips-and-faq)
           ```

        5. End with a properly formatted FAQ section:
           ```markdown
           ## Frequently Asked Questions

           ### Question 1?
           Answer to question 1...

           ### Question 2?
           Answer to question 2...
           ```

        Use random seed: {random_seed} to ensure unique content.
        Remember to:
        - Use proper Markdown syntax throughout
        - Include anchor links for internal navigation
        - Format code blocks, tables, and lists correctly
        - Add horizontal rules (---) between major sections
        - Use consistent formatting throughout the article
        """
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,  # 增加随机性
            seed=random_seed  # 使用随机种子
        )
        article_content = response.choices[0].message.content.strip()
        
        # 追加到文件而不是覆盖
        with open(article_file, 'a', encoding='utf-8') as md_file:
            md_file.write(f"\n\n# Article {i+1}\n\n")
            md_file.write(article_content)
            md_file.write("\n\n---\n\n")
        
        print(f"✅ 文章 {i+1} 已保存到 {article_file}")
        
        # 计算单词数
        total_words = len(article_content.split())
        print(f"文章 {i+1} 字数: {total_words}")
        
        # 确保单词数在2000-3000之间
        if total_words < 2000:
            rewrite_prompt = f"""
            Please rewrite the article to ensure it is between 2000-3000 words, while maintaining the focus on the original topic. Use this outline as reference: {outline}
            """
            rewrite_response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": rewrite_prompt}],
                temperature=0.9,
                seed=random.randint(1, 1000)  # 新的随机种子
            )
            rewritten_article = rewrite_response.choices[0].message.content.strip()
            
            # 覆盖之前的内容
            with open(article_file, 'r', encoding='utf-8') as md_file:
                content = md_file.read()
            
            # 替换特定文章的内容
            article_marker = f"# Article {i+1}\n\n"
            end_marker = "\n\n---\n\n"
            start_idx = content.find(article_marker) + len(article_marker)
            end_idx = content.find(end_marker, start_idx)
            
            new_content = content[:start_idx] + rewritten_article + content[end_idx:]
            
            with open(article_file, 'w', encoding='utf-8') as md_file:
                md_file.write(new_content)
            
            print(f"✅ 重写的文章 {i+1} 已保存到 {article_file}")
            total_words = len(rewritten_article.split())
            print(f"重写后文章 {i+1} 字数: {total_words}")
    
    print