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
food='chocolate'
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
        # print(parsed['hits'][i]['fields']['item_name'], " | ", parsed['hits'][i]['fields']['nf_calories'])
        #item_names.append(parsed['hits'][i]['fields']['item_name'])
        key = parsed['hits'][i]['fields']['item_name']
        value = parsed['hits'][i]['fields']['nf_calories']
        item_name_with_calories.update({key: value})

    #print(item_names)
    return item_name_with_calories

female_calorie_intake ={"13": 2000.0, "14-18": 2000.0, "19-20": 2000.0, "21-25": 2200.0, "26-30": 2000.0, "31-50": 2000.0,
     "51-60": 1800.0, "61 & up": 1800.0}
male_calorie_intake = {"13": 2200.0, "14-15": 2500.0, "16-18": 2800.0, "19-20": 2800.0, "21-25": 2800.0, "26-35": 2600.0,
     "36-40": 2600.0, "41-45": 2600.0, "46-55": 2400.0, "56-60": 2400.0, "61-65": 2400.0, "66-75": 2200.0,
     "76 & up": 2200.0}


for (l,v) in enumerate(female_calorie_intake):
    print(l,v)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = "Nutrition"

app.layout =html.Div([
                  html.H1(children = 'Welcome to Balanced Bites!',
                          style = {'textAlign':'center'
                          }),
                  html.Div('Gender'),
                  dcc.RadioItems(
                   id = 'checkbox',
                   options={
                        'male_calorie_intake': 'Male',
                        'female_calorie_intake': 'Female'
                   },
                   value='male_calorie_intake',
                    ),
                    html.Br(),
                    dcc.Dropdown(
                        id='age',
                        placeholder="SELECT AGE RANGE",
                        multi=False,
                        disabled=True
                    ),
                    html.Br(),
                    dcc.Textarea(
                        id='weight_input',
                        value='Enter your weight',
                        style={'width': '50%', 'height': 50},
                    ),
                    dcc.Textarea(
                        id='height_input',
                        value='Enter your height',
                        style={'width': '50%', 'height': 50},
                    ),
                    html.Br(),
                    dbc.Button(
                        'Get BMI Result',
                        id='call1',
                        n_clicks=0
                    ),
                    html.Div(id='textarea1', style={'whiteSpace': 'pre-line'}),
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
                    style={'font-size': '13px', 'width': '140px', 'display': 'inline-block', 'margin-bottom': '10px', 'margin-right': '5px', 'height':'50px', 'verticalAlign': 'top'},
                    n_clicks=0
                ),
                    html.Div(id='textarea5', style={'whiteSpace': 'pre-line'}),
                    html.Br(),
                    dcc.Dropdown(
                        id='item_name',
                        placeholder="SELECT TYPE",
                        multi=True
                    ),
                    html.Div(id='textarea3', style={'whiteSpace': 'pre-line'}),
                    html.Div(id='textarea4', style={'whiteSpace': 'pre-line'}),
                    html.Br(),
                    dbc.Button(
                            'Submit',
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
        weight_inp = int(weight_inp)
        height_inp = int(height_inp) / 100
        bmi = weight_inp/(height_inp**2)
        bmi_msg = '\nYour BMI: {}\n\n'.format(round(bmi, 2))
        status = {'Underweight': 500,
                  'Overweight': -500,
                  'Obese': -500}
        if bmi < 18.5:
            value = status['Underweight']
            ideal_calories = ideal_calories + value
            health_status = 'Health Status: Underweight\nIt is recommended for you to add 500 calories to your diet everyday\nNumber of calories you should consume: {}\n'.format(
                ideal_calories)
        elif bmi <= 24.9:
            value = 0
            ideal_calories = ideal_calories + value
            health_status = 'Health Status: Healthy\nNumber of calories you should consume:{}'.format(ideal_calories)
        elif bmi <= 29.9:
            value = status['Overweight']
            ideal_calories = ideal_calories + value
            health_status = 'Health Status: Overweight\nIt is recommended for you to reduce 500 calories in your diet everyday\nNumber of calories you should consume: {}\n'.format(ideal_calories)
        else:
            value = status['Obese']
            ideal_calories = ideal_calories + value
            health_status = 'Health Status: Overweight\nIt is recommended for you to reduce 500 calories in your diet everyday\nNumber of calories you should consume: {}\n'.format(ideal_calories)
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
    msg = 'Please choose your items below'
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'call2' in changed_id:
        food_options = get_food(food_inp)
        food_items = [dict(label=l, value=v) for i,(l,v) in enumerate(food_options.items())]
        return food_items,False,msg
    else:
        raise PreventUpdate


@app.callback(Output('textarea3', 'children'),
              Output('textarea4', 'children'),
              State('age', 'value'),
              State('item_name', 'value'),
              [Input('food_input', 'value'),
               Input('weight_input', 'value'),
               Input('height_input', 'value'),
               Input('call3', 'n_clicks')])
def count_calories(ideal_calories, desired_calories, food, weight, height, call_clicks):
    global total_calories
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
    print(ideal_calories)
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'call3' in changed_id:
        for i in range(len(desired_calories)):
            print(total_calories)
            total_calories = total_calories + desired_calories[i]
            if total_calories <= ideal_calories:
                total_cals_str = '\n\nTotal calories: {}\n\n'.format(round(total_calories, 2))
                return total_cals_str,end_msg
            else:
                end_msg = '\n\nYour total calorie intake has exceeded\n\n'
                return total_cals_str, end_msg

    else:
        raise PreventUpdate


# waitress.serve(app.server, listen="*:1234")
if __name__ == '__main__':
    app.run_server(debug=True)