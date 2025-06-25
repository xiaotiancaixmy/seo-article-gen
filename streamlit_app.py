import streamlit as st
import pandas as pd
import os
import zipfile
import io
from openai import OpenAI
import csv  
from datetime import datetime

# 导入生成函数 - 修正函数名
from step1_keyword import generate_keywords
from step2_titles import generate_titles_from_keywords
from step3_reference import generate_references_from_titles
from step4_summary import generate_summaries_from_references
from step5_outline import generate_outlines_from_titles_and_references  # 修正函数名
from step6_generate_article import generate_articles_from_outlines
from config import *

# 设置页面配置
st.set_page_config(
    page_title="SEO文章生成器",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化OpenRouter客户端
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# 创建必要的目录
data_dir = "data"
output_dir = "output"
os.makedirs(data_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)
os.makedirs(os.path.join(output_dir, "articles"), exist_ok=True)

# 初始化session state
if 'selected_keywords' not in st.session_state:
    st.session_state.selected_keywords = []
if 'selected_titles' not in st.session_state:
    st.session_state.selected_titles = []
if 'selected_references' not in st.session_state:
    st.session_state.selected_references = []
if 'selected_summaries' not in st.session_state:
    st.session_state.selected_summaries = []
if 'selected_outlines' not in st.session_state:
    st.session_state.selected_outlines = []

def save_selected_data(selected_items, file_path, column_name):
    """保存选择的数据到CSV文件"""
    if selected_items:
        df_selected = pd.DataFrame({column_name: selected_items})
        df_selected.to_csv(file_path, index=False)
        return True
    return False

def main():
    st.title("📝 SEO文章生成器")
    st.markdown("""
    这是一个基于AI的SEO文章生成工具，可以帮助您：
    - 🔍 生成相关关键词
    - 📝 创建吸引人的标题
    - 📚 收集参考资料
    - 📋 生成内容摘要
    - 🧱 构建文章大纲
    - 📄 生成完整文章
    """)
    
    # 创建标签页
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🔍 关键词生成", 
        "📝 标题生成", 
        "📚 参考资料生成",
        "📋 内容摘要生成",
        "🧱 大纲生成", 
        "📄 文章生成", 
        "📊 结果查看"
    ])
    
    # Tab 1: 关键词生成
    with tab1:
        st.header("🔍 Step 1: 关键词生成")
        st.markdown("""
        输入主题，AI将为您生成相关的SEO关键词。
        - 长尾关键词优化
        - 竞争度分析
        - 搜索意图匹配
        """)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            topic = st.text_input("请输入主题:", placeholder="例如：人工智能在医疗中的应用")
            
            # 添加知识范围选择
            knowledge_scope_options = {
                "AI/人工智能": "AI",
                "科技/技术": "科技", 
                "商业/营销": "商业",
                "教育/学习": "教育",
                "自定义范围": "custom"
            }
            
            # 知识范围选择
            selected_scope = st.selectbox(
                "选择知识范围:",
                options=list(knowledge_scope_options.keys()),
                index=0
            )
            
            # 自定义范围处理
            if selected_scope == "自定义范围":
                custom_scope = st.text_input("请输入自定义知识范围:", placeholder="例如：医疗健康")
                knowledge_scope = custom_scope if custom_scope else topic
            else:
                knowledge_scope = knowledge_scope_options[selected_scope]
            
            # 关键词数量
            num_keywords = st.slider("关键词数量:", min_value=5, max_value=50, value=20, step=5)
            
            # 生成关键词
            if st.button("🔍 生成关键词", type="primary", use_container_width=True):
                if topic:
                    # 检查必要参数是否存在
                    if not os.path.exists(data_dir):
                        os.makedirs(data_dir)
                    keyword_csv = os.path.join(data_dir, "keyword.csv")
                    
                    try:
                        generate_keywords(
                            client=client,
                            model_name=KEYWORD_MODEL, 
                            output_file=keyword_csv,
                            num_keywords=num_keywords,
                            knowledge_scope=knowledge_scope,
                            topic=topic 
                        )
                        st.success("关键词生成成功!")
                    except Exception as e:
                        st.error(f"生成关键词时发生错误: {str(e)}")
                else:
                    st.warning("请先输入主题")
        
        with col2:
            # 显示生成的关键词并提供选择
            keyword_file = os.path.join(data_dir, "keyword.csv")
            if os.path.exists(keyword_file):
                try:
                    df_keywords = pd.read_csv(keyword_file)
                    st.subheader("📋 生成的关键词 - 请选择用于下一步的关键词")
                    
                    # 创建checkbox选择
                    selected_keywords = []
                    for idx, row in df_keywords.iterrows():
                        keyword = row['Keyword']  # 改为大写的 Keyword
                        if st.checkbox(f"🔑 {keyword}", key=f"keyword_{idx}", value=keyword in st.session_state.selected_keywords):
                            selected_keywords.append(keyword)
                    
                    # 更新session state
                    st.session_state.selected_keywords = selected_keywords
                    
                    if selected_keywords:
                        st.success(f"已选择 {len(selected_keywords)} 个关键词")
                        
                        # 保存选择的关键词
                        if st.button("💾 保存选择的关键词", use_container_width=True):
                            save_selected_data(selected_keywords, keyword_file, 'keyword')
                            st.success("选择已保存！")
                    else:
                        st.warning("请至少选择一个关键词")
                        
                except Exception as e:
                    st.warning("关键词文件读取失败")
    
    # Tab 2: 标题生成
    with tab2:
        st.header("📝 Step 2: 标题生成")
        st.markdown("""
        基于选择的关键词生成吸引人的文章标题。
        - SEO优化标题
        - 点击率优化
        - 多种风格选择
        """)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if not st.session_state.selected_keywords:
                st.warning("⚠️ 请先选择关键词")
            else:
                st.info(f"将为 {len(st.session_state.selected_keywords)} 个关键词生成标题")
                
                if st.button("📝 生成标题", type="primary", use_container_width=True):
                    with st.spinner("正在为选择的关键词生成标题..."):
                        try:
                            keyword_file = os.path.join(data_dir, "keyword.csv")
                            title_csv = os.path.join(data_dir, "title.csv")
                            generate_titles_from_keywords(client, TITLE_MODEL, keyword_file, title_csv)
                            st.success("标题生成完成！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"生成失败: {str(e)}")
        
        with col2:
            # 显示生成的标题并提供选择
            title_file = os.path.join(data_dir, "title.csv")
            if os.path.exists(title_file):
                try:
                    df_titles = pd.read_csv(title_file)
                    st.subheader("📋 生成的标题 - 请选择用于下一步的标题")
                    
                    # 创建checkbox选择
                    selected_titles = []
                    for idx, row in df_titles.iterrows():
                        title = row['title']
                        if st.checkbox(f"📝 {title}", key=f"title_{idx}", value=title in st.session_state.selected_titles):
                            selected_titles.append(title)
                    
                    # 更新session state
                    st.session_state.selected_titles = selected_titles
                    
                    if selected_titles:
                        st.success(f"已选择 {len(selected_titles)} 个标题")
                        
                        # 保存选择的标题
                        if st.button("💾 保存选择的标题", use_container_width=True):
                            save_selected_data(selected_titles, title_file, 'title')
                            st.success("选择已保存！")
                    else:
                        st.warning("请至少选择一个标题")
                        
                except Exception as e:
                    st.warning("标题文件读取失败")
    
    # Tab 3: 参考资料生成
    with tab3:
        st.header("📚 Step 3: 参考资料生成")
        st.markdown("""
        基于选择的标题生成相关的参考资料和权威来源。
        - 权威网站推荐
        - 学术研究资源
        - 行业统计数据
        - 专家观点来源
        """)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if not st.session_state.selected_titles:
                st.warning("⚠️ 请先选择标题")
            else:
                st.info(f"将为 {len(st.session_state.selected_titles)} 个标题生成参考资料")
                
                if st.button("📚 生成参考资料", type="primary", use_container_width=True):
                    with st.spinner("正在为选择的标题生成参考资料..."):
                        try:
                            title_file = os.path.join(data_dir, "title.csv")
                            reference_csv = os.path.join(data_dir, "reference.csv")
                            generate_references_from_titles(client, REFERENCE_MODEL, title_file, reference_csv)
                            st.success("参考资料生成完成！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"生成失败: {str(e)}")
        
        with col2:
            # 显示生成的参考资料并提供选择
            reference_file = os.path.join(data_dir, "reference.csv")
            if os.path.exists(reference_file):
                try:
                    df_references = pd.read_csv(reference_file)
                    st.subheader("📋 生成的参考资料 - 请选择用于下一步的参考资料")
                    
                    # 创建checkbox选择
                    selected_references = []
                    
                    # 初始化session state
                    if 'selected_references' not in st.session_state:
                        st.session_state.selected_references = []
                    
                    for idx, row in df_references.iterrows():
                        title = row['title']
                        reference_type = row['reference_type']
                        description = row['expected_info']
                        
                        reference_preview = f"{reference_type}: {description[:50]}..." if len(description) > 50 else f"{reference_type}: {description}"
                        
                        if st.checkbox(f"📚 {reference_preview}", key=f"reference_{idx}", value=idx in st.session_state.selected_references):
                            selected_references.append(idx)
                            
                        # 显示完整参考资料信息
                        with st.expander(f"查看完整参考资料 {idx+1}"):
                            st.write(f"**标题:** {title}")
                            st.write(f"**类型:** {reference_type}")
                            st.write(f"**描述:** {description}")
                            if 'raw_content' in row and pd.notna(row['raw_content']):
                                st.write(f"**原始内容:** {row['raw_content'][:200]}...")
                    
                    st.session_state.selected_references = selected_references
                    
                    if selected_references:
                        st.success(f"已选择 {len(selected_references)} 个参考资料")
                        
                        # 保存选择的参考资料
                        if st.button("💾 保存选择的参考资料", use_container_width=True):
                            # 保存选择的参考资料行
                            selected_df = df_references.iloc[selected_references]
                            selected_df.to_csv(reference_file, index=False)
                            st.success("选择已保存！")
                    else:
                        st.warning("请至少选择一个参考资料")
                        
                except Exception as e:
                    st.warning("参考资料文件读取失败")
    
    # Tab 4: 内容摘要生成
    with tab4:
        st.header("📋 Step 4: 内容摘要生成")
        st.markdown("""
        基于选择的参考资料生成内容摘要。
        - 核心概念提取
        - 关键数据汇总
        - 趋势分析
        - 案例研究总结
        """)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if not st.session_state.selected_references:
                st.warning("⚠️ 请先选择参考资料")
            else:
                st.info(f"将基于 {len(st.session_state.selected_references)} 个参考资料生成摘要")
                
                if st.button("📋 生成内容摘要", type="primary", use_container_width=True):
                    with st.spinner("正在基于参考资料生成内容摘要..."):
                        try:
                            reference_file = os.path.join(data_dir, "reference.csv")
                            summary_csv = os.path.join(data_dir, "summary.csv")
                            generate_summaries_from_references(client, SUMMARY_MODEL, reference_file, summary_csv)
                            st.success("内容摘要生成完成！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"生成失败: {str(e)}")
        
        with col2:
            # 显示生成的摘要并提供选择
            summary_file = os.path.join(data_dir, "summary.csv")
            if os.path.exists(summary_file):
                try:
                    df_summaries = pd.read_csv(summary_file)
                    st.subheader("📋 生成的内容摘要 - 请选择用于下一步的摘要")
                    
                    # 创建checkbox选择
                    selected_summaries = []
                    for idx, row in df_summaries.iterrows():
                        core_concepts = row['core_concepts']
                        main_points = row['main_points']
                        
                        summary_preview = f"核心概念: {core_concepts[:30]}..." if len(core_concepts) > 30 else f"核心概念: {core_concepts}"
                        
                        if st.checkbox(f"📋 摘要 {idx+1}: {summary_preview}", key=f"summary_{idx}", value=idx in st.session_state.selected_summaries):
                            selected_summaries.append(idx)
                            
                        # 显示完整摘要
                        with st.expander(f"查看完整摘要 {idx+1}"):
                            st.write(f"**核心概念:** {core_concepts}")
                            st.write(f"**主要观点:** {main_points}")
                            if 'key_data' in row:
                                st.write(f"**关键数据:** {row['key_data']}")
                            if 'case_studies' in row:
                                st.write(f"**案例研究:** {row['case_studies']}")
                            if 'trends' in row:
                                st.write(f"**趋势分析:** {row['trends']}")
                            if 'challenges_solutions' in row:
                                st.write(f"**挑战与解决方案:** {row['challenges_solutions']}")
                    
                    # 更新session state
                    st.session_state.selected_summaries = selected_summaries
                    
                    if selected_summaries:
                        st.success(f"已选择 {len(selected_summaries)} 个摘要")
                        
                        # 保存选择的摘要
                        if st.button("💾 保存选择的摘要", use_container_width=True):
                            # 保存选择的摘要行
                            selected_df = df_summaries.iloc[selected_summaries]
                            selected_df.to_csv(summary_file, index=False)
                            st.success("选择已保存！")
                    else:
                        st.warning("请至少选择一个摘要")
                        
                except Exception as e:
                    st.warning("摘要文件读取失败")
    
    # Tab 5: 大纲生成
    with tab5:
        st.header("🧱 Step 5: 大纲生成")
        st.markdown("""
        基于选择的标题、参考资料和内容摘要生成详细的文章大纲。
        - 遵循Google EEAT原则
        - 结构化的6个主要部分
        - 约2000字的长篇SEO文章大纲
        - 融合参考资料和摘要内容
        """)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if not st.session_state.selected_titles:
                st.warning("⚠️ 请先选择标题")
            elif not st.session_state.selected_summaries:
                st.warning("⚠️ 请先选择内容摘要")
            else:
                st.info(f"将为 {len(st.session_state.selected_titles)} 个标题生成大纲")
                st.info(f"基于 {len(st.session_state.selected_summaries)} 个摘要")
                
                # 在 Tab 5 中修正大纲生成调用
                if st.button("🧱 生成大纲", type="primary", use_container_width=True):
                    if st.session_state.selected_titles:
                        with st.spinner("正在生成大纲..."):
                            try:
                                title_csv = os.path.join(data_dir, "title.csv")
                                reference_csv = os.path.join(data_dir, "reference.csv")
                                summary_csv = os.path.join(data_dir, "summary.csv")
                                outline_csv = os.path.join(data_dir, "outline.csv")
                                
                                # 修正函数名和参数
                                generate_outlines_from_titles_and_references(
                                    client, 
                                    OUTLINE_MODEL, 
                                    title_csv, 
                                    reference_csv, 
                                    summary_csv, 
                                    outline_csv
                                )
                                st.success("大纲生成完成！")
                                st.rerun()
                            except Exception as e:
                                st.error(f"生成失败: {str(e)}")
                    else:
                        st.warning("请先选择标题")
        
        with col2:
            # 显示生成的大纲并提供选择
            outline_file = os.path.join(data_dir, "outline.csv")
            if os.path.exists(outline_file):
                try:
                    df_outlines = pd.read_csv(outline_file)
                    st.subheader("📋 生成的大纲 - 请选择用于下一步的大纲")
                    
                    # 创建checkbox选择
                    selected_outlines = []
                    for idx, row in df_outlines.iterrows():
                        outline = row['outline']
                        outline_preview = outline[:100] + "..." if len(outline) > 100 else outline
                        
                        if st.checkbox(f"📋 大纲 {idx+1}: {outline_preview}", key=f"outline_{idx}", value=outline in st.session_state.selected_outlines):
                            selected_outlines.append(outline)
                            
                        # 显示完整大纲
                        with st.expander(f"查看完整大纲 {idx+1}"):
                            st.text(outline)
                    
                    # 更新session state
                    st.session_state.selected_outlines = selected_outlines
                    
                    if selected_outlines:
                        st.success(f"已选择 {len(selected_outlines)} 个大纲")
                        
                        # 保存选择的大纲
                        if st.button("💾 保存选择的大纲", use_container_width=True):
                            save_selected_data(selected_outlines, outline_file, 'outline')
                            st.success("选择已保存！")
                    else:
                        st.warning("请至少选择一个大纲")
                        
                except Exception as e:
                    st.warning("大纲文件读取失败")
    
    # Tab 6: 文章生成
    with tab6:
        st.header("📄 Step 6: 文章生成")
        st.markdown("""
        基于选择的大纲生成完整的文章内容。
        - 使用GitHub链接的图片
        - Markdown格式输出
        - 2000-3000字的完整文章
        """)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if not st.session_state.selected_outlines:
                st.warning("⚠️ 请先选择大纲")
            else:
                st.info(f"将为 {len(st.session_state.selected_outlines)} 个大纲生成文章")
                
                if st.button("📄 生成文章", type="primary", use_container_width=True):
                    with st.spinner("正在生成完整文章..."):
                        try:
                            outline_file = os.path.join(data_dir, "outline.csv")
                            article_dir = os.path.join(output_dir, "articles")
                            metadata_csv = os.path.join(output_dir, "metadata.csv")
                            generate_articles_from_outlines(client, ARTICLE_MODEL, outline_file, article_dir, metadata_csv)
                            st.success("文章生成完成！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"生成失败: {str(e)}")
        
        with col2:
            # 显示生成进度和结果
            article_dir = os.path.join(output_dir, "articles")
            if os.path.exists(article_dir):
                # 获取所有生成的文章文件
                article_files = [f for f in os.listdir(article_dir) if f.endswith('.md')]
                if article_files:
                    # 按修改时间排序，获取最新的文件
                    latest_file = max(article_files, key=lambda x: os.path.getmtime(os.path.join(article_dir, x)))
                    article_file = os.path.join(article_dir, latest_file)
                    
                    st.success(f"✅ 已生成文章")
                    
                    # 显示文章统计信息
                    try:
                        with open(article_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            word_count = len(content.split())
                            char_count = len(content)
                            line_count = len(content.split('\n'))
                            
                        col_stat1, col_stat2, col_stat3 = st.columns(3)
                        with col_stat1:
                            st.metric("最新文章字数", f"{word_count:,}")
                        with col_stat2:
                            st.metric("字符数", f"{char_count:,}")
                        with col_stat3:
                            st.metric("总文章数", f"{len(article_files)}")
                            
                        # 存储最新文章路径到session state
                        st.session_state.latest_article_file = article_file
                        
                        # 下载选项
                        st.subheader("📥 下载选项")
                        
                        # 单篇文章下载
                        with open(article_file, 'rb') as f:
                            st.download_button(
                                label="📄 下载最新文章",
                                data=f.read(),
                                file_name=f"latest_article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                mime="text/markdown"
                            )
                        
                        # 多篇文章zip打包下载
                        if len(article_files) > 1:
                            def create_zip_file():
                                zip_buffer = io.BytesIO()
                                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                    for file_name in article_files:
                                        file_path = os.path.join(article_dir, file_name)
                                        zip_file.write(file_path, file_name)
                                zip_buffer.seek(0)
                                return zip_buffer.getvalue()
                            
                            st.download_button(
                                label=f"📦 下载所有文章 (ZIP包含{len(article_files)}篇)",
                                data=create_zip_file(),
                                file_name=f"all_articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                mime="application/zip"
                            )
                            
                    except Exception as e:
                        st.warning(f"无法读取文章统计信息: {str(e)}")
                else:
                    st.info("暂无生成的文章")
            else:
                st.info("暂无生成的文章")
    
    # Tab 7: 结果查看
    with tab7:
        st.header("📊 生成结果")
        
        # 显示选择统计
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("选择的关键词", len(st.session_state.selected_keywords))
        with col2:
            st.metric("选择的标题", len(st.session_state.selected_titles))
        with col3:
            st.metric("选择的参考资料", len(st.session_state.selected_references))
        with col4:
            st.metric("选择的摘要", len(st.session_state.selected_summaries))
        with col5:
            st.metric("选择的大纲", len(st.session_state.selected_outlines))
        
        # 在Tab 7的结果查看部分，修改文章预览逻辑
        st.subheader("📄 生成的文章")
        
        # 获取最新的文章文件
        article_dir = os.path.join(output_dir, "articles")
        latest_article_file = None
        
        if hasattr(st.session_state, 'latest_article_file') and os.path.exists(st.session_state.latest_article_file):
            latest_article_file = st.session_state.latest_article_file
        elif os.path.exists(article_dir):
            article_files = [f for f in os.listdir(article_dir) if f.endswith('.md')]
            if article_files:
                latest_file = max(article_files, key=lambda x: os.path.getmtime(os.path.join(article_dir, x)))
                latest_article_file = os.path.join(article_dir, latest_file)
        
        if latest_article_file and os.path.exists(latest_article_file):
            # 显示文章统计信息
            try:
                with open(latest_article_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    word_count = len(content.split())
                    char_count = len(content)
                    
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.metric("文章字数", f"{word_count:,}")
                with col_stat2:
                    st.metric("字符数", f"{char_count:,}")
            except Exception as e:
                st.warning(f"无法读取文章统计信息: {str(e)}")
            
            # 文章下载
            with open(latest_article_file, 'rb') as f:
                st.download_button(
                    label="📥 下载最新文章",
                    data=f.read(),
                    file_name=f"generated_article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
            
            # 预览文章内容
            st.subheader("📖 文章预览")
            
            # 添加刷新按钮
            if st.button("🔄 刷新预览", key="refresh_preview"):
                st.rerun()
            
            try:
                with open(latest_article_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 提供预览长度选择
                preview_length = st.selectbox(
                    "预览长度",
                    [500, 1000, 2000, "完整文章"],
                    index=1
                )
                
                if preview_length == "完整文章":
                    preview_content = content
                else:
                    preview_content = content[:preview_length] + "..." if len(content) > preview_length else content
                    
                st.markdown(preview_content)
                
            except Exception as e:
                st.error(f"无法预览文章: {str(e)}")
        else:
            st.info("暂无生成的文章")
        
        # 重置选择按钮
        st.markdown("---")
        if st.button("🔄 重置所有选择", type="secondary"):
            st.session_state.selected_keywords = []
            st.session_state.selected_titles = []
            st.session_state.selected_references = []
            st.session_state.selected_summaries = []
            st.session_state.selected_outlines = []
            st.success("所有选择已重置！")
            st.rerun()

if __name__ == "__main__":
    main()