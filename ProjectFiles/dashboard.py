from cmath import nan
from tempfile import SpooledTemporaryFile
import dash
from dash import Dash, html, dcc, Output, Input, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import utilities as ut #um Funktionen aus utilities zu bekommen 
import numpy as np
import os
import re
import matplotlib.pyplot as plt #importieren für Einfügen der Marker 

app = Dash(__name__)

#importieren der Daten
list_of_subjects = []
subj_numbers = []
number_of_subjects = 0

folder_current = os.path.dirname(__file__) 
print(folder_current)
folder_input_data = os.path.join(folder_current, "input_data")
for file in os.listdir(folder_input_data):
    
    if file.endswith(".csv"):
        number_of_subjects += 1
        file_name = os.path.join(folder_input_data, file)
        print(file_name)
        list_of_subjects.append(ut.Subject(file_name))


df = list_of_subjects[0].subject_data


for i in range(number_of_subjects):
    subj_numbers.append(list_of_subjects[i].subject_id)
print(subj_numbers)

data_names = ["SpO2 (%)", "Blood Flow (ml/s)","Temp (C)"]
#Benennung der Auswahl-Button 
algorithm_names = ['min','max']
blood_flow_functions = ['CMA','SMA','Show Limits']

#Funktion der Plots 
fig0= go.Figure()
fig1= go.Figure()
fig2= go.Figure()
fig3= go.Figure()

#Beschriftung der Plots 
fig0 = px.line(df, x="Time (s)", y = "SpO2 (%)")
fig1 = px.line(df, x="Time (s)", y = "Blood Flow (ml/s)")
fig2 = px.line(df, x="Time (s)", y = "Temp (C)")
fig3 = px.line(df, x="Time (s)", y = "Blood Flow (ml/s)")

app.layout = html.Div(children=[
    html.H1(children='Cardiopulmonary Bypass Dashboard', style={"text-align": "center"}),
#Überschrift center
    html.Div(children='''
        Standort: Universitätsklinikum Innsbruck Chirugie Haus C
    '''),
#Geräteinfo, hardcoded

    dcc.Checklist(
    id= 'checklist-algo',
    options=algorithm_names,
    inline=False
    ),

    html.Div([
        dcc.Dropdown(options = subj_numbers, placeholder='Select a subject', value='1', id='subject-dropdown'),
        html.Div(id='dd-output-container')
    ],
        style={"width": "15%"},
    ),
    html.Div([
        dcc.Graph(
            id='dash-graph0',
            figure=fig0
        ),
    ], style={"width": "50%", "float": "left"}),

    html.Div([
        dcc.Graph(
            id='dash-graph1',
            figure=fig1,
        )
    ], style={"width": "50%", "margin-left": "50%"}),

    html.Div([
        dcc.Graph(
            id='dash-graph2',
            figure=fig2
        )
    ], style={"width": "100%"}),

#Übersichtlicher

    dcc.Checklist(
        id= 'checklist-bloodflow',
        options=blood_flow_functions,
        inline=False
    ),
    dcc.Graph(
        id='dash-graph3',
        figure=fig3
    ),
    dcc.Textarea(
        id='text-area1',
        # readOnly=True,
        disabled=True,  # disabled --> User cannot interact with textarea
        style={"width": "100%", 'height': "auto"}
    ),

#Alert Message in Textfeld

])
### Callback Functions ###
## Graph Update Callback
@app.callback(
    # In- or Output('which html element','which element property')
    Output('dash-graph0', 'figure'),
    Output('dash-graph1', 'figure'),
    Output('dash-graph2', 'figure'),
    Input('subject-dropdown', 'value'),
    Input('checklist-algo','value')
)
def update_figure(value, algorithm_checkmarks):

    print("Current Subject: ", value)
    print("current checked checkmarks are: ", algorithm_checkmarks)

    ts = list_of_subjects[int(value)-1].subject_data #ts ist time series in panda

    #SpO2
    fig0 = px.line(ts, x="Time (s)", y = data_names[0])
    # Blood Flow
    fig1 = px.line(ts, x="Time (s)", y = data_names[1])
    # Blood Temperature
    fig2 = px.line(ts, x="Time (s)", y = data_names[2])
    
    ### Aufgabe 2: Min / Max ###

    #https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.agg.html
    #https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html

    #es werden 2 Fkt. für max und min erstellt. Aus der time series ts werden mithilfe von . agg direkt die Werte berechnet
    max_values = ts.agg(['max', 'idxmax']) #Funktionen um gleich Maxima und Minima zu berechnen
    min_values = ts.agg(['min', 'idxmin']) #idxmax siehe Tafelbild 16.05.2022 (Darstellung welche Werte für Scatter notwendig)
    
    ##DataFrame.agg(func=None, axis=0, *args (positional), **kwargs(keyword))
    
    #print(max_values, 'idxmax')
    #print(min_values, 'idxmin')

# https://www.geeksforgeeks.org/matplotlib-pyplot-scatter-in-python/

    ####

    if algorithm_checkmarks is not None: #Fkt. dient zur Fehlerminimierung (verhindert Durchlauf obwohl auswahl 0 ist ) 

        if 'min' in (algorithm_checkmarks):   #Prüfung ob checkmark 'min' ausgewählt wurde
            fig0.add_trace(go.Scatter(x= [min_values.loc['idxmin', data_names[0]]],y= [min_values.loc['min', data_names[0]]], mode = 'markers', name = 'minimum', marker_color='red'))
            #add_trace => fügt trace hinzu, Scatter => fügt Punkte hinzu 
            #data_names zeigt um welche figure es sich handelt 
            #mithilfe von .loc können bestimmte Werte herausgefiltert werden
            #mode/name/marker_color sind zum beschreiben des Punktes/Legende 
            fig1.add_trace(go.Scatter(x= [min_values.loc['idxmin', data_names[1]]],y= [min_values.loc['min', data_names[1]]], mode = 'markers', name = 'minimum', marker_color='red'))
            fig2.add_trace(go.Scatter(x= [min_values.loc['idxmin', data_names[2]]],y= [min_values.loc['min', data_names[2]]], mode = 'markers', name = 'minimum', marker_color='red'))


        if 'max' in (algorithm_checkmarks) :   #Prüfung ob checkmark 'max' ausgewählt wurde 
            fig0.add_trace(go.Scatter(x= [max_values.loc['idxmax', data_names[0]]],y= [max_values.loc['max', data_names[0]]], mode = 'markers', name = 'maximum', marker_color='green'))
            fig1.add_trace(go.Scatter(x= [max_values.loc['idxmax', data_names[1]]],y= [max_values.loc['max', data_names[1]]], mode = 'markers', name = 'maximum', marker_color='green'))
            fig2.add_trace(go.Scatter(x= [max_values.loc['idxmax', data_names[2]]],y= [max_values.loc['max', data_names[2]]], mode = 'markers', name = 'maximum', marker_color='green'))

    return fig0, fig1, fig2 


## Blodflow Simple Moving Average Update
@app.callback(
    # In- or Output('which html element','which element property')
    Output('dash-graph3', 'figure'),
    Output('text-area1', 'value'),  # Output textarea for alert box
    Input('subject-dropdown', 'value'),
    Input('checklist-bloodflow','value'),
)
def bloodflow_figure(value, bloodflow_checkmarks):

    ## Calculate Moving Average: Aufgabe 2
    print(bloodflow_checkmarks)
    bf = list_of_subjects[int(value)-1].subject_data
    fig3 = px.line(bf, x="Time (s)", y="Blood Flow (ml/s)")

    if bloodflow_checkmarks is not None:
#Probleme bei importieren => keine Rückgabe der Werte aus utilities-Datei => Kein CMA/SMA Graph
#print(bf) zur Nachverfolgung der Ausgabe
#Programm hat allerdings auf Laptop von Studienkollegen funktioniert => hin und her pushen (deshalb wurde weitere Person ins repository eingeladen)
# => anschließend hat Programm ohne Änderun wieder funktioniert

        if bloodflow_checkmarks == ["CMA"]:
            bf["Blood Flow (ml/s) - CMA"] = ut.calculate_CMA(bf["Blood Flow (ml/s)"], 2) #n gibt an ab welchem Intervall berechnet wird (kann durch probieren ermittelt werden)
            fig3 = px.line(bf, x="Time (s)", y="Blood Flow (ml/s) - CMA") #Beschriftung der Achsen


        if bloodflow_checkmarks == ["SMA"]:
            bf["Blood Flow (ml/s) - SMA"] = ut.calculate_SMA(bf["Blood Flow (ml/s)"],5) #durch ut.calculate wird Funktion aus utilities aufgerufen
            fig3 = px.line(bf, x="Time (s)", y="Blood Flow (ml/s) - SMA") 


#Aufgabe 3.1

    avg = bf.mean() #Funktion zur Berechnung des Mittlewerts (aus Listen)

    fig3.add_trace(go.Scatter(x = [0, 480], y= [avg.loc['Blood Flow (ml/s)'], avg.loc['Blood Flow (ml/s)']], mode = 'lines', name = 'average'))

#Aufgabe 3.2
    
#if 'Show Limits' in bloodflow_checkmarks:

        #Funktion für 15% Intervallsgrenzen
    y_unten = (avg.loc['Blood Flow (ml/s)'])*0.85 #Faktor zur Berechnung der 15%
        #avg.loc weil die Intervallsgrenzen um den Mittelwert gesucht sind 
    fig3.add_trace(go.Scatter(x = [0, 480], y= [y_unten, y_unten], mode = 'lines', marker_color = 'red', name = 'untere Intervallsgrenze'))

    y_oben = (avg.loc['Blood Flow (ml/s)'])*1.15 
    fig3.add_trace(go.Scatter(x = [0, 480], y= [y_oben, y_oben], mode = 'lines', marker_color = 'green', name = 'obere Intervallsgrenze'))


    # Aufgabe 3.3
    alert_count = []
    alert_sum = 0 #holds invalid values, int

    alert_msg = ""
    sma_key = "Blood Flow (ml/s) - SMA"
    if sma_key in bf:
        bf_SMA = bf[sma_key]

        for i in bf_SMA:
            if i > y_oben or i < y_unten: #SMA value > or <
                alert_count.append(bf.index[bf_SMA==i].tolist()) #adds invalid values to list
                alert_sum += 1 #+1 for each invalid


        #Content message + sec
        alert_msg = 'ALert! Ecceded limets for ' + str(alert_sum) + ' seconds!'

    return fig3, alert_msg


if __name__ == '__main__':
    app.run_server(debug=True)

# Aufgabe 3.4
# SMA wurde so gewählt (n=4), dass erst ab größer 3 Alarm ausgelöst wird. Erst ab da ist ein "Trend" absehbar. -Fehlalarm