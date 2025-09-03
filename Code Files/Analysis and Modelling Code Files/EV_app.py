import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')

# ---------------------------------
# App
# ---------------------------------
app = dash.Dash(__name__)

# ---------------------------------
# Data
# ---------------------------------
df = pd.read_csv(
    "C:\\Users\\Ashish Siwach\\OneDrive - University of Exeter\\Dissertation_Cld\\Datasets\\enhanced_imputed_dataset.csv",
    parse_dates=['date'],
    index_col='date'
)

# ---------------------------------
# Helpers
# ---------------------------------
def kpi_card(title, big, sub=None, accent='#2c3e50', bg='#ecf0f1'):
    """Simple pretty KPI card."""
    return html.Div([
        html.H4(title, style={'margin':'0 0 8px 0', 'textAlign':'center'}),
        html.H1(big, style={'color': accent, 'fontSize':'44px', 'margin':'0', 'textAlign':'center'}),
        html.Div(sub or "", style={'textAlign':'center', 'color':'#555', 'marginTop':'6px'})
    ], style={
        'backgroundColor': bg, 'padding':'18px', 'borderRadius':'12px',
        'boxShadow':'0 2px 4px rgba(0,0,0,0.08)'
    })

# ---------------------------------
# Modelling (same core logic)
# ---------------------------------
def logistic_function(t, L, k, t0):
    return L / (1 + np.exp(-k * (t - t0)))

historical_share = df['BEV_Share']
time_index = np.arange(len(historical_share))
market_ceiling = 0.98

params, _ = curve_fit(
    logistic_function,
    time_index,
    historical_share,
    p0=[market_ceiling, 0.1, 100],
    bounds=([0.97, 0, 0], [0.99, 1, 200])
)
logistic_L, logistic_k, logistic_t0 = params

scenario_params = {
    'Baseline': {'k_adj': 1.0, 'color': '#0077b6'},
    'Economic Stress': {'k_adj': 0.95, 'color': '#d62828'},
    'Market Driven': {'k_adj': 1.05, 'color': '#2d7d32'},
    'Infrastructure Acceleration': {'k_adj': 1.07, 'color': '#f57c00'}
}

full_date_range = pd.date_range(start=df.index.min(), end='2035-12-01', freq='MS')
full_time_index = np.arange(len(full_date_range))

# 2030 projections for all scenarios (point estimate)
scenario_2030_projections = {}
for scenario, params_dict in scenario_params.items():
    adjusted_k = logistic_k * params_dict['k_adj']
    scenario_curve = logistic_function(full_time_index, logistic_L, adjusted_k, logistic_t0)
    scenario_series = pd.Series(scenario_curve, index=full_date_range)
    try:
        projection_2030 = scenario_series.loc['2030-01-01']
    except KeyError:
        projection_2030 = scenario_series[scenario_series.index >= '2030-01-01'].iloc[0]
    scenario_2030_projections[scenario] = float(np.clip(projection_2030, 0, 1))

# Simulated SARIMAX near-term (keep as-is)
future_dates_sarimax = pd.date_range(start='2024-07-01', end='2027-06-01', freq='MS')
baseline_sarimax = np.linspace(df['BEV_Registrations'].iloc[-1], 120000, len(future_dates_sarimax))
stress_sarimax = baseline_sarimax * 0.75

# ---------------------------------
# KPI CALCULATIONS (3 metrics)
# ---------------------------------
last_date = df.index.max()
last_share = float(df['BEV_Share'].iloc[-1])  # 0..1

# 1) Current BEV Share with YoY change (pp)
if len(df) >= 13 and pd.notna(df['BEV_Share'].shift(12).iloc[-1]):
    yoy_pp = (df['BEV_Share'].iloc[-1] - df['BEV_Share'].shift(12).iloc[-1]) * 100
else:
    yoy_pp = np.nan

# 2) 2030 Projection (Baseline)
adjusted_k_base = logistic_k * scenario_params['Baseline']['k_adj']
baseline_curve = logistic_function(full_time_index, logistic_L, adjusted_k_base, logistic_t0)
baseline_series = pd.Series(baseline_curve, index=full_date_range)
try:
    proj2030 = float(baseline_series.loc['2030-01-01'])
except KeyError:
    proj2030 = float(baseline_series[baseline_series.index >= '2030-01-01'].iloc[0])

# 3) Timeline to 80% (Baseline)
try:
    milestone_80 = baseline_series[baseline_series >= 0.80].index[0]
    months_delta = (milestone_80.year - 2030) * 12 + (milestone_80.month - 1)  # vs Jan 2030
    timing_text = f"{milestone_80.strftime('%b %Y')}  •  {'ahead' if months_delta<0 else 'behind'} by {abs(months_delta)} mo"
    timing_accent = '#27ae60' if months_delta <= 0 else '#e74c3c'
    milestone_label = milestone_80.strftime('%b %Y')
except Exception:
    milestone_80 = None
    milestone_label = "Not by 2035"
    months_delta = None
    timing_text = "Not reached by 2035"
    timing_accent = '#e74c3c'

# ---------------------------------
# Layout
# ---------------------------------
app.layout = html.Div([
    html.Div([
        html.H1("UK BEV Adoption Forecasting Dashboard",
                style={'textAlign': 'center', 'marginBottom': '30px', 'color': '#2c3e50'})
    ]),

    dcc.Tabs(id="main-tabs", value='executive-tab', children=[
        # ---------------- Executive Summary ----------------
        dcc.Tab(label='Executive Summary', value='executive-tab', children=[
            html.Div([
                html.H2("Top-Line Performance: The Core Challenge",
                        style={'color': '#e74c3c', 'marginBottom': '20px', 'marginTop': '30px'}),

                # >>> NEW KPI ROW (3 cards) <<<
                html.Div([
                    kpi_card(
                        "Current BEV Share",
                        f"{last_share*100:.0f}%",
                        sub=(f"YoY change: {yoy_pp:+.1f} pp" if not np.isnan(yoy_pp) else "YoY change: n/a"),
                        accent='#3498db', bg='#eef6ff'
                    ),
                    kpi_card(
                        "2030 Projection (Baseline)",
                        f"{proj2030*100:.0f}%",
                        sub="Projected share in Jan 2030",
                        accent='#f39c12', bg='#fef9e7'
                    ),
                    kpi_card(
                        "Timeline to 80% (Baseline)",
                        milestone_label,
                        sub=timing_text,
                        accent=timing_accent, bg='#f4f9f4' if timing_accent=='#27ae60' else '#fdecea'
                    ),
                ], style={'display':'grid', 'gridTemplateColumns':'repeat(3, 1fr)', 'gap':'20px', 'marginBottom':'28px'}),

                # Strategic figure
                html.Div([
                    html.H2("Strategic Trajectory: Current Path vs. Target",
                            style={'color': '#2c3e50', 'marginBottom': '20px'}),
                    dcc.Graph(id='executive-chart', style={'height': '500px'}),
                    html.P("Explore detailed scenarios and analysis in the tabs above",
                           style={'textAlign': 'center', 'fontStyle': 'italic', 'color': '#7f8c8d'})
                ]),

                # Insights
                html.Div([
                    html.H2("Key Insights: What Should We Focus On?",
                            style={'color': '#2c3e50', 'marginTop': '40px', 'marginBottom': '30px'}),
                    html.Div([
                        html.Div([
                            html.H3("Consumer attention beats economic factors",
                                    style={'color': '#3498db', 'margin': '0', 'cursor': 'pointer', 'textAlign': 'center'},
                                    title="Google Trends is the most powerful predictor with 2-month lead time. Traditional economic factors show no predictive power.")
                        ], style={'backgroundColor': '#ebf3fd', 'padding': '15px', 'borderRadius': '10px',
                                  'marginBottom': '15px', 'border': '1px solid #d5e8f7'}),
                        html.Div([
                            html.H3("More chargers ≠ more adoption after 40k",
                                    style={'color': '#f39c12', 'margin': '0', 'cursor': 'pointer', 'textAlign': 'center'},
                                    title="Infrastructure shows diminishing returns after 40,000 charging points. Focus should shift from quantity to quality.")
                        ], style={'backgroundColor': '#fef9e7', 'padding': '15px', 'borderRadius': '10px',
                                  'marginBottom': '15px', 'border': '1px solid #f0e6a6'}),
                        html.Div([
                            html.H3("Subsidies no longer drive growth",
                                    style={'color': '#27ae60', 'margin': '0', 'cursor': 'pointer', 'textAlign': 'center'},
                                    title="2022 grant withdrawal had zero impact on underlying trend, indicating market maturation beyond direct subsidies.")
                        ], style={'backgroundColor': '#eafaf1', 'padding': '15px', 'borderRadius': '10px',
                                  'border': '1px solid #c8e6c9'})
                    ], style={'display':'grid', 'gridTemplateColumns':'repeat(3, 1fr)', 'gap':'14px'})
                ])
            ])
        ]),

        # ---------------- Strategic Outlook ----------------
        dcc.Tab(label='Strategic Outlook (2024-2035)', value='strategic-tab', children=[
            html.Div([
                html.H2("Long-Term Strategic Forecasting",
                        style={'color': '#2c3e50', 'marginTop': '30px', 'marginBottom': '20px'}),

                html.Div([
                    html.Label("Select Scenario:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                    dcc.Dropdown(
                        id='strategic-scenario-dropdown',
                        options=[{'label': s, 'value': s} for s in scenario_params.keys()],
                        value='Baseline',
                        multi=False,
                        style={'marginBottom': '20px', 'width': '300px'}
                    )
                ]),

                dcc.Graph(id='strategic-chart', style={'height': '600px'}),

                html.Div([
                    html.H3("Milestone Achievement Dates", style={'marginTop': '30px'}),
                    html.Div(id='milestone-table')
                ])
            ])
        ]),

        # ---------------- Tactical Risks ----------------
        dcc.Tab(label='Tactical Risks (3-Year)', value='tactical-tab', children=[
            html.Div([
                html.H2("Short-Term Vulnerability Assessment",
                        style={'color': '#2c3e50', 'marginTop': '30px', 'marginBottom': '20px'}),

                html.P("3-year forecast shows steady growth under normal conditions, and a clear shortfall if a recession hits.",
                       style={'fontSize': '16px', 'marginBottom': '20px'}),

                html.Div([
                    html.Label("Economic Scenario:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                    dcc.RadioItems(
                        id='tactical-stress-toggle',
                        options=[
                            {'label': ' Normal Conditions', 'value': 'normal'},
                            {'label': ' Economic Stress', 'value': 'stress'}
                        ],
                        value='normal',
                        inline=True,
                        style={'marginBottom': '30px'}
                    )
                ]),

                html.Div([
                    dcc.Graph(id='sarimax-tactical-chart', style={'height': '500px'}),
                ], style={'marginBottom': '30px'}),

                html.Div([
                    html.Div(id='tactical-kpi-main',
                             style={'backgroundColor': '#ecf0f1', 'padding': '30px', 'borderRadius': '10px',
                                    'textAlign': 'center', 'marginBottom': '30px',
                                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

                    html.Div(id='tactical-risk-analysis',
                             style={'backgroundColor': '#fff3cd', 'padding': '20px', 'borderRadius': '10px',
                                    'border': '1px solid #ffeaa7'})
                ])
            ])
        ])
    ])
])

# ---------------------------------
# Callbacks
# ---------------------------------
@app.callback(
    Output('executive-chart', 'figure'),
    Input('main-tabs', 'value')
)
def update_executive_chart(tab):
    adjusted_k = logistic_k * scenario_params['Baseline']['k_adj']
    scenario_curve = logistic_function(full_time_index, logistic_L, adjusted_k, logistic_t0)
    scenario_series = pd.Series(scenario_curve, index=full_date_range)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['BEV_Share'] * 100,
        mode='lines',
        name='Historical Data',
        line=dict(color='black', width=3)
    ))

    fig.add_trace(go.Scatter(
        x=scenario_series.index,
        y=scenario_series * 100,
        mode='lines',
        name='Baseline Forecast',
        line=dict(color='#0077b6', width=3, dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=[pd.to_datetime('2030-01-01'), pd.to_datetime('2035-01-01')],
        y=[80, 98],
        mode='markers',
        name='Government Targets',
        marker=dict(color='red', size=15, symbol='diamond')
    ))

    fig.add_annotation(
        x=pd.to_datetime('2028-01-01'),
        y=50,
        text="50% expected by early 2028",
        showarrow=True,
        arrowhead=2,
        bgcolor='white',
        bordercolor='black'
    )

    fig.add_annotation(
        x=pd.to_datetime('2030-01-01'),
        y=80,
        text=f"Baseline forecast: ~{scenario_2030_projections['Baseline']:.0%}<br>Policy gap: ~{0.80 - scenario_2030_projections['Baseline']:.0%}",
        showarrow=True,
        arrowhead=2,
        bgcolor='#ffcccb',
        bordercolor='red'
    )

    fig.update_layout(
        title='UK BEV Adoption: Current Trajectory vs. Government Targets',
        xaxis_title='Year',
        yaxis_title='BEV Market Share (%)',
        hovermode='x unified',
        legend=dict(x=0.02, y=0.98),
        height=500,
        yaxis=dict(range=[0, 105])
    )
    return fig

@app.callback(
    Output('strategic-chart', 'figure'),
    Input('strategic-scenario-dropdown', 'value')
)
def update_strategic_chart(selected_scenario):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['BEV_Share'] * 100,
        mode='lines',
        name='Historical Data',
        line=dict(color='black', width=3)
    ))

    adjusted_k = logistic_k * scenario_params[selected_scenario]['k_adj']
    scenario_curve = logistic_function(full_time_index, logistic_L, adjusted_k, logistic_t0)
    scenario_series = pd.Series(scenario_curve, index=full_date_range)

    fig.add_trace(go.Scatter(
        x=scenario_series.index,
        y=scenario_series * 100,
        mode='lines',
        name=f'{selected_scenario} Scenario',
        line=dict(color=scenario_params[selected_scenario]['color'], width=3, dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=[pd.to_datetime('2030-01-01'), pd.to_datetime('2035-01-01')],
        y=[80, 98],
        mode='markers',
        name='Government Targets',
        marker=dict(color='red', size=12, symbol='diamond')
    ))

    milestone_50 = scenario_series[scenario_series >= 0.50].index[0] if len(scenario_series[scenario_series >= 0.50]) > 0 else None
    if milestone_50:
        fig.add_annotation(
            x=milestone_50,
            y=50,
            text=f"50% achieved: {milestone_50.strftime('%b %Y')}",
            showarrow=True,
            arrowhead=2,
            bgcolor='white',
            bordercolor='black'
        )

    milestone_80 = scenario_series[scenario_series >= 0.80].index[0] if len(scenario_series[scenario_series >= 0.80]) > 0 else None
    if milestone_80:
        fig.add_annotation(
            x=milestone_80,
            y=80,
            text=f"80% achieved: {milestone_80.strftime('%b %Y')}",
            showarrow=True,
            arrowhead=2,
            bgcolor='lightgreen',
            bordercolor='green'
        )
    else:
        try:
            projection_2030 = scenario_series.loc['2030-01-01']
        except KeyError:
            projection_2030 = scenario_series[scenario_series.index >= '2030-01-01'].iloc[0]

        fig.add_annotation(
            x=pd.to_datetime('2030-01-01'),
            y=projection_2030 * 100,
            text=f"2030 projection: {projection_2030:.0%}<br>Gap: {0.80 - projection_2030:.0%}",
            showarrow=True,
            arrowhead=2,
            bgcolor='#ffcccb',
            bordercolor='red'
        )

    fig.update_layout(
        title=f'Long-Term Strategic Forecast: {selected_scenario} Scenario',
        xaxis_title='Year',
        yaxis_title='BEV Market Share (%)',
        hovermode='x unified',
        legend=dict(x=0.02, y=0.98),
        height=600,
        yaxis=dict(range=[0, 105])
    )
    return fig

@app.callback(
    Output('sarimax-tactical-chart', 'figure'),
    Input('tactical-stress-toggle', 'value')
)
def update_sarimax_chart(stress_scenario):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['BEV_Registrations'],
        mode='lines',
        name='Historical',
        line=dict(color='rgba(0,0,0,0.7)', width=2),
        hovertemplate='%{x|%b %Y}<br>Historical: %{y:,.0f} registrations<extra></extra>'
    ))

    if stress_scenario == 'normal':
        fig.add_trace(go.Scatter(
            x=future_dates_sarimax,
            y=baseline_sarimax,
            mode='lines',
            name='Forecast',
            line=dict(color='#0077b6', width=4),
            hovertemplate='%{x|%b %Y}<br>Forecast: %{y:,.0f} registrations<extra></extra>'
        ))

        upper = baseline_sarimax * 1.06
        lower = baseline_sarimax * 0.94
        fig.add_trace(go.Scatter(
            x=future_dates_sarimax, y=upper,
            mode='lines', line=dict(width=0),
            showlegend=False, hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=future_dates_sarimax, y=lower,
            mode='lines', line=dict(width=0),
            fill='tonexty', fillcolor='rgba(0,119,182,0.12)',
            name='Uncertainty range', hoverinfo='skip'
        ))

        title = '3-Year Outlook: Monthly BEV Registrations (Normal Conditions)'

    else:
        fig.add_trace(go.Scatter(
            x=future_dates_sarimax,
            y=baseline_sarimax,
            mode='lines',
            name='Normal (no recession)',
            line=dict(color='rgba(120,120,120,0.9)', width=2, dash='dash'),
            hovertemplate='%{x|%b %Y}<br>Normal: %{y:,.0f}<extra></extra>'
        ))

        fig.add_trace(go.Scatter(
            x=future_dates_sarimax,
            y=stress_sarimax,
            mode='lines',
            name='Recession case',
            line=dict(color='#d62828', width=4),
            hovertemplate='%{x|%b %Y}<br>Recession case: %{y:,.0f}<extra></extra>'
        ))

        shortfall = baseline_sarimax - stress_sarimax
        fig.add_trace(go.Scatter(
            x=future_dates_sarimax,
            y=baseline_sarimax,
            mode='lines',
            line=dict(width=0),
            showlegend=False, hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=future_dates_sarimax,
            y=stress_sarimax,
            mode='lines',
            fill='tonexty',
            fillcolor='rgba(214,40,40,0.22)',
            line=dict(width=0),
            name='Monthly shortfall',
            hovertemplate='%{x|%b %Y}<br>Shortfall: %{customdata:,.0f} units<extra></extra>',
            customdata=shortfall
        ))

        peak_idx = int(np.argmax(shortfall))
        peak_date = future_dates_sarimax[peak_idx]
        peak_val = shortfall[peak_idx]
        total_at_risk = shortfall.sum()

        fig.add_annotation(
            x=peak_date, y=stress_sarimax[peak_idx],
            text=f"Peak monthly shortfall: {int(peak_val):,}",
            showarrow=True, arrowhead=2,
            bgcolor='white', bordercolor='#d62828'
        )
        fig.add_annotation(
            x=future_dates_sarimax[int(len(future_dates_sarimax) * 0.65)],
            y=(baseline_sarimax.max() * 0.55),
            text=f"Total units at risk (3 yrs): {int(total_at_risk):,}",
            showarrow=False, bgcolor='#ffecec', bordercolor='#d62828'
        )

        title = 'Economic Stress: What a Recession Does to Monthly Registrations'

    fig.update_layout(
        title=title,
        xaxis_title='Month',
        yaxis_title='Monthly BEV Registrations',
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.7)'),
        height=500,
        margin=dict(l=40, r=20, t=70, b=40)
    )

    ymax = (max(np.max(baseline_sarimax), np.max(stress_sarimax))
            if stress_scenario == 'stress' else np.max(baseline_sarimax))
    fig.update_yaxes(range=[0, ymax * 1.2])
    return fig

@app.callback(
    [Output('tactical-kpi-main', 'children'),
     Output('tactical-risk-analysis', 'children')],
    Input('tactical-stress-toggle', 'value')
)
def update_tactical_outlook(stress_scenario):
    try:
        if stress_scenario == 'normal':
            kpi_content = [
                html.H3("3-Year Outlook (Normal)", style={'color': '#3498db', 'margin': '0'}),
                html.H1(f"{int(baseline_sarimax[-1]):,}",
                        style={'color': '#3498db', 'fontSize': '42px', 'margin': '10px 0'}),
                html.P("Projected monthly registrations by mid-2027",
                       style={'fontSize': '16px', 'margin': '0'})
            ]
            risk_content = [
                html.H4("Risk Level: Moderate", style={'color': '#f39c12', 'marginBottom': '10px'}),
                html.P("Steady growth expected if economic conditions remain stable.")
            ]
        else:
            shortfall = baseline_sarimax - stress_sarimax
            peak_val = int(shortfall.max())
            total_at_risk = int(shortfall.sum())

            kpi_content = [
                html.H3("Economic Stress Impact", style={'color': '#e74c3c', 'margin': '0'}),
                html.H1(f"-{peak_val:,}",
                        style={'color': '#e74c3c', 'fontSize': '42px', 'margin': '10px 0'}),
                html.P("Peak monthly shortfall vs. normal",
                       style={'fontSize': '16px', 'margin': '0'})
            ]
            risk_content = [
                html.H4("Risk Level: High", style={'color': '#e74c3c', 'marginBottom': '10px'}),
                html.P(f"A recession could reduce cumulative registrations by ~{total_at_risk:,} units over 3 years, delaying the adoption timeline.")
            ]

        return kpi_content, risk_content

    except Exception:
        fallback_kpi = [html.H3("Loading...", style={'color': '#7f8c8d'})]
        fallback_risk = [html.P("Loading risk assessment...", style={'color': '#7f8c8d'})]
        return fallback_kpi, fallback_risk

@app.callback(
    Output('milestone-table', 'children'),
    Input('strategic-scenario-dropdown', 'value')
)
def update_milestone_table(selected_scenario):
    milestones = ['50% Adoption', '80% Adoption', '98% Adoption']
    milestone_values = [0.50, 0.80, 0.98]

    adjusted_k = logistic_k * scenario_params[selected_scenario]['k_adj']
    scenario_curve = logistic_function(full_time_index, logistic_L, adjusted_k, logistic_t0)
    scenario_series = pd.Series(scenario_curve, index=full_date_range)

    table_data = []
    for label, value in zip(milestones, milestone_values):
        try:
            date_achieved = scenario_series[scenario_series >= value].index[0]
            table_data.append([label, date_achieved.strftime('%b %Y')])
        except IndexError:
            table_data.append([label, "Not Achieved by 2035"])

    table = html.Table([
        html.Thead([html.Tr([html.Th("Milestone"), html.Th(f"{selected_scenario} Scenario")])]),
        html.Tbody([html.Tr([html.Td(c) for c in row]) for row in table_data])
    ], style={'width': '100%', 'textAlign': 'center', 'border': '1px solid #ddd'})

    return table

# ---------------------------------
# Basic CSS
# ---------------------------------
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f8f9fa;
            }
            .dash-table-container { margin: 20px 0; }
            table { border-collapse: collapse; margin: 20px 0; width: 100%; }
            th, td { padding: 12px; border: 1px solid #ddd; text-align:center; }
            th { background-color: #f8f9fa; font-weight: bold; }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# ---------------------------------
# Run
# ---------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
