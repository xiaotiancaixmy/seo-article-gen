import requests
import os
from PIL import Image
import io
import time
from urllib.parse import urlparse

class PixabayImageDownloader:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://pixabay.com/api/"
        self.download_folder = "pixabay_ai_images"
        
        # 创建下载文件夹
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
    
    def search_images(self, query, per_page=100, image_type="photo", category="science", orientation="horizontal"):
        """
        搜索Pixabay图片
        """
        params = {
            'key': self.api_key,
            'q': query,
            'image_type': image_type,
            'category': category,
            'orientation': orientation,  # 添加横向（landscape）参数
            'per_page': per_page,
            'safesearch': 'true',
            'order': 'popular',
            'min_width': 1920,  # 确保图片质量，最小宽度
            'min_height': 1080   # 确保图片质量，最小高度
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"搜索图片时出错: {e}")
            return None
    
    def download_and_convert_image(self, image_url, filename):
        """
        下载图片并转换为webp格式
        """
        try:
            # 下载图片
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # 使用PIL打开图片
            image = Image.open(io.BytesIO(response.content))
            
            # 检查图片是否为landscape格式（宽度大于高度）
            width, height = image.size
            if width <= height:
                print(f"跳过非landscape格式图片: {filename} ({width}x{height})")
                return False
            
            # 转换为RGB模式（webp需要）
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # 保存为webp格式
            webp_filename = f"{filename}.webp"
            webp_path = os.path.join(self.download_folder, webp_filename)
            
            # 保存时设置质量参数
            image.save(webp_path, 'WEBP', quality=85, optimize=True)
            
            print(f"成功下载并转换: {webp_filename} ({width}x{height})")
            return True
            
        except Exception as e:
            print(f"下载图片 {filename} 时出错: {e}")
            return False
    
    def download_ai_images(self, max_images=50):
        """
        下载AI相关的科技感图片（landscape格式，不包含机器人）
        """
        # 科技感相关的搜索关键词（排除机器人相关）
        tech_keywords = [
            "hardware technology",
            "keyboard",
            "technology",
            "fiber cable",
            "workspace",
            "computer science technology",
            "digital transformation",
            "tech innovation",
            "futuristic technology",
            "digital network",
            "cyber technology",
            "AI abstract concept",
            "technology background",
            "digital innovation"
        ]
        
        downloaded_count = 0
        
        for keyword in tech_keywords:
            if downloaded_count >= max_images:
                break
                
            print(f"\n正在搜索关键词: {keyword}")
            
            # 计算这次搜索需要的图片数量
            remaining_images = max_images - downloaded_count
            per_page = min(remaining_images, 20)  # Pixabay API限制每次最多20张
            
            # 搜索图片（指定横向orientation）
            search_result = self.search_images(keyword, per_page=per_page, orientation="horizontal")
            
            if not search_result or 'hits' not in search_result:
                print(f"搜索 {keyword} 失败")
                continue
            
            images = search_result['hits']
            print(f"找到 {len(images)} 张图片")
            
            # 过滤掉包含机器人相关标签的图片
            filtered_images = []
            robot_keywords = ['robot', 'android', 'humanoid', 'cyborg', 'droid']
            
            for image_data in images:
                tags = image_data.get('tags', '').lower()
                if not any(robot_word in tags for robot_word in robot_keywords):
                    filtered_images.append(image_data)
            
            print(f"过滤后剩余 {len(filtered_images)} 张非机器人相关图片")
            
            # 下载图片
            for i, image_data in enumerate(filtered_images):
                if downloaded_count >= max_images:
                    break
                
                # 获取图片URL（优先选择高质量）
                image_url = image_data.get('largeImageURL') or image_data.get('webformatURL')
                
                if not image_url:
                    continue
                
                # 生成文件名
                filename = f"tech_landscape_{downloaded_count + 1:03d}_{keyword.replace(' ', '_')}_{image_data['id']}"
                
                # 下载并转换图片
                if self.download_and_convert_image(image_url, filename):
                    downloaded_count += 1
                    print(f"进度: {downloaded_count}/{max_images}")
                
                # 添加延迟避免请求过快
                time.sleep(0.5)
        
        print(f"\n下载完成！总共下载了 {downloaded_count} 张科技感landscape图片")
        print(f"图片保存在: {os.path.abspath(self.download_folder)}")
        
        return downloaded_count

def main():
    # Pixabay API密钥
    API_KEY = "50940935-6df1a344f2b603680d7a7f9b6"
    
    if API_KEY == "YOUR_PIXABAY_API_KEY":
        print("错误: 请先设置您的Pixabay API密钥")
        print("1. 访问 https://pixabay.com/api/docs/")
        print("2. 注册账户并获取API密钥")
        print("3. 将API_KEY变量替换为您的密钥")
        return
    
    # 创建下载器实例
    downloader = PixabayImageDownloader(API_KEY)
    
    print("开始下载科技感landscape图片...")
    print("目标: 50张图片，webp格式，landscape方向，无机器人内容")
    print("-" * 60)
    
    # 开始下载
    downloaded_count = downloader.download_ai_images(max_images=50)
    
    if downloaded_count > 0:
        print(f"\n✅ 成功下载 {downloaded_count} 张科技感landscape图片")
        print(f"📁 保存位置: {os.path.abspath(downloader.download_folder)}")
        print("🖼️  格式: WebP")
        print("📐 方向: Landscape (横向)")
        print("🚫 已排除: 机器人相关内容")
    else:
        print("❌ 没有成功下载任何图片")

if __name__ == "__main__":
    main()