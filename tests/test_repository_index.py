"""Keep the generated repository directory free of pages the generator no longer renders."""
from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_repository_index
from build_repository_index import CATEGORIES, GENERATED_MARKER


def snapshot(directory):
    return {path.name: path.read_bytes() for path in directory.glob('*.md')}


class RepositoryIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rendered = build_repository_index.rendered_files()

    def run_generator(self, output, *arguments):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(build_repository_index, 'OUTPUT', output), \
                patch.object(build_repository_index, 'rendered_files', return_value=self.rendered), \
                patch.object(sys, 'argv', ['build_repository_index.py', *arguments]), \
                redirect_stdout(stdout), redirect_stderr(stderr):
            code = build_repository_index.main()
        return code, stderr.getvalue()

    def test_category_pages_link_their_website_category_page(self):
        from build_browse_pages import browse_path
        files, _ = self.rendered
        for category, labels in CATEGORIES.items():
            for language, suffix, label in (('en', '', 'On the website'), ('zh', '.zh-CN', '在网站浏览')):
                with self.subTest(category=category, language=language):
                    navigation = files[f'{category}{suffix}.md'].splitlines()[2]
                    self.assertIn(f'[{label}](https://awesomerea.org{browse_path(language, category)})', navigation)
                    self.assertEqual(navigation.count('https://awesomerea.org/'), 1)

    def test_obsolete_pages_fail_check_and_only_generated_ones_are_removed(self):
        tracked = ROOT / 'docs/repositories'
        before = snapshot(tracked)
        files, _ = self.rendered
        pages = {name for name in files if not name.startswith('../')}
        self.assertEqual(len(pages), 2 * (len(CATEGORIES) + 1))
        self.assertEqual(set(before), pages)
        with tempfile.TemporaryDirectory() as directory:
            # Mirror the repository layout so the root README summaries resolve inside the copy.
            output = Path(directory) / 'docs/repositories'
            shutil.copytree(tracked, output)
            for name in ('README.md', 'README.zh-CN.md'):
                shutil.copy2(ROOT / name, Path(directory) / name)
            self.assertEqual(self.run_generator(output, '--check'), (0, ''))

            (output / 'old-category.md').write_text('# Old category\n\n' + GENERATED_MARKER + '\n', encoding='utf-8')
            (output / 'notes.md').write_text('# Maintainer notes\n', encoding='utf-8')
            code, message = self.run_generator(output, '--check')
            self.assertEqual(code, 1)
            self.assertIn('docs/repositories/old-category.md', message)
            self.assertIn('docs/repositories/notes.md', message)

            code, message = self.run_generator(output)
            self.assertEqual(code, 0)
            self.assertFalse((output / 'old-category.md').exists())
            self.assertEqual((output / 'notes.md').read_text(encoding='utf-8'), '# Maintainer notes\n')
            self.assertIn('Kept docs/repositories/notes.md', message)
            self.assertEqual({name: data for name, data in snapshot(output).items() if name != 'notes.md'}, before)
            for name in ('README.md', 'README.zh-CN.md'):
                self.assertEqual((Path(directory) / name).read_bytes(), (ROOT / name).read_bytes())

            code, message = self.run_generator(output, '--check')
            self.assertEqual(code, 1)
            self.assertIn('docs/repositories/notes.md', message)
            self.assertNotIn('old-category.md', message)
            self.assertNotIn('needs regeneration', message)
        self.assertEqual(snapshot(tracked), before)


if __name__ == '__main__':
    unittest.main()
