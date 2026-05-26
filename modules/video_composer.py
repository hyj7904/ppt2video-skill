"""
视频合成器模块
"""

import os
import glob
from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_audioclips, CompositeVideoClip

class VideoComposer:
    """视频合成器"""
    
    def __init__(self, config=None):
        self.config = config
        self.preset = config.get("video", "preset", "normal")
        self.crf = config.get("video", "crf", 23)
        self.width = config.get("video", "width", 1920)
        self.height = config.get("video", "height", 1080)
        
        # 设置FFmpeg路径
        ffmpeg_path = config.get("video", "ffmpeg_path", "")
        if ffmpeg_path:
            os.environ["FFMPEG_BINARY"] = ffmpeg_path
    
    def compose(self, img_folder: str, audio_folder: str, output_path: str) -> dict:
        """
        合成视频
        
        Args:
            img_folder: 图片文件夹
            audio_folder: 音频文件夹
            output_path: 输出视频路径
        
        Returns:
            合成结果
        """
        try:
            # 获取图片列表（按序号排序）
            img_pattern = os.path.join(img_folder, "slide_*.png")
            img_files = sorted(glob.glob(img_pattern))
            
            # 获取音频列表（按序号排序）
            audio_pattern = os.path.join(audio_folder, "audio_*.mp3")
            audio_files = sorted(glob.glob(audio_pattern))
            
            if not img_files:
                return {"status": "error", "message": "未找到幻灯片图片"}
            
            # 确保图片和音频数量匹配
            min_count = min(len(img_files), len(audio_files))
            if min_count == 0:
                return {"status": "error", "message": "没有可用的媒体文件"}
            
            # 准备剪辑片段
            clips = []
            total_duration = 0
            
            for i in range(min_count):
                img_path = img_files[i]
                audio_path = audio_files[i] if i < len(audio_files) else None
                
                # 获取音频时长
                try:
                    if audio_path and os.path.exists(audio_path):
                        audio_clip = AudioFileClip(audio_path)
                        duration = audio_clip.duration
                    else:
                        # 默认3秒
                        duration = 3.0
                        audio_clip = None
                except:
                    duration = 3.0
                    audio_clip = None
                
                # 创建图片剪辑
                img_clip = ImageSequenceClip([img_path], durations=[duration])
                
                # 设置尺寸
                img_clip = img_clip.resize(width=self.width, height=self.height)
                
                # 添加音频
                if audio_clip:
                    img_clip = img_clip.set_audio(audio_clip)
                
                clips.append(img_clip)
                total_duration += duration
            
            # 拼接所有片段
            final_clip = concatenate_audioclips(clips) if len(clips) > 1 else clips[0]
            
            # 写入视频文件
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                preset=self.preset,
                crf=self.crf,
                audio_codec="aac"
            )
            
            # 计算时长
            minutes = int(total_duration // 60)
            seconds = int(total_duration % 60)
            duration_str = f"{minutes}:{seconds:02d}"
            
            return {
                "status": "success",
                "message": "视频合成完成",
                "duration": duration_str,
                "output_file": output_path,
                "frames": len(clips)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"视频合成失败: {str(e)}"
            }
    
    def create_slideshow(self, img_folder: str, output_path: str, 
                        duration_per_slide: float = 3.0) -> dict:
        """
        创建简单的幻灯片视频（无音频）
        
        Args:
            img_folder: 图片文件夹
            output_path: 输出视频路径
            duration_per_slide: 每张幻灯片的时长
        
        Returns:
            合成结果
        """
        try:
            # 获取图片列表
            img_pattern = os.path.join(img_folder, "slide_*.png")
            img_files = sorted(glob.glob(img_pattern))
            
            if not img_files:
                return {"status": "error", "message": "未找到幻灯片图片"}
            
            # 创建图片序列剪辑
            clip = ImageSequenceClip(img_files, durations=[duration_per_slide] * len(img_files))
            
            # 设置尺寸
            clip = clip.resize(width=self.width, height=self.height)
            
            # 写入视频文件
            clip.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                preset=self.preset,
                crf=self.crf
            )
            
            total_duration = len(img_files) * duration_per_slide
            minutes = int(total_duration // 60)
            seconds = int(total_duration % 60)
            duration_str = f"{minutes}:{seconds:02d}"
            
            return {
                "status": "success",
                "message": "幻灯片视频创建完成",
                "duration": duration_str,
                "output_file": output_path,
                "frames": len(img_files)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"视频创建失败: {str(e)}"
            }
