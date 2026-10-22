"""Keep the README's long-task count tied to an explicit case classification."""
import json
from collections import Counter
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

# Shorter than a three-hour computer-use session: one function, one rule, or a small teaching rebuild.
SHORT = frozenset({
    'rea-dinosaur-speed-case', 'rea-dino-runner-community-case', 'rea-dxball-case', 'rea-th04-case',
    'rea-calculator-percent-case', 'rea-aegis-case', 'rea-notion-case', 'rea-ctf-case',
    'rea-engine-tictactoe-case', 'snowball-war-rea-case', 'pocket-tasks-reconstruction-case',
    'sa3-marun-ai-decomp-case', 'ultrasunnymoon-rea-case', 'screen-studio-auto-zoom-case',
    'littlebird-static-rebuild-case', 'claude-code-background-lab-case', 'feishu-dual-instance-case',
    'kef-lsx-volume-case',
})
# Essays and studies. They describe other work and are not a job to rerun.
NOT_A_TASK = frozenset({
    'rea-touhou-reconstruction-method-case', 'agent-decompilation-oracle-case',
    'noflag-rea-evidence-architecture-study', 'rea-claude-code-isolated-ab-case',
})
TARGET = 1000


def cases():
    records = []
    for name in ('data/rea-resources.json', 'data/tool-resources.json'):
        records.extend(json.loads((ROOT / name).read_text(encoding='utf-8')))
    return [record for record in records if record.get('kind') == 'case-study']


class LongTaskScopeTests(unittest.TestCase):
    def test_every_case_is_classified_once_and_the_readme_states_the_gap(self):
        catalog = cases()
        identifiers = {record['id'] for record in catalog}
        self.assertFalse(SHORT & NOT_A_TASK)
        self.assertLessEqual(SHORT | NOT_A_TASK, identifiers)
        long_cases = [record for record in catalog if record['id'] not in SHORT and record['id'] not in NOT_A_TASK]
        by_target = Counter((record.get('targets') or ['?'])[0] for record in long_cases)
        self.assertEqual(
            (len(catalog), len(SHORT), len(NOT_A_TASK), len(long_cases), dict(sorted(by_target.items()))),
            (214, 18, 4, 192, {
                'app': 22, 'binary': 1, 'firmware': 5, 'game': 151, 'protocol': 9, 'website': 4,
            }),
        )
        self.assertLess(len(long_cases), TARGET)
        english = (ROOT / 'README.md').read_text(encoding='utf-8')
        chinese = (ROOT / 'README.zh-CN.md').read_text(encoding='utf-8')
        self.assertIn(
            '**192** of 214 curated cases are whole-program work large enough for a computer-use session past three hours, against a target of **1,000** (game 151, app 22, protocol 9, firmware 5, website 4, native binary 1).',
            english,
        )
        self.assertIn(
            '214 条精选案例中有 **192** 条属于完整程序规模，足够一次超过三小时的计算机使用会话，目标是 **1,000**（游戏 151、应用 22、协议 9、固件 5、网站 4、原生二进制 1）。',
            chinese,
        )


if __name__ == '__main__':
    unittest.main()
