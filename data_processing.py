import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.figure_factory as ff
from io import BytesIO
import base64

def load_and_process_data():
    # Cargar datos
    sales_df = pd.read_csv('data/sales_data_sample.csv', encoding='unicode_escape')
    
    # Procesamiento inicial
    sales_df['ORDERDATE'] = pd.to_datetime(sales_df['ORDERDATE'])
    df_drop = ['ADDRESSLINE1', 'ADDRESSLINE2', 'POSTALCODE', 'CITY', 
                'TERRITORY', 'PHONE', 'STATE', 'CONTACTFIRSTNAME', 
                'CONTACTLASTNAME', 'CUSTOMERNAME', 'ORDERNUMBER', 'STATUS']
    sales_df = sales_df.drop(df_drop, axis=1)
    
    # Guardar datos categóricos originales para visualización
    original_data = {
        'COUNTRY': sales_df['COUNTRY'].copy(),
        'PRODUCTLINE': sales_df['PRODUCTLINE'].copy(),
        'DEALSIZE': sales_df['DEALSIZE'].copy()
    }
    
    # Convertir variables categóricas
    sales_df = pd.get_dummies(sales_df, columns=['COUNTRY', 'PRODUCTLINE', 'DEALSIZE'])
    sales_df['PRODUCTCODE'] = pd.Categorical(sales_df['PRODUCTCODE']).codes
    
    # Agrupar por fecha
    sales_df_group = sales_df.groupby('ORDERDATE').sum()
    
    # Escalar datos para clustering
    scaler = StandardScaler()
    sales_df_scaled = scaler.fit_transform(sales_df.drop('ORDERDATE', axis=1))
    
    # Clustering con K=5
    kmeans = KMeans(n_clusters=5, random_state=42)
    labels = kmeans.fit_predict(sales_df_scaled)
    sale_df_cluster = pd.concat([sales_df, pd.DataFrame({'cluster': labels})], axis=1)
    
    # PCA 3D
    pca_3d = PCA(n_components=3)
    principal_comp_3d = pca_3d.fit_transform(sales_df_scaled)
    pca_df_3d = pd.DataFrame(data=principal_comp_3d, columns=['pca1', 'pca2', 'pca3'])
    pca_df_3d = pd.concat([pca_df_3d, pd.DataFrame({'cluster': labels})], axis=1)
    
    # PCA 2D
    pca_2d = PCA(n_components=2)
    principal_comp_2d = pca_2d.fit_transform(sales_df_scaled)
    pca_df_2d = pd.DataFrame(data=principal_comp_2d, columns=['pca1', 'pca2'])
    pca_df_2d['cluster'] = labels
    
    # Método del codo
    wcss = []
    for i in range(1, 15):
        kmeans = KMeans(n_clusters=i, random_state=42)
        kmeans.fit(sales_df_scaled)
        wcss.append(kmeans.inertia_)
    
    return sales_df, sales_df_group, sale_df_cluster, pca_df_3d, pca_df_2d, original_data, wcss

def generate_visualizations(sales_df, sales_df_group, sale_df_cluster, pca_df_3d, pca_df_2d, original_data, wcss):
    # Convertir gráficos matplotlib a HTML
    def fig_to_html(fig):
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        return f'<img src="data:image/png;base64,{img_str}" class="img-fluid">'
    
    visualizations = {}
    
    # 1. Gráficos de barras categóricos
    for col in ['COUNTRY', 'PRODUCTLINE', 'DEALSIZE']:
        fig = px.bar(x=original_data[col].value_counts().index, 
                    y=original_data[col].value_counts().values,
                    color=original_data[col].value_counts().index,
                    title=f'Distribución de {col}',
                    height=600)
        visualizations[f'bar_{col.lower()}'] = fig.to_html(full_html=False)
    
    # 2. Serie temporal de ventas
    fig = px.line(x=sales_df_group.index, y=sales_df_group['SALES'],
                    title='Evolución de Ventas', labels={'x': 'Fecha', 'y': 'Ventas'})
    visualizations['sales_trend'] = fig.to_html(full_html=False)
    
    # 3. Matriz de correlación
    plt.figure(figsize=(20, 20))
    corr_matrix = sales_df.iloc[:, :9].corr(numeric_only=True)  # Añadido numeric_only
    sns.heatmap(corr_matrix, annot=True, cbar=False)
    visualizations['correlation_matrix'] = fig_to_html(plt.gcf())
    plt.close()
    
    # 4. Distplots - Solo para columnas numéricas
    distplots = {}
    numeric_cols = sales_df.select_dtypes(include=['number']).columns.tolist()
    
    for col in numeric_cols[:8]:  # Limitar a las primeras 8 columnas numéricas
        try:
            # Convertir a float solo si es necesario
            data = sales_df[col].astype(float) if not pd.api.types.is_float_dtype(sales_df[col]) else sales_df[col]
            
            fig = ff.create_distplot([data], [col], show_hist=True, show_rug=True)
            fig.update_layout(title_text=col)
            distplots[col] = fig.to_html(full_html=False)
        except Exception as e:
            print(f"No se pudo crear distplot para {col}: {str(e)}")
            continue
    
    visualizations['distplots'] = distplots
    
    # 5. Scatter matrix - Solo columnas numéricas
    numeric_cols_for_scatter = [col for col in sales_df.columns[:8] if pd.api.types.is_numeric_dtype(sales_df[col])]
    fig = px.scatter_matrix(sales_df, dimensions=numeric_cols_for_scatter, 
                            color='MONTH_ID', title='Relación entre Variables')
    fig.update_layout(width=1100, height=1100)
    visualizations['scatter_matrix'] = fig.to_html(full_html=False)
    
    # Resto del código permanece igual...
    # 6. Método del codo
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, 15), wcss, 'bx-')
    plt.title('Método del Codo para Número Óptimo de Clusters')
    plt.xlabel('Número de clusters')
    plt.ylabel('WCSS')
    plt.grid(True)
    visualizations['elbow_method'] = fig_to_html(plt.gcf())
    plt.close()
    
    # 7. Histogramas por cluster - Solo columnas numéricas
    cluster_hists = {}
    numeric_cols = sales_df.select_dtypes(include=['number']).columns.tolist()
    
    for col in numeric_cols[:8]:
        plt.figure(figsize=(30, 6))
        for j in range(5):
            plt.subplot(1, 5, j+1)
            cluster = sale_df_cluster[sale_df_cluster['cluster'] == j]
            cluster[col].hist()
            plt.title(f'{col}\nCluster {j}')
        cluster_hists[col] = fig_to_html(plt.gcf())
        plt.close()
    visualizations['cluster_hists'] = cluster_hists
    
    # 8. Visualización 3D PCA
    fig = px.scatter_3d(pca_df_3d, x='pca1', y='pca2', z='pca3',
                        color='cluster', symbol='cluster',
                        title='Clusters en Espacio 3D (PCA)',
                        width=800, height=600)
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=30)),
    visualizations['pca_3d'] = fig.to_html(full_html=False)
    
    # 9. Visualización 2D PCA
    fig = px.scatter(pca_df_2d, x='pca1', y='pca2', color='cluster',
                    title='Clusters en Espacio 2D (PCA)',
                    width=800, height=600)
    visualizations['pca_2d'] = fig.to_html(full_html=False)
    
    # 10. Interpretación de clusters
    cluster_interpretation = """
    <div class="cluster-interpretation">
        <h4>Interpretación de Clusters:</h4>
        <div class="row">
            <div class="col-md-4">
                <div class="card cluster-card" style="border-left: 5px solid #636EFA;">
                    <div class="card-body">
                        <h5>Cluster 0</h5>
                        <p>Clientes que compran grandes cantidades (~47) de productos caros (~99). Ventas altas (~8296). Activos todo el año. MSRP alto (~158).</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card cluster-card" style="border-left: 5px solid #EF553B;">
                    <div class="card-body">
                        <h5>Cluster 1</h5>
                        <p>Clientes con compras moderadas (~35) de productos caros (~96). Ventas promedio (~4435). MSRP alto (~133).</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card cluster-card" style="border-left: 5px solid #00CC96;">
                    <div class="card-body">
                        <h5>Cluster 2</h5>
                        <p>Clientes que compran pequeñas cantidades (~30) de productos baratos (~68). Ventas bajas (~2041). MSRP bajo (~75).</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    visualizations['cluster_interpretation'] = cluster_interpretation
    
    return visualizations