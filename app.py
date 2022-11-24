import requests
import json
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, dash_table
import dash_bootstrap_components as dbc
from dash import html
import waitress
from dash.exceptions import PreventUpdate

total_calories = 0
list_msg= 'Your Food List\n'
def get_food(food):
    requested_url = 'https://api.nutritionix.com/v1_1/search'
    API_KEY = '2d1da0c85fa38c516ac20a7094f22265'
    APP_ID = 'bf990bc9'
    headers = {'Content-Type': 'application/json',
               "x-app-id": APP_ID,
               "x-app-key": API_KEY
               }
    parameters = {"fields": ["item_name", "item_id", "nf_calories"], "query": food}
    response = requests.post(requested_url, headers=headers, json=parameters)
    response.raise_for_status()
    parsed = json.loads(response.text)
    response.close()
    x = len(parsed['hits'])

    item_name_with_calories = {}
    for i in range(0, x):
        key = parsed['hits'][i]['fields']['item_name']
        value = parsed['hits'][i]['fields']['nf_calories']
        item_name_with_calories.update({key: value})

    return item_name_with_calories

female_calorie_intake ={"13": 2000.0, "14-18": 2000.001, "19-20": 2000.002, "21-25": 2200.0, "26-30": 2000.003, "31-50": 2000.004,
     "51-60": 1800.0, "61 & up": 1800.001}
male_calorie_intake = {"13": 2200.0, "14-15": 2500.0, "16-18": 2800.0, "19-20": 2800.001, "21-25": 2800.002, "26-35": 2600.0,
     "36-40": 2600.001, "41-45": 2600.002, "46-55": 2400.0, "56-60": 2400.001, "61-65": 2400.002, "66-75": 2200.001,
     "76 & up": 2200.002}



app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = "Balanced Bites Application"

app.layout =html.Div([
                  html.H1(children = 'Welcome to Balanced Bites! 🍏',
                          style = {'textAlign':'center'
                          }),
                  html.H6(children = 'An application to check if your daily diet meets your calorie needs 💪',
                          style = {'textAlign':'center'
                          }),
                  html.Div('Gender', style={'font-weight': 'bold'}),
                  dcc.RadioItems(
                   id = 'checkbox',
                   options={
                        'male_calorie_intake': 'Male\t',
                        'female_calorie_intake': 'Female'
                   },
                    labelStyle={'display': 'block'},
                   value='male_calorie_intake',
                    ),
                    html.Br(),
                    dcc.Dropdown(
                        id='age',
                        placeholder="SELECT YOUR AGE RANGE",
                        multi=False,
                        disabled=True
                    ),
                    html.Br(),
                    dcc.Textarea(
                        id='weight_input',
                        value='Enter your weight in kg',
                        style={'width': '50%', 'height': 50},
                    ),
                    dcc.Textarea(
                        id='height_input',
                        value='Enter your height in cm',
                        style={'width': '50%', 'height': 50},
                    ),
                    html.Br(),
                    dbc.Button(
                        'Get BMI Result',
                        style = {
                        'background-color': '#F08E19',
                        'font-weight': 'bold',
                            "display": "block",
                            "margin-left": "580px",
                            "verticalAlign": "middle"
                        },
                        id='call1',
                        n_clicks=0
                    ),
                    html.Div(id='textarea1', style={'whiteSpace': 'pre-line','font-weight': 'bold'}),
                    html.Div(id='textarea2', style={'whiteSpace': 'pre-line'}),
                    html.Br(),
                    dcc.Textarea(
                    id='food_input',
                    value='Enter food name',
                    style={'width': '50%', 'height': 50},
                ),
                    dbc.Button(
                    'Submit Food Choice',
                    id='call2',
                    style={'font-weight': 'bold',
                            "display": "block",
                            "margin-left": "555px",
                            "verticalAlign": "middle",
                           'font-weight': 'bold'},
                    n_clicks=0
                ),
                    html.Div(id='textarea5', style={'whiteSpace': 'pre-line','font-weight': 'bold'}),
                    html.Br(),
                    dcc.Dropdown(
                        id='item_name',
                        placeholder="SELECT TYPE",
                        multi=True
                    ),
                    html.Div(id='textarea3', style={'whiteSpace': 'pre-line'}),
                    html.Div(id='textarea6', style={'whiteSpace': 'pre-line'}),
                    html.Div(id='textarea4', style={'whiteSpace': 'pre-line'}),
                    html.Br(),
                    dbc.Button(
                            'Calculate Total Calories',
                            style = {
                            'background-color': '#36BF50',
                            'font-weight': 'bold',
                                "display": "block",
                                "margin-left": "545px",
                                "verticalAlign": "middle"
                            },
                            id='call3',
                            n_clicks=0
                        )])


@app.callback(
    [Output('textarea1', 'children'),
     Output('textarea2', 'children')],
    State('age', 'value'),
    [Input('weight_input', 'value'),
    Input('height_input', 'value'),
    Input('call1', 'n_clicks')],
    prevent_initial_call=False
)
def food_op(ideal_calories, weight_inp, height_inp,call_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'call1' in changed_id:
        weight_inp = float(weight_inp)
        height_inp = float(height_inp) / 100
        bmi = weight_inp/(height_inp**2)
        bmi_msg = 'Your BMI: {}\n\n'.format(round(bmi, 2))
        status = {'Underweight': 500,
                  'Overweight': -500,
                  'Obese': -500}
        if bmi < 18.5:
            value = status['Underweight']
            ideal_calories = ideal_calories + value
            health_status = 'Health Status: Underweight\nIt is recommended for you to add 500 calories to your diet everyday\n\nNumber of calories you should consume daily: {} calories\n'.format(
                int(ideal_calories))
        elif bmi <= 24.9:
            value = 0
            ideal_calories = ideal_calories + value
            health_status = 'Health Status: Healthy\n\nNumber of calories you should consume daily: {} calories'.format(int(ideal_calories))
        elif bmi <= 29.9:
            value = status['Overweight']
            ideal_calories = ideal_calories + value
            health_status = 'Health Status: Overweight\nIt is recommended for you to reduce 500 calories in your diet everyday\n\nNumber of calories you should consume daily: {} calories\n'.format(int(ideal_calories))
        else:
            value = status['Obese']
            ideal_calories = ideal_calories + value
            health_status = 'Health Status: Overweight\nIt is recommended for you to reduce 500 calories in your diet everyday\n\nNumber of calories you should consume daily: {} calories\n'.format(int(ideal_calories))
        return bmi_msg, health_status
    else:
        raise PreventUpdate

@app.callback(
    [Output('age', 'options'),
    Output('age', 'disabled')
     ],
    Input('checkbox', 'value'),
    prevent_initial_call=False
)
def gender_op(selected):
    if selected:
        if selected == 'male_calorie_intake':
            age = [dict(label=l, value=v) for i, (l, v) in enumerate(male_calorie_intake.items())]
        else:
            age = [dict(label=l, value=v) for i, (l, v) in enumerate(female_calorie_intake.items())]
        return age,False
    else:
        raise PreventUpdate

@app.callback(
    [Output('item_name', 'options'),
    Output('item_name', 'disabled'),
     Output('textarea5','children')
     ],
    [Input('food_input', 'value'),
    Input('call2', 'n_clicks')],
    prevent_initial_call=False
)
def food_op(food_inp,call_clicks):
    msg = 'Please choose your items below till you meet your calorie needs'
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'call2' in changed_id:
        food_options = get_food(food_inp)
        food_items = [dict(label=l, value=v) for i,(l,v) in enumerate(food_options.items())]
        return food_items,False,msg
    else:
        raise PreventUpdate


@app.callback(Output('textarea3', 'children'),
              Output('textarea6', 'children'),
              Output('textarea4', 'children'),
              State('age', 'value'),
              State('item_name', 'value'),
              [Input('food_input', 'value'),
               Input('weight_input', 'value'),
               Input('height_input', 'value'),
               Input('call3', 'n_clicks')])
def count_calories(ideal_calories, desired_calories, food, weight, height, call_clicks):
    global total_calories
    global list_msg
    selected_food_list =[]
    selected_calorie_list= []
    total_cals_str =''
    end_msg = ''
    status = {'Underweight':500,
              'Overweight': -500,
              'Obese': -500}
    weight = int(weight)
    height = int(height) / 100
    bmi = weight / (height ** 2)
    if bmi < 18.5:
        value = status['Underweight']
    elif bmi <24.9:
        value = 0
    elif bmi < 29.9:
        value = status['Overweight']
    else:
        value = status['Obese']
    ideal_calories = ideal_calories + value
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'call3' in changed_id:
        for i in range(len(desired_calories)):
            total_calories = total_calories + desired_calories[i]
            selected_food_list.append(food)
            selected_calorie_list.append(desired_calories[i])
            if total_calories <= ideal_calories:
                total_cals_str = '\n\nTotal calories: {}\n\n'.format(round(total_calories, 2))
                for j in range(0, len(selected_food_list)):
                    list_msg = list_msg + selected_food_list[j].upper() + ': ' + str(selected_calorie_list[j]) + ' cals' + '\n'
                return total_cals_str,list_msg,end_msg
            else:
                end_msg = '\n\nYour total calorie intake has exceeded\n\n'
                return total_cals_str,list_msg, end_msg

    else:
        raise PreventUpdate


waitress.serve(app.server, listen="*:1234")



