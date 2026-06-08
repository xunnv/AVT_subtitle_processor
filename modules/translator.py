"""
翻译器模块
支持 Ollama 和 LM Studio 两个本地模型框架
"""

import time
import requests
import json
import asyncio
import aiohttp
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from .logger import logger


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
                        logger.debug(f"Ollama翻译成功: {text[:30]}... -> {translated[:30]}...")
                        return translated
                    else:
                        logger.debug(f"Ollama返回空结果，重试中 ({attempt + 1}/{self.max_retries})")
                else:
                    logger.warning(f"Ollama请求失败，状态码: {response.status_code}，重试中 ({attempt + 1}/{self.max_retries})")

            except requests.exceptions.Timeout:
                logger.warning(f"Ollama请求超时，重试中 ({attempt + 1}/{self.max_retries})")
                continue
            except requests.exceptions.ConnectionError:
                logger.error(f"Ollama连接失败，请检查服务是否正常运行")
                break
            except json.JSONDecodeError:
                logger.error(f"Ollama返回无效JSON响应")
                continue
            except Exception as e:
                logger.exception(f"Ollama翻译异常: {e}")
                continue

            if attempt < self.max_retries - 1:
                time.sleep(2)

        logger.warning(f"Ollama翻译失败，已达到最大重试次数 ({self.max_retries})")
        return None

    def translate_batch(self, texts: List[str], source_lang: str = "ja", target_lang: str = "zh") -> List[Optional[str]]:
        """批量翻译多个文本（使用异步并发）"""
        if not texts:
            return []

        logger.info(f"开始批量翻译 {len(texts)} 条文本")
        start_time = time.time()

        try:
            results = asyncio.run(self._async_translate_batch(texts, source_lang, target_lang))
        except Exception as e:
            logger.exception(f"批量翻译异步执行失败: {e}")
            results = [self.translate(t, source_lang, target_lang) for t in texts]

        elapsed = time.time() - start_time
        success_count = sum(1 for r in results if r is not None)
        logger.info(f"批量翻译完成: {success_count}/{len(texts)} 成功，耗时 {elapsed:.2f} 秒")

        return results

    async def _async_translate_batch(self, texts: List[str], source_lang: str, target_lang: str) -> List[Optional[str]]:
        """异步批量翻译"""
        semaphore = asyncio.Semaphore(3)

        async def translate_with_limit(text: str, index: int):
            async with semaphore:
                for attempt in range(self.max_retries):
                    try:
                        prompt = self._build_prompt(text, source_lang, target_lang)
                        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                            async with session.post(
                                self.api_base,
                                json={
                                    "model": self.model,
                                    "prompt": prompt,
                                    "stream": False,
                                    "options": {
                                        "temperature": self.temperature,
                                        "num_predict": 512
                                    }
                                }
                            ) as response:
                                if response.status == 200:
                                    result = await response.json()
                                    translated = result.get("response", "").strip()
                                    translated = self._clean_response(translated)
                                    if translated:
                                        return index, translated
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(1)
                    except Exception:
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(2)
                            continue
                        return index, None
                return index, None

        tasks = [translate_with_limit(text, i) for i, text in enumerate(texts)]
        results = await asyncio.gather(*tasks)

        sorted_results = [None] * len(texts)
        for index, translated in results:
            sorted_results[index] = translated

        return sorted_results

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
                        logger.debug(f"LM Studio翻译成功: {text[:30]}... -> {translated[:30]}...")
                        return translated
                    else:
                        logger.debug(f"LM Studio返回空结果，重试中 ({attempt + 1}/{self.max_retries})")
                else:
                    logger.warning(f"LM Studio请求失败，状态码: {response.status_code}，重试中 ({attempt + 1}/{self.max_retries})")

            except requests.exceptions.Timeout:
                logger.warning(f"LM Studio请求超时，重试中 ({attempt + 1}/{self.max_retries})")
                continue
            except requests.exceptions.ConnectionError:
                logger.error(f"LM Studio连接失败，请检查服务是否正常运行")
                break
            except json.JSONDecodeError:
                logger.error(f"LM Studio返回无效JSON响应")
                continue
            except Exception as e:
                logger.exception(f"LM Studio翻译异常: {e}")
                continue

            if attempt < self.max_retries - 1:
                time.sleep(2)

        logger.warning(f"LM Studio翻译失败，已达到最大重试次数 ({self.max_retries})")
        return None

    def translate_batch(self, texts: List[str], source_lang: str = "ja", target_lang: str = "zh") -> List[Optional[str]]:
        """批量翻译多个文本（使用异步并发）"""
        if not texts:
            return []

        logger.info(f"开始批量翻译 {len(texts)} 条文本")
        start_time = time.time()

        try:
            results = asyncio.run(self._async_translate_batch(texts, source_lang, target_lang))
        except Exception as e:
            logger.exception(f"批量翻译异步执行失败: {e}")
            results = [self.translate(t, source_lang, target_lang) for t in texts]

        elapsed = time.time() - start_time
        success_count = sum(1 for r in results if r is not None)
        logger.info(f"批量翻译完成: {success_count}/{len(texts)} 成功，耗时 {elapsed:.2f} 秒")

        return results

    async def _async_translate_batch(self, texts: List[str], source_lang: str, target_lang: str) -> List[Optional[str]]:
        """异步批量翻译"""
        semaphore = asyncio.Semaphore(3)

        async def translate_with_limit(text: str, index: int):
            async with semaphore:
                for attempt in range(self.max_retries):
                    try:
                        prompt = self._build_prompt(text, source_lang, target_lang)
                        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                            async with session.post(
                                self.api_base,
                                json={
                                    "model": self.model,
                                    "prompt": prompt,
                                    "max_tokens": 512,
                                    "temperature": self.temperature,
                                    "stream": False
                                },
                                headers={"Content-Type": "application/json"}
                            ) as response:
                                if response.status == 200:
                                    result = await response.json()
                                    translated = result.get("choices", [{}])[0].get("text", "").strip()
                                    translated = self._clean_response(translated)
                                    if translated:
                                        return index, translated
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(1)
                    except Exception:
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(2)
                            continue
                        return index, None
                return index, None

        tasks = [translate_with_limit(text, i) for i, text in enumerate(texts)]
        results = await asyncio.gather(*tasks)

        sorted_results = [None] * len(texts)
        for index, translated in results:
            sorted_results[index] = translated

        return sorted_results

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
