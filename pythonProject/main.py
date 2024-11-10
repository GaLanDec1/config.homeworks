import os
import zipfile
import io
import yaml


class ShellEmulator:
    def __init__(self, config_file):
        # Загружаем конфигурацию
        self.config = self.load_config(config_file)
        self.username = self.config.get('username', 'user')
        self.fs_path = self.config['fs_path']
        self.current_dir = '/'

        # Инициализация виртуальной файловой системы
        self.fs = {}  # Словарь для хранения файловой системы
        self.owners = {}  # Словарь для хранения владельцев файлов
        self.init_fs()

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)

    def init_fs(self):
        # Загружаем виртуальную файловую систему из zip-архива в словари
        with open(self.fs_path, 'rb') as f:
            zip_buffer = io.BytesIO(f.read())
        with zipfile.ZipFile(zip_buffer) as zip_file:
            for file_info in zip_file.infolist():
                path = file_info.filename
                if file_info.is_dir():
                    self.fs[path] = None  # None для директорий
                else:
                    with zip_file.open(path) as file:
                        self.fs[path] = file.read()  # Содержимое файла в байтах
                self.owners[path] = 'system'  # По умолчанию владелец 'system'

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
        # Список файлов в текущей директории внутри архива
        path = self.current_dir.lstrip('/')
        entries = {p for p in self.fs.keys() if p.startswith(path)}
        for entry in entries:
            relative_entry = os.path.relpath(entry, path)
            print(relative_entry.split('/')[0])  # Only print top-level files in the current directory

    def cd(self, path):
        # Переход в другую директорию внутри словаря fs
        new_dir = os.path.normpath(os.path.join(self.current_dir, path)).lstrip('/')
        if new_dir in self.fs and self.fs[new_dir] is None:  # Проверка на существование директории
            self.current_dir = new_dir
        else:
            print(f"cd: {path}: No such directory")

    def mkdir(self, path):
        # Создание новой директории в словаре fs
        new_dir = os.path.normpath(os.path.join(self.current_dir, path)).lstrip('/')
        if new_dir in self.fs:
            print(f"mkdir: cannot create directory '{path}': Directory exists")
        else:
            self.fs[new_dir] = None  # Добавляем директорию в fs
            self.owners[new_dir] = self.username  # Назначаем владельца текущего пользователя
            print(f"Directory '{path}' created.")

    def chown(self, user, path):
        # Изменение владельца файла/директории в словаре owners
        target_path = os.path.normpath(os.path.join(self.current_dir, path)).lstrip('/')
        if target_path in self.fs:
            self.owners[target_path] = user  # Изменяем владельца
            print(f"Owner of '{path}' changed to {user}.")
        else:
            print(f"chown: cannot access '{path}': No such file or directory")


if __name__ == "__main__":
    emulator = ShellEmulator('config.yaml')
    emulator.run()
