import os, csv

def generate_articles_from_outlines(client, model_name, input_file, output_dir, metadata_file):
    with open(input_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        outlines = [row[0] for row in reader]

    prompt = """
    Generate a comprehensive SEO-optimized article in Markdown format following the provided outline. The article should be >2,000 words, written in a third-person, educational tone.

    Follow this outline: {{outline}}

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

    Remember to:
    - Use proper Markdown syntax throughout
    - Include anchor links for internal navigation
    - Format code blocks, tables, and lists correctly
    - Add horizontal rules (---) between major sections
    - Use consistent formatting throughout the article
    """
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    article_content = response.choices[0].message.content.strip()
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "articles.md"), 'w', encoding='utf-8') as md_file:
        md_file.write(article_content)
    print("✅ Articles saved to", os.path.join(output_dir, "articles.md"))
    
    # Count total words
    total_words = len(article_content.split())
    print(f"Total word count: {total_words}")
    
    # Ensure word count is between 2000-3000
    if total_words < 2000:
        rewrite_prompt = """
        Please rewrite the article to ensure it is between 2000-3000 words, while maintaining the focus on remio ai - ai assistant's features and benefits.
        """
        rewrite_response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": rewrite_prompt}]
        )
        rewritten_article = rewrite_response.choices[0].message.content.strip()
        with open(os.path.join(output_dir, "articles.md"), 'w', encoding='utf-8') as md_file:
            md_file.write(rewritten_article)
        print("✅ Rewritten article saved to", os.path.join(output_dir, "articles.md"))
        total_words = len(rewritten_article.split())
        print(f"Total word count after rewrite: {total_words}")