
import os
from openai import OpenAI
from config import OPENROUTER_API_KEY, KEYWORD_MODEL, OUTLINE_MODEL, ARTICLE_MODEL
from step1_keyword import generate_keywords_via_openrouter
from step2_titles import generate_titles_from_keywords
from step3_reference import generate_references_from_titles
from step4_summary import generate_summaries_from_references
from step5_outline import generate_outlines_from_titles_and_references
from step6_generate_article import generate_articles_from_outlines

client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

data_dir = "data"
output_dir = "output"
os.makedirs(data_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

keyword_csv = os.path.join(data_dir, "keyword.csv")
title_csv = os.path.join(data_dir, "title.csv")
reference_csv = os.path.join(data_dir, "reference.csv")
summary_csv = os.path.join(data_dir, "summary.csv")
outline_csv = os.path.join(data_dir, "outline.csv")
article_dir = os.path.join(output_dir, "articles")
metadata_csv = os.path.join(output_dir, "metadata.csv")
os.makedirs(article_dir, exist_ok=True)

def main():
    print("🚀 Step 1: Generating keywords from website...")
    generate_keywords_via_openrouter(client, KEYWORD_MODEL, keyword_csv)

    print("📝 Step 2: Generating titles...")
    generate_titles_from_keywords(client, KEYWORD_MODEL, keyword_csv, title_csv)
    
    print("🔍 Step 3: Generating references...")
    generate_references_from_titles(client, KEYWORD_MODEL, title_csv, reference_csv)
    
    print("📋 Step 4: Generating summaries...")
    generate_summaries_from_references(client, KEYWORD_MODEL, reference_csv, summary_csv)

    print("🧱 Step 5: Generating outlines...")
    generate_outlines_from_titles_and_references(client, OUTLINE_MODEL, title_csv, reference_csv, summary_csv, outline_csv)

    print("📄 Step 6: Generating articles...")
    generate_articles_from_outlines(client, ARTICLE_MODEL, outline_csv, article_dir, metadata_csv)

    print("✅ All done. Check output.")

if __name__ == "__main__":
    main()