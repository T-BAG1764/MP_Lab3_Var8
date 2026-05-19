import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random


# =============================================================================
# MODEL
# =============================================================================
class DictionaryModel:
    def __init__(self):
        self.filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dictionary.json")
        self.words = {}
        self.stats = {
            "added": 0,
            "edited": 0,
            "tests_total": 0,
            "tests_correct": 0
        }
        self.load_data()

    def load_data(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.words = data.get("words", {})
                    self.stats = data.get("stats", self.stats)
            except (json.JSONDecodeError, OSError):
                self.words = {}
                self.stats = {
                    "added": 0,
                    "edited": 0,
                    "tests_total": 0,
                    "tests_correct": 0
                }

    def save_data(self):
        data = {
            "words": self.words,
            "stats": self.stats
        }
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_word(self, english, russian):
        english = english.strip().lower()
        russian = russian.strip().lower()

        if not english or not russian:
            raise ValueError("Оба поля должны быть заполнены.")

        if english in self.words:
            raise ValueError("Такое английское слово уже существует.")

        self.words[english] = russian
        self.stats["added"] += 1
        self.save_data()

    def edit_word(self, english, new_russian):
        english = english.strip().lower()
        new_russian = new_russian.strip().lower()

        if english not in self.words:
            raise ValueError("Слово не найдено.")

        if not new_russian:
            raise ValueError("Перевод не может быть пустым.")

        self.words[english] = new_russian
        self.stats["edited"] += 1
        self.save_data()

    def search_word(self, english):
        english = english.strip().lower()
        return self.words.get(english)

    def get_all_words(self):
        return sorted(self.words.items())

    def get_random_word(self):
        if not self.words:
            return None
        return random.choice(list(self.words.items()))

    def check_translation(self, english, answer):
        correct = self.words.get(english.strip().lower())
        if correct is None:
            raise ValueError("Слово не найдено в словаре.")

        self.stats["tests_total"] += 1
        is_correct = correct == answer.strip().lower()
        if is_correct:
            self.stats["tests_correct"] += 1

        self.save_data()
        return is_correct, correct

    def get_stats_text(self):
        total_words = len(self.words)
        total_tests = self.stats["tests_total"]
        correct_tests = self.stats["tests_correct"]
        accuracy = (correct_tests / total_tests * 100) if total_tests > 0 else 0

        return (
            f"Количество слов в словаре: {total_words}\n"
            f"Добавлено слов: {self.stats['added']}\n"
            f"Отредактировано слов: {self.stats['edited']}\n"
            f"Всего тестов: {total_tests}\n"
            f"Правильных ответов: {correct_tests}\n"
            f"Точность: {accuracy:.2f}%"
        )


# =============================================================================
# VIEW
# =============================================================================
class DictionaryView:
    def __init__(self, root):
        self.root = root
        self.root.title("Англо-русский словарь")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)

        self.status_var = tk.StringVar(value="Готово")
        self.current_test_word = None

        self._cb = {}

        self._build_widgets()

    def _cb_call(self, name):
        return lambda: self._cb.get(name, lambda: None)()

    def _build_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_dictionary = ttk.Frame(notebook)
        self.tab_test = ttk.Frame(notebook)
        self.tab_stats = ttk.Frame(notebook)

        notebook.add(self.tab_dictionary, text="Словарь")
        notebook.add(self.tab_test, text="Тест")
        notebook.add(self.tab_stats, text="Статистика")

        self._build_dictionary_tab()
        self._build_test_tab()
        self._build_stats_tab()
        self._build_statusbar()

    def _build_dictionary_tab(self):
        input_frame = ttk.LabelFrame(self.tab_dictionary, text="Добавление и редактирование", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(input_frame, text="Английское слово:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.english_var = tk.StringVar()
        self.english_entry = ttk.Entry(input_frame, textvariable=self.english_var, width=30)
        self.english_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Русский перевод:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.russian_var = tk.StringVar()
        self.russian_entry = ttk.Entry(input_frame, textvariable=self.russian_var, width=30)
        self.russian_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(input_frame, text="Добавить слово", command=self._cb_call("add_word")).grid(row=0, column=2, padx=10, pady=5)
        ttk.Button(input_frame, text="Редактировать", command=self._cb_call("edit_word")).grid(row=1, column=2, padx=10, pady=5)

        search_frame = ttk.LabelFrame(self.tab_dictionary, text="Поиск", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(search_frame, text="Введите английское слово:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Найти", command=self._cb_call("search_word")).pack(side=tk.LEFT, padx=5)

        self.search_result_var = tk.StringVar(value="Результат поиска появится здесь")
        ttk.Label(search_frame, textvariable=self.search_result_var).pack(side=tk.LEFT, padx=15)

        list_frame = ttk.LabelFrame(self.tab_dictionary, text="Список слов", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("english", "russian")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.tree.heading("english", text="English")
        self.tree.heading("russian", text="Русский")
        self.tree.column("english", width=250)
        self.tree.column("russian", width=250)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _build_test_tab(self):
        test_frame = ttk.LabelFrame(self.tab_test, text="Проверка знаний", padding=20)
        test_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.test_word_var = tk.StringVar(value="Нажмите «Следующее слово»")
        ttk.Label(test_frame, textvariable=self.test_word_var, font=("Arial", 16)).pack(pady=20)

        ttk.Label(test_frame, text="Введите перевод:").pack(pady=5)
        self.test_answer_var = tk.StringVar()
        self.test_answer_entry = ttk.Entry(test_frame, textvariable=self.test_answer_var, width=30)
        self.test_answer_entry.pack(pady=5)

        btn_frame = ttk.Frame(test_frame)
        btn_frame.pack(pady=15)

        ttk.Button(btn_frame, text="Следующее слово", command=self._cb_call("next_test_word")).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Проверить", command=self._cb_call("check_test")).pack(side=tk.LEFT, padx=10)

        self.test_result_var = tk.StringVar(value="")
        ttk.Label(test_frame, textvariable=self.test_result_var, foreground="blue").pack(pady=15)

    def _build_stats_tab(self):
        stats_frame = ttk.LabelFrame(self.tab_stats, text="Статистика работы", padding=20)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.stats_text = tk.Text(stats_frame, height=12, width=60, state=tk.DISABLED, font=("Consolas", 12))
        self.stats_text.pack(pady=10)

        ttk.Button(stats_frame, text="Обновить статистику", command=self._cb_call("refresh_stats")).pack(pady=10)

    def _build_statusbar(self):
        status_bar = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(status_bar, textvariable=self.status_var, anchor=tk.W, padding=(6, 2)).pack(side=tk.LEFT)

    def set_status(self, text):
        self.status_var.set(text)

    def update_words_list(self, words):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for eng, rus in words:
            self.tree.insert("", tk.END, values=(eng, rus))

    def show_stats(self, text):
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert("1.0", text)
        self.stats_text.config(state=tk.DISABLED)

    def _on_tree_select(self, event=None):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.english_var.set(values[0])
            self.russian_var.set(values[1])


# =============================================================================
# CONTROLLER
# =============================================================================
class DictionaryController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view._cb.update({
            "add_word": self.add_word,
            "edit_word": self.edit_word,
            "search_word": self.search_word,
            "next_test_word": self.next_test_word,
            "check_test": self.check_test,
            "refresh_stats": self.refresh_stats
        })

        self.refresh_words()
        self.refresh_stats()

    def add_word(self):
        try:
            self.model.add_word(self.view.english_var.get(), self.view.russian_var.get())
            self.refresh_words()
            self.refresh_stats()
            self.view.set_status("Слово успешно добавлено")
            self.view.english_var.set("")
            self.view.russian_var.set("")
        except ValueError as e:
            messagebox.showwarning("Ошибка добавления", str(e))

    def edit_word(self):
        try:
            self.model.edit_word(self.view.english_var.get(), self.view.russian_var.get())
            self.refresh_words()
            self.refresh_stats()
            self.view.set_status("Слово успешно отредактировано")
        except ValueError as e:
            messagebox.showwarning("Ошибка редактирования", str(e))

    def search_word(self):
        english = self.view.search_var.get()
        result = self.model.search_word(english)
        if result:
            self.view.search_result_var.set(f"{english.strip().lower()} → {result}")
            self.view.set_status("Слово найдено")
        else:
            self.view.search_result_var.set("Слово не найдено")
            self.view.set_status("Поиск завершён")

    def refresh_words(self):
        self.view.update_words_list(self.model.get_all_words())

    def next_test_word(self):
        pair = self.model.get_random_word()
        if pair is None:
            messagebox.showinfo("Тест", "Словарь пуст. Сначала добавьте слова.")
            return

        english, _ = pair
        self.view.current_test_word = english
        self.view.test_word_var.set(f"Переведите слово: {english}")
        self.view.test_answer_var.set("")
        self.view.test_result_var.set("")
        self.view.set_status("Новое слово для теста показано")

    def check_test(self):
        if not self.view.current_test_word:
            messagebox.showinfo("Тест", "Сначала нажмите «Следующее слово».")
            return

        answer = self.view.test_answer_var.get()
        is_correct, correct = self.model.check_translation(self.view.current_test_word, answer)

        if is_correct:
            self.view.test_result_var.set("Верно!")
            self.view.set_status("Ответ правильный")
        else:
            self.view.test_result_var.set(f"Неверно. Правильный перевод: {correct}")
            self.view.set_status("Ответ неправильный")

        self.refresh_stats()

    def refresh_stats(self):
        self.view.show_stats(self.model.get_stats_text())


# =============================================================================
# ENTRY POINT
# =============================================================================
def main():
    root = tk.Tk()
    model = DictionaryModel()
    view = DictionaryView(root)
    DictionaryController(model, view)
    root.mainloop()


if __name__ == "__main__":
    main()