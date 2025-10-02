from shiny import App, render, ui
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Sample data
def create_sample_data():
    np.random.seed(123)
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    data = pd.DataFrame({
        'date': dates,
        'sales': np.random.normal(1000, 200, 100).cumsum(),
        'users': np.random.poisson(500, 100),
        'conversion': np.random.uniform(0.01, 0.05, 100)
    })
    return data

df = create_sample_data()

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h2("Dashboard Controls"),
        ui.input_date_range("date_range", "Select Date Range:", 
                           start=df['date'].min(), 
                           end=df['date'].max()),
        ui.input_select("metric", "Select Metric:", 
                       choices={"sales": "Sales", 
                               "users": "Users", 
                               "conversion": "Conversion Rate"}),
        ui.input_slider("window", "Moving Average Window:", 
                       min=1, max=30, value=7),
        width=300
    ),
    ui.layout_columns(
        ui.value_box(
            title="Total Sales",
            value=ui.output_text("total_sales"),
            theme="primary"
        ),
        ui.value_box(
            title="Average Users",
            value=ui.output_text("avg_users"),
            theme="success"
        ),
        ui.value_box(
            title="Conversion Rate",
            value=ui.output_text("conv_rate"),
            theme="warning"
        ),
        col_widths=[4, 4, 4]
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Time Series Trend"),
            ui.output_plot("trend_plot")
        ),
        ui.card(
            ui.card_header("Data Summary"),
            ui.output_table("summary_table")
        ),
        col_widths=[8, 4]
    ),
    ui.card(
        ui.card_header("Raw Data"),
        ui.output_data_frame("raw_data")
    ),
    title="Business Analytics Dashboard",
    fillable=True
)

def server(input, output, session):
    
    # Filter data based on date range
    @reactive.Calc
    def filtered_data():
        date_filter = (df['date'] >= input.date_range()[0]) & (df['date'] <= input.date_range()[1])
        return df[date_filter]
    
    @output
    @render.text
    def total_sales():
        data = filtered_data()
        return f"${data['sales'].iloc[-1]:,.0f}"
    
    @output
    @render.text
    def avg_users():
        data = filtered_data()
        return f"{data['users'].mean():.0f}"
    
    @output
    @render.text
    def conv_rate():
        data = filtered_data()
        return f"{data['conversion'].mean():.2%}"
    
    @output
    @render.plot
    def trend_plot():
        data = filtered_data()
        metric = input.metric()
        window = input.window()
        
        # Calculate moving average
        data['ma'] = data[metric].rolling(window=window).mean()
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(data['date'], data[metric], alpha=0.3, label='Daily')
        ax.plot(data['date'], data['ma'], linewidth=2, label=f'{window}-day MA')
        ax.set_title(f'{metric.title()} Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig
    
    @output
    @render.table
    def summary_table():
        data = filtered_data()
        summary = data[['sales', 'users', 'conversion']].describe().round(2)
        return summary
    
    @output
    @render.data_frame
    def raw_data():
        data = filtered_data()
        return render.DataGrid(data, row_selection_mode='multiple')

app = App(app_ui, server)
