import os
import sys
import subprocess
import threading
import time
from pathlib import Path
import pystray
from PIL import Image
import psutil

class TrayApp:
    def __init__(self):
        self.processes = []
        self.programs = [
            r"C:\Apps\TilingForWindows\Apps\GlazeWM\glazewm.exe",
            r"C:\Apps\TilingForWindows\Apps\Yasb\yasb.exe",
            r"C:\Apps\TilingForWindows\Apps\FlowLauncher\Flow.Launcher.exe",
            r"C:\Program Files (x86)\Winstep\Nexus.exe"
        ]
        # Путь к ярлыку/батнику автозагрузки
        self.startup_entry = Path(os.getenv('APPDATA')) / r"Microsoft\Windows\Start Menu\Programs\Startup\TilingForWindows.bat"
        
        # Проверяем существование файлов программ
        self.check_programs_exist()
        
        # Создаем иконку для трея
        self.create_tray_icon()
    
    def check_programs_exist(self):
        """Проверяем, существуют ли указанные программы"""
        for program in self.programs:
            if not os.path.exists(program):
                print(f"Предупреждение: Программа не найдена: {program}")
                # Можно закомментировать следующую строку, если хотите продолжить
                # input("Нажмите Enter для продолжения...")
    
    def run_program(self, program_path):
        """Запускает программу и добавляет процесс в список"""
        try:
            if os.path.exists(program_path):
                # Запускаем программу
                process = subprocess.Popen(program_path)
                self.processes.append(process)
                print(f"Запущено: {os.path.basename(program_path)} (PID: {process.pid})")
            else:
                print(f"Ошибка: Файл не найден: {program_path}")
        except Exception as e:
            print(f"Ошибка при запуске {program_path}: {e}")
    
    def start_all_programs(self):
        """Запускает все программы в отдельных потоках"""
        print("Запуск всех программ...")
        
        # Запускаем каждую программу в отдельном потоке
        for program in self.programs:
            thread = threading.Thread(target=self.run_program, args=(program,))
            thread.daemon = True
            thread.start()
            # Небольшая задержка между запусками
            time.sleep(1)
        
        print("Все программы запущены")
    
    def kill_all_programs(self):
        """Завершает все запущенные процессы"""
        print("\nЗавершение всех программ...")
        
        # Завершаем процессы, созданные нашим приложением
        for process in self.processes:
            try:
                if process.poll() is None:  # Если процесс еще работает
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"Завершено: PID {process.pid}")
            except Exception as e:
                print(f"Ошибка при завершении процесса {process.pid}: {e}")
        
        # Также пытаемся найти и завершить процессы по имени
        process_names = ["glazewm", "yasb", "Flow.Launcher", "nexus"]
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                for target_name in process_names:
                    if target_name in proc_name:
                        p = psutil.Process(proc.info['pid'])
                        p.terminate()
                        print(f"Завершено по имени: {proc.info['name']} (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        self.processes.clear()
        print("Все программы завершены")
    
    def create_tray_icon(self):
        """Создает иконку для системного трея"""
        
        icon_image = Image.open("icon.ico")
        
        # Создаем меню для иконки в трее
        menu = pystray.Menu(
            pystray.MenuItem("Запустить всё", self.on_restart, default=True),
            pystray.MenuItem("Закрыть всё", self.on_exit),
            pystray.MenuItem("Добавить в автозагрузку", self.on_add_startup),
            pystray.MenuItem("Удалить из автозагрузки", self.on_remove_startup),
            pystray.MenuItem("Выход", self.on_exit_app)
        )
        
        # Создаем иконку в трее
        self.icon = pystray.Icon("program_launcher", icon_image, "Программа-запускатель", menu)
    
    def on_restart(self, icon, item):
        """Перезапускает все программы"""
        print("Перезапуск программ...")
        self.kill_all_programs()
        time.sleep(2)
        self.start_all_programs()
    
    def on_exit(self, icon, item):
        """Закрывает все программы (но оставляет иконку в трее)"""
        print("Закрытие всех программ...")
        self.kill_all_programs()
    
    def on_exit_app(self, icon, item):
        """Полностью закрывает приложение"""
        print("Полное завершение...")
        self.kill_all_programs()
        self.icon.stop()

    def on_add_startup(self, icon, item):
        """Создает батник в папке автозагрузки для запуска текущего скрипта"""
        try:
            # startup_dir = self.startup_entry.parent
            # startup_dir.mkdir(parents=True, exist_ok=True)

            # python_exe = sys.executable
            # script_path = Path(__file__).resolve()

            # Используем батник, чтобы не требовались сторонние зависимости для .lnk
            # content = f'"{python_exe}" "{script_path}"\n'
            content = f'start "" "C:\\Apps\\TilingForWindows\\TilingForWindows.exe"'
            self.startup_entry.write_text(content, encoding="utf-8")
            print(f"Добавлено в автозагрузку: {self.startup_entry}")
        except Exception as e:
            print(f"Не удалось добавить в автозагрузку: {e}")

    def on_remove_startup(self, icon, item):
        """Удаляет батник из папки автозагрузки"""
        try:
            if self.startup_entry.exists():
                self.startup_entry.unlink()
                print(f"Удалено из автозагрузки: {self.startup_entry}")
            else:
                print("Запись автозагрузки не найдена")
        except Exception as e:
            print(f"Не удалось удалить из автозагрузки: {e}")
    
    def run(self):
        """Запускает приложение"""
        # Сначала запускаем все программы
        self.start_all_programs()
        
        # Затем запускаем иконку в трее
        print("Приложение запущено. Иконка в трее активна.")
        print("ПКМ по иконке для управления программами.")
        
        self.icon.run()

def main():
    # Проверяем, запущено ли приложение с правами администратора (рекомендуется)
    try:
        # Добавляем текущую директорию в PATH для импорта модулей
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Создаем и запускаем приложение
        app = TrayApp()
        app.run()
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)

if __name__ == "__main__":
    main()