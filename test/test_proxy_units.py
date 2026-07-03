import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "proxy"))
import csswitch_proxy as cs


class ToolChoiceMapping(unittest.TestCase):
    def setUp(self):
        cs.PROV = cs.PROVIDERS["qwen"]

    def test_tool_named_maps_to_function(self):
        out = cs.map_tool_choice({"type": "tool", "name": "grade"}, [{"name": "grade"}])
        self.assertEqual(out, {"type": "function", "function": {"name": "grade"}})

    def test_any_single_tool_names_that_function(self):
        out = cs.map_tool_choice({"type": "any"}, [{"name": "only"}])
        self.assertEqual(out, {"type": "function", "function": {"name": "only"}})

    def test_any_multi_tool_falls_back_to_required(self):
        out = cs.map_tool_choice({"type": "any"}, [{"name": "a"}, {"name": "b"}])
        self.assertEqual(out, "required")

    def test_auto_and_none_passthrough(self):
        self.assertEqual(cs.map_tool_choice({"type": "auto"}, []), "auto")
        self.assertEqual(cs.map_tool_choice({"type": "none"}, []), "none")

    def test_missing_returns_none(self):
        self.assertIsNone(cs.map_tool_choice(None, []))

    def test_translation_carries_tool_choice_stop_top_p(self):
        req = {
            "model": "claude-haiku-4-5",
            "messages": [{"role": "user", "content": "hi"}],
            "tools": [{"name": "grade", "input_schema": {"type": "object"}}],
            "tool_choice": {"type": "tool", "name": "grade"},
            "stop_sequences": ["STOP"],
            "top_p": 0.5,
        }
        out = cs.anthropic_to_openai(req)
        self.assertEqual(out["tool_choice"], {"type": "function", "function": {"name": "grade"}})
        self.assertEqual(out["stop"], ["STOP"])
        self.assertEqual(out["top_p"], 0.5)


class MaxTokensPerModel(unittest.TestCase):
    def setUp(self):
        cs.PROV = cs.PROVIDERS["deepseek"]

    def test_cap_uses_target_model_entry(self):
        self.assertEqual(cs.clamp_max_tokens(100000, "deepseek-v4-pro"), 65536)
        self.assertEqual(cs.clamp_max_tokens(100000, "deepseek-v4-flash"), 32768)

    def test_unknown_model_uses_default_cap(self):
        self.assertEqual(cs.clamp_max_tokens(100000, "who-knows"), 8192)

    def test_not_clamped_below_request(self):
        self.assertEqual(cs.clamp_max_tokens(500, "deepseek-v4-pro"), 500)

    def test_none_passthrough(self):
        self.assertIsNone(cs.clamp_max_tokens(None, "deepseek-v4-pro"))

    def test_qwen_per_model(self):
        cs.PROV = cs.PROVIDERS["qwen"]
        self.assertEqual(cs.clamp_max_tokens(100000, "qwen-max"), 8192)


class CustomUrlNormalization(unittest.TestCase):
    def test_anthropic_root_gets_messages_path(self):
        self.assertEqual(cs.normalize_custom_url("https://api.vveai.com/", "anthropic"),
                         "https://api.vveai.com/v1/messages")

    def test_anthropic_v1_and_vendor_prefix(self):
        self.assertEqual(cs.normalize_custom_url("https://example.com/v1", "anthropic"),
                         "https://example.com/v1/messages")
        self.assertEqual(cs.normalize_custom_url("https://example.com/anthropic/", "anthropic"),
                         "https://example.com/anthropic/v1/messages")

    def test_explicit_endpoint_is_preserved(self):
        url = "https://example.com/custom/messages?region=cn"
        self.assertEqual(cs.normalize_custom_url(url, "anthropic"), url)

    def test_openai_root_gets_chat_completions_path(self):
        self.assertEqual(cs.normalize_custom_url("https://example.com", "openai"),
                         "https://example.com/v1/chat/completions")


if __name__ == "__main__":
    unittest.main()
