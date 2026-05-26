"""
配置管理器模块
"""

import os
import json
from pathlib import Path

# 默认配置
DEFAULT_CONFIG = {
    "tts": {
        "api_url": "https://models.csdn.net/v1/audio/speech",
        "api_key": "",
        "default_voice": "zh-CN-XiaoxiaoNeural",
        "default_speed": 1.0
    },
    "llm": {
        "enabled": False,
        "api_url": "",
        "api_key": "",
        "default_model": "",
        "system_prompt": """你是一位专业的 PPT 讲解员。请将以下 PPT 页面文本改写为自然流畅的口头讲解稿。

要求：
1. 保持关键信息不丢失
2. 语言口语化，适合语音合成
3. 如果文本是英文，请用英文改写；如果是中文，请用中文改写
4. 只输出改写后的文本，不要任何解释或标注
5. 适当添加连接词和过渡语，使讲解更流畅"""
    },
    "video": {
        "ffmpeg_path": "",
        "preset": "normal",
        "crf": 23,
        "width": 1920,
        "height": 1080
    }
}

class ConfigManager:
    """配置管理器，单例模式"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = self._load_config()
    
    def _load_config(self):
        """从环境变量和配置文件加载配置"""
        config = DEFAULT_CONFIG.copy()
        
        # 从环境变量加载API密钥
        tts_api_key = os.environ.get("TTS_API_KEY", "")
        llm_api_key = os.environ.get("LLM_API_KEY", "")
        ffmpeg_path = os.environ.get("FFMPEG_PATH", "")
        
        if tts_api_key:
            config["tts"]["api_key"] = tts_api_key
        if llm_api_key:
            config["llm"]["api_key"] = llm_api_key
        if ffmpeg_path:
            config["video"]["ffmpeg_path"] = ffmpeg_path
        
        # 尝试从配置文件加载
        config_file = Path.home() / ".ppt2video" / "config.json"
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    saved_config = json.load(f)
                    # 合并配置
                    for key in saved_config:
                        if key in config:
                            if isinstance(config[key], dict):
                                config[key].update(saved_config[key])
                            else:
                                config[key] = saved_config[key]
            except Exception:
                pass
        
        return config
    
    def get(self, section, key, default=None):
        """获取配置值"""
        return self._config.get(section, {}).get(key, default)
    
    def set(self, section, key, value):
        """设置配置值"""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
        self._save_config()
    
    def get_section(self, section):
        """获取整个section的配置"""
        return self._config.get(section, {})
    
    def _save_config(self):
        """保存配置到文件"""
        config_dir = Path.home() / ".ppt2video"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(self._config, f, ensure_ascii=False, indent=2)

# 全局配置实例
config = ConfigManager()
