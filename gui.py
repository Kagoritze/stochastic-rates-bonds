import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import numpy as np

class BinomialModelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Биномиальная модель процентных ставок")
        self.root.geometry("1200x900")
        
        self.instruction_button = ttk.Button(root, text="Инструкция", command=self.open_instruction)
        self.instruction_button.grid(row=0, column=1, sticky='ne', padx=10, pady=10)

        # Выбор режима работы
        mode_frame = ttk.Frame(root)
        mode_frame.grid(row=0, column=0, sticky='w')
        
        self.mode_var = tk.StringVar(value="Стандартный")  # По умолчанию стандартный режим
        ttk.Label(mode_frame, text="Режим работы:").grid(row=0, column=0, sticky='w')
        ttk.Radiobutton(mode_frame, text="Продвинутый", variable=self.mode_var, value="Продвинутый", command=self.toggle_mode).grid(row=0, column=1, sticky='w')
        ttk.Radiobutton(mode_frame, text="Стандартный", variable=self.mode_var, value="Стандартный", command=self.toggle_mode).grid(row=0, column=2, sticky='w')
        
        # Создание пользовательского интерфейса
        input_frame = ttk.Frame(root)
        input_frame.grid(row=1, column=0, sticky='w')
        
        ttk.Label(input_frame, text="Число периодов (n):").grid(row=0, column=0, sticky='w')
        self.n_var = tk.IntVar(value=10)
        self.n_entry = ttk.Entry(input_frame, textvariable=self.n_var, validate="key", validatecommand=(root.register(self.validate_numeric_input), "%P"))
        self.n_entry.grid(row=0, column=1, sticky='w')
        
        ttk.Label(input_frame, text="Начальная ставка (r0, %):").grid(row=1, column=0, sticky='w')
        self.r0_var = tk.DoubleVar(value=5)
        self.r0_entry = ttk.Entry(input_frame, textvariable=self.r0_var, validate="key", validatecommand=(root.register(self.validate_numeric_input), "%P"))
        self.r0_entry.grid(row=1, column=1, sticky='w')
        
        ttk.Label(input_frame, text="Волатильность (σ):").grid(row=2, column=0, sticky='w')
        self.sigma_var = tk.DoubleVar(value=0.1)
        self.sigma_entry = ttk.Entry(input_frame, textvariable=self.sigma_var, validate="key", validatecommand=(root.register(self.validate_numeric_input), "%P"))
        self.sigma_entry.grid(row=2, column=1, sticky='w')
        
        ttk.Label(input_frame, text="Общее время (T, лет):").grid(row=3, column=0, sticky='w')
        self.T_var = tk.IntVar(value=10)
        self.T_entry = ttk.Entry(input_frame, textvariable=self.T_var, validate="key", validatecommand=(root.register(self.validate_numeric_input), "%P"))
        self.T_entry.grid(row=3, column=1, sticky='w')
        
        ttk.Label(input_frame, text="Период экспирации форварда (t, лет):").grid(row=4, column=0, sticky='w')
        self.t_var = tk.IntVar(value=3)
        self.t_entry = ttk.Entry(input_frame, textvariable=self.t_var, validate="key", validatecommand=(root.register(self.validate_numeric_input), "%P"))
        self.t_entry.grid(row=4, column=1, sticky='w')

        ttk.Label(input_frame, text="Период экспирации фьючерса (k, лет):").grid(row=5, column=0, sticky='w')
        self.k_var = tk.IntVar(value=6)
        self.k_entry = ttk.Entry(input_frame, textvariable=self.k_var, validate="key", validatecommand=(root.register(self.validate_numeric_input), "%P"))
        self.k_entry.grid(row=5, column=1, sticky='w')

        ttk.Label(input_frame, text="Страйк цена (E, %):").grid(row=6, column=0, sticky='w')
        self.strike_var = tk.DoubleVar(value=70)
        self.strike_entry = ttk.Entry(input_frame, textvariable=self.strike_var, validate="key", validatecommand=(root.register(self.validate_numeric_input), "%P"))
        self.strike_entry.grid(row=6, column=1, sticky='w')

        ttk.Button(input_frame, text="Сгенерировать модель", command=self.generate_model).grid(row=7, column=0, columnspan=2, pady=10)
        
        self.matrix_frames = []
        self.create_text_frame(8, "Матрица ставок", "rates")
        self.create_text_frame(9, "Матрица ZCB_n", "zcb")
        self.create_text_frame(10, "Матрица ZCB_t", "zcb_t")
        self.create_text_frame(11, "Матрица стоимости фьючерса", "futures")
        self.create_text_frame(12, "Матрица стоимости опциона на фьючерс (американский тип)", "futures_buyer")
        
        output_frame = ttk.Frame(input_frame)
        output_frame.grid(row=0, column=3, rowspan=9, padx=20, sticky='w')

        ttk.Label(output_frame, text="Форвардная цена F (t):").grid(row=0, column=0, sticky='w')
        self.forward_price_var = tk.StringVar(value="—")
        ttk.Label(output_frame, textvariable=self.forward_price_var).grid(row=0, column=1, sticky='w')

        ttk.Label(output_frame, text="Начальная цена ZCB (t):").grid(row=2, column=0, sticky='w')
        self.zcb_T_price_var = tk.StringVar(value="—")
        ttk.Label(output_frame, textvariable=self.zcb_T_price_var).grid(row=2, column=1, sticky='w')

        ttk.Label(output_frame, text="Фьючерсная цена ZCB (k):").grid(row=3, column=0, sticky='w')
        self.futures_price_var = tk.StringVar(value="—")
        ttk.Label(output_frame, textvariable=self.futures_price_var).grid(row=3, column=1, sticky='w')

        ttk.Label(output_frame, text="Цена амер. опциона на фьючерс (E):  ").grid(row=4, column=0, sticky='w')
        self.futures_buyer_price_var = tk.StringVar(value="—")
        ttk.Label(output_frame, textvariable=self.futures_buyer_price_var).grid(row=4, column=1, sticky='w')
        
        ttk.Label(output_frame, text="Начальная стоимость ZCB (T):").grid(row=1, column=0, sticky='w')
        self.zcb_T_0_0_price_var = tk.StringVar(value="—")
        ttk.Label(output_frame, textvariable=self.zcb_T_0_0_price_var).grid(row=1, column=1, sticky='w')

        
        self.toggle_mode()

    def toggle_mode(self):
        mode = self.mode_var.get()

        if mode == "Стандартный":
            self.reset_standard_values()
            self.disable_advanced_settings()
        else:
            self.enable_all_settings()

        for frame in self.matrix_frames:
            frame.grid_remove() if mode == "Стандартный" else frame.grid()

    def reset_standard_values(self):
        self.n_var.set(10)
        self.r0_var.set(5)
        self.sigma_var.set(0.1)
        self.T_var.set(10)

    def disable_advanced_settings(self):
        # Делаем все параметры, кроме k, t и E, недоступными
        self.n_entry.config(state="readonly")
        self.r0_entry.config(state="readonly")
        self.sigma_entry.config(state="readonly")
        self.T_entry.config(state="readonly")
        
    def enable_all_settings(self):
        # Включаем все параметры
        self.n_entry.config(state="normal")
        self.r0_entry.config(state="normal")
        self.sigma_entry.config(state="normal")
        self.T_entry.config(state="normal")
        
    def create_text_frame(self, row, label_text, attr_name):
        frame = ttk.Frame(self.root)
        frame.grid(row=row, column=0, columnspan=2, sticky='nsew')
        
        ttk.Label(frame, text=label_text).grid(row=0, column=0, sticky='w')
        text_widget = tk.Text(frame, wrap="none", state="disabled")
        text_widget.grid(row=1, column=0, sticky='nsew')
        
        scrollbar_y = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        scrollbar_y.grid(row=1, column=1, sticky='ns')
        
        scrollbar_x = ttk.Scrollbar(frame, orient="horizontal", command=text_widget.xview)
        scrollbar_x.grid(row=2, column=0, sticky='ew')
        
        text_widget.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(row, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        setattr(self, f"result_{attr_name}_text", text_widget)
        self.matrix_frames.append(frame)

    def open_instruction(self):
        instructions_window = tk.Toplevel(self.root)
        instructions_window.title("Инструкция")
        instructions_window.geometry("630x350")

        instructions_window.configure(bg="#d9f4ff") 

        instruction_text = """Инструкция:
        1. Введите параметры модели: cтрайк, период экспирации форварда, период экспирации фьючерса и т.д.
        2. Нажмите на кнопку 'Сгенерировать модель', чтобы увидеть результаты.
        3. Окна с матрицами отображают рассчитанные значения.
        
        По умолчанию стандартный режим ввода и вывода результатов. Вы можете переключить в продвинутый режим для более тонкой настройки и просмотра матриц.
        Параметры T, k, n и t округляются в меньшую сторону автоматически.
        Ввод только положительных чисел и для разделения десятичных дробей используется точка. Другие символы не принимаются и не печатаются.
        Вопросы и предложения можно отправлять на электронную почту: eak120@tpu.ru
        """

        label = ttk.Label(instructions_window, text=instruction_text, wraplength=550, background="#d9f4ff")
        label.pack(padx=2, pady=2)

        close_button = ttk.Button(instructions_window, text="Закрыть", command=instructions_window.destroy)
        close_button.pack(pady=5)
        
    def validate_numeric_input(self, value):
        if value == "" or value.replace(".", "", 1).isdigit():
            return True
        return False

    def validate_input(self, value, param):
        try:
            value = float(value)
            if param == "n" and (value < 1 or value > 100):
                raise ValueError("Число периодов должно быть от 1 до 100.")
            elif param == "r0" and (value < 0 or value > 50):
                raise ValueError("Начальная ставка должна быть в пределах от 0% до 50%.")
            elif param == "sigma" and (value < 0 or value > 1):
                raise ValueError("Волатильность должна быть в пределах от 0 до 1.")
            elif param == "T" and (value < 1 or value > 100):
                raise ValueError("Общее время должно быть от 1 до 100 лет.")
            elif param == "t" and (value < 1 or value > self.n_var.get()):
                raise ValueError(f"Период экспирации форварда от 1 до {self.n_var.get()}.")
            elif param == "k" and (value < 1 or value > self.n_var.get()):
                raise ValueError(f"Период экспирации фьючерса от 1 до {self.n_var.get()}.")
            elif param == "strike" and (value < 50 or value > 100):
                raise ValueError("Страйк цена должна быть в пределах от 50% до 100%.")
            
            return True
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return False

    def isfloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def generate_model(self):
        # Проверка ввода
        if not (self.validate_input(self.n_var.get(), "n") and
                self.validate_input(self.r0_var.get(), "r0") and
                self.validate_input(self.sigma_var.get(), "sigma") and
                self.validate_input(self.T_var.get(), "T") and
                self.validate_input(self.t_var.get(), "t") and
                self.validate_input(self.k_var.get(), "k") and
                self.validate_input(self.strike_var.get(), "strike")):
            return
        
        n = self.n_var.get()
        r0 = self.r0_var.get() / 100
        sigma = self.sigma_var.get()
        T = self.T_var.get()
        t = self.t_var.get()
        k = self.k_var.get()
        strike = self.strike_var.get() / 100
        
        dt = T / n
        u = np.exp(sigma * np.sqrt(dt))
        d = 1 / u
        p = (np.exp(r0 * dt) - d) / (u - d)
        
        rates = np.zeros((n + 1, n + 1))
        for i in range(n + 1):
            for j in range(i + 1):
                rates[i - j, i] = (r0 * (u ** (i - j)) * (d ** j)) * 100
        
        self.display_matrix(self.result_rates_text, rates, n)
        self.generate_zcb_model(rates, n, p, "zcb")
        self.generate_zcb_model(rates, t, p, "zcb_t")
        self.generate_futures_model(rates, n, p, k)
        self.generate_futures_buyer_model(rates, n, p, k, strike)

        self.forward_price_var.set(f"{self.zcb[0, 0] / self.zcb_t[0, 0] * 100:.3f}%")
        self.zcb_T_price_var.set(f"{self.zcb_t[0, 0]:.3f}%")
        self.futures_price_var.set(f"{self.futures[0, 0]:.3f}%")
        self.futures_buyer_price_var.set(f"{self.futures_buyer[0, 0]:.3f}%")
        self.zcb_T_0_0_price_var.set(f"{self.zcb[0, 0]:.3f}%")

    def generate_zcb_model(self, rates, periods, p, attr_name):
        zcb = np.zeros((periods + 1, periods + 1))
        zcb[:, periods] = 100.0
        
        for j in range(periods - 1, -1, -1):
            for i in range(j + 1):
                r = rates[i, j] / 100
                f_u = zcb[i, j + 1]
                f_d = zcb[i + 1, j + 1]
                
                zcb[i, j] = ((1 - p) * f_u + p * f_d) / (1 + r)
        
        setattr(self, attr_name, zcb)
        self.display_matrix(getattr(self, f"result_{attr_name}_text"), zcb, periods)
    
    def generate_futures_model(self, rates, n, p, k):
        futures = np.zeros((k + 1, k + 1))
        
        for i in range(k + 1):
            futures[i, k] = self.zcb[i, k]
        
        for j in range(k - 1, -1, -1):
            for i in range(j + 1):
                f_d = futures[i, j + 1]
                f_u = futures[i + 1, j + 1]
            
                futures[i, j] = (1 - p) * f_d + p * f_u
        
        self.futures = futures
        self.display_matrix(self.result_futures_text, futures, k)

    def generate_futures_buyer_model(self, rates, n, p, k, strike):
        futures_buyer = np.zeros((k + 1, k + 1))
        
        for i in range(k + 1):
            futures_buyer[i, k] = max(self.futures[i, k] - strike * 100, 0)

        for j in range(k - 1, -1, -1):
            for i in range(j + 1):
                f_d = futures_buyer[i, j + 1]
                f_u = futures_buyer[i + 1, j + 1]
                
                discounted_value = (p * f_u + (1 - p) * f_d) / np.exp(self.r0_var.get() / 100 * self.T_var.get() / k)
                futures_buyer[i, j] = max(discounted_value, max(self.futures[i, j] - strike * 100, 0))
        
        self.futures_buyer = futures_buyer
        self.display_matrix(self.result_futures_buyer_text, futures_buyer, k)

    def display_matrix(self, text_widget, matrix, size):
        text_widget.configure(state="normal")
        text_widget.delete('1.0', tk.END)
        
        header = "\t".join([str(j) for j in range(size + 1)])
        text_widget.insert(tk.END, f"\t{header}\n")
        
        for i in range(size, -1, -1):
            row_text = "\t".join([f"{matrix[i, j]:.3f}%" if i <= j else " " for j in range(size + 1)])
            text_widget.insert(tk.END, f"{i}\t{row_text}\n")
        
        text_widget.configure(state="disabled")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = BinomialModelApp(root)
    root.mainloop()
