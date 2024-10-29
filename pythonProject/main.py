import os
import zipfile
import shutil
import yaml
import pwd

class ShellEmulator:
    def __init__(self, config_file):
        # Загружаем конфигурацию
        self.config = self.load_config(config_file)
        self.username = self.config.get('username', 'user')
        self.fs_path = self.config['fs_path']
        self.current_dir = '/'
        self.mount_point = '/tmp/emulator_fs'

        # Инициализация виртуальной файловой системы
        self.init_fs()

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)

    def init_fs(self):
        # Распаковываем виртуальную файловую систему
        if os.path.exists(self.mount_point):
            shutil.rmtree(self.mount_point)
        os.makedirs(self.mount_point)

        with zipfile.ZipFile(self.fs_path, 'r') as zip_ref:
            zip_ref.extractall(self.mount_point)

    def run(self):
        while True:
            try:
                command = input(f'{self.username}@shell:{self.current_dir}$ ')
                if command.strip():
                    self.execute_command(command.strip())
            except (KeyboardInterrupt, EOFError):
                print("\nExiting shell.")
                break

    def execute_command(self, command):
        args = command.split()
        cmd = args[0]

        if cmd == 'exit':
            print("Exiting shell.")
            exit(0)
        elif cmd == 'ls':
            self.ls()
        elif cmd == 'cd':
            self.cd(args[1] if len(args) > 1 else '/')
        elif cmd == 'mkdir':
            if len(args) < 2:
                print("mkdir: missing operand")
            else:
                self.mkdir(args[1])
        elif cmd == 'chown':
            if len(args) < 3:
                print("chown: missing operand")
            else:
                self.chown(args[1], args[2])
        else:
            print(f'{cmd}: command not found')

    def ls(self):
        # Список файлов в текущей директории
        path = os.path.join(self.mount_point, self.current_dir.lstrip('/'))
        try:
            for entry in os.listdir(path):
                print(entry)
        except FileNotFoundError:
            print(f"ls: cannot access '{self.current_dir}': No such directory")

    def cd(self, path):
        # Переход в другую директорию
        new_dir = os.path.abspath(os.path.join(self.mount_point, self.current_dir, path))
        if os.path.isdir(new_dir):
            self.current_dir = os.path.relpath(new_dir, self.mount_point)
        else:
            print(f"cd: {path}: No such directory")

    def mkdir(self, path):
        # Создание директории
        new_dir = os.path.join(self.mount_point, self.current_dir, path)
        try:
            os.makedirs(new_dir)
        except FileExistsError:
            print(f"mkdir: cannot create directory '{path}': File exists")

    def chown(self, user, path):
        # Изменение владельца файла или директории
        target = os.path.join(self.mount_point, self.current_dir, path)
        try:
            uid = pwd.getpwnam(user).pw_uid
            os.chown(target, uid, -1)
        except KeyError:
            print(f"chown: invalid user: '{user}'")
        except FileNotFoundError:
            print(f"chown: cannot access '{path}': No such file or directory")

if __name__ == "__main__":
    emulator = ShellEmulator('config.yaml')
    emulator.run()
