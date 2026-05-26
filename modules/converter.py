"""
PPT转视频核心转换器
"""

import os
import tempfile
from typing import Dict, Any, List

class PPTConverter:
    """PPT转视频协调器"""
    
    def __init__(self, config=None):
        self.config = config
        self.ppt_processor = self._create_ppt_processor()
        self.tts_processor = self._create_tts_processor()
        self.llm_processor = self._create_llm_processor()
        self.video_composer = self._create_video_composer()
    
    def _create_ppt_processor(self):
        """创建PPT处理器（优先纯Python方案）"""
        from .ppt_processor import PurePPTProcessor
        return PurePPTProcessor()
    
    def _create_tts_processor(self):
        """创建TTS处理器"""
        from .tts_processor import TTSProcessor
        return TTSProcessor(self.config)
    
    def _create_llm_processor(self):
        """创建LLM处理器"""
        from .llm_processor import LLMProcessor
        return LLMProcessor(self.config)
    
    def _create_video_composer(self):
        """创建视频合成器"""
        from .video_composer import VideoComposer
        return VideoComposer(self.config)
    
    def convert(self, ppt_path: str, output_path: str, 
               mode: str = "full", **kwargs) -> Dict[str, Any]:
        """
        完整转换流程
        
        Args:
            ppt_path: PPT文件路径
            output_path: 输出视频路径
            mode: 转换模式 (preview_3/full)
            **kwargs: 其他参数
        
        Returns:
            转换结果
        """
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            img_folder = os.path.join(temp_dir, "slides")
            audio_folder = os.path.join(temp_dir, "audio")
            os.makedirs(img_folder, exist_ok=True)
            os.makedirs(audio_folder, exist_ok=True)
            
            # 1. 解析PPT
            max_slides = 3 if mode == "preview_3" else None
            slides = self.ppt_processor.export_slides(ppt_path, img_folder, max_slides)
            
            if not slides:
                return {
                    "status": "error",
                    "message": "未能解析PPT文件"
                }
            
            # 2. 优化讲稿
            if kwargs.get("use_llm", True):
                slides = self.llm_processor.optimize_slides(slides)
            
            # 3. 生成音频
            audio_files = self.tts_processor.generate_audio(
                slides, audio_folder, 
                voice=kwargs.get("voice", "longanyang"),
                speed=kwargs.get("speed", 1.0)
            )
            
            # 4. 合成视频
            result = self.video_composer.compose(
                img_folder, audio_folder, output_path
            )
            
            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": "转换完成",
                    "output_file": output_path,
                    "stats": {
                        "slides": len(slides),
                        "duration": result.get("duration", "0:00"),
                        "audio_files": len(audio_files)
                    }
                }
            else:
                return result
