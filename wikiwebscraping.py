from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from bs4 import BeautifulSoup
from bs4.element import Tag
import requests
import bleach
from bleach import clean
import multiprocessing
import time
import warnings
import os
from bleach.css_sanitizer import CSSSanitizer
import tinycss2
import random
import pandas as pd
import json
# Consider validating the URL format before making requests
from urllib.parse import urlparse
from tabulate import tabulate as to_table

app = Flask(
    __name__,
    static_url_path="/static",
    static_folder='static',
    template_folder='template'  # Removed leading slash, assumed relative folder name
)

app.secret_key = "Alexander Oluwaseun Kwesi"

CORS(app)

list_, res_ = [0,1,2], ''

warnings.filterwarnings("ignore", category=UserWarning, message="resource_tracker:.*")


# Background worker function using semaphore
def worker(sem):
    print("Worker: Trying to acquire semaphore...")
    sem.acquire()
    print("Worker: Semaphore acquired.")
    time.sleep(2)  # Simulated work
    print("Worker: Releasing semaphore.")
    sem.release()
    print("Worker: Done.")
    


def is_valid_url(url):
    parsed = urlparse(url)
    return all([parsed.scheme in ['http', 'https'], parsed.netloc])


Dict, i, headers = {}, 0, []

#@app.route('/', methods=['POST'])
@app.route('/scrapes', methods=['POST'])
def scrapes():
    global list_
    if request.method == 'POST':

        data = request.get_json()
        url = data.get('url_')
        
        if not is_valid_url(url):
            return jsonify({
                "error": "Not a valid 'url_'"
            }), 400 
        elif is_valid_url(url):

        

            if not url:
                return jsonify({
                    "error": "Missing required field: 'url_'"
                }), 400

            try:
                
                #table_num = random.choice(list_)
                #print(table_num)
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                divs = soup.find_all('table')[0]  # Raise HTTPError for bad requests
                responses = [
                    str(tag).replace('\n', '').replace('[', '') if isinstance(tag, Tag) else str(tag).replace('\n', '').replace(']', '')
                        for tag in divs
                    ]
            
                
            # 1. Parse all table rows
                new_row = divs.find_all('tr')

                # 2. Define only the 7 columns you want
                columns_used = ['Rank', 'Name', 'Industry', 'Revenue(USD in Millions)', 'Revenue Growth', 'State Own', 'HeadQuarters']
                df = pd.DataFrame(columns=columns_used)

                # 3. Extract row data and ensure only 7 values are appended
                for col in new_row:
                    new_col = col.find_all("td")
                    new_data = [data.text.strip() for data in new_col]

                    if len(new_data) >= 7:  # Only proceed if there's enough data
                        row = new_data[:7]  # Trim to first 7 values
                        df.loc[len(df)] = row  # Append to the DataFrame

                # Drops the first and third columns
                #responses = df.get(columns_used)
                
                
                #df = [col.strip() for col in df.columns]  # remove extra spaces
                #json.dumps(df.to_dict(orient='records'))
                #print(json.dumps(df.to_dict(orient='records'), indent=2))
               
                #df_records = df.to_dict(orient='records', indent=4)  # Convert DataFrame to list of dictionaries (row-wise)

                #for i, row in enumerate(df_records, start=1):
                    #Dict[i] = row  # Store each row with index as key

                #for values_ in Dict.values():
                    #for key, value_ in values_.items():
                        #print(f'{key}\n{value_}')
                        #headers.append(key) 
                html = to_table(df, headers=columns_used, stralign='center', tablefmt="html")
                html = f"""
                                        <html>
                                        <head>
                                        <style>
                                        table {{
                                            width: 100%;
                                            border-collapse: collapse;
                                        }}
                                        th, td {{
                                            padding: 8px;
                                            text-align: center;
                                            border: 1px solid #ddd;
                                            min-width: 200px; /* 👈 Adjust this as needed */
                                        }}
                                        </style>
                                        </head>
                                        <body>
                                        {html}
                                        </body>
                                        </html>
                                        """
                return html
                #return html
                # Return the Dict as JSON
                #return JsonResponse(Dict)  # Django
                # OR, if you're using Flask:
                #responses = json.dumps(Dict)
                responses = json.dumps(headers, indent=2)
                #return Response(responses, content_type='application/json')
                #return jsonify({"responses": responses}), 200
                        #res_ = df.to_string(index=False)
                #response = df.to_html(table_id=1)



            except requests.exceptions.RequestException as e:
                return jsonify({
                    "error": f"Request failed: {str(e)}"
                }), 500


if __name__ == '__main__':
    # Use 'spawn' on platforms like Windows; 'fork' is okay on UNIX.
    if os.name != 'nt':
        multiprocessing.set_start_method("fork", force=True)

    sem = multiprocessing.Semaphore(1)
    process = multiprocessing.Process(target=worker, args=(sem,))
    process.start()
    process.join()

    app.run(debug=True, host='127.0.0.1', port=5000)





