import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from spire.doc import *
from spire.doc.common import *

class ODTtoDOCXConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("ODT → DOCX Конвертер with love by Dimasik")
        self.root.geometry("750x550")
        
        # Список файлов для конвертации
        self.files_to_convert = []
        
        # Папка для сохранения (по умолчанию - папка с исходными файлами)
        self.output_folder = ""
        
        # Настройка интерфейса
        self.setup_ui()
        
    def setup_ui(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок
        title = ttk.Label(main_frame, text="ODT в DOCX Конвертер with love by Dimasik", font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Инструкция
        info = ttk.Label(main_frame, text="Выбирай ODT файлы для конвертации в DOCX")
        info.pack(pady=(0, 10))
        
        # Рамка для выбора папки сохранения
        folder_frame = ttk.LabelFrame(main_frame, text="📁 Папка для сохранения", padding=10)
        folder_frame.pack(fill=tk.X, pady=10)
        
        # Поле для отображения пути
        self.folder_path_var = tk.StringVar()
        self.folder_path_var.set("(будут сохранены рядом с исходными файлами)")
        
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path_var, 
                                 state='readonly', font=("Arial", 9))
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Кнопка выбора папки
        self.btn_folder = ttk.Button(folder_frame, text="📂 Выбрать папку", 
                                     command=self.choose_output_folder)
        self.btn_folder.pack(side=tk.RIGHT)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        self.btn_add = ttk.Button(button_frame, text="📁 Добавить файлы", 
                                  command=self.add_files)
        self.btn_add.pack(side=tk.LEFT, padx=5)
        
        self.btn_clear = ttk.Button(button_frame, text="🗑️ Очистить список", 
                                    command=self.clear_list)
        self.btn_clear.pack(side=tk.LEFT, padx=5)
        
        self.btn_convert = ttk.Button(button_frame, text="⚡ Конвертировать все", 
                                      command=self.start_conversion)
        self.btn_convert.pack(side=tk.LEFT, padx=5)
        
        # Список файлов
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Создаем Listbox с Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, 
                                      yscrollcommand=scrollbar.set,
                                      font=("Arial", 9), height=12)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Статус бар
        self.status_label = ttk.Label(main_frame, text="Готов к работе")
        self.status_label.pack(pady=(10, 5))
        
        # Прогресс бар
        self.progress = ttk.Progressbar(main_frame, length=500, mode='determinate')
        self.progress.pack(pady=5)
        
        # Статистика
        self.stats_label = ttk.Label(main_frame, text="", font=("Arial", 9))
        self.stats_label.pack(pady=5)
        
    def choose_output_folder(self):
        """Выбор папки для сохранения"""
        folder = filedialog.askdirectory(
            title="Выбирай папку для сохранения DOCX файлов"
        )
        if folder:
            self.output_folder = folder
            self.folder_path_var.set(folder)
        else:
            # Если пользователь отменил выбор
            self.output_folder = ""
            self.folder_path_var.set("(будут сохранены рядом с исходными файлами)")
    
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Выбирай ODT файлы",
            filetypes=[("ODT файлы", "*.odt"), ("Все файлы", "*.*")]
        )
        if files:
            for f in files:
                if f not in self.files_to_convert:
                    self.files_to_convert.append(f)
                    self.file_listbox.insert(tk.END, f)
            self.update_status()
    
    def clear_list(self):
        self.files_to_convert.clear()
        self.file_listbox.delete(0, tk.END)
        self.update_status()
        self.stats_label.config(text="")
        self.progress['value'] = 0
    
    def update_status(self):
        count = len(self.files_to_convert)
        self.status_label.config(text=f"Выбрано файлов: {count}")
    
    def start_conversion(self):
        if not self.files_to_convert:
            messagebox.showwarning("Нихерасе", "Добавь хотя бы один ODT файл!")
            return
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=self.convert_files)
        thread.daemon = True
        thread.start()
    
    def convert_files(self):
        # Блокируем кнопки
        self.btn_add.config(state=tk.DISABLED)
        self.btn_clear.config(state=tk.DISABLED)
        self.btn_convert.config(state=tk.DISABLED)
        self.btn_folder.config(state=tk.DISABLED)
        self.status_label.config(text="Пошёл процесс...")
        
        total = len(self.files_to_convert)
        success = 0
        failed = 0
        failed_files = []
        
        self.progress['maximum'] = total
        self.progress['value'] = 0
        
        for i, file_path in enumerate(self.files_to_convert):
            try:
                # Обновляем статус
                self.root.after(0, lambda f=file_path: self.status_label.config(
                    text=f"Конвертация: {os.path.basename(f)}"
                ))
                
                # Загружаем документ
                doc = Document()
                doc.LoadFromFile(file_path)
                
                # Определяем путь для сохранения
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                
                if self.output_folder:
                    # Если выбрана папка - сохраняем туда
                    output_path = os.path.join(self.output_folder, f"{base_name}.docx")
                else:
                    # Иначе сохраняем рядом с исходником
                    source_folder = os.path.dirname(file_path)
                    output_path = os.path.join(source_folder, f"{base_name}.docx")
                
                # Сохраняем в DOCX
                doc.SaveToFile(output_path, FileFormat.Docx)
                doc.Close()
                
                success += 1
                
            except Exception as e:
                failed += 1
                failed_files.append(os.path.basename(file_path))
                print(f"Ошибка при конвертации {file_path}: {str(e)}")
            
            # Обновляем прогресс
            self.progress['value'] = i + 1
            self.root.update_idletasks()
        
        # Выводим результат
        self.root.after(0, lambda: self.show_result(success, failed, failed_files))
    
    def show_result(self, success, failed, failed_files):
        # Разблокируем кнопки
        self.btn_add.config(state=tk.NORMAL)
        self.btn_clear.config(state=tk.NORMAL)
        self.btn_convert.config(state=tk.NORMAL)
        self.btn_folder.config(state=tk.NORMAL)
        
        # Показываем, куда сохранялись файлы
        save_location = self.output_folder if self.output_folder else "рядом с исходными файлами"
        
        message = f"📁 Сохранено: {save_location}\n\n"
        message += f"✅ Успешно: {success}\n❌ Ошибок: {failed}"
        
        if failed_files:
            message += f"\n\nНе удалось конвертировать:\n" + "\n".join(failed_files[:5])
            if len(failed_files) > 5:
                message += f"\n... и еще {len(failed_files) - 5} файлов"
        
        self.stats_label.config(text=message)
        self.status_label.config(text="Конвертация завершена!")
        
        if failed == 0 and success > 0:
            messagebox.showinfo("Успешно!", f"Все {success} Готово, ёмаё!\n\nСохранено: {save_location}")
        elif failed > 0 and success > 0:
            messagebox.showwarning("Завершено с ошибками", message)
        else:
            messagebox.showerror("Ошибка", "Не удалось сконвертировать ни одного файла!")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = ODTtoDOCXConverter(root)
    root.mainloop()