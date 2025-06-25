import csv
import random

def generate_titles_from_keywords(client, model_name, input_file, output_file):
    with open(input_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        keywords = [row[0] for row in reader]

    all_titles = []
    for keyword in keywords:
        random_seed = random.randint(1, 1000)
        prompt = f"""
        Generate 2 educational article titles for the keyword: {keyword}
 

        Use random seed: {random_seed} to ensure unique results.
        Make the titles engaging and SEO-friendly. Focus on educational and informative content.
        title need to be catch the attention of the reader, and lead readers into the topic.
        Output each title on a new line without any additional text or numbering.
        make sure only output only titles. Nothing else.
        and the concept need to be more wiki like.
        """
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,  # 增加随机性
            seed=random_seed  # 使用随机种子
        )
        titles = response.choices[0].message.content.strip().split('\n')
        all_titles.extend([t.strip() for t in titles if t.strip()])

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['title'])
        for title in all_titles:
            writer.writerow([title])
    print(f"✅ 已保存{len(all_titles)}个标题到{output_file}")