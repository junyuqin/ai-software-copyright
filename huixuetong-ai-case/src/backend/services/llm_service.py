"""
慧学通 (HuiXueTong) - 大模型服务模块
功能：文心一言4.0接入、OAuth2 Token缓存、诊断报告生成
申报映射：AI赋能/内容生成/伦理合规
"""

import os
import time
import requests
from typing import Optional


class LLMService:
    """
    文心一言大模型服务类
    实现OAuth2鉴权、Token内存缓存、Prompt封装与异常降级
    """
    
    def __init__(self, api_key: str = None, secret_key: str = None,
                 token_url: str = None, chat_url: str = None):
        # 从参数或环境变量读取配置（禁止硬编码）
        from config import Config
        self.api_key = api_key or Config.BAIDU_API_KEY
        self.secret_key = secret_key or Config.BAIDU_SECRET_KEY
        self.token_url = token_url or Config.BAIDU_TOKEN_URL
        self.chat_url = chat_url or Config.BAIDU_CHAT_URL
        
        # Token缓存（内存级，生产环境可改用Redis）
        self._access_token: Optional[str] = None
        self._token_expire_time: float = 0
    
    def _get_access_token(self) -> Optional[str]:
        """
        获取访问令牌（带缓存机制）
        返回：有效的access_token，失败返回None
        """
        # 检查缓存是否有效
        if self._access_token and time.time() < self._token_expire_time:
            return self._access_token
        
        # 请求新Token
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
                # 设置过期时间（预留60秒缓冲）
                expires_in = data.get("expires_in", 2592000)
                self._token_expire_time = time.time() + expires_in - 60
                return self._access_token
            else:
                return None
        except Exception as e:
            print(f"获取Token失败: {str(e)}")
            return None
    
    def generate_diagnosis(self, k_score: float, s_score: float, l_score: float) -> str:
        """
        生成个性化诊断报告
        约束：≤200字，含优势/薄弱点/2条建议，末尾附加[AI辅助生成]
        
        参数：
            k_score: 知识得分
            s_score: 技能得分
            l_score: 素养得分
        
        返回：诊断报告文本（含合规标记）
        """
        token = self._get_access_token()
        if not token:
            return "【系统提示】AI服务暂时不可用，请稍后重试。[AI辅助生成]"
        
        # 构建强制约束Prompt
        prompt = f"""请根据以下学生三维能力得分生成诊断报告：
- 知识维度：{k_score}分
- 技能维度：{s_score}分
- 素养维度：{l_score}分

要求：
1. 字数严格控制在200字以内
2. 必须包含：①优势分析 ②薄弱点定位 ③2条可操作学习建议
3. 语言简洁专业，适合中职学生阅读
4. 末尾必须附加标记：[AI辅助生成]

请直接输出报告内容，无需额外说明。"""
        
        # 调用文心一言API
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
                if "[AI辅助生成]" not in report:
                    report += " [AI辅助生成]"
                return report
            else:
                return "【系统提示】AI响应格式异常，请联系管理员。[AI辅助生成]"
                
        except requests.exceptions.Timeout:
            return "【系统提示】AI服务响应超时，请稍后重试。[AI辅助生成]"
        except requests.exceptions.RequestException as e:
            return f"【系统提示】网络请求失败：{str(e)[:50]}... [AI辅助生成]"
        except Exception as e:
            return f"【系统提示】服务异常：{str(e)[:50]}... [AI辅助生成]"
