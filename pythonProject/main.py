import os
import zipfile
import io
import yaml
import pwd


class ShellEmulator:
    def __init__(self, config_file):
        # Загружаем конфигурацию
        self.config = self.load_config(config_file)
        self.username = self.config.get('username', 'user')
        self.fs_path = self.config['fs_path']
        self.current_dir = '/'

        # Инициализация виртуальной файловой системы
        self.init_fs()

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)

    def init_fs(self):
        # Загружаем виртуальную файловую систему в оперативную память
        with open(self.fs_path, 'rb') as f:
            self.zip_buffer = io.BytesIO(f.read())
        self.zip_file = zipfile.ZipFile(self.zip_buffer)

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
        try:
            entries = {info.filename for info in self.zip_file.infolist() if info.filename.startswith(path)}
            for entry in entries:
                relative_entry = os.path.relpath(entry, path)
                print(relative_entry.split('/')[0])  # Only print top-level files in the current directory
        except KeyError:
            print(f"ls: cannot access '{self.current_dir}': No such directory")

    def cd(self, path):
        # Переход в другую директорию внутри архива
        new_dir = os.path.normpath(os.path.join(self.current_dir, path)).lstrip('/')
        entries = {info.filename for info in self.zip_file.infolist()}
        if any(entry.startswith(new_dir) for entry in entries):
            self.current_dir = new_dir
        else:
            print(f"cd: {path}: No such directory")

    def mkdir(self, path):
        print("mkdir: cannot create directory in a read-only virtual filesystem")

    def chown(self, user, path):
        print("chown: cannot change ownership in a read-only virtual filesystem")


if __name__ == "__main__":
    emulator = ShellEmulator('config.yaml')
    emulator.run()
