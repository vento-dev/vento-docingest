from mimetypes import MimeTypes
from flask import Flask, render_template, request, jsonify

import time, json
import os

from com.services.docIngest.doc_service import DocService
from com.services.docIngest.goog_llm import GoogleLLMModel

'''
Created on Feb 23, 2024
s
@author: john_
'''

app = Flask(__name__, template_folder='templates')

@app.route('/')
@app.route('/hello')
@app.route('/hello/<user>')
def hello(user=None):
    user = user or 'Shalabh'
    return render_template('hello.html', user=user)

@app.route('/doc_ingest_test')
def doc_ingest_test():
    docService = DocService([])
    document = docService.process_document(*CLIENT_INIT_DATA)
    return render_template("docresult.html", result = document.entities)


@app.route('/bank_stmt_ingest')
def bank_stmt_ingest():
    my_args = request.args.to_dict(flat=False)
    print(f"full req is { repr(request) }")
    for key in my_args:
        print(f"Bank Stmt API Call key { key }, value { my_args[key] }")
    doc_locs = _get_doc_locs(my_args)
    docService = DocService(CLIENT_INIT_DATA)
    docService.processor_id = "5e0895236aec99a"
    doc_results = _extract_doc_results(doc_locs, docService)
    # return render_template("docresult.html", result=doc_results)
    return jsonify(_prep4json(doc_results))
    
"""745d893047e6ddee processor_id for ID docs AKA vento-dl-proceswor-2"""
@app.route('/id_doc_ingest')
def id_doc_ingest():
    my_args = request.args.to_dict(flat=False)
    doc_locs = _get_doc_locs(my_args)
    docService = DocService(CLIENT_INIT_DATA)
    docService.processor_id = "745d893047e6ddee"
    '''https://us-documentai.googleapis.com/v1/projects/720913457461/locations/us/processors/745d893047e6ddee/processorVersions/pretrained-foundation-model-v1.0-2023-08-22:process'''
    doc_results = _extract_doc_results(doc_locs, docService)
    # return render_template("dl_result.html", result=doc_results)
    return jsonify(_prep4json(doc_results))

"""d43f290379996510 processor_id for US Passport"""
@app.route('/us_passport_ingest')
def us_passport_ingest():
    my_args = request.args.to_dict(flat=False)
    doc_locs = _get_doc_locs(my_args)
    docService = DocService(CLIENT_INIT_DATA)
    docService.processor_id = "d43f290379996510"
    doc_results = _extract_doc_results(doc_locs, docService)
    return jsonify(_prep4json(doc_results))
    # return render_template("dl_result.html", result=doc_results)

"""217bd0b2061fba2b processor_id for US Tax docs"""
@app.route('/tax_doc_ingest')
def tax_doc_ingest():
    #TODO adapt to patterns
    my_args = request.args.to_dict(flat=False)
    urllib.parse.urlencode
    docpaths = my_args['docpath']
    #TODO Security ALERT
    doc_locs = _get_doc_locs(my_args)
    docService = DocService(CLIENT_INIT_DATA)
    docService.processor_id = "217bd0b2061fba2b"
    doc_results = _extract_doc_results(doc_locs, docService)
    return jsonify(_prep4json(doc_results))
    # return render_template("docresult.html", result=doc_results)
  
@app.route('/google_llm_process')  
def google_llm_process():
    my_args = request.args.to_dict(flat=False)
    doc_locs = _get_doc_locs(my_args)
    input_docs = [doc_loc.replace(' ', '%20') for doc_loc in doc_locs]
    for doc in input_docs:
        print(f"found doc uri { doc } in input")
    doc_results = {}
    start = time.time()
    docpaths = json.dumps(my_args['docpath'][0])
    print(f"feeding data to LLM ==> {docpaths}")
    llmService = GoogleLLMModel({"project_id":"720913457461", "model_name":"text-bison@001", "location" : "us-central1" })
    llm_response = llmService.predict_large_language_model_sample(0.2, 256, 0.8, 40,
                                    #'''provide html from following data [{'fileUrl': 'https:\\/\\/dca572a6cd30f9e6de9adf367ee3655c.cdn.bubble.io/f1714062562716x559275462956352100/Driverslic.jpg', 'address': '20 TAMARISK MORAGA, CA 94556', 'height': '5-11', 'surname': 'BERTOT', 'weight': '267 lb', 'haircolor': 'BLK', 'sex': 'M', 'firstname': 'GABRIEL', 'dln': 'F7463304', 'rest': 'CORR LENS', 'eyecolor': 'BRN', 'dob': '11/22/1970', 'end': 'NONE', 'expiration': '11\/22\/2028', 'class': 'C', 'issuedate': '11\/07\/2023'}] ''',
                                    f"{LLM_REQUEST} {docpaths}"
                                    )
    endtime = time.time()
    return llm_response.text.replace("`", "").replace("html", "")
    

def _extract_doc_results(doc_locs, docService):
    input_docs = [doc_loc.replace(' ', '%20') for doc_loc in doc_locs]
    for doc in input_docs:
        print(f"found doc uri { doc } in input")
    doc_results = {}
    start = time.time()
    for doc_uri in input_docs:
        document = docService.process_document(file_url = doc_uri)
        doc_results[doc_uri] = document
    endtime = time.time()
    print(f"API calls took { endtime - start } seconds to complete")
    show_extracted_data(doc_results)
    return doc_results

def _get_doc_locs(url_args):
    if 'docpath' not in url_args:
        return url_args
    docpaths = url_args['docpath']
    return [docpath if docpath.startswith("http") else "https://" + docpath.replace("//", "") for docpath in docpaths]

""" Take dict of results - key is processed document, value is DocumentAI result
    and creates a similarly structured dict whose values are an array of extracted key-value pairs
"""
def _prep4json(res_dict):
    package = []
    for doc_url in res_dict:
        prepped = {}
        # prepped["fileUrl"] = doc_url
        for ent in res_dict[doc_url].entities:
            print(f"Retrieved Entities { repr(ent)} ")
            prepped[ent.type] = ent.mention_text
        package.append(prepped)
    return package

def show_extracted_data(doc_results):
    # if not app.debug:
    #     return
    nu_doc_results = _prep4json(doc_results)
    j_results = json.dumps(nu_doc_results)
    print(f"JSON RESULTS     { j_results }")
    
    """If we want each field in a list in log"""
    # for doc_uri in doc_result:
    #     for ent in doc_result[doc_uri].entities:
    #         print(f"EXTRACTED    {ent.type}    {ent.mention_text}    {ent.confidence}")

CLIENT_INIT_DATA = {
    "project_id" : "720913457461",
    "location" : "us",
    "processor_id" : "745d893047e6ddee",
    "processor_version" : "rc",
    "gcs_output_uri" : "gs://staging.vento-document-ingestion-1.appspot.com/results/bank-stmt/",
    "mime_type" : "application/pdf",
    "processor_version_id" : "pretrained-foundation-model-v1.0-2023-08-22"
}

LLM_REQUEST = '''extract data from following image and show in human readable '''
PROJECT_ID = ""
if __name__ == "__main__":
    
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    app.run(host='0.0.0.0', port=4444, debug=True)
    
    