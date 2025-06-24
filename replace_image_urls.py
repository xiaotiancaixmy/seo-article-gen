import os
import re
import glob

def replace_local_images_with_github_urls(github_username="xiaotiancaixmy", repo_name="seo-article-gen", branch="main"):
    """
    替换所有Markdown文件中的本地图片路径为GitHub raw链接
    """
    # 查找所有Markdown文件
    md_files = glob.glob("output/articles/*.md")
    
    # 本地图片路径的正则表达式模式
    local_image_pattern = r'!\[([^\]]*)\]\(\.\.?/?\.\./pixabay_ai_images/([^\)]+)\)'
    
    for md_file in md_files:
        print(f"处理文件: {md_file}")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找所有匹配的图片引用
        matches = re.findall(local_image_pattern, content)
        
        if matches:
            print(f"  找到 {len(matches)} 个本地图片引用")
            
            # 替换每个匹配项
            def replace_match(match):
                alt_text = match.group(1)
                filename = match.group(2)
                github_url = f"https://raw.githubusercontent.com/{github_username}/{repo_name}/{branch}/pixabay_ai_images/{filename}"
                return f"![{alt_text}]({github_url})"
            
            # 执行替换
            new_content = re.sub(local_image_pattern, replace_match, content)
            
            # 写回文件
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✅ 已替换完成")
        else:
            print(f"  ℹ️  未找到需要替换的图片引用")

if __name__ == "__main__":
    print("开始替换本地图片路径为GitHub raw链接...")
    replace_local_images_with_github_urls()
    print("\n🎉 所有文件处理完成！")