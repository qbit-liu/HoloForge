import copy
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("workflow_measure", ROOT / "evals/agent-workflows/measure.py")
measure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(measure)


class WorkflowMetricsTests(unittest.TestCase):
    def setUp(self):
        self.usage = dict(input_tokens=10, cached_input_tokens=6, cache_write_input_tokens=0,
                          output_tokens=4, reasoning_output_tokens=2, total_tokens=14)
        self.records = [
            {"type": "turn_context", "payload": {"model": "synthetic-model", "effort": "high"}},
            {"type": "event_msg", "timestamp": "2026-01-01T00:00:00Z", "payload": {"type": "task_started", "turn_id": "one"}},
            {"type": "token_usage_record", "payload": {"response_id": "r1", "usage": self.usage, "thread_token_usage": self.usage}},
            {"type": "event_msg", "timestamp": "2026-01-01T00:00:02Z", "payload": {"type": "task_complete", "turn_id": "one", "duration_ms": 2000}},
        ]

    def test_duplicate_usage_and_cumulative_counts_are_not_added_twice(self):
        self.records.append(copy.deepcopy(self.records[2]))
        result = measure.summarize(self.records)
        self.assertEqual(result["tokens"]["total_tokens"], 14)
        self.assertEqual(result["tokens"]["uncached_input_tokens"], 4)
        self.assertEqual(result["tokens"]["output_tokens"], 4)
        self.assertEqual(result["response_count"], 1)

    def test_missing_usage_is_unavailable(self):
        self.records.pop(2)
        result = measure.summarize(self.records)
        self.assertIsNone(result["tokens"])
        self.assertIsNone(measure.aggregate([result])["tokens"])

    def test_conflicting_usage_fails(self):
        duplicate = copy.deepcopy(self.records[2])
        duplicate["payload"]["usage"]["input_tokens"] = 99
        self.records.append(duplicate)
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            measure.summarize(self.records)

    def test_cumulative_mismatch_fails(self):
        self.records[2]["payload"]["thread_token_usage"] = dict(self.usage, total_tokens=99)
        with self.assertRaisesRegex(ValueError, "cumulative"):
            measure.summarize(self.records)

    def test_tool_outputs_and_duplicate_calls_are_not_counted(self):
        call = {"type": "response_item", "payload": {"type": "custom_tool_call", "call_id": "c1"}}
        output = {"type": "response_item", "payload": {"type": "custom_tool_call_output", "call_id": "c1"}}
        self.records += [call, call, output]
        self.assertEqual(measure.summarize(self.records)["top_level_tool_calls"], 1)

    def test_incomplete_turn_has_no_completed_cohort_latency(self):
        self.records.pop()
        result = measure.aggregate([measure.summarize(self.records)])
        self.assertFalse(result["complete"])
        self.assertIsNone(result["cohort_elapsed_seconds"])

    def test_parallel_role_time_is_separate_from_cohort_latency(self):
        role = measure.summarize(self.records)
        result = measure.aggregate([role, role])
        self.assertEqual(result["cohort_elapsed_seconds"], 2)
        self.assertEqual(result["sum_turn_seconds"], 4)


if __name__ == "__main__":
    unittest.main()
