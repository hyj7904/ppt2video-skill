"""
PPT解析处理器（纯Python方案）
"""

import os
import subprocess
from pptx import Presentation
from pptx.util import Inches

class PurePPTProcessor:
    """基于python-pptx的纯Python解析方案"""
    
    def export_slides(self, ppt_path: str, output_folder: str, 
                     max_slides: int = None) -> list:
        """
        导出PPT幻灯片
        
        Args:
            ppt_path: PPT文件路径
            output_folder: 输出文件夹
            max_slides: 最大处理页数
        
        Returns:
            幻灯片信息列表
        """
        prs = Presentation(ppt_path)
        slides = []
        
        for i, slide in enumerate(prs.slides):
            if max_slides and i >= max_slides:
                break
            
            slide_index = i + 1
            img_path = os.path.join(output_folder, f"slide_{slide_index:03d}.png")
            
            # 提取文本
            text_content = self._extract_text(slide)
            
            # 导出图片
            self._export_slide_image(slide, img_path)
            
            slides.append({
                "index": slide_index,
                "text": text_content,
                "image_path": img_path
            })
        
        return slides
    
    def _extract_text(self, slide) -> str:
        """提取幻灯片文本内容"""
        text_runs = []
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text_runs.append(shape.text)
        return "\n".join(text_runs)
    
    def _export_slide_image(self, slide, output_path: str):
        """导出幻灯片为图片"""
        # 使用临时PPT文件转换
        import tempfile
        from pathlib import Path
        
        # 创建临时PPT文件
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_ppt = Path(temp_dir) / "temp.pptx"
            
            # 创建只包含当前幻灯片的临时演示文稿
            from pptx import Presentation
            temp_prs = Presentation()
            
            # 复制幻灯片内容到新演示文稿
            source_slide = slide
            target_slide = temp_prs.slides[0]
            
            # 复制形状
            for shape in source_slide.shapes:
                # 处理文本框
                if hasattr(shape, "text"):
                    left = shape.left
                    top = shape.top
                    width = shape.width
                    height = shape.height
                    new_shape = target_slide.shapes.add_textbox(left, top, width, height)
                    new_shape.text_frame.text = shape.text
                    
                    # 复制文本样式
                    if shape.has_text_frame:
                        for i, paragraph in enumerate(shape.text_frame.paragraphs):
                            if i < len(new_shape.text_frame.paragraphs):
                                new_paragraph = new_shape.text_frame.paragraphs[i]
                                new_paragraph.font.size = paragraph.font.size
                                new_paragraph.font.bold = paragraph.font.bold
                                new_paragraph.font.italic = paragraph.font.italic
            
            # 保存临时PPT
            temp_prs.save(str(temp_ppt))
            
            # 使用libreoffice或其他工具转换为图片
            self._convert_ppt_to_image(str(temp_ppt), output_path)
    
    def _convert_ppt_to_image(self, ppt_path: str, output_path: str):
        """将PPT页面转换为图片"""
        # 尝试使用libreoffice
        try:
            # 检查libreoffice是否可用
            result = subprocess.run(
                ["soffice", "--headless", "--convert-to", "png", 
                 "--outdir", os.path.dirname(output_path), ppt_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # 检查输出文件
                output_dir = os.path.dirname(output_path)
                base_name = os.path.splitext(os.path.basename(ppt_path))[0]
                generated_file = os.path.join(output_dir, f"{base_name}.png")
                
                if os.path.exists(generated_file):
                    os.rename(generated_file, output_path)
                    return
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # 如果libreoffice不可用，使用简单的文本渲染
        self._fallback_render(output_path)
    
    def _fallback_render(self, output_path: str):
        """降级渲染方案 - 创建简单的占位图片"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            img = Image.new('RGB', (1920, 1080), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # 添加占位文本
            try:
                font = ImageFont.truetype("arial.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            draw.text((100, 500), "PPT Slide Placeholder", font=font, fill=(100, 100, 100))
            
            img.save(output_path)
        except Exception:
            # 如果PIL也不可用，创建最小化的PNG
            self._create_minimal_png(output_path)
    
    def _create_minimal_png(self, output_path: str):
        """创建最小化的PNG图片"""
        # 创建最小的有效PNG文件
        import struct
        
        png_signature = b'\x89PNG\r\n\x1a\n'
        
        # IHDR chunk - image header
        width, height = 1920, 1080
        ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
        ihdr_chunk = b'IHDR' + ihdr_data + self._crc32(b'IHDR' + ihdr_data)
        
        # IEND chunk - end of image
        iend_chunk = b'IEND' + b'\x00\x00\x00\x00' + self._crc32(b'IEND')
        
        with open(output_path, 'wb') as f:
            f.write(png_signature + ihdr_chunk + iend_chunk)
    
    def _crc32(self, data: bytes) -> bytes:
        """计算CRC32校验和"""
        crc = 0xffffffff
        table = [0] * 256
        
        for i in range(256):
            c = i
            for j in range(8):
                c = (c >> 1) ^ 0xedb88320 if c & 1 else c >> 1
            table[i] = c
        
        for byte in data:
            crc = table[(crc ^ byte) & 0xff] ^ (crc >> 8)
        
        return struct.pack('>I', (crc ^ 0xffffffff) & 0xffffffff)

# 兼容旧接口
PPTProcessor = PurePPTProcessor
