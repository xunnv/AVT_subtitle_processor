"""
P0 修复验证测试
测试三个核心问题修复：
1. 整理阶段文本合并（非替换）
2. 翻译成功/失败统计
3. 断点续传缺失翻译检测
"""

import os
import sys
import tempfile

# 在导入模块前模拟缺失的依赖
import unittest.mock

# 模拟 aiohttp（venv 中未安装）
aiohttp_mock = unittest.mock.MagicMock()
sys.modules['aiohttp'] = aiohttp_mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.subtitle_engine import SubtitleEngine, SubtitleItem


class MockConfigManager:
    """模拟配置管理器"""

    def __init__(self):
        self.config = {
            "subtitle": {
                "min_length": 2,
                "max_gap": 3.0,
                "max_duration": 30.0,
                "similarity_threshold": 0.8
            },
            "ocr": {
                "frame_interval": 1,
                "lang": "japan",
                "use_gpu": False,
                "rec_score_thresh": 0.5,
                "det_db_thresh": 0.3,
                "det_db_box_thresh": 0.5,
                "enable_mkldnn": False
            },
            "translation": {},
            "ass_style": {},
            "burn": {"preset": "p4", "crf": 23},
            "paths": {"output_dir": ""},
            "processing": {"cleanup_temp": False, "temp_dir": ""}
        }

    def get(self, key_path, default=None):
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def get_ocr_config(self):
        return self.config.get('ocr', {})

    def get_translation_config(self):
        return self.config.get('translation', {})

    def get_ass_config(self):
        return self.config.get('ass_style', {})

    def get_burn_config(self):
        return self.config.get('burn', {})


class TestOrganizeSubtitles:
    """测试 Fix 1: 整理阶段文本合并"""

    def test_text_merging_instead_of_replacement(self):
        """验证相似帧文本合并而非替换"""
        engine = SubtitleEngine(MockConfigManager())
        engine.translator = None  # 禁用翻译器

        # 模拟 3 帧：第 1 帧和第 2 帧高度相似（字符级 Jaccard > 0.8），应合并
        # Frame1: "これは日本語のテストです" (12个不同字符)
        # Frame2: "これは日本語のテストです文章" (14个不同字符, 12交集)
        # 相似度 = 12/14 ≈ 0.857 > 0.8 ✓
        raw = [
            {'frame_idx': 1, 'timestamp': 0, 'texts': ['これは日本語のテストです']},
            {'frame_idx': 2, 'timestamp': 1, 'texts': ['これは日本語のテストです', '文章']},
            {'frame_idx': 3, 'timestamp': 3, 'texts': ['違う内容']},
        ]

        result = engine._organize_subtitles(raw)

        # 预期：第1帧和第2帧合并（文本应包含所有去重后的内容）
        assert len(result) == 2, f"预期 2 条字幕，实际 {len(result)} 条"

        # 第1条合并后的文本应包含全部去重词汇
        text1 = result[0].text
        assert "これは日本語のテストです" in text1, f"缺少'これは日本語のテストです'，实际: {text1}"
        assert "文章" in text1, f"缺少'文章'，实际: {text1}"
        print(f"  ✓ 合并结果: '{text1}'")
        print(f"  ✓ 合并时间范围: {result[0].start:.0f}s -> {result[0].end:.0f}s")

        # 第2条应为不同的新文本
        text2 = result[1].text
        assert "違う内容" in text2, f"第2条缺少'違う内容'，实际: {text2}"
        print(f"  ✓ 新条目: '{text2}'")

    def test_no_duplicate_text_in_merge(self):
        """验证合并时不会产生重复文本"""
        engine = SubtitleEngine(MockConfigManager())
        engine.translator = None

        # 3帧完全相同，合并后不应有重复
        raw = [
            {'frame_idx': 1, 'timestamp': 0, 'texts': ['同じ', 'テキスト']},
            {'frame_idx': 2, 'timestamp': 1, 'texts': ['同じ', 'テキスト']},
            {'frame_idx': 3, 'timestamp': 2, 'texts': ['同じ', 'テキスト']},
        ]

        result = engine._organize_subtitles(raw)
        text = result[0].text
        # 去重后应该只有两个词
        words = text.split(" ")
        assert len(set(words)) == len(words), f"存在重复文本: {text}"
        print(f"  ✓ 去重成功: '{text}'")

    def test_not_similar_creates_new_entry(self):
        """验证不相似的帧不会合并"""
        engine = SubtitleEngine(MockConfigManager())
        engine.translator = None

        raw = [
            {'frame_idx': 1, 'timestamp': 0, 'texts': ['完全', '不同']},
            {'frame_idx': 2, 'timestamp': 1, 'texts': ['的内容', '在这里']},
        ]

        result = engine._organize_subtitles(raw)
        assert len(result) == 2, "不相似的内容应生成 2 条独立字幕"
        print(f"  ✓ 不相似内容正确分成 {len(result)} 条: '{result[0].text}' | '{result[1].text}'")


class TestTranslationStats:
    """测试 Fix 2: 翻译统计"""

    def test_translate_subtitles_no_translator(self):
        """无翻译器时应直接返回"""
        engine = SubtitleEngine(MockConfigManager())
        engine.translator = None

        subtitles = [
            SubtitleItem(start=0, end=1, text="こんにちは"),
            SubtitleItem(start=1, end=2, text="世界"),
        ]

        result = engine._translate_subtitles(subtitles)
        assert len(result) == 2
        assert result[0].translation == ""
        print("  ✓ 无翻译器时返回原字幕，translation 保持空")

    def test_already_translated_skipped(self):
        """验证已翻译的条目被跳过"""
        engine = SubtitleEngine(MockConfigManager())
        engine.translator = None

        subtitles = [
            SubtitleItem(start=0, end=1, text="こんにちは", translation="你好"),
            SubtitleItem(start=1, end=2, text="世界", translation=""),
        ]

        result = engine._translate_subtitles(subtitles)
        assert result[0].translation == "你好"
        print("  ✓ 已有翻译的条目被正确跳过")


class TestResumeMissingTranslation:
    """测试 Fix 3: 断点续传缺失翻译检测"""

    def test_detect_missing_translations_in_srt(self):
        """验证从SRT加载后能检测到缺失翻译"""
        engine = SubtitleEngine(MockConfigManager())
        engine.translator = None

        # 创建测试 SRT 文件（第2条无翻译）
        srt_content = """1
00:00:00,000 --> 00:00:01,000
こんにちは
你好

2
00:00:01,000 --> 00:00:02,000
世界

3
00:00:02,000 --> 00:00:03,000
テストです
テスト
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt',
                                         encoding='utf-8', delete=False) as f:
            f.write(srt_content)
            temp_path = f.name

        try:
            subtitles = engine._load_subtitles_from_srt(temp_path)

            assert len(subtitles) == 3, f"预期 3 条字幕，实际 {len(subtitles)}"

            assert subtitles[0].translation == "你好", "第1条翻译加载错误"
            print(f"  ✓ 第1条: text='{subtitles[0].text}', translation='{subtitles[0].translation}'")

            assert subtitles[1].translation == "", "第2条翻译应为空"
            assert subtitles[1].text == "世界", "第2条文本加载错误"
            print(f"  ✓ 第2条(缺翻译): text='{subtitles[1].text}', translation='{subtitles[1].translation}'")

            # 验证缺失检测逻辑
            missing = [sub for sub in subtitles if not sub.translation]
            assert len(missing) == 1, f"预期 1 条缺失翻译，实际 {len(missing)}"
            print(f"  ✓ 缺失检测: 正确识别 1/3 条缺少翻译")

        finally:
            os.unlink(temp_path)

    def test_load_srt_all_translated(self):
        """验证所有条目都有翻译时正确加载"""
        engine = SubtitleEngine(MockConfigManager())
        engine.translator = None

        srt_content = """1
00:00:00,000 --> 00:00:01,000
こんにちは
你好

2
00:00:01,000 --> 00:00:02,000
世界
世界
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt',
                                         encoding='utf-8', delete=False) as f:
            f.write(srt_content)
            temp_path = f.name

        try:
            subtitles = engine._load_subtitles_from_srt(temp_path)
            missing = [sub for sub in subtitles if not sub.translation]
            assert len(missing) == 0, f"全部翻译时不应有缺失"
            print(f"  ✓ 全部有翻译: 0 条缺失，正确")

        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    print("=" * 60)
    print("P0 修复验证测试")
    print("=" * 60)

    passed = 0
    failed = 0

    print("\n" + "─" * 60)
    print("Fix 1: 整理阶段文本合并")
    print("─" * 60)
    t1 = TestOrganizeSubtitles()
    for method in [t1.test_text_merging_instead_of_replacement,
                   t1.test_no_duplicate_text_in_merge,
                   t1.test_not_similar_creates_new_entry]:
        try:
            method()
            print("  ✅ 通过")
            passed += 1
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            failed += 1

    print("\n" + "─" * 60)
    print("Fix 2: 翻译统计")
    print("─" * 60)
    t2 = TestTranslationStats()
    for method in [t2.test_translate_subtitles_no_translator,
                   t2.test_already_translated_skipped]:
        try:
            method()
            print("  ✅ 通过")
            passed += 1
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            failed += 1

    print("\n" + "─" * 60)
    print("Fix 3: 断点续传缺失翻译检测")
    print("─" * 60)
    t3 = TestResumeMissingTranslation()
    for method in [t3.test_detect_missing_translations_in_srt,
                   t3.test_load_srt_all_translated]:
        try:
            method()
            print("  ✅ 通过")
            passed += 1
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"结果: {passed} 通过, {failed} 失败")
    if failed == 0:
        print("所有测试通过！✅")
    else:
        print(f"有 {failed} 个测试失败 ❌")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)
