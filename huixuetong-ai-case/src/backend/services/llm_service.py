"""
慧学通 (HuiXueTong) - 大模型服务模块
功能：文心一言 4.0 接入、OAuth2 Token 缓存、诊断报告生成
申报映射：AI 赋能/内容生成/伦理合规
"""

import os
import time
import requests
from typing import Optional


class LLMService:
    """
    文心一言大模型服务类
    实现 OAuth2 鉴权、Token 内存缓存、Prompt 封装与异常降级
    """
    
    def __init__(self, api_key: str = None, secret_key: str = None,
                 token_url: str = None, chat_url: str = None):
        # 从参数或环境变量读取配置（禁止硬编码）
        from config import Config
        self.api_key = api_key or Config.BAIDU_API_KEY
        self.secret_key = secret_key or Config.BAIDU_SECRET_KEY
        self.token_url = token_url or Config.BAIDU_TOKEN_URL
        self.chat_url = chat_url or Config.BAIDU_CHAT_URL
        
        # Token 缓存（内存级，生产环境可改用 Redis）
        self._access_token: Optional[str] = None
        self._token_expire_time: float = 0
    
    def _get_access_token(self) -> Optional[str]:
        """
        获取访问令牌（带缓存机制）
        返回：有效的 access_token，失败返回 None
        """
        # 检查缓存是否有效
        if self._access_token and time.time() < self._token_expire_time:
            return self._access_token
        
        # 请求新 Token
        try:
            params = {
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.secret_key
            }
            response = requests.post(self.token_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if "access_token" in data:
                self._access_token = data["access_token"]
                # 设置过期时间（预留 60 秒缓冲）
                expires_in = data.get("expires_in", 2592000)
                self._token_expire_time = time.time() + expires_in - 60
                return self._access_token
            else:
                return None
        except Exception as e:
            print(f"获取 Token 失败：{str(e)}")
            return None
    
    def generate_diagnosis(self, k_score: float, s_score: float, l_score: float) -> str:
        """
        生成个性化诊断报告
        约束：≤200 字，含优势/薄弱点/2 条建议，末尾附加 [AI 辅助生成]
        
        参数：
            k_score: 知识得分
            s_score: 技能得分
            l_score: 素养得分
        
        返回：诊断报告文本（含合规标记）
        """
        # 如果没有配置 API Key，返回降级提示
        if not self.api_key or not self.secret_key:
            return "【系统提示】AI 服务未配置，请联系管理员设置 BAIDU_API_KEY。[AI 辅助生成]"
        
        token = self._get_access_token()
        if not token:
            return "【系统提示】AI 服务暂时不可用，请稍后重试。[AI 辅助生成]"
        
        # 构建强制约束 Prompt
        prompt = f"""请根据以下学生三维能力得分生成诊断报告：
- 知识维度：{k_score}分
- 技能维度：{s_score}分
- 素养维度：{l_score}分

要求：
1. 字数严格控制在 200 字以内
2. 必须包含：①优势分析 ②薄弱点定位 ③2 条可操作学习建议
3. 语言简洁专业，适合中职学生阅读
4. 末尾必须附加标记：[AI 辅助生成]

请直接输出报告内容，无需额外说明。"""
        
        # 调用文心一言 API
        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            url = f"{self.chat_url}?access_token={token}"
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            
            # 解析返回结果
            if "result" in result:
                report = result["result"].strip()
                # 确保末尾有合规标记
                if "[AI 辅助生成]" not in report:
                    report += " [AI 辅助生成]"
                return report
            else:
                return "【系统提示】AI 响应格式异常，请联系管理员。[AI 辅助生成]"
                
        except requests.exceptions.Timeout:
            return "【系统提示】AI 服务响应超时，请稍后重试。[AI 辅助生成]"
        except requests.exceptions.RequestException as e:
            return f"【系统提示】网络请求失败：{str(e)[:50]}... [AI 辅助生成]"
        except Exception as e:
            return f"【系统提示】服务异常：{str(e)[:50]}... [AI 辅助生成]"
