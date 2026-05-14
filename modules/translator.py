"""
翻译器模块
支持 Ollama 和 LM Studio 两个本地模型框架
"""

import time
import requests
import json
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod


class BaseTranslator(ABC):
    """翻译器基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.host = config.get('host', 'http://localhost:11434')
        self.model = config.get('model', '')
        self.timeout = config.get('timeout', 120)
        self.temperature = config.get('temperature', 0.3)
        self.max_retries = config.get('max_retries', 3)

    @abstractmethod
    def translate(self, text: str, source_lang: str = "ja", target_lang: str = "zh") -> Optional[str]:
        """翻译文本"""
        pass

    @abstractmethod
    def test_connection(self) -> tuple[bool, str]:
        """测试连接"""
        pass


class OllamaTranslator(BaseTranslator):
    """Ollama 翻译器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_base = f"{self.host}/api/generate"

    def translate(self, text: str, source_lang: str = "ja", target_lang: str = "zh") -> Optional[str]:
        """使用 Ollama 翻译"""
        prompt = self._build_prompt(text, source_lang, target_lang)

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_base,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": self.temperature,
                            "num_predict": 512
                        }
                    },
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    result = response.json()
                    translated = result.get("response", "").strip()
                    translated = self._clean_response(translated)
                    if translated:
                        return translated

            except requests.exceptions.Timeout:
                continue
            except requests.exceptions.ConnectionError:
                break
            except Exception:
                continue

            if attempt < self.max_retries - 1:
                time.sleep(2)

        return None

    def translate_batch(self, texts: List[str], source_lang: str = "ja", target_lang: str = "zh") -> List[Optional[str]]:
        """批量翻译多个文本"""
        results = []
        for text in texts:
            translated = self.translate(text, source_lang, target_lang)
            results.append(translated)
        return results

    def _build_prompt(self, text: str, source_lang: str, target_lang: str) -> str:
        """构建翻译提示词"""
        lang_map = {
            "ja": "日语", "zh": "中文", "en": "英语",
            "ko": "韩语", "fr": "法语", "de": "德语",
            "es": "西班牙语", "ru": "俄语"
        }
        src = lang_map.get(source_lang, source_lang)
        tgt = lang_map.get(target_lang, target_lang)
        return f"请将以下{src}翻译成{tgt}，只输出翻译结果，不要添加任何解释或注释：\n\n{text}"

    def _clean_response(self, text: str) -> str:
        """清理响应文本"""
        text = text.strip()
        text = text.replace("「", "").replace("」", "")
        text = text.replace("『", "").replace("』", "")
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace("'", "'").replace("'", "'")
        return text

    def test_connection(self) -> tuple[bool, str]:
        """测试 Ollama 连接"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                available = [m["name"] for m in models]
                if self.model in available:
                    return True, f"连接成功，模型 {self.model} 可用"
                elif available:
                    return False, f"模型 {self.model} 未找到，可用模型: {', '.join(available)}"
                return False, "未找到可用模型"
            return False, f"连接失败: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "无法连接到 Ollama，请确保服务已启动"
        except Exception as e:
            return False, f"连接错误: {str(e)}"


class LMStudioTranslator(BaseTranslator):
    """LM Studio 翻译器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_base = f"{self.host}/v1/completions"

    def translate(self, text: str, source_lang: str = "ja", target_lang: str = "zh") -> Optional[str]:
        """使用 LM Studio 翻译"""
        prompt = self._build_prompt(text, source_lang, target_lang)

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_base,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "max_tokens": 512,
                        "temperature": self.temperature,
                        "stream": False
                    },
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    result = response.json()
                    translated = result.get("choices", [{}])[0].get("text", "").strip()
                    translated = self._clean_response(translated)
                    if translated:
                        return translated

            except requests.exceptions.Timeout:
                continue
            except requests.exceptions.ConnectionError:
                break
            except Exception:
                continue

            if attempt < self.max_retries - 1:
                time.sleep(2)

        return None

    def translate_batch(self, texts: List[str], source_lang: str = "ja", target_lang: str = "zh") -> List[Optional[str]]:
        """批量翻译多个文本"""
        results = []
        for text in texts:
            translated = self.translate(text, source_lang, target_lang)
            results.append(translated)
        return results

    def _build_prompt(self, text: str, source_lang: str, target_lang: str) -> str:
        """构建翻译提示词"""
        lang_map = {
            "ja": "日语", "zh": "中文", "en": "英语",
            "ko": "韩语", "fr": "法语", "de": "德语",
            "es": "西班牙语", "ru": "俄语"
        }
        src = lang_map.get(source_lang, source_lang)
        tgt = lang_map.get(target_lang, target_lang)
        return f"请将以下{src}翻译成{tgt}，只输出翻译结果：\n\n{text}\n\n翻译："

    def _clean_response(self, text: str) -> str:
        """清理响应文本"""
        text = text.strip()
        text = text.replace("「", "").replace("」", "")
        text = text.replace("『", "").replace("』", "")
        text = text.replace('"', '"').replace('"', '"')
        return text

    def test_connection(self) -> tuple[bool, str]:
        """测试 LM Studio 连接"""
        try:
            response = requests.get(f"{self.host}/v1/models", timeout=5)
            if response.status_code == 200:
                models = response.json().get("data", [])
                available = [m.get("id", "") for m in models]
                if self.model in available:
                    return True, f"连接成功，模型 {self.model} 可用"
                elif available:
                    return False, f"模型 {self.model} 未找到，可用模型: {', '.join(available)}"
                return False, "未找到可用模型"
            return False, f"连接失败: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "无法连接到 LM Studio，请确保服务已启动"
        except Exception as e:
            return False, f"连接错误: {str(e)}"


class TranslatorFactory:
    """翻译器工厂"""

    @staticmethod
    def create(framework: str, config: Dict[str, Any]) -> BaseTranslator:
        """创建翻译器"""
        framework = framework.lower()
        if framework == "ollama":
            return OllamaTranslator(config)
        elif framework == "lmstudio":
            return LMStudioTranslator(config)
        else:
            raise ValueError(f"不支持的翻译框架: {framework}")

    @staticmethod
    def get_default_config(framework: str) -> Dict[str, Any]:
        """获取默认配置"""
        configs = {
            "ollama": {
                "host": "http://localhost:11434",
                "model": "quantumcookie/sakura-galtransl-v3.7:7b",
                "timeout": 120,
                "temperature": 0.3,
                "max_retries": 3
            },
            "lmstudio": {
                "host": "http://localhost:1234/v1",
                "model": "sakura-galtransl-v3.7",
                "timeout": 120,
                "temperature": 0.3,
                "max_retries": 3
            }
        }
        return configs.get(framework.lower(), {})
