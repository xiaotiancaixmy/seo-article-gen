
import os
from openai import OpenAI
from config import OPENROUTER_API_KEY, KEYWORD_MODEL, OUTLINE_MODEL, ARTICLE_MODEL
from step1_keyword import generate_keywords_via_openrouter
from step2_titles import generate_titles_from_keywords
from step3_outline import generate_outlines_from_titles
from step4_generate_article import generate_articles_from_outlines

client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

data_dir = "data"
output_dir = "output"
os.makedirs(data_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

keyword_csv = os.path.join(data_dir, "keyword.csv")
title_csv = os.path.join(data_dir, "title.csv")
outline_csv = os.path.join(data_dir, "outline.csv")
article_dir = os.path.join(output_dir, "articles")
metadata_csv = os.path.join(output_dir, "metadata.csv")
os.makedirs(article_dir, exist_ok=True)

def main():
    print("🚀 Step 1: Generating keywords from website...")
    generate_keywords_via_openrouter(client, KEYWORD_MODEL, keyword_csv)

    print("📝 Step 2: Generating titles...")
    generate_titles_from_keywords(client, KEYWORD_MODEL, keyword_csv, title_csv)

    print("🧱 Step 3: Generating outlines...")
    generate_outlines_from_titles(client, OUTLINE_MODEL, title_csv, outline_csv)

    print("📄 Step 4: Generating articles...")
    generate_articles_from_outlines(client, ARTICLE_MODEL, outline_csv, article_dir, metadata_csv)

    print("✅ All done. Check output.")

if __name__ == "__main__":
    main()