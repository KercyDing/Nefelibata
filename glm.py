import zhipuai

class ZhipuAI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = zhipuai.ZhipuAI(api_key=api_key)

    def chat(self, messages, model="glm-4-flash", stream=False):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream
            )
            
            if not response.choices:
                raise KeyError("API响应中未找到有效回复内容")
            
            return response.choices[0].message.content
        except Exception as e:
            error_msg = f"API请求错误: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\n响应状态码: {e.response.status_code}"
                try:
                    error_detail = e.response.json()
                    error_msg += f"\n错误详情: {error_detail}"
                except:
                    error_msg += f"\n响应内容: {e.response.text}"
            raise Exception(error_msg)