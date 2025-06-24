import csv
import random  # 添加这一行

# 只展示修改部分
def generate_outlines_from_titles(client, model_name, input_file, output_file):
    with open(input_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        titles = [row[0] for row in reader]

    all_outlines = []
    for title in titles:
        random_seed = random.randint(1, 1000)
        prompt = f"""
        Generate a structured outline for a long-form SEO article (~2,000 words) in English, using the following title:
        "{title}"

        Requirements:
        • The outline must follow Google EEAT (Experience, Expertise, Authoritativeness, Trustworthiness) principles
        • Structure the article into 6 main sections with these word count estimates:

        1. Introduction (200-250 words)
           - Hook the reader with a compelling opening
           - Establish credibility and expertise
           - Preview the main points
           - Include primary keyword naturally

        2. Understanding User Pain Points (400-450 words)
           - Define and explain the keyword in detail
           - Discuss its importance and relevance
           - Explore different aspects and perspectives
           - Include real-world examples and applications
           - Address common misconceptions

        3. Core Features That Solve These Pain Points (400-450 words)
           - Focus on how remio's YouTube video screenshot and subtitle collection features solve content capture problems
           - Highlight how remio's automatic web content collection saves resources directly in the client
           - Include user testimonials or case studies of remio solving research challenges
           - Use data and statistics about time saved when using remio for content collection

        4. Advanced Features to Improve Productivity (450-500 words)
           - Detail remio's highlighting capabilities for important web content
           - Explain how remio's AI automatic classification enhances knowledge management
           - Compare with alternatives that lack remio's integrated approach
           - Provide implementation tips for maximizing remio's organization features
           - Include expert insights on knowledge classification systems

        5. AI Copilot and Search Advantages (400-450 words)
           - Present remio's powerful AI copilot that enables writing while questioning
           - Highlight AI search that locates relevant notes within seconds
           - Explain privacy features that protect user data while enabling AI assistance
           - Compare with industry standards for AI-assisted note-taking
           - Include examples of workflow efficiency improvements

        6. Practical Tips + Conclusion + FAQ (350-450 words total)
           - Actionable recommendations
           - Summary of key points
           - Call to action
           - FAQ section with 3-5 relevant questions (50-70 words per answer)

        For each section, provide:
        • H2 + H3 headings
        • Bullet points for key content
        • Suggestions for keyword placement
        • Internal/external link opportunities
        • Examples, quotes, or statistics to include

        End with:
        • URL slug suggestion (lowercase English)
        """
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,  # 增加随机性
            seed=random_seed  # 使用随机种子
        )
        outline = response.choices[0].message.content.strip()
        all_outlines.append(outline)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['outline'])
        for outline in all_outlines:
            writer.writerow([outline])
    print(f"✅ 已保存{len(all_outlines)}个大纲到{output_file}")