from shiny import App, render, ui, reactive
import numpy as np
import matplotlib.pyplot as plt
import tempfile
import os
import time

# MSE
def calculate_mse(x, y):
    return np.mean((x - y) ** 2)

# PLOTS
def generate_plot(x, y1, y2):
    fig, ax = plt.subplots()
    ax.plot(x, y1, label='Функция 1')
    ax.plot(x, y2, label='Функция 2', linestyle='--')
    ax.legend()
    ax.set_xlabel('x')
    ax.set_ylabel('y')

    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(tmpfile.name, format='png')
    tmpfile.close()
    
    plt.close(fig)
    
    return tmpfile.name

# APP
app_ui = ui.page_fluid(
    ui.h2("Расчёт MSE"),
    
    ui.input_slider("n_points", "Количество точек", min=10, max=100, value=50),
    ui.input_slider("amplitude_1", "Амплитуда функции 1", min=0.5, max=5.0, value=1.0),
    ui.input_slider("amplitude_2", "Амплитуда функции 2", min=0.5, max=5.0, value=1.5),
    
    ui.input_action_button("calculate", "Рассчитать"),
    
    ui.output_text("progress_message"),
    
    ui.output_text_verbatim("result"),
    ui.output_image("plot")
)

# SERVER
def server(input, output, session):
    @reactive.Calc
    def data():
        n = input.n_points()
        x = np.linspace(0, 2 * np.pi, n)
        y1 = input.amplitude_1() * np.sin(x)
        y2 = input.amplitude_2() * np.sin(x)
        return x, y1, y2
    
    @output
    @render.text
    def progress_message():
        if input.calculate() > 0:
            return "Выполняется расчет..."
        return ""
    
    @reactive.Effect
    def calculate_with_progress():
        if input.calculate() > 0:
            with ui.Progress(min=1, max=100) as p:
                for i in range(1, 101):
                    p.set(i) 
                    time.sleep(0.02)  

    @output
    @render.text
    def result():
        if input.calculate() > 0:
            x, y1, y2 = data()
            mse_value = calculate_mse(y1, y2)
            return f"Среднеквадратичная ошибка (MSE): {mse_value:.4f}"

    @output
    @render.image
    def plot():
        if input.calculate() > 0:
            x, y1, y2 = data()
            plot_path = generate_plot(x, y1, y2)
            return {"src": plot_path, "alt": "График сравнения"}

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
