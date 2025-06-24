# SEO Article Generator (Auto Pipeline)

一个基于OpenRouter GPT模型的SEO文章自动生成器，可以从社交媒体趋势中提取关键词并生成高质量的SEO优化文章。

## 功能特点

- 从X（Twitter）获取热门AI相关关键词
- 自动生成SEO友好的文章标题
- 生成符合Google EEAT原则的文章大纲
- 生成2000字以上的Markdown格式文章
- 支持批量生成多篇文章
- 包含元数据和URL优化建议

## 项目结构

```
├── data/               # 存储生成的关键词、标题和大纲
├── output/             # 存储生成的文章
├── step1_keyword.py    # 关键词生成模块
├── step2_titles.py     # 标题生成模块
├── step3_outline.py    # 大纲生成模块
├── step4_generate_article.py  # 文章生成模块
└── main.py            # 主程序入口
```

## 环境配置

1. 安装依赖：
```bash
pip install openai jinja2
```

2. 配置API密钥：
- 创建config.py文件
- 设置OpenRouter API密钥和模型名称

## 使用方法

运行主程序：
```bash
python main.py
```

## 输出结果

- 关键词保存在 data/keyword.csv
- 标题保存在 data/title.csv
- 大纲保存在 data/outline.csv
- 生成的文章保存在 output/articles/articles.md