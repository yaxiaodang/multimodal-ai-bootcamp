"""工程检查：不运行 Docling 解析，不生成学习实验结果。"""

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("run_pipeline.py")
spec = importlib.util.spec_from_file_location("week06_pipeline", SCRIPT)
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)


class PipelineTests(unittest.TestCase):
    def test_export_and_schema_check_without_pdf_parsing(self):
        from docling_core.types.doc import DocItemLabel, DoclingDocument, Size
        document = DoclingDocument(name="engineering-fixture")
        document.add_page(page_no=1, size=Size(width=100, height=100))
        document.add_text(label=DocItemLabel.TEXT, text="Engineering fixture, not PDF output.")
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            document.save_as_markdown(folder / "document.md")
            document.save_as_json(folder / "document.json")
            self.assertTrue(pipeline.check_outputs(folder, 1)["passed"])
            (folder / "document.json").write_text("{invalid json")
            self.assertFalse(pipeline.check_outputs(folder, 1)["passed"])

    def test_changed_input_hash_is_rejected(self):
        config = json.loads((pipeline.WEEK / "configs/baseline.json").read_text())
        manifest = json.loads(pipeline.repo_file(config["manifest"]).read_text())
        manifest["documents"][0]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory(dir=pipeline.WEEK) as temporary:
            folder = Path(temporary)
            (folder / "manifest.json").write_text(json.dumps(manifest))
            config["manifest"] = str((folder / "manifest.json").relative_to(pipeline.REPO))
            config_path = folder / "config.json"
            config_path.write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                pipeline.preflight(config_path)

    def test_prepare_only_does_not_create_run_directory(self):
        config_path = pipeline.WEEK / "configs/baseline.json"
        before = set((pipeline.WEEK / "runs").iterdir())
        config, manifest, _ = pipeline.preflight(config_path)
        self.assertEqual(len(manifest["documents"]), 3)
        self.assertEqual(config["device"], "cpu")
        self.assertEqual(set((pipeline.WEEK / "runs").iterdir()), before)

    def exercise_failure(self, first_worker_timeout):
        config_path = pipeline.WEEK / "configs/baseline.json"
        config, manifest, manifest_path = pipeline.preflight(config_path)
        calls = []

        def fake_subprocess(command, **kwargs):
            if command[0] == "git":
                return SimpleNamespace(stdout="engineering-test\n", returncode=0)
            if "freeze" in command:
                return SimpleNamespace(stdout="engineering-test==0\n", returncode=0)
            calls.append(command)
            kwargs["stderr"].write(b"Engineering fault injection; no document parsed.\n")
            if len(calls) == 1:
                if first_worker_timeout:
                    raise subprocess.TimeoutExpired(command, 600)
                return SimpleNamespace(returncode=1)
            return SimpleNamespace(returncode=0)

        with tempfile.TemporaryDirectory(dir=pipeline.WEEK) as temporary:
            config["output_root"] = str((Path(temporary) / "runs").relative_to(pipeline.REPO))
            with patch.object(pipeline.subprocess, "run", side_effect=fake_subprocess), \
                 patch.object(pipeline, "verify_model_files"), \
                 patch.object(pipeline, "pipeline_options", return_value=SimpleNamespace(model_dump=lambda **kw: {})), \
                 patch.object(pipeline, "check_outputs", return_value={"passed": True, "scope": "mock engineering check"}):
                result = pipeline.run(config_path, (config, manifest, manifest_path))
            run_dir, = (Path(temporary) / "runs").iterdir()
            metadata = json.loads((run_dir / "run-metadata.json").read_text())
            self.assertEqual(result, 1)
            self.assertEqual(len(calls), 3)
            self.assertEqual(metadata["status"], "failed")
            self.assertEqual([doc["status"] for doc in metadata["documents"]], ["failed", "completed", "completed"])
            self.assertEqual(metadata["documents"][0]["exit_code"], 124 if first_worker_timeout else 1)
            for doc in manifest["documents"]:
                self.assertTrue((run_dir / doc["id"] / "stderr.log").exists())
            self.assertIn("待核验", (run_dir / "review.csv").read_text())

    def test_worker_failure_keeps_logs_and_continues(self):
        self.exercise_failure(first_worker_timeout=False)

    def test_worker_timeout_keeps_logs_and_continues(self):
        self.exercise_failure(first_worker_timeout=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
