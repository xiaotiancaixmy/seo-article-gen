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
        Generate a comprehensive structured outline for a long-form SEO article (~2,000-3,000 words) in English, using the following title:
    "{title}"

    Requirements:
    • Follow Google EEAT (Experience, Expertise, Authoritativeness, Trustworthiness) principles
    • Create an in-depth, authoritative guide on the topic
   •	Begin with a concise lead section defining the topic.
	  ( •	Include sections like:
	   •	History / Origin
	   •	Key Concepts
	   •	Applications / Use Cases
	   •	Advantages and Limitations
	   •	Related Topics
	   •	References & External Links (as placeholders) )
	•	Do not write the full article. Only generate the structured outline.
	•	Avoid first-person tone or marketing language.
    • Structure into 6-8 main sections with estimated word counts
    • Include relevant subtopics and key points for each section
    • Suggest internal and external link opportunities
    • Include FAQ section with 5-7 relevant questions
    • Provide URL slug suggestion

    For each section, provide:
    • Specific H2/H3 headings with target keywords
    • Detailed bullet points for content coverage
    • Keyword placement suggestions
    • Link opportunities and references
    • Examples and case studies to include

    End with:
    • URL slug suggestion (SEO-friendly, lowercase)
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