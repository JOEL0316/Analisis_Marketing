from flask import Flask, render_template
from data_processing import load_and_process_data, generate_visualizations

app = Flask(__name__)

# Cargar y procesar datos
sales_df, sales_df_group, sale_df_cluster, pca_df_3d, pca_df_2d, original_data, wcss = load_and_process_data()

# Generar visualizaciones
visualizations = generate_visualizations(sales_df, sales_df_group, sale_df_cluster, pca_df_3d, pca_df_2d, original_data, wcss)

@app.route('/')
def index():
    return render_template('index.html', viz=visualizations)

@app.route('/data-exploration')
def data_exploration():
    return render_template('data_exploration.html', viz=visualizations)

@app.route('/sales-analysis')
def sales_analysis():
    return render_template('sales_analysis.html', viz=visualizations)

@app.route('/clustering')
def clustering():
    return render_template('clustering.html', viz=visualizations)

@app.route('/dimensionality-reduction')
def dimensionality_reduction():
    return render_template('dimensionality.html', viz=visualizations)

if __name__ == '__main__':
    app.run(debug=True)