"""
语音合成处理器模块
"""

import os
import requests
import json
import asyncio
from pathlib import Path

class TTSProcessor:
    """语音合成处理器"""
    
    # 旧发音人到EDGE TTS的映射
    VOICE_MAPPING = {
        "longanyang": "zh-CN-XiaoxiaoNeural",
        "longanyun": "zh-CN-YunyangNeural",
        "longhuhu": "zh-CN-XiaoyiNeural",
        "loongdonna_v2": "en-US-JennyNeural",
        "local_zh": "zh-CN-XiaoxiaoNeural",
        "local_en": "en-US-JennyNeural"
    }
    
    def __init__(self, config=None):
        self.config = config
        self.api_url = config.get("tts", "api_url", "https://models.csdn.net/v1/audio/speech")
        self.api_key = config.get("tts", "api_key", "")
        self.default_voice = config.get("tts", "default_voice", "zh-CN-XiaoxiaoNeural")
    
    def generate_audio(self, slides: list, output_folder: str, 
                      voice: str = None, speed: float = 1.0) -> list:
        """
        为幻灯片文本生成音频文件
        
        Args:
            slides: 幻灯片列表，每个元素包含 'text' 和 'index'
            output_folder: 输出文件夹
            voice: 发音人
            speed: 语速
        
        Returns:
            音频文件路径列表
        """
        audio_files = []
        voice = voice or self.default_voice
        
        for slide in slides:
            text = slide.get("text", "")
            index = slide.get("index", 0)
            
            if not text.strip():
                # 如果没有文本，创建静音音频
                audio_path = self._create_silent_audio(output_folder, index)
            else:
                # 根据发音人和配置选择TTS方式
                # EDGE TTS 发音人都以 "zh-"、"en-" 等开头
                if voice.startswith(("zh-", "en-", "ja-", "ko-", "fr-", "de-", "es-")):
                    audio_path = self._generate_edge_audio(text, output_folder, index, voice, speed)
                # 如果有API密钥，使用远程TTS API
                elif self.api_key:
                    audio_path = self._generate_single_audio(text, output_folder, index, voice, speed)
                # 否则，默认使用EDGE TTS
                else:
                    audio_path = self._generate_edge_audio(text, output_folder, index, voice, speed)
            
            if audio_path:
                audio_files.append(audio_path)
        
        return audio_files
    
    def _generate_single_audio(self, text: str, output_folder: str, 
                              index: int, voice: str, speed: float) -> str:
        """
        使用远程API为单段文本生成音频
        
        Args:
            text: 文本内容
            output_folder: 输出文件夹
            index: 索引
            voice: 发音人
            speed: 语速
        
        Returns:
            音频文件路径
        """
        audio_path = os.path.join(output_folder, f"audio_{index:03d}.mp3")
        
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            data = {
                "text": text,
                "voice": voice,
                "speed": speed,
                "format": "mp3"
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=60
            )
            
            response.raise_for_status()
            
            with open(audio_path, "wb") as f:
                f.write(response.content)
            
            return audio_path
        
        except Exception as e:
            print(f"TTS API调用失败，切换到EDGE TTS: {e}")
            return self._generate_edge_audio(text, output_folder, index, voice, speed)
    
    def _generate_edge_audio(self, text: str, output_folder: str, 
                            index: int, voice: str, speed: float) -> str:
        """
        使用EDGE TTS为单段文本生成音频
        
        Args:
            text: 文本内容
            output_folder: 输出文件夹
            index: 索引
            voice: 发音人
            speed: 语速
        
        Returns:
            音频文件路径
        """
        audio_path = os.path.join(output_folder, f"audio_{index:03d}.mp3")
        
        try:
            import edge_tts
            
            # 转换速度参数为EDGE TTS格式（支持百分比）
            # 输入范围 0.8-1.5 转换为 -20% 到 +50%
            rate_percent = int((speed - 1.0) * 100)
            if rate_percent >= 0:
                rate_str = f"+{rate_percent}%"
            else:
                rate_str = f"{rate_percent}%"
            
            # 如果发音人不是EDGE TTS格式，检查映射表或使用默认
            if not voice.startswith(("zh-", "en-", "ja-", "ko-", "fr-", "de-", "es-")):
                # 检查是否在映射表中
                if voice in self.VOICE_MAPPING:
                    voice = self.VOICE_MAPPING[voice]
                else:
                    # 检测文本语言，选择合适的默认发音人
                    if any("\u4e00" <= c <= "\u9fff" for c in text):
                        voice = "zh-CN-XiaoxiaoNeural"
                    else:
                        voice = "en-US-JennyNeural"
            
            # 运行异步函数
            async def _save_audio():
                communicate = edge_tts.Communicate(
                    text=text,
                    voice=voice,
                    rate=rate_str
                )
                await communicate.save(audio_path)
            
            asyncio.run(_save_audio())
            
            return audio_path
        
        except Exception as e:
            print(f"EDGE TTS调用失败: {e}")
            return self._create_silent_audio(output_folder, index)
    
    def _create_silent_audio(self, output_folder: str, index: int) -> str:
        """
        创建静音音频文件
        
        Args:
            output_folder: 输出文件夹
            index: 索引
        
        Returns:
            静音音频文件路径
        """
        audio_path = os.path.join(output_folder, f"audio_{index:03d}.mp3")
        
        silent_mp3 = (
            b"\xff\xfb\x3c\x80\x44\xac\x00\x00\x00\x03U\xf8\xfcL\xa9\x00\x01\x00"
            b"\x00\x00\x03U\xf8\xfcL\xa9\x00\x01\x00\x00\x00\x03U\xf8\xfcL\xa9"
            b"\x00\x01\x00\x00\x00\x03U\xf8\xfcL\xa9\x00\x01\x00\x00"
        )
        
        with open(audio_path, "wb") as f:
            f.write(silent_mp3)
        
        return audio_path
    
    def list_voices(self) -> list:
        """
        获取支持的发音人列表
        
        Returns:
            发音人列表
        """
        return [
            # EDGE TTS 发音人
            {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓 (中文女声)"},
            {"id": "zh-CN-YunyangNeural", "name": "云扬 (中文男声)"},
            {"id": "zh-CN-XiaoyiNeural", "name": "晓伊 (中文女声)"},
            {"id": "zh-CN-YunxiNeural", "name": "云希 (中文男声)"},
            {"id": "zh-CN-YunjianNeural", "name": "云健 (中文男声)"},
            {"id": "zh-CN-XiaohanNeural", "name": "晓涵 (中文女声)"},
            {"id": "en-US-JennyNeural", "name": "Jenny (英语女声)"},
            {"id": "en-US-AriaNeural", "name": "Aria (英语女声)"},
            {"id": "en-US-GuyNeural", "name": "Guy (英语男声)"},
            {"id": "en-GB-SoniaNeural", "name": "Sonia (英语女声)"},
            {"id": "ja-JP-NanamiNeural", "name": "Nanami (日语女声)"},
            {"id": "ja-JP-KeitaNeural", "name": "Keita (日语男声)"},
            {"id": "ko-KR-SunHiNeural", "name": "SunHi (韩语女声)"},
            {"id": "ko-KR-InJoonNeural", "name": "InJoon (韩语男声)"},
            {"id": "fr-FR-DeniseNeural", "name": "Denise (法语女声)"},
            {"id": "fr-FR-HenriNeural", "name": "Henri (法语男声)"},
            {"id": "de-DE-KatjaNeural", "name": "Katja (德语女声)"},
            {"id": "de-DE-ConradNeural", "name": "Conrad (德语男声)"},
            {"id": "es-ES-ElviraNeural", "name": "Elvira (西语女声)"},
            {"id": "es-ES-AlvaroNeural", "name": "Alvaro (西语男声)"},
            # 兼容旧发音人（自动映射到EDGE TTS）
            {"id": "longanyang", "name": "优雅知性女 (映射到晓晓)", "map_to": "zh-CN-XiaoxiaoNeural"},
            {"id": "longanyun", "name": "居家暖男 (映射到云扬)", "map_to": "zh-CN-YunyangNeural"},
            {"id": "longhuhu", "name": "天真烂漫女童 (映射到晓伊)", "map_to": "zh-CN-XiaoyiNeural"},
            {"id": "loongdonna_v2", "name": "美式英文女 (映射到Jenny)", "map_to": "en-US-JennyNeural"}
        ]
    
    def test_connection(self) -> bool:
        """
        测试TTS连通性
        
        Returns:
            True表示连通性正常或使用EDGE TTS，False表示失败
        """
        # EDGE TTS 不需要API密钥，直接返回True
        if not self.api_key:
            return True
        
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            test_text = "测试"
            data = {
                "text": test_text,
                "voice": self.default_voice,
                "speed": 1.0,
                "format": "mp3"
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if 200 <= response.status_code < 500:
                return True
            
            return False
        
        except Exception:
            return False
