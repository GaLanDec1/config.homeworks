import unittest
import os
import shutil
from main import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        # Создаем тестовый эмулятор и виртуальную файловую систему
        self.emulator = ShellEmulator('config.yaml')
        self.emulator.init_fs()

    def tearDown(self):
        # Очищаем временные файлы
        if os.path.exists(self.emulator.mount_point):
            shutil.rmtree(self.emulator.mount_point)

    def test_ls(self):
        self.emulator.current_dir = '/'
        output = self._run_command('ls')
        self.assertIn('testdir', output)

    def test_cd(self):
        self.emulator.current_dir = '/'
        self.emulator.cd('testdir')
        self.assertEqual(self.emulator.current_dir, 'testdir')

    def test_mkdir(self):
        self.emulator.current_dir = '/'
        self.emulator.mkdir('newdir')
        self.assertTrue(os.path.isdir(os.path.join(self.emulator.mount_point, 'newdir')))

    def test_chown_invalid_user(self):
        output = self._run_command('chown invaliduser testfile')
        self.assertIn("chown: invalid user", output)

    def _run_command(self, command):
        from io import StringIO
        import sys
        old_stdout = sys.stdout
        sys.stdout = output = StringIO()
        self.emulator.execute_command(command)
        sys.stdout = old_stdout
        return output.getvalue().strip()

if __name__ == '__main__':
    unittest.main()
