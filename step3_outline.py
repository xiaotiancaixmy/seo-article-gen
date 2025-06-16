import csv

def generate_outlines_from_titles(client, model_name, input_file, output_file):
    with open(input_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        titles = [row[0] for row in reader]

    all_outlines = []
    for title in titles:
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
           - Focus on primary solutions
           - Include user testimonials or case studies
           - Highlight key benefits
           - Use data and statistics when possible

        4. Advanced Features to Improve Productivity (450-500 words)
           - Detail advanced capabilities
           - Compare with alternatives
           - Provide implementation tips
           - Include expert insights

        5. Privacy & Security Advantages (400-450 words)
           - Address security concerns
           - Explain privacy features
           - Compare with industry standards
           - Include compliance information

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
            messages=[{"role": "user", "content": prompt}]
        )
        outline = response.choices[0].message.content.strip()
        all_outlines.append(outline)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['outline'])
        for outline in all_outlines:
            writer.writerow([outline])
    print("✅ Saved outlines to", output_file)