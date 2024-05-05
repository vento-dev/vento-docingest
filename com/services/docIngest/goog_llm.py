import vertexai
from vertexai.preview.language_models import TextGenerationModel


class GoogleLLMModel(object):
    
    def __init__(self, params) -> None:
        vertexai.init(project="720913457461", location="us-central1")
        self.project_id = params["project_id"] if "project_id" in params else "720913457461"
        self.model_name = params["model_name"] if "model_name" in params else "text-bison@001"
        self.location = params["location"] if "location" in params else "us-central1"
        self.tuned_model_name = params["tuned_model_name"] if "tuned_model_name" in params else ""
        self.mime_type = params["mime_type"] if "mime_type" in params else [ "application/pdf" ]
    
    def predict_large_language_model_sample(
        self,
        temperature: float,
        max_decode_steps: int,
        top_p: float,
        top_k: int,
        content: str
        ) :
        """Predict using a Large Language Model."""
        vertexai.init(project=self.project_id, location=self.location)
        model = TextGenerationModel.from_pretrained(self.model_name)
        if self.tuned_model_name:
            model = model.get_tuned_model(self.tuned_model_name)
        response = model.predict(
            content,
            temperature=temperature,
            max_output_tokens=max_decode_steps,
            top_k=top_k,
            top_p=top_p,)
        print(f"Response from Model: {response.text}")
        return response
 
        
            
if __name__ == "__main__":
    llmModel = GoogleLLMModel({"project_id":"720913457461", "model_name":"text-bison@001", "location" : "us-central1" })
    llmModel.predict_large_language_model_sample(0.2, 256, 0.8, 40,
                                    #'''Give me ten interview questions for the role of program manager 
                                    '''provide readable html from following data [{"fileUrl":"https://dca572a6cd30f9e6de9adf367ee3655c.cdn.bubble.io/f1714062562716x559275462956352100/Driverslic.jpg", "address": "20 TAMARISK MORAGA, CA 94556", "height": "5-11", "surname": "BERTOT", "weight": "267 lb", "haircolor": "BLK", "sex": "M", "firstname": "GABRIEL", "dln": "F7463304", "rest": "CORR LENS", "eyecolor": "BRN", "dob": "11/22/1970", "end": "NONE", "expiration": "11/22/2028", "class": "C", "issuedate": "11/07/2023"}] ''',
                                    # location = "us-central1"
                                    )

