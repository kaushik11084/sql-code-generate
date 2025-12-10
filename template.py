import os, time
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import dash
import dash_bootstrap_components as dbc
from dash import dash_table, Input, Output, State, html, dcc
import pandas as pd
import requests
import json
import base64
import io
from jproperties import Properties
from markdownify import markdownify as md
from datetime import datetime
import bcrypt
from furl import furl

# instantiate config
configs = Properties()
# load properties into configs
with open('app-config.properties', 'rb') as config_file:
    configs.load(config_file)
# read into dictionary
configs_dict = {}
items_view = configs.items()
for item in items_view:
    configs_dict[item[0]] = item[1].data

# For LLM call
SERVER_URL = os.getenv('SERVER_URL')
WATSONX_PROJECT_ID = os.getenv('WATSONX_PROJECT_ID')
API_KEY = os.getenv("WATSONX_API_KEY", default="")
HEADERS = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'Authorization': 'Bearer {}'.format(API_KEY)
    }

# Read Sample text from file
sample_from_file = ""
with open('sample-brief-gen.txt', 'r') as sample_text_f:
    sample_from_file = sample_text_f.read()

salt = os.getenv("SALT")
email_store = dict(email="", ibmid="", verified=False)

# ---- UI code ----

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP, 'https://fonts.googleapis.com/css?family=IBM+Plex+Sans:400,600&display=swap'])
app.title = configs_dict['tabtitle']

navbar_main = dbc.Navbar([
                    dbc.Col(children=[html.A(configs_dict['navbartitle'], href=os.getenv("HEADER_URL"), target='_blank', style={'color': 'white', 'textDecoration': 'none'})],
                        style={'fontSize': '0.875rem','fontWeight': '600'},
                    ),
                    dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem("View payload", id="payload-button", n_clicks=0, class_name="dmi-class"),
                        ],
                        toggle_class_name="nav-dropdown-btn", caret=False,
                        nav=True, in_navbar=True,
                        label=html.Img(src="/assets/settings.svg", height="16px", width="16px", style={'filter': 'invert(1)'}),
                        align_end=True,
                    ),
        ],
    style={'paddingLeft': '1rem', 'height': '3rem', 'borderBottom': '1px solid #393939', 'color': '#fff'},
    class_name = "bg-dark"
)

payload_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("My Payloads")),
        dbc.ModalBody([
            dbc.Tabs(id="payload-modal-tb", active_tab="payload-tab-0")
        ]),
    ],
    id="payload-modal",
    size="xl",
    scrollable=True,
    is_open=False,
)

email_modal = dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Verification")),
                dbc.ModalBody([
                    dbc.Input(id="user-email", placeholder="abc@xyz.com", type="text", className="carbon-input"),
                    dbc.Button("Verify email",id="verify-email-button", n_clicks=0, className="carbon-btn", outline=True, color="primary", disabled=False),
                    html.Br(),
                    html.Br(),
                    html.Div(id="verification-alert-div")
                ]),
            ],
            id="email-modal",
            size="md",
            is_open=False
        )

email_modal_upload = dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Verification")),
                dbc.ModalBody([
                    dbc.Input(id="user-email-upload", placeholder="abc@xyz.com", type="text", className="carbon-input"),
                    dbc.Button("Verify email",id="verify-email-upload-button", n_clicks=0, className="carbon-btn", outline=True, color="primary", disabled=False),
                    html.Br(),
                    html.Br(),
                    html.Div(id="verification-alert-upload-div")
                ]),
            ],
            id="email-modal-upload",
            size="md",
            is_open=False,
        )


user_input = dbc.InputGroup([
        dbc.Textarea(id="user-input",
                     value="",
                     placeholder=configs_dict['input_placeholder_text'],
                     rows=configs_dict['input_h_rows'] if configs_dict['layout'] == 'horizontal' else configs_dict['input_v_rows'],
                     class_name="carbon-input"
                     ),
    ],
    className="mb-3",
)

generate_button = dbc.Button(
    configs_dict['generate_btn_text'], id="generate-button", color="primary", n_clicks=0, className="carbon-btn"
)

sample_text_button = dbc.Button(
    "Sample text", id="sample-text-button", outline=True, color="primary", n_clicks=0, className="carbon-btn", style={"overflow": "hidden","whiteSpace": "nowrap","display": "block","textOverflow": "ellipsis"}
)

upload_file_note = dbc.Row(dbc.Col(
                            html.Div(
                                children=[html.I(className="bi bi-info-circle"),html.P("Allowed file types: .txt & File size limit to upload: 50Kb", style={"color": "#525252", "fontSize": "0.8rem","fontWeight": 400,"letterSpacing": 0,"paddingLeft":"0.5rem", "paddingTop":"3px"})],
                            style={"display":"flex"}),
                    )
                )


upload_button = dcc.Upload(id="upload-data", className="upload-data",
    children=[
        dbc.Button("Upload File", outline=True, color="primary", n_clicks=0, className="carbon-btn"),
    ],
    max_size=50000,
    accept=".txt",
    disabled=False
)

buttonsPanel = dbc.Row([
                dbc.Col(sample_text_button),
                dbc.Col(upload_button),
                dbc.Col(generate_button),
            ]) if configs_dict['show_upload'] in ["true", "True"] else dbc.Row([
                 dbc.Col(sample_text_button), dbc.Col(generate_button),
                ])

footer = html.Footer(
    dbc.Row([
        dbc.Col(children=[dcc.Markdown(configs_dict['footer_text'])],className="p-3 pb-0")]),
    style={'paddingLeft': '1rem', 'paddingRight': '5rem', 'color': '#c6c6c6', 'lineHeight': '22px'},
    className="bg-dark position-fixed bottom-0"
)

vertical_layout = dbc.Row(
                    [
                        dbc.Col(className="col-2"),
                        dbc.Col(
                            children=[
                                html.H5(configs_dict['Input_title']),
                                html.Div(user_input),
                                buttonsPanel,
                                upload_file_note,
                                html.Br(),
                                html.Hr(),
                                html.Div([
                                        # html.H5(configs.get('Output_title')),
                                        html.Div(children=[html.P(configs_dict["helper_text"], style={"color": "#525252", "fontSize": "1rem", "fontStyle": "italic"})],id='generate-output')
                                    ],
                                    style={'padding': '1rem 1rem'}
                                ),
                            ],
                            className="col-8"
                        ),
                        dbc.Col(className="col-2"),
                    ],
                    className="px-3 pb-5"
                )

horizontal_layout = dbc.Row(
                    [
                        dbc.Col(className="col-1"),
                        dbc.Col(
                            children=[
                                html.H5(configs_dict['Input_title']),
                                html.Div(user_input),
                                buttonsPanel,
                                upload_file_note,
                                html.Br(),
                                html.Br(),
                            ],
                            className="col-5 border-end",
                            style={'padding': '1rem'}
                        ),
                        dbc.Col(
                            children=[
                                html.Div([
                                        # html.H5(configs.get('Output_title')),
                                        html.Div(children=[html.P(configs_dict["helper_text"], style={"color": "#525252", "fontSize": "1rem", "fontStyle": "italic"})],id='generate-output')
                                    ],
                                    style={'padding': '1rem 3rem'}
                                ),
                            ],
                            className="col-5"
                        ),
                        dbc.Col(className="col-1"),
                    ],
                    className="px-3 pb-5"
                )

app.layout = html.Div(children=[
                    dcc.Location(id='url', refresh=False),
                    dcc.Store(id="email-store", data=email_store),
                    navbar_main,
                    html.Div(payload_modal),
                    html.Div(email_modal),
                    html.Div(email_modal_upload),
                    html.Br(),
                    html.Br(),
                    horizontal_layout if configs_dict['layout'] == 'horizontal' else vertical_layout,
                    html.Br(),
                    html.Br(),
                    footer
], className="bg-white", style={"fontFamily": "'IBM Plex Sans', sans-serif"}
)

# ---- end UI code ----

# get email and user id
def get_user_email_and_id(email_store):
    try:
        emailDomain = email_store["email"].split("@")[1] if(email_store["email"]!="") else ""
        user_id = email_store["ibmid"] if(email_store["ibmid"]!="") else "default"
    except:
        emailDomain = ""
        user_id = "default"
    return emailDomain, user_id

# Fetch payloads for viewing
def get_payloads(text, email_store):
    emailDomain,user_id = get_user_email_and_id(email_store)
    sendTrackEvent(user_id, { "objectType": "nav-button", "text": "View payload", "emailDomain": emailDomain}, None)
    payloads_output = []
    labels = configs_dict['generate_btn_output_labels'].split(',')
    payloads = configs_dict['generate_btn_payload_files'].split(',')
    
    for label, payload_file, n in zip(labels, payloads, range(len(payloads))):
        with open('payload/{}-view.json'.format(payload_file)) as payload_f:
            payload_f_json = json.load(payload_f)
        payload_f_json['data']['input'] = text
        payload_f_json = json.dumps(payload_f_json, indent=2)
        payloads_output.append(
            dbc.Tab([
                    dcc.Markdown(f'''```json
{payload_f_json}
                        '''
                    ),
                ],
                tab_id=f'payload-tab-{n}',
                label=label, label_style={'borderRadius': 0}
            ),
        )
    return payloads_output

def parse_output(res, type):
    parseoutput = []
    if(type == 'text'):
        return res
    if(type == 'label'):
        return html.H5(dbc.Badge(res, color="#1192e8", style={'borderRadius': '12px','marginLeft':'8px','paddingLeft':'16px', 'paddingRight':'16px'}))
    elif(type == 'key-value'):
        try:
            pairs = res.split(',')
            for pair in pairs:
                pair = pair.strip()
                if(pair!="" and ":" in pair and len(pair.split(":"))==2):
                    k, v = pair.split(':')
                    parseoutput.append(html.Div([html.B(k+':'), v], className="key-value-div"))
            return html.Div(parseoutput, className="key-value-div-parent")
        except:
            return res
    elif(type == 'markdown'):
        res = res.replace("###", "\n\n")
        return dcc.Markdown(md(res))

# Get IBM access token and return headers
def get_header_with_access_tkn(access_token):
    headers_with_access_tkn = HEADERS.copy()
    headers_with_access_tkn['Authorization'] = 'Bearer {}'.format(access_token)
    return headers_with_access_tkn

# LLM API call
def llm_fn(text, payload_json, type, access_token):
    payload_json['project_id'] = WATSONX_PROJECT_ID
    payload_json['input'] = payload_json['input']+text+"\n\nOutput:\n"
    print("calling LLM", datetime.now())
    response_llm = requests.post(SERVER_URL, headers=get_header_with_access_tkn(access_token), data=json.dumps(payload_json))
    response_llm_json = response_llm.json()
    brief = response_llm_json['results'][0]['generated_text']
    brief = brief.replace("Input:","")
    try:
        return parse_output(brief, type)
    except Exception as e:
        print("{} Error from LLM -->".format(datetime.now()),response_llm_json)
        return "Error occured. Status code: {}. Please try again.".format(response_llm_json['status_code'])

# For Upload Data processing
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        f = io.StringIO(decoded.decode('utf-8'))
        return f.getvalue()
    except Exception as e:
        print(e)
        return "There is some error while processing the file."

# For Upload Data
if configs_dict['show_upload'] in ["true", "True"]:
    @app.callback(Output('user-input', 'value'),
                  Output('email-modal-upload', 'is_open'),
                  Output('generate-output', 'children', allow_duplicate=True),
                Input('upload-data', 'contents'),
                Input('verify-email-upload-button', 'disabled'),
                State('upload-data', 'filename'),
                State('upload-data', 'last_modified'),
                State('generate-output', 'children'),
                State('url', 'href'),
                State('user-input', 'value'),
                State('email-store', 'data'),
                prevent_initial_call=True)
    def uploadData(list_of_contents, verification_completed, list_of_names, list_of_dates, generated_output, href: str, current_input, email_store):
        if list_of_contents is not None:
            file_type = list_of_names.split('.')[1]
            if(file_type!="txt"):
                return current_input, False, dbc.Alert("Only .txt files are allowed and file size should not exceed 50Kb", color="danger")
            
            query_parameters = list(furl(href).args.keys())
            if('p' not in query_parameters or 't' not in query_parameters or 'p1' not in query_parameters):
                # it will return msg to login from dsce
                return current_input,False,dbc.Alert(dcc.Markdown(configs_dict["error_msg_login_prompt"]), color="info")
            
            if(email_store['verified']==False):
                # it will open the modal to enter email
                return current_input, True if not verification_completed else False, html.P(configs_dict["helper_text"], style={"color": "#525252", "fontSize": "1rem", "fontStyle": "italic"})
            emailDomain,user_id = get_user_email_and_id(email_store)
            sendTrackEvent(user_id, { "milestoneName": "Upload button clicked", "objectType": "button", "text": "Upload File", "emailDomain": emailDomain}, None)
            return parse_contents(list_of_contents, list_of_names, list_of_dates), False, html.P(configs_dict["helper_text"], style={"color": "#525252", "fontSize": "1rem", "fontStyle": "italic"})

def verify_user(url, email):
    try:
        randNumber = os.getenv("RANDOM_NUMBER") or 9973
        separator = os.getenv("SEPARATOR") or '##@'
        url_p=url.args['p'] # Match email with this bcrypted str
        url_ts=int(url.args['t'])-int(randNumber)
        constructed_email = f'{email}{separator}{url_ts}'
        enc_user_email = bcrypt.hashpw(constructed_email.encode('utf-8'), salt.encode('utf-8')).decode("utf-8")
        # Verify the email bcrypt
        verified = enc_user_email == url_p

        # Ibmid
        url_ibmid = base64.b64decode(url.args['p1']).decode("utf-8")
        constructed_ibmid = "IBMid-{}".format(url_ibmid[4:]) if verified else "default"
    except Exception as e:
        print("Error while validating the user : ", e)
        email=""
        verified = False
        constructed_ibmid="default"
        url_p=None
    return email, constructed_ibmid, verified


# LLM Call
@app.callback(
    Output('generate-output', 'children'),
    Output("email-modal", "is_open", allow_duplicate=True),
    Input('generate-button', 'n_clicks'),
    Input('verify-email-button', 'disabled'),
    State('user-input', 'value'),
    State('url','href'),
    State('email-store','data'),
    State("email-modal", "is_open"),
    prevent_initial_call=True
)
def generate_output_llm(n, verification_completed, text, href: str, email_store, is_open):
    if(n>0 or verification_completed==True):
        isCustomText = "No"
        
        # Input is tampered
        if(text not in [sample_from_file]):
            if(text.strip()==""):
                time.sleep(0.5)
                return dbc.Alert(dcc.Markdown(configs_dict["error_msg_empty_input"]), color="danger"), False
            
            isCustomText = "Yes"

            # URL has p,t,p1 then open modal
            query_parameters = list(furl(href).args.keys())
            if('p' not in query_parameters or 't' not in query_parameters or 'p1' not in query_parameters):
                time.sleep(0.5)
                return dbc.Alert(dcc.Markdown(configs_dict["error_msg_login_prompt"]), color="info"), False

            # Email is not verified by user
            if(email_store['verified']==False):
                time.sleep(0.5)
                return html.P(configs_dict["helper_text"], style={"color": "#525252", "fontSize": "1rem", "fontStyle": "italic"}), True

        emailDomain,user_id = get_user_email_and_id(email_store)
        #sendTrackEvent(user_id, { "milestoneName": "Generate button clicked", "objectType": "button", "text": configs_dict['generate_btn_text'], "isCustomText": isCustomText, "emailDomain": emailDomain}, None)
        output = []
        actions = configs_dict['generate_btn_actions'].split(',')
        labels = configs_dict['generate_btn_output_labels'].split(',')
        payloads = configs_dict['generate_btn_payload_files'].split(',')
        types = configs_dict['generate_btn_output_type'].split(',')
        authenticator = IAMAuthenticator(API_KEY)
        access_token = authenticator.token_manager.get_token()
        
        for action, label, payload_file, type in zip(actions, labels, payloads, types):
            try:
                with open('payload/{}.json'.format(payload_file)) as payload_f:
                    payload_f_json = json.load(payload_f)

                if(action == "llm"):
                    output.append(html.Div([html.H5(label), llm_fn(text, payload_f_json, type, access_token)], className="output-div"))

            except Exception as e:
                print(action, e)
                time.sleep(1)
        return output, False
    return [], is_open

# For loading spinner
@app.callback(
    Output('generate-output', 'children', allow_duplicate=True),
    Input('generate-button', 'n_clicks'),
    Input('verify-email-button', 'disabled'),
    prevent_initial_call=True
)
def generate_output_llm(n, verification_completed):
    if(n>0 or verification_completed==True):
        return [dbc.Spinner(color="primary", size="sm"), " Please wait..."]

# Open/Close payload modal
@app.callback(
    Output("payload-modal", "is_open"),
    Output("payload-modal-tb", "children"),
    [Input("payload-button", "n_clicks")],
    [State("payload-modal", "is_open"), State('user-input', 'value'),State('email-store','data')],
    prevent_initial_call=True
)
def toggle_payload_modal(n1, is_open, text, email_store):
    if n1:
        op=[]
        if(not is_open):
            op=get_payloads(text, email_store)
        return not is_open,op
    return is_open, []

# populate sample text in text box
@app.callback(
        Output("user-input", "value", allow_duplicate=True),
        Input("sample-text-button", "n_clicks"),
        prevent_initial_call=True
)
def populate_sample_text(n_clicks):
    if(n_clicks>0):
        return sample_from_file if len(sample_from_file)>0 else configs_dict['sample_text']

# save to email store
@app.callback(
    Output("email-store", "data", allow_duplicate=True),
    Output("email-modal", "is_open", allow_duplicate=True),
    Output("verification-alert-div", "children", allow_duplicate=True),
    Output("verify-email-button", "disabled"),
    Input("verify-email-button", "n_clicks"),
    State('url','href'),
    State("user-email", "value"),
    State("email-store", "data"),
    State("email-modal", "is_open"),
    prevent_initial_call=True
)
def save_email(n_clicks, href, email, store, is_open):
    if(n_clicks>0):
        email_v, ibmid, verified = verify_user(furl(href), email.strip().lower())
        store['email'] = email_v
        store['ibmid'] = ibmid
        store['verified'] = verified
        return store, not is_open if(verified) else is_open, dbc.Alert("Failed to verify email.", color="danger") if(not verified) else dbc.Alert("Email verified successfully.", color="success"), True if(verified) else False
    return store

# save to email store using upload file modal
@app.callback(
    Output("email-store", "data", allow_duplicate=True),
    Output("email-modal-upload", "is_open", allow_duplicate=True),
    Output("verification-alert-upload-div", "children", allow_duplicate=True),
    Output("verify-email-upload-button", "disabled"),
    Input("verify-email-upload-button", "n_clicks"),
    State('url','href'),
    State("user-email-upload", "value"),
    State("email-store", "data"),
    State("email-modal-upload", "is_open"),
    prevent_initial_call=True
)
def save_email(n_clicks, href, email, store, is_open):
    if(n_clicks>0):
        email_v, ibmid, verified = verify_user(furl(href), email.strip().lower())
        store['email'] = email_v
        store['ibmid'] = ibmid
        store['verified'] = verified
        return store, not is_open if(verified) else is_open, dbc.Alert("Failed to verify email.", color="danger") if(not verified) else dbc.Alert("Email verified successfully.", color="success"), True if(verified) else False
    return store


# main -- runs on localhost. change the port to run multiple apps on your machine
if __name__ == '__main__':
    SERVICE_PORT = os.getenv("SERVICE_PORT", default="8055")
    DEBUG_MODE = eval(os.getenv("DEBUG_MODE", default="True"))
    app.run(host="0.0.0.0", port=SERVICE_PORT, debug=DEBUG_MODE, dev_tools_hot_reload=False)
