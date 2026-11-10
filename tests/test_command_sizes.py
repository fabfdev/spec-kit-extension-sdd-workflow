import unittest
from pathlib import Path

# invariant: every command is loaded whole on each invocation; this caps its token cost.
LIMIT_BYTES = 3072
# why: these run once per project (inception or migration), so their size is not a per-session cost.
ONE_TIME = {"setup", "product-prd", "sdd", "import-notion"}
ONE_TIME_LIMIT_BYTES = 8192
COMMANDS = Path(__file__).resolve().parents[1] / "commands"


class CommandSizeTest(unittest.TestCase):
    def test_commands_stay_small(self):
        files = sorted(COMMANDS.glob("*.md"))
        self.assertTrue(files)
        too_big = {}
        for path in files:
            name = path.stem.rpartition(".")[2]
            limit = ONE_TIME_LIMIT_BYTES if name in ONE_TIME else LIMIT_BYTES
            if path.stat().st_size > limit:
                too_big[path.name] = (path.stat().st_size, limit)
        self.assertEqual(too_big, {})


if __name__ == "__main__":
    unittest.main()
