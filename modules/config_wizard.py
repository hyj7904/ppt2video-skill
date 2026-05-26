"""
配置引导模块 - 帮助用户首次安装时配置技能
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

class ConfigWizard:
    """配置引导助手"""
    
    def __init__(self, config):
        self.config = config
    
    def run_wizard(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        运行配置引导
        
        Args:
            inputs: 用户输入的配置参数（可选）
        
        Returns:
            配置结果
        """
        if inputs:
            return self._apply_config(inputs)
        else:
            return self._generate_wizard_steps()
    
    def _generate_wizard_steps(self) -> Dict[str, Any]:
        """
        生成引导步骤
        
        Returns:
            引导步骤信息
        """
        return {
            "status": "wizard",
            "message": "请完成配置（带 * 的为必填项）",
            "steps": [
                {
                    "step": 1,
                    "title": "语音合成配置 *",
                    "description": "配置语音合成服务，用于生成讲解音频（必须配置）",
                    "is_required": True,
                    "fields": [
                        {
                            "name": "default_voice",
                            "label": "默认发音人",
                            "type": "select",
                            "required": True,
                            "description": "选择默认的语音发音人",
                            "options": [
                                {"value": "longanyang", "label": "优雅知性女"},
                                {"value": "longanyun", "label": "居家暖男"},
                                {"value": "longhuhu", "label": "天真烂漫女童"},
                                {"value": "loongdonna_v2", "label": "美式英文女"}
                            ],
                            "default": self.config.get("tts", "default_voice", "longanyang")
                        },
                        {
                            "name": "default_speed",
                            "label": "默认语速",
                            "type": "number",
                            "required": False,
                            "description": "语速范围 0.8-1.5，默认1.0",
                            "default": self.config.get("tts", "default_speed", 1.0),
                            "min": 0.8,
                            "max": 1.5,
                            "step": 0.1
                        },
                        {
                            "name": "tts_api_key",
                            "label": "TTS API密钥",
                            "type": "password",
                            "required": False,
                            "description": "语音合成API密钥（可选，不配置则使用内置发音）",
                            "default": ""
                        },
                        {
                            "name": "tts_api_url",
                            "label": "TTS API地址",
                            "type": "text",
                            "required": False,
                            "description": "语音合成API服务地址",
                            "default": self.config.get("tts", "api_url", "")
                        }
                    ]
                },
                {
                    "step": 2,
                    "title": "AI优化配置",
                    "description": "配置AI服务优化讲稿（可选，不影响基础功能）",
                    "is_required": False,
                    "fields": [
                        {
                            "name": "enable_llm",
                            "label": "启用AI优化演讲稿",
                            "type": "boolean",
                            "required": False,
                            "description": "是否启用AI优化讲稿功能（可选）",
                            "default": self.config.get("llm", "enabled", False)
                        },
                        {
                            "name": "llm_api_key",
                            "label": "LLM API密钥",
                            "type": "password",
                            "required": False,
                            "description": "AI服务API密钥（启用时必填）",
                            "default": ""
                        },
                        {
                            "name": "llm_api_url",
                            "label": "LLM API地址",
                            "type": "text",
                            "required": False,
                            "description": "AI服务API地址",
                            "default": self.config.get("llm", "api_url", "")
                        },
                        {
                            "name": "llm_model",
                            "label": "AI模型",
                            "type": "text",
                            "required": False,
                            "description": "使用的AI模型名称",
                            "default": self.config.get("llm", "default_model", "")
                        }
                    ]
                },
                {
                    "step": 3,
                    "title": "完成配置",
                    "description": "确认配置并保存",
                    "is_required": False,
                    "fields": []
                }
            ]
        }
    
    def _apply_config(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用用户配置
        
        Args:
            inputs: 用户输入的配置参数
        
        Returns:
            配置结果
        """
        config_data = {}
        
        # 处理TTS配置（必须）
        tts_config = {}
        if "default_voice" in inputs:
            tts_config["default_voice"] = inputs["default_voice"]
        if "default_speed" in inputs:
            tts_config["default_speed"] = inputs["default_speed"]
        if "tts_api_key" in inputs and inputs["tts_api_key"]:
            tts_config["api_key"] = inputs["tts_api_key"]
        if "tts_api_url" in inputs and inputs["tts_api_url"]:
            tts_config["api_url"] = inputs["tts_api_url"]
        
        if tts_config:
            config_data["tts"] = tts_config
        
        # 处理LLM配置（可选）
        llm_config = {}
        if "enable_llm" in inputs:
            llm_config["enabled"] = inputs["enable_llm"]
        if "llm_api_key" in inputs and inputs["llm_api_key"]:
            llm_config["api_key"] = inputs["llm_api_key"]
        if "llm_api_url" in inputs and inputs["llm_api_url"]:
            llm_config["api_url"] = inputs["llm_api_url"]
        if "llm_model" in inputs and inputs["llm_model"]:
            llm_config["default_model"] = inputs["llm_model"]
        
        if llm_config:
            config_data["llm"] = llm_config
        
        # 更新配置
        for section, settings in config_data.items():
            for key, value in settings.items():
                self.config.set(section, key, value)
        
        # 保存配置
        self.config.save()
        
        # 测试连通性
        from modules.tts_processor import TTSProcessor
        from modules.llm_processor import LLMProcessor
        
        tts_ok = True
        tts_key = tts_config.get("api_key")
        if tts_key:
            try:
                tts_processor = TTSProcessor(self.config)
                tts_ok = tts_processor.test_connection()
            except:
                tts_ok = False
        
        llm_ok = True
        llm_enabled = llm_config.get("enabled", False)
        if llm_enabled:
            try:
                llm_processor = LLMProcessor(self.config)
                llm_ok = llm_processor.test_connection()
            except:
                llm_ok = False
        
        return {
            "status": "success",
            "message": "配置保存成功",
            "updated_config": config_data,
            "connection_test": {
                "tts": tts_ok,
                "llm": llm_ok
            },
            "config_status": self.get_config_status()
        }
    
    def is_configured(self) -> bool:
        """
        检查是否已配置
        
        Returns:
            是否已配置（必须完成语音配置）
        """
        config_file = Path.home() / ".ppt2video" / "config.json"
        if not config_file.exists():
            return False
        
        # 检查是否配置了发音人
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                saved_config = json.load(f)
                # 至少需要配置发音人
                return saved_config.get("tts", {}).get("default_voice") is not None
        except:
            return False
    
    def get_config_status(self) -> Dict[str, Any]:
        """
        获取配置状态
        
        Returns:
            配置状态信息
        """
        config_file = Path.home() / ".ppt2video" / "config.json"
        has_config_file = config_file.exists()
        
        return {
            "configured": self.is_configured(),
            "has_config_file": has_config_file,
            "default_voice": self.config.get("tts", "default_voice", "longanyang"),
            "default_speed": self.config.get("tts", "default_speed", 1.0),
            "tts_api_configured": bool(self.config.get("tts", "api_key", "")),
            "llm_enabled": self.config.get("llm", "enabled", False),
            "llm_api_configured": bool(self.config.get("llm", "api_key", ""))
        }
    
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
            # 兼容旧发音人
            {"id": "longanyang", "name": "优雅知性女 (映射到晓晓)"},
            {"id": "longanyun", "name": "居家暖男 (映射到云扬)"},
            {"id": "longhuhu", "name": "天真烂漫女童 (映射到晓伊)"},
            {"id": "loongdonna_v2", "name": "美式英文女 (映射到Jenny)"}
        ]