"""Run with python -m unittest discover -s .ig-growth/tests -v."""
import copy
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import carousel_visuals as visuals
spec = importlib.util.spec_from_file_location("pipeline", ROOT / "content_pipeline.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / "tests", prefix="run-")
        self.directory = Path(self.tmp.name)
        self.content = p.read_json(ROOT / "content/sample-gmail.json")
        self.brand = p.read_json(ROOT / "content/brand.json")
        self.bundle = p.read_json(ROOT / "content/sources.json")
        for source in self.bundle["sources"]:
            source["checked_on"] = datetime.now(timezone.utc).date().isoformat()
        self.topic = {"id": "test-post", "title": "Test", "format": "carousel"}

    def tearDown(self):
        self.tmp.cleanup()

    def test_real_sample_passes_checks(self):
        self.assertEqual(p.validate(self.content, self.bundle), [])

    def test_unknown_source_blocks_export(self):
        self.content["slides"][0]["source_ids"] = ["invented"]
        self.assertTrue(p.validate(self.content, self.bundle))

    def test_fabricated_quote_blocks_export(self):
        self.content["claims"][0]["evidence"] = "Something the source never said."
        self.assertTrue(p.validate(self.content, self.bundle))

    def test_unrelated_claim_is_rejected(self):
        self.content["claims"][0]["text"] = "Not in post"
        self.assertTrue(p.validate(self.content, self.bundle))

    def test_price_without_evidence_is_rejected(self):
        self.content["caption"] = "Cijena je 99 EUR mjesečno."
        self.assertTrue(p.validate(self.content, self.bundle))

    def test_invented_personal_outcome_is_rejected(self):
        self.content["caption"] = "Zaradio sam mnogo."
        self.assertTrue(p.validate(self.content, self.bundle))

    def test_duplicate_titles_are_rejected(self):
        self.content["slides"][1]["title"] = self.content["slides"][0]["title"]
        self.assertTrue(p.validate(self.content, self.bundle))

    def test_malformed_model_output_fails_closed(self):
        for value in (None, [], "not json", {"slides": [None, None, None]}):
            with self.subTest(value=value):
                self.assertTrue(p.validate(value, self.bundle))

    def test_source_age_and_future_date(self):
        path = self.directory / "sources.json"
        for days in (31, -1):
            self.bundle["sources"][0]["checked_on"] = (
                datetime.now(timezone.utc).date() - timedelta(days=days)).isoformat()
            p.write_json(path, self.bundle)
            with self.assertRaises(ValueError):
                p.source_bundle(path)

    def test_duplicate_sources_rejected(self):
        self.bundle["sources"].append(copy.deepcopy(self.bundle["sources"][0]))
        path = self.directory / "sources.json"
        p.write_json(path, self.bundle)
        with self.assertRaises(ValueError):
            p.source_bundle(path)

    def test_path_traversal_rejected(self):
        for value in ("../other", "C:/outside", "", "UPPER", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                p.slug(value)

    def build(self):
        return p.produce(self.topic, self.brand, self.bundle, self.directory, content=self.content)

    def test_export_dimensions_and_review_files(self):
        from PIL import Image
        self.build()
        package = self.directory / "test-post"
        images = sorted(package.glob("slajd-*.png"))
        self.assertEqual(len(images), 6)
        for file in images:
            with Image.open(file) as image:
                self.assertEqual(image.size, (1080, 1350))
        self.assertTrue((package / "index.html").is_file())
        self.assertTrue((package / "izvori.md").is_file())
        self.assertEqual(p.read_json(package / "status.json")["status"], "ready_for_review")

    def test_cache_does_not_regenerate_or_reset_approval(self):
        self.build()
        package = self.directory / "test-post"
        p.approve(package, "Test Editor")
        result = self.build()
        self.assertTrue(result["cached"])
        self.assertEqual(result["status"], "approved")

    def test_changed_caption_invalidates_approval(self):
        self.build()
        package = self.directory / "test-post"
        (package / "opis.txt").write_text("Changed", encoding="utf-8")
        with self.assertRaises(ValueError):
            p.approve(package, "Test Editor")

    def test_changed_inputs_require_new_version(self):
        self.build()
        self.topic["title"] = "Changed title"
        with self.assertRaises(ValueError):
            self.build()

    def test_long_word_fails_without_leaving_partial_package(self):
        self.content["slides"][0]["body"] = "W" * 200
        with self.assertRaises(ValueError):
            self.build()
        self.assertFalse((self.directory / "test-post").exists())
        self.assertFalse(list(self.directory.glob(".build-*")))

    def test_retry_passes_feedback_and_stops_after_success(self):
        class Writer:
            model = "test"
            calls = 0

            def generate(writer, topic, brand, bundle, feedback):
                writer.calls += 1
                if writer.calls == 1:
                    return {"slides": []}
                self.assertTrue(feedback)
                return copy.deepcopy(self.content)

            def review(writer, content, bundle):
                return []

        writer = Writer()
        result = p.produce(self.topic, self.brand, self.bundle, self.directory, writer=writer)
        self.assertEqual(writer.calls, 2)
        self.assertEqual(result["status"], "ready_for_review")

    def test_failed_ai_review_exhausts_bounded_retries(self):
        class Writer:
            model = "test"
            calls = 0

            def generate(writer, *args):
                writer.calls += 1
                return copy.deepcopy(self.content)

            def review(writer, *args):
                return ["Unsupported implication"]

        writer = Writer()
        with self.assertRaises(ValueError):
            p.produce(self.topic, self.brand, self.bundle, self.directory, writer=writer, attempts=2)
        self.assertEqual(writer.calls, 2)
        self.assertFalse((self.directory / "test-post").exists())

    def test_partial_batch_continues_after_missing_source(self):
        p.write_json(self.directory / "sources.json", self.bundle)
        p.write_json(self.directory / "content.json", self.content)
        queue = {"topics": [
            {"id": "bad", "format": "carousel", "sources_file": "missing.json"},
            {"id": "good", "format": "carousel", "sources_file": "sources.json", "content_file": "content.json"},
        ]}
        p.write_json(self.directory / "queue.json", queue)
        code = p.main(["build", "--queue", str(self.directory / "queue.json"),
                       "--output", str(self.directory / "out"), "--brand", str(ROOT / "content/brand.json")])
        self.assertEqual(code, 1)
        report = p.read_json(self.directory / "out/batch-report.json")
        self.assertEqual([r["status"] for r in report], ["needs_attention", "ready_for_review"])

    def test_script_and_style_are_excluded_from_research(self):
        parser = p.PageText()
        parser.feed("<h1>Official source</h1><script>bad()</script><style>x</style><p>Useful text</p>")
        self.assertEqual(" ".join(parser.parts), "Official source Useful text")

    def test_failed_refresh_does_not_replace_source_notes(self):
        path = self.directory / "sources.json"
        p.write_json(path, self.bundle)
        before = path.read_bytes()
        with patch.object(p, "urlopen", side_effect=OSError("offline")):
            with self.assertRaises(OSError):
                p.refresh_sources(path)
        self.assertEqual(path.read_bytes(), before)

    def test_provider_request_and_review_json_contract(self):
        responses = iter([self.content, {"supported": True, "problems": []}])
        requests = []

        def create(**kwargs):
            requests.append(kwargs)
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(
                content=json.dumps(next(responses), ensure_ascii=False)))])

        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        with patch("openai.OpenAI", return_value=client):
            writer = p.AIWriter("test-model", "https://example.com/v1")
        draft = writer.generate(self.topic, self.brand, self.bundle, [])
        self.assertEqual(writer.review(draft, self.bundle), [])
        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0]["response_format"], {"type": "json_object"})
        payload = json.loads(requests[0]["messages"][1]["content"])
        self.assertEqual(payload["topic"], self.topic)
        self.assertEqual(payload["sources"], self.bundle["sources"])

    def test_duplicate_post_across_themes_is_blocked(self):
        self.build()
        self.topic["id"] = "another-post"
        with self.assertRaises(ValueError):
            self.build()
        self.assertFalse((self.directory / "another-post").exists())

    def test_approval_rejects_stale_package_sources(self):
        self.build()
        package = self.directory / "test-post"
        bundle = p.read_json(package / "sources.json")
        bundle["sources"][0]["checked_on"] = "2000-01-01"
        p.write_json(package / "sources.json", bundle)
        state = p.read_json(package / "status.json")
        state["files"] = p.manifest(package)
        p.write_json(package / "status.json", state)
        with self.assertRaises(ValueError):
            p.approve(package, "Test Editor")

    def asset_catalogue(self, **overrides):
        from PIL import Image
        image = self.directory / "screen.png"
        Image.new("RGB", (1000, 600), "#FFFFFF").save(image)
        entry = {"id": "real-screen", "file": "screen.png", "type": "screenshot",
                 "description": "Testni snimak sa označenim poljem pretrage", **overrides}
        path = self.directory / "assets.json"
        p.write_json(path, {"assets": [entry]})
        return path, visuals.load_catalogue(path)

    def test_unknown_asset_cannot_be_invented_by_model(self):
        self.content["slides"][1]["visual"] = {"kind": "image", "asset_id": "invented"}
        self.assertTrue(p.validate(self.content, self.bundle))

    def test_malformed_visuals_are_rejected(self):
        for value in (None, [], {}, {"kind": "imaginary"}, {"kind": "image", "asset_id": []},
                      {"kind": "inbox", "layout": "text"}, {"kind": "none", "layout": "split"}):
            with self.subTest(value=value):
                self.content["slides"][0]["visual"] = value
                self.assertTrue(p.validate(self.content, self.bundle))

    def test_catalogue_checks_missing_file_before_api_call(self):
        path = self.directory / "assets.json"
        p.write_json(path, {"assets": [{"id": "missing", "file": "missing.png", "type": "screenshot", "description": "Missing file"}]})
        with self.assertRaises(FileNotFoundError):
            visuals.load_catalogue(path)

    def test_catalogue_rejects_traversal_and_invalid_boxes(self):
        path, _ = self.asset_catalogue()
        for override in ({"file": "../outside.png"}, {"redactions": [[.9, 0, .5, .2]]},
                         {"crop": [0, 0, 0, 1]}, {"min_display_width": "small"},
                         {"annotations": [{"box": [0, 0, .2, .2], "label": "Field", "arrow_from": [-1, 0]}]}):
            with self.subTest(override=override):
                data = p.read_json(path)
                data["assets"][0].update(override)
                p.write_json(path, data)
                with self.assertRaises(ValueError):
                    visuals.load_catalogue(path)
                path, _ = self.asset_catalogue()

    def test_crop_and_redaction_are_applied_to_exported_asset(self):
        _, catalogue = self.asset_catalogue(crop=[.1, .1, .8, .8], redactions=[[.1, .1, .2, .2]])
        image = visuals.prepared_asset(catalogue["real-screen"], p.font_path)
        self.assertEqual(image.size, (800, 480))
        self.assertEqual(image.getpixel((160, 96)), (20, 32, 51))
        self.assertEqual(image.getpixel((790, 470)), (255, 255, 255))

    def test_screen_package_bundles_only_prepared_asset_and_visual_alt(self):
        from PIL import Image
        _, catalogue = self.asset_catalogue(redactions=[[.1, .1, .2, .2]], annotations=[
            {"box": [.45, .3, .3, .2], "label": "Polje pretrage", "arrow_from": [.15, .65]}])
        self.content["slides"][1]["visual"] = {"kind": "image", "layout": "stacked", "asset_id": "real-screen"}
        p.produce(self.topic, self.brand, self.bundle, self.directory / "out", content=self.content, catalogue=catalogue)
        package = self.directory / "out/test-post"
        self.assertFalse((package / "screen.png").exists())
        with Image.open(package / "vizual-real-screen.png") as image:
            self.assertEqual(image.getpixel((200, 120)), (20, 32, 51))
        document = p.read_json(package / "content.json")
        self.assertIn("Polje pretrage", document["slides"][1]["alt"])
        self.assertIn("real-screen", p.read_json(package / "visuals.json"))
        p.approve(package, "Test Editor")
        (package / "vizual-real-screen.png").write_bytes(b"modified")
        with self.assertRaises(ValueError):
            p.approve(package, "Test Editor")

    def test_tiny_screenshot_is_blocked_instead_of_silently_shrunk(self):
        _, catalogue = self.asset_catalogue()
        self.content["slides"][1]["visual"] = {"kind": "image", "layout": "split", "asset_id": "real-screen"}
        with self.assertRaises(ValueError):
            p.produce(self.topic, self.brand, self.bundle, self.directory / "out", content=self.content, catalogue=catalogue)
        self.assertFalse((self.directory / "out/test-post").exists())

    def test_source_image_changes_invalidate_package_cache(self):
        from PIL import Image
        path, catalogue = self.asset_catalogue()
        self.content["slides"][1]["visual"] = {"kind": "image", "layout": "stacked", "asset_id": "real-screen"}
        p.produce(self.topic, self.brand, self.bundle, self.directory / "out", content=self.content, catalogue=catalogue)
        Image.new("RGB", (1000, 600), "#000000").save(self.directory / "screen.png")
        updated = visuals.load_catalogue(path)
        self.assertNotEqual(visuals.catalogue_snapshot(catalogue), visuals.catalogue_snapshot(updated))
        with self.assertRaises(ValueError):
            p.produce(self.topic, self.brand, self.bundle, self.directory / "out", content=self.content, catalogue=updated)

    def test_layouts_are_visually_distinct_and_have_correct_dimensions(self):
        hashes = set()
        for layout in ("cover", "split", "stacked", "comparison"):
            image = visuals.render_slide(self.content["slides"][1], {"kind": "filter", "layout": layout},
                                         self.brand, {}, 2, 6, p.font_path, p.fit)
            self.assertEqual(image.size, (1080, 1350))
            hashes.add(p.digest(image.tobytes().hex()))
        self.assertEqual(len(hashes), 4)


if __name__ == "__main__":
    unittest.main()
