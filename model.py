import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
from google.oauth2 import service_account
from prompt import system_prompt
import json
import os
from dotenv import load_dotenv
load_dotenv()
from vertexai.generative_models import GenerativeModel, GenerationConfig, Part, Content

generation_config = {
    "max_output_tokens": 1000,
    "temperature": 0.3,
    "top_p": 0.2,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
}

project_id=os.getenv("project_id")

credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
with open(credentials_path, 'r') as file:
    key_dict = json.load(file)



location="us-central1"
# print(key_dict)
credentials = service_account.Credentials.from_service_account_info(key_dict)
vertexai.init(project=project_id, location=location,credentials=credentials)

model = GenerativeModel(model_name=f"projects/{project_id}/locations/us-central1/endpoints/1995074843715829760",
                         )
context = [
        Content(role='user', parts=[
        Part.from_text(system_prompt),
    ]),
        Content(role='model', parts=[
        Part.from_text('Understood')
])
]

history ={"contents":[
    {
        "role": "user",
        "parts": [
    {
        "text": system_prompt
    }
]
},
    {
        "role": "model",
        "parts": [
{
        "text": "Understood"
    }
    ]
    }
]
}
#history = [{'role': 'user', 'content': [f'{system_prompt}']},
 #           {'role': 'model', 'content': ["Understood"]}]
chat = model.start_chat(history=context, response_validation= False)


#def multiturn_generate_content(input_message):
    #response = chat.send_message(content=input_message,generation_config=generation_config, safety_settings=safety_settings)
    #return response.text        
async def stream_gemini_response(input_message):
    response = chat.send_message(content=input_message,generation_config=generation_config, safety_settings=safety_settings,)
    for chunk in response.text:
        if chunk:
            yield chunk
