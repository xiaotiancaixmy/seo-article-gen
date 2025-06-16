import csv

def generate_titles_from_keywords(client, model_name, input_file, output_file):
    with open(input_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        keywords = [row[0] for row in reader]

    all_titles = []
    for keyword in keywords:
        prompt = f"""
        Generate 2-3 educational article titles for the keyword: {keyword}
        The titles should follow these patterns:
        1. "What is [keyword]? A Comprehensive Guide"
        2. "How to [keyword]: Tips and Best Practices"
        3. "Understanding [keyword]: A Beginner's Guide"

        Make the titles engaging and SEO-friendly. Focus on educational and informative content.
        Output each title on a new line without any additional text or numbering.
        """
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        titles = response.choices[0].message.content.strip().split('\n')
        all_titles.extend([t.strip() for t in titles if t.strip()])

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['title'])
        for title in all_titles:
            writer.writerow([title])
    print("✅ Saved titles to", output_file)