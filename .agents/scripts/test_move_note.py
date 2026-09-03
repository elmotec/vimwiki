from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / ".agents/scripts/move_note.py"
SPEC = importlib.util.spec_from_file_location("move_note", SCRIPT)
assert SPEC and SPEC.loader
move_note = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = move_note
SPEC.loader.exec_module(move_note)


class MoveNoteTests(unittest.TestCase):
    def make_notebook(self) -> tempfile.TemporaryDirectory[str]:
        temporary = tempfile.TemporaryDirectory[str]()
        root = Path(temporary.name)
        (root / "notes").mkdir()
        (root / "Home.md").write_text(
            "# Home\n\n[Target](notes/Target.md)\n", encoding="utf-8"
        )
        (root / "notes/Linker.md").write_text(
            "# Linker\n\n[Target](Target.md)\n", encoding="utf-8"
        )
        (root / "notes/Sibling.md").write_text("# Sibling\n", encoding="utf-8")
        (root / "notes/Target.md").write_text(
            "# Target\n\n[Sibling](Sibling.md#details)\n", encoding="utf-8"
        )
        return temporary

    def test_plan_updates_inbound_and_moved_note_relative_links(self) -> None:
        temporary = self.make_notebook()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)

        plan = move_note.build_plan(root, "notes/Target.md", "archive/Target.md")
        move_note.validate_plan(plan)

        self.assertEqual(len(plan.rewrites), 3)
        self.assertIn("[Target](archive/Target.md)", plan.contents[root / "Home.md"])
        self.assertIn(
            "[Target](../archive/Target.md)", plan.contents[root / "notes/Linker.md"]
        )
        self.assertIn(
            "[Sibling](../notes/Sibling.md#details)",
            plan.contents[root / "archive/Target.md"],
        )
        self.assertTrue((root / "notes/Target.md").exists(), "planning must not write")

    def test_apply_moves_and_rewrites(self) -> None:
        temporary = self.make_notebook()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        plan = move_note.build_plan(root, "notes/Target.md", "archive/Target.md")

        move_note.apply_plan(plan)

        self.assertFalse((root / "notes/Target.md").exists())
        self.assertTrue((root / "archive/Target.md").exists())
        self.assertIn("archive/Target.md", (root / "Home.md").read_text(encoding="utf-8"))

    def test_reference_style_link_to_moved_note_fails_without_writes(self) -> None:
        temporary = self.make_notebook()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        reference = root / "References.md"
        original = "# References\n\n[target]: notes/Target.md\n"
        reference.write_text(original, encoding="utf-8")

        with self.assertRaises(move_note.MoveError):
            move_note.build_plan(root, "notes/Target.md", "archive/Target.md")

        self.assertEqual(reference.read_text(encoding="utf-8"), original)
        self.assertTrue((root / "notes/Target.md").exists())

    def test_inline_code_link_is_not_rewritten_or_validated(self) -> None:
        temporary = self.make_notebook()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "Example.md").write_text(
            "# Example\n\n`[Target](notes/Target.md)`\n", encoding="utf-8"
        )

        plan = move_note.build_plan(root, "notes/Target.md", "archive/Target.md")

        self.assertIn(
            "`[Target](notes/Target.md)`", plan.contents[root / "Example.md"]
        )


if __name__ == "__main__":
    unittest.main()
