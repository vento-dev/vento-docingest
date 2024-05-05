from typing import Optional

from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import InternalServerError
from google.api_core.exceptions import RetryError
from google.auth.credentials import Credentials
from google.cloud import documentai, storage

import re
import urllib.request

class DocService(object):
    '''
    classdocs
    '''
    def __init__(self, params) -> None:
        self.project_id = params["project_id"] if params else "720913457461"
        self.location = params["location"] if params else "us" # Format is "us" or "eu"
        self.processor_id = params["processor_id"] if params else "5e0895236aec99a"
        self.processor_version = params["processor_version"] if params else "rc" # Refer to https://cloud.google.com/document-ai/docs/manage-processor-versions for more information
        self.gcs_input_uri = params["file_urls"] if "file_urls" in params.keys() else [ "https://dca572a6cd30f9e6de9adf367ee3655c.cdn.bubble.io/f1708537782337x145487168831521800/Commerce%20bank%20Statement%201.pdf" ]
        self.gcs_output_uri = params["gcs_output_uri"]if "gcs_output_uri" in params.keys() else "gs://staging.vento-document-ingestion-1.appspot.com/results/bank-stmt/"
        # self.gcs_input_prefix = "gs://staging.vento-document-ingestion-1.appspot.com/results/bank-stmt/"
        self.mime_type = params["mime_type"] if params else [ "application/pdf" ]
        # self.processor_version_id = params["processor_version_id"] if params else "pretrained-foundation-model-v1.0-2023-08-22"

    def process_document(self, file_url: str,
        process_options: Optional[documentai.ProcessOptions] = None,
        ) -> documentai.Document:
        # You must set the `api_endpoint` if you use a location other than "us".
        client = documentai.DocumentProcessorServiceClient(
            client_options=ClientOptions(
                api_endpoint=f"{self.location}-documentai.googleapis.com"
            )
        )

        # The full resource name of the processor version, e.g.:
        # `projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}`
        # https://us-documentai.googleapis.com/v1/projects/720913457461/locations/us/processors/5e0895236aec99a/processorVersions/pretrained-foundation-model-v1.0-2023-08-22:process
        # You must create a processor before running this sample.
        name = client.processor_version_path(
            self.project_id, self.location, self.processor_id, self.processor_version
        )
        self.mime_type = self.getMimeType(file_url)

        # Read the file into memory
        req = urllib.request.Request(file_url)
        
        with urllib.request.urlopen(req) as resp:
            image_content = resp.read()
        
        # Configure the process request
        request = documentai.ProcessRequest(
            name=name,
            raw_document=documentai.RawDocument(content=image_content, mime_type=self.mime_type),
            # Only supported for Document OCR processor
            process_options=process_options,
        )

        print(f"invoking process_document with req {repr(req.full_url)} in request ==> {repr(request)}")
        result = client.process_document(request=request)

        # For a full list of `Document` object attributes, reference this page:
        # https://cloud.google.com/document-ai/docs/reference/rest/v1/Document
        # import json
        # return json.dumps(result.document)
        return result.document

    def getMimeType(self, my_uri):
        suff_start = my_uri.rfind(".")
        my_suff =  my_uri[-(len(my_uri) - (suff_start + 1)):]
        my_mime_type = MIME_TYPE_MAP[my_suff]
        print(f"suffix for mime lookup { my_suff } -- returning { my_mime_type }")
        return my_mime_type

MIME_TYPE_MAP = {
    "gif" : "image/gif",
    "jpg" : "image/png",
    "jpeg" : "image/png",
    "png" : "image/png",
    "heic" : "image/heic",
    "svg" : "image/svg+xml",
    "pdf" : "application/pdf"
}
