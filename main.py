"""
PPT转视频技能 - Hermes Agent 入口
"""

import os
import json
import tempfile
from typing import Dict, Any

# 导入核心模块
from modules.converter import PPTConverter
from modules.config import ConfigManager
from modules.tts_processor import TTSProcessor
from modules.llm_processor import LLMProcessor
from modules.config_wizard import ConfigWizard

def validate_input(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证输入参数
    """
    errors = []
    
    # 验证PPT文件
    ppt_file = inputs.get("ppt_file")
    if ppt_file and not os.path.exists(ppt_file):
        errors.append({"field": "ppt_file", "message": "PPT文件不存在"})
    elif ppt_file and not ppt_file.lower().endswith(".pptx"):
        errors.append({"field": "ppt_file", "message": "仅支持 .pptx 格式"})
    
    # 验证模式
    mode = inputs.get("mode", "full")
    if mode not in ["preview_3", "full"]:
        errors.append({"field": "mode", "message": "无效的模式值"})
    
    # 验证语速
    speed = inputs.get("speed", 1.0)
    if not (0.8 <= speed <= 1.5):
        errors.append({"field": "speed", "message": "语速必须在 0.8-1.5 之间"})
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def execute(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行任务（支持多种操作类型）
    
    Args:
        inputs: 输入参数字典，包含 action 字段指定操作类型
    
    Returns:
        执行结果
    """
    try:
        # 获取操作类型，默认为转换
        action = inputs.get("action", "convert")
        
        if action == "convert":
            return _execute_convert(inputs)
        elif action == "configure":
            return _execute_configure(inputs)
        elif action == "validate":
            return _execute_validate(inputs)
        elif action == "get_config":
            return _execute_get_config(inputs)
        elif action == "wizard":
            return _execute_wizard(inputs)
        elif action == "setup":
            return _execute_setup(inputs)
        elif action == "check_config":
            return _execute_check_config(inputs)
        elif action == "list_voices":
            return _execute_list_voices(inputs)
        else:
            return {
                "status": "error",
                "message": f"未知操作类型: {action}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"执行失败: {str(e)}",
            "error_type": type(e).__name__
        }

def _execute_convert(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行PPT转视频任务
    """
    # 检查是否已完成首次配置
    config = ConfigManager()
    wizard = ConfigWizard(config)
    
    if not wizard.is_configured():
        return {
            "status": "needs_config",
            "message": "请先完成语音合成配置",
            "suggestion": "请调用 action='wizard' 获取配置引导，然后使用 action='setup' 提交配置",
            "config_info": {
                "required": "语音合成配置（发音人）",
                "optional": "AI优化配置（LLM讲稿优化）",
                "note": "LLM优化为可选配置，不影响基础的PPT转视频功能"
            },
            "config_status": wizard.get_config_status()
        }
    
    # 验证输入
    validation = validate_input(inputs)
    if not validation["valid"]:
        return {
            "status": "error",
            "message": "参数验证失败",
            "errors": validation["errors"]
        }
    
    # 获取输入参数（优先使用输入参数，其次使用配置默认值）
    ppt_file = inputs["ppt_file"]
    output_path = inputs.get("output_path")
    mode = inputs.get("mode", "full")
    voice = inputs.get("voice", config.get("tts", "default_voice", "longanyang"))
    speed = inputs.get("speed", config.get("tts", "default_speed", 1.0))
    use_llm = inputs.get("use_llm", config.get("llm", "enabled", False))
    
    # 设置输出路径
    if not output_path:
        output_dir = os.path.dirname(ppt_file)
        base_name = os.path.splitext(os.path.basename(ppt_file))[0]
        output_path = os.path.join(output_dir, f"{base_name}_视频.mp4")
    
    # 初始化转换器
    converter = PPTConverter(config)
    
    # 执行转换
    result = converter.convert(
        ppt_path=ppt_file,
        output_path=output_path,
        mode=mode,
        voice=voice,
        speed=speed,
        use_llm=use_llm
    )
    
    return {
        "status": result["status"],
        "message": result["message"],
        "video_file": result.get("output_file"),
        "stats": result.get("stats")
    }

def _execute_configure(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    配置技能参数（直接更新配置）
    """
    config = ConfigManager()
    config_data = inputs.get("config", {})
    
    if not config_data:
        return {
            "status": "error",
            "message": "配置数据不能为空"
        }
    
    # 更新配置
    for section, settings in config_data.items():
        if isinstance(settings, dict):
            for key, value in settings.items():
                config.set(section, key, value)
    
    # 保存配置
    config.save()
    
    return {
        "status": "success",
        "message": "配置更新成功",
        "updated_config": config_data
    }

def _execute_validate(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证连通性（TTS和LLM API）
    """
    config = ConfigManager()
    results = {}
    
    # 验证TTS连通性
    tts_key = config.get("tts", "api_key", "")
    if tts_key:
        try:
            tts_processor = TTSProcessor(config)
            tts_result = tts_processor.test_connection()
            results["tts"] = {
                "status": "success" if tts_result else "error",
                "message": "TTS API连通性测试通过" if tts_result else "TTS API连通性测试失败"
            }
        except Exception as e:
            results["tts"] = {
                "status": "error",
                "message": f"TTS测试失败: {str(e)}"
            }
    else:
        results["tts"] = {
            "status": "info",
            "message": "未配置TTS API，将使用内置发音"
        }
    
    # 验证LLM连通性
    llm_enabled = config.get("llm", "enabled", False)
    if llm_enabled:
        llm_key = config.get("llm", "api_key", "")
        if llm_key:
            try:
                llm_processor = LLMProcessor(config)
                llm_result = llm_processor.test_connection()
                results["llm"] = {
                    "status": "success" if llm_result else "error",
                    "message": "LLM API连通性测试通过" if llm_result else "LLM API连通性测试失败"
                }
            except Exception as e:
                results["llm"] = {
                    "status": "error",
                    "message": f"LLM测试失败: {str(e)}"
                }
        else:
            results["llm"] = {
                "status": "warning",
                "message": "LLM已启用但未配置API密钥"
            }
    else:
        results["llm"] = {
            "status": "info",
            "message": "LLM功能未启用"
        }
    
    # 综合结果
    has_error = any(r["status"] == "error" for r in results.values())
    
    return {
        "status": "success" if not has_error else "partial",
        "message": "连通性测试完成" if not has_error else "部分测试失败",
        "details": results
    }

def _execute_get_config(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取当前配置
    """
    config = ConfigManager()
    
    # 获取完整配置（隐藏敏感信息）
    full_config = config.get_all()
    
    # 隐藏API密钥
    if "tts" in full_config and "api_key" in full_config["tts"]:
        full_config["tts"]["api_key"] = "******"
    if "llm" in full_config and "api_key" in full_config["llm"]:
        full_config["llm"]["api_key"] = "******"
    
    return {
        "status": "success",
        "message": "获取配置成功",
        "config": full_config
    }

def _execute_wizard(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取配置引导步骤
    """
    config = ConfigManager()
    wizard = ConfigWizard(config)
    
    return wizard.run_wizard()

def _execute_setup(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    提交配置（首次安装或修改配置时使用）
    """
    config = ConfigManager()
    wizard = ConfigWizard(config)
    
    # 获取用户提交的配置参数
    config_params = inputs.get("config", {})
    
    if not config_params:
        return {
            "status": "error",
            "message": "配置参数不能为空",
            "suggestion": "请提供配置参数，例如: {\"default_voice\": \"longanyang\", \"enable_llm\": true}"
        }
    
    result = wizard.run_wizard(config_params)
    
    return result

def _execute_check_config(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    检查配置状态
    """
    config = ConfigManager()
    wizard = ConfigWizard(config)
    
    status = wizard.get_config_status()
    
    return {
        "status": "success",
        "message": "配置状态检查完成",
        "config_status": status
    }

def _execute_list_voices(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取发音人列表
    """
    config = ConfigManager()
    wizard = ConfigWizard(config)
    
    voices = wizard.list_voices()
    
    return {
        "status": "success",
        "message": "获取发音人列表成功",
        "voices": voices,
        "current_voice": config.get("tts", "default_voice", "longanyang")
    }

def describe() -> Dict[str, Any]:
    """
    获取技能描述信息
    """
    with open("skill.yaml", "r", encoding="utf-8") as f:
        import yaml
        return yaml.safe_load(f)

if __name__ == "__main__":
    # 测试模式
    import sys
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
    else:
        action = "test"
    
    if action == "validate":
        # 测试连通性
        result = execute({"action": "validate"})
        print("=== 连通性测试 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif action == "config":
        # 测试获取配置
        result = execute({"action": "get_config"})
        print("=== 当前配置 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif action == "set_config":
        # 测试设置配置
        config_data = {
            "tts": {
                "default_voice": "longanyun",
                "default_speed": 1.1
            },
            "llm": {
                "enabled": False
            }
        }
        result = execute({"action": "configure", "config": config_data})
        print("=== 配置更新 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif action == "wizard":
        # 测试获取引导步骤
        result = execute({"action": "wizard"})
        print("=== 配置引导 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif action == "setup":
        # 测试提交配置
        setup_data = {
            "action": "setup",
            "config": {
                "default_voice": "longanyang",
                "default_speed": 1.0,
                "enable_llm": False
            }
        }
        result = execute(setup_data)
        print("=== 配置提交 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif action == "check":
        # 测试检查配置状态
        result = execute({"action": "check_config"})
        print("=== 配置状态 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif action == "voices":
        # 测试获取发音人列表
        result = execute({"action": "list_voices"})
        print("=== 发音人列表 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        # 测试转换
        test_inputs = {
            "ppt_file": "test.pptx",
            "mode": "preview_3",
            "voice": "longanyang",
            "speed": 1.0,
            "use_llm": False
        }
        
        result = execute(test_inputs)
        print(json.dumps(result, ensure_ascii=False, indent=2))