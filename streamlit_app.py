import streamlit as st
import pandas as pd
import os
from datetime import datetime
from openai import OpenAI
import zipfile
import io
from config import *
from step1_keyword import generate_keywords_via_openrouter
from step2_titles import generate_titles_from_keywords
from step3_outline import generate_outlines_from_titles
from step4_generate_article import generate_articles_from_outlines
import csv
import tempfile

# 页面配置
st.set_page_config(
    page_title="📄 AI文章生成器",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化OpenAI客户端
client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

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
if 'selected_outlines' not in st.session_state:
    st.session_state.selected_outlines = []

def save_selected_data(data_list, filename, header):
    """保存用户选择的数据到CSV文件"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([header])
        for item in data_list:
            writer.writerow([item])

def main():
    st.title("📄 AI文章生成器")
    st.markdown("---")
    
    # 侧边栏 - 流程状态
    with st.sidebar:
        st.header("🔄 生成流程")
        step_status = {
            "step1": "⏳ 待执行",
            "step2": "⏳ 待执行", 
            "step3": "⏳ 待执行",
            "step4": "⏳ 待执行"
        }
        
        # 检查文件状态
        if os.path.exists(os.path.join(data_dir, "keyword.csv")):
            step_status["step1"] = "✅ 已完成"
        if os.path.exists(os.path.join(data_dir, "title.csv")):
            step_status["step2"] = "✅ 已完成"
        if os.path.exists(os.path.join(data_dir, "outline.csv")):
            step_status["step3"] = "✅ 已完成"
        if os.path.exists(os.path.join(output_dir, "articles", "articles.md")):
            step_status["step4"] = "✅ 已完成"
        
        st.markdown("**当前状态:**")
        st.markdown(f"1️⃣ 关键词生成: {step_status['step1']}")
        st.markdown(f"2️⃣ 标题生成: {step_status['step2']}")
        st.markdown(f"3️⃣ 大纲生成: {step_status['step3']}")
        st.markdown(f"4️⃣ 文章生成: {step_status['step4']}")
        
        st.markdown("---")
        st.markdown("**选择统计:**")
        st.markdown(f"🔑 已选关键词: {len(st.session_state.selected_keywords)}")
        st.markdown(f"📝 已选标题: {len(st.session_state.selected_titles)}")
        st.markdown(f"🧱 已选大纲: {len(st.session_state.selected_outlines)}")
        
    # 主界面
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 关键词生成", "📝 标题生成", "🧱 大纲生成", "📄 文章生成", "📊 结果查看"])
    
    # Tab 1: 关键词生成
    with tab1:
        st.header("🎯 Step 1: 关键词生成")
        st.markdown("""
        通过AI分析当前热门趋势，自动生成相关关键词。
        - 分析X(Twitter)、Reddit、Medium等平台讨论
        - 识别高搜索量和病毒式讨论话题
        """)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # 添加知识范围选择
            knowledge_scope_option = st.selectbox(
                "🎯 选择知识范围",
                ["AI技术", "科技创新", "商业营销", "教育学习", "自定义"],
                help="选择关键词生成的知识领域范围"
            )
            
            # 如果选择自定义，显示文本输入框
            if knowledge_scope_option == "自定义":
                custom_scope = st.text_input(
                    "📝 输入自定义知识范围",
                    placeholder="例如：医疗健康、金融科技、环保技术等",
                    help="请输入您感兴趣的具体知识领域"
                )
                knowledge_scope = custom_scope if custom_scope else "通用技术"
            else:
                knowledge_scope = knowledge_scope_option
            
            # 添加关键词数量输入控件
            num_keywords = st.number_input(
                "🔢 生成关键词数量",
                min_value=1,
                max_value=20,
                value=2,
                step=1,
                help="选择要生成的关键词数量（1-20个）"
            )
            
            if st.button("🚀 生成关键词", type="primary", use_container_width=True):
                with st.spinner(f"正在分析{knowledge_scope}领域热门趋势并生成{num_keywords}个关键词..."):
                    try:
                        keyword_csv = os.path.join(data_dir, "keyword.csv")
                        generate_keywords_via_openrouter(client, KEYWORD_MODEL, keyword_csv, num_keywords, knowledge_scope)
                        st.success(f"成功生成{num_keywords}个{knowledge_scope}相关关键词！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"生成失败: {str(e)}")
        
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
                        keyword = row['keyword']
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
        基于选择的关键词，为每个关键词创建多个SEO优化的文章标题。
        - 每个关键词生成2个标题
        - 遵循教育性和信息性内容模式
        - SEO友好的标题结构
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
                            # 使用选择的关键词生成标题
                            keyword_file = os.path.join(data_dir, "keyword.csv")
                            title_csv = os.path.join(data_dir, "title.csv")
                            generate_titles_from_keywords(client, KEYWORD_MODEL, keyword_file, title_csv)
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
    
    # Tab 3: 大纲生成
    with tab3:
        st.header("🧱 Step 3: 大纲生成")
        st.markdown("""
        为选择的标题生成详细的文章大纲。
        - 遵循Google EEAT原则
        - 结构化的6个主要部分
        - 约2000字的长篇SEO文章大纲
        """)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if not st.session_state.selected_titles:
                st.warning("⚠️ 请先选择标题")
            else:
                st.info(f"将为 {len(st.session_state.selected_titles)} 个标题生成大纲")
                
                if st.button("🧱 生成大纲", type="primary", use_container_width=True):
                    with st.spinner("正在为选择的标题生成大纲..."):
                        try:
                            title_file = os.path.join(data_dir, "title.csv")
                            outline_csv = os.path.join(data_dir, "outline.csv")
                            generate_outlines_from_titles(client, OUTLINE_MODEL, title_file, outline_csv)
                            st.success("大纲生成完成！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"生成失败: {str(e)}")
        
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
    
    # Tab 4: 文章生成
    with tab4:
        st.header("📄 Step 4: 文章生成")
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
                    
                    st.success(f"✅ 已生成 {len(article_files)} 篇文章")
                    
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
    
    # Tab 5: 结果查看
    with tab5:
        st.header("📊 生成结果")
        
        # 显示选择统计
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("选择的关键词", len(st.session_state.selected_keywords))
        # 在Tab 5的结果查看部分，修改文章预览逻辑
        with col2:
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
            st.session_state.selected_outlines = []
            st.success("所有选择已重置！")
            st.rerun()

if __name__ == "__main__":
    main()