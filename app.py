import pandas as pd
import plotly.graph_objs as go
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from cleaning import *
from results import *
from dash.exceptions import PreventUpdate
import numpy as np
from sklearn.cluster import KMeans
# Création de l'application Dash
app = Dash(__name__)
server = app.server



kmeans = KMeans(n_clusters=6, random_state=42)
kmeans.fit(X)

# Mise en page du tableau de bord
app.layout = html.Div([
    html.H1("Tableau de bord avancé des données"),
    dcc.Tabs(id='tabs', value='general-tab', children=[
        dcc.Tab(label='Informations générales', value='general-tab'),
        dcc.Tab(label='Statistiques descriptives', value='descriptive-stats-tab'),
        dcc.Tab(label='Graphiques', value='graphs-tab'),
        dcc.Tab(label="Clustering",value="results")
    ]),
    html.Div(id='tabs-content')
])

# Callback pour mettre à jour le contenu des onglets
@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value')]
)

def update_tab_content(tab):
    if tab == 'general-tab':
        return html.Div([
            html.H2("Informations générales sur les données"),
            html.Table([
                html.Thead([
                    html.Tr([html.Th(col) for col in df.columns])
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td(df.iloc[i][col]) for col in df.columns
                    ]) for i in range(min(len(df), 10))  # Affiche uniquement les 10 premières lignes pour éviter un rendu trop long
                ])
            ])
        ])
    elif tab == "results" :
        return html.Div([
    dcc.Input(id='input-recency', type='number', placeholder='Enter Recency value'),
    dcc.Input(id='input-frequency', type='number', placeholder='Enter Frequency value'),
    dcc.Input(id='input-monetary', type='number', placeholder='Enter Monetary value'),
    html.Button('Submit', id='submit-val', n_clicks=0),
    html.Div(id='output-container-button')
     ])
    elif tab == 'descriptive-stats-tab':
        return html.Div([
            html.H2("Statistiques descriptives"),
            html.Pre(children=df.describe().to_string())
        ])
    elif tab == 'graphs-tab':
        # Exemple de graphique : Calculez le montant total des frais de livraison pour chaque client
        fig1 = go.Figure(data=[go.Bar(x=top_20.index,y=top_20.values)])
        fig1.update_layout(title='Top 20 des clients avec les frais de livraison les plus élevés')
        # Exemple de graphique : Diagramme à barres du nombre de commandes par catégorie de produits
        fig2 = go.Figure(data=[go.Bar(x=df['product_category_name'], y=df.groupby('product_category_name')['order_id'].count())])
        fig2.update_layout(title='Nombre de commandes par catégorie de produits')

        # Exemple de graphique : Diagramme circulaire de la répartition des modes de paiement
        fig3 = go.Figure(data=[go.Pie(labels=df['payment_type'], values=df.groupby('payment_type')['order_id'].count())])
        fig3.update_layout(title='Répartition des modes de paiement')

        # Exemple de graphique : Nuage de points pour visualiser la relation entre le prix et le poids des produits
        fig4 = go.Figure(data=[go.Scatter(x=df['product_weight_g'], y=df['price'], mode='markers')])
        fig4.update_layout(title='Relation entre le prix et le poids des produits', xaxis_title='Poids du produit (g)', yaxis_title='Prix')

        # Exemple de graphique : Diagramme à secteurs multiples pour la composition du chiffre d'affaires total par catégorie de produits et par mois
        df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
        df['month'] = df['order_purchase_timestamp'].dt.month
        fig5 = go.Figure()
        for category in df['product_category_name'].unique():
            df_category = df[df['product_category_name'] == category]
            fig5.add_trace(go.Bar(x=df_category['month'], y=df_category['price'], name=category))
        fig5.update_layout(barmode='stack', title='Composition du chiffre d\'affaires par catégorie de produits et par mois', xaxis_title='Mois', yaxis_title='Chiffre d\'affaires')
        return html.Div([
            dcc.Graph(figure=fig1),
            dcc.Graph(figure=fig2),
            dcc.Graph(figure=fig3),
            dcc.Graph(figure=fig4),
            dcc.Graph(figure=fig5)
    ])


@app.callback(
    Output('output-container-button', 'children'),
    [Input('submit-val', 'n_clicks')],
    [Input('input-recency', 'value'),
     Input('input-frequency', 'value'),
     Input('input-monetary', 'value')]
)


def update_output(n_clicks, input_recency, input_frequency, input_monetary):
    if n_clicks == 0:
        raise PreventUpdate

    if input_recency is None or input_frequency is None or input_monetary is None:
        return "Please enter all Recency, Frequency, and Monetary values"

    # Predict cluster for the input values
    cluster = kmeans.predict([[input_recency, input_frequency, input_monetary]])[0]
    return f"The data point (Recency: {input_recency}, Frequency: {input_frequency}, Monetary: {input_monetary}) belongs to cluster {cluster}"


# Lancement de l'application Dash
if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0', port=8051)
