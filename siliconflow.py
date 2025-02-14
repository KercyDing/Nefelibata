import requests

class DeepSeekAI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api.siliconflow.cn/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def chat(self, messages, model="deepseek-ai/DeepSeek-V3", stream=False):
        try:
            system_message = {"role": "system", "content": "你是由中国的深度求索公司开发的智能助手DeepSeek，"}
            full_messages = [system_message] + messages
            
            payload = {
                "model": model,
                "stream": stream,
                "messages": full_messages
            }
            
            response = requests.post(self.url, json=payload, headers=self.headers)
            
            if response.status_code == 403:
                error_msg = "API认证失败(403 Forbidden)。可能的原因：\n"
                error_msg += "1. API密钥无效或已过期\n"
                error_msg += "2. API密钥没有访问该模型的权限\n"
                error_msg += "3. 账户余额不足或已被禁用"
                raise Exception(error_msg)
            
            response.raise_for_status()
            response_json = response.json()
            
            if "choices" not in response_json or not response_json["choices"]:
                raise KeyError("API响应中未找到有效的回复内容")
            
            return response_json["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            error_msg = ""
            if isinstance(e, requests.exceptions.Timeout):
                error_msg = "API请求超时，请稍后重试。可能的原因：\n"
                error_msg += "1. 服务器响应时间过长\n"
                error_msg += "2. 网络连接不稳定\n"
                error_msg += "3. 服务器负载过高"
            else:
                error_msg = f"API请求错误: {str(e)}\n"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"响应状态码: {e.response.status_code}\n"
                try:
                    error_detail = e.response.json()
                    error_msg += f"错误详情: {error_detail}"
                except:
                    error_msg += f"响应内容: {e.response.text}"
            raise Exception(error_msg)
        except (KeyError, IndexError) as e:
            raise Exception(f"API响应格式错误: {str(e)}")
        except Exception as e:
            raise Exception(f"错误: {str(e)}")