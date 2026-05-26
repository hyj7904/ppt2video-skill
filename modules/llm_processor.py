"""
LLM处理器模块 - 用于优化讲稿内容
"""

import os
import json
from openai import OpenAI

class LLMProcessor:
    """LLM处理器"""
    
    def __init__(self, config=None):
        self.config = config
        self.enabled = config.get("llm", "enabled", True)
        self.api_url = config.get("llm", "api_url", "https://models.csdn.net/v1")
        self.api_key = config.get("llm", "api_key", "")
        self.default_model = config.get("llm", "default_model", "deepseek-chat")
        self.system_prompt = config.get("llm", "system_prompt", "")
        
        # 初始化OpenAI客户端
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_url
            )
        else:
            self.client = None
    
    def optimize_slides(self, slides: list) -> list:
        """
        优化幻灯片文本内容
        
        Args:
            slides: 幻灯片列表
        
        Returns:
            优化后的幻灯片列表
        """
        if not self.enabled or not self.client:
            return slides
        
        for slide in slides:
            text = slide.get("text", "")
            if text.strip():
                optimized_text = self._optimize_text(text)
                if optimized_text:
                    slide["optimized_text"] = optimized_text
                    slide["text"] = optimized_text
        
        return slides
    
    def _optimize_text(self, text: str) -> str:
        """
        使用LLM优化文本
        
        Args:
            text: 原始文本
        
        Returns:
            优化后的文本
        """
        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return text
    
    def summarize_content(self, slides: list) -> str:
        """
        对所有幻灯片内容进行总结
        
        Args:
            slides: 幻灯片列表
        
        Returns:
            总结文本
        """
        if not self.enabled or not self.client:
            return ""
        
        all_text = "\n\n".join([slide.get("text", "") for slide in slides])
        
        prompt = f"""请对以下PPT内容进行总结，提取核心要点：

{all_text}

总结要求：
1. 不超过300字
2. 用简洁的语言概括主要内容
3. 列出关键点"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"LLM总结失败: {e}")
            return ""
    
    def is_available(self) -> bool:
        """
        检查LLM服务是否可用
        
        Returns:
            是否可用
        """
        return self.enabled and self.client is not None
    
    def test_connection(self) -> bool:
        """
        测试LLM API连通性
        
        Returns:
            True表示连通性正常，False表示失败
        """
        if not self.enabled or not self.client:
            return False
        
        try:
            # 发送一个简单的测试请求
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ],
                temperature=0.0,
                max_tokens=10
            )
            
            # 如果成功返回响应，认为连通性正常
            if response and response.choices:
                return True
            
            return False
        
        except Exception:
            return False
