import os
import json
import calendar
import datetime
import torch
import pandas as pd
import openai
import language_tool_python
import speech_recognition as sr
#-----------------------------------------------------------------
from llama_index import SimpleDirectoryReader
from llama_index import VectorStoreIndex
from langchain.llms import OpenAI
from llama_index import LLMPredictor , PromptHelper , GPTVectorStoreIndex
from pandasai import PandasAI
from pandasai.llm import OpenAI
from transformers import T5Tokenizer, T5ForConditionalGeneration,T5Config
from better_profanity import profanity
from llama_hub.tools.text_to_image.base import TextToImageToolSpec
from llama_index.agent import OpenAIAgent
from transformers import pipeline
from tqdm import tqdm
from time import sleep
from gtts import gTTS
from pptx.util import Pt
from pptx.enum.text import PP_PARAGRAPH_ALIGNMENT
from ydata_profiling import ProfileReport
#-------------------------------------------------------------------------
#api key
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key
#-------------------------------------------------------------------------
#data 
document = SimpleDirectoryReader('data').load_data()
index = VectorStoreIndex.from_documents(document)
#-------------------------------------------------------------------------
# time and weather key words
time_intents = [
    "What time is it?","Do you have the time?","Could you tell me the time?","What's the current time?","Do you know what time it is?", "Could you give me the time?",
    "I need to know the time.","Is there a way to find out the time?","May I know the time, please?","Would you mind telling me the time?","I'm wondering what the time is.",
    "Is it possible to know the time right now?","Can you inform me of the current time?","Tell me the time, if you could.","I'd like to know the time, if that's okay.",
    "Do you happen to have the time?","Could you clue me in on the time?","Are you able to provide me with the time?","Can you give me the current time?",
    "I'm curious about the time.","Mind letting me know the time?","What's the time at the moment?","I'd appreciate if you could tell me the time.",
    "Can you share the time with me?","I want to find out the time.","Could you possibly tell me the time?", "What time do you have?","Would you let me know the time?",
    "I'm asking for the time, please.","Do you know what time it is right now?"
]
weather_intents = [
    "What's the weather like?","Can you tell me about the weather?", "How's the weather today?", "Could you inform me about the weather?",
    "Is there a weather update?","Do you have the current weather information?","What's the weather forecast?","What's the weather report?",
    "Could you give me a weather update?", "I'm curious about the weather.",  "Can you provide me with the weather details?", "Tell me about the weather conditions.",
    "I'd like to know the weather forecast.","Do you know what the weather will be like?","What can you tell me about the weather?",   "I'm wondering if you know the weather today.",
    "Can you share the weather forecast?","Would you mind telling me about the weather?","I want to find out the weather.","Do you happen to know the weather conditions?",
    "Can you give me the weather report?","What's the weather expected to be?","I'm interested in the weather today.", "Could you possibly give me the weather update?",
    "What's the forecast for the day?","Could you clue me in on the weather?","Are you able to provide me with the weather forecast?","Can you give me the weather outlook?",
    "I'd appreciate if you could tell me about the weather.", "Do you know what the weather is right now?","What's the weather prediction?",
    "Would you let me know about the weather?","I'm asking about the weather, please.", "Can you tell me the weather conditions?","How's the weather expected to be?",
    "Can you provide the weather information?","I'd like to get the weather forecast.", "Can you share the weather details?","What's the weather report for today?"
]
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
#llm predictor
os.environ["OPENAI_API_KEY"] = api_key

llm_predictor = LLMPredictor(llm=OpenAI( temperature=0.6 , model_name= 'text-davinci-003'))

max_input_size , num_outputs , max_chunk_overlap = 4096 , 256 , 0.20
prompt_helper = PromptHelper( max_input_size , num_outputs , max_chunk_overlap )

custom_llm_index = GPTVectorStoreIndex( document , llm_predictor= llm_predictor , prompt_helper= prompt_helper )
#-----------------------------------------------------------------------------
#class chatpot
class Chatbot:
    def _init_(self):
        self.index = index
        openai.api_key = api_key
        self.chat_history = []

    def generate_response(self, user_input):
        prompt = "\n".join([f"{message['role']}: {message['content']}" for message in self.chat_history[-5:]])
        prompt += f"\nUser: {user_input}"
        query_engine = custom_llm_index.as_query_engine()
        response = query_engine.query(user_input)

        message = {"role": "assistant", "content": response.response}
        self.chat_history.append({"role": "user", "content": user_input})
        self.chat_history.append(message)
        return message

    def load_chat_history(self, filename):
        try:
            with open(filename, 'r') as f:
                self.chat_history = json.load(f)
        except FileNotFoundError:
            pass

    def save_chat_history(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.chat_history, f)
#--------------------------------------------------------------------------
# initialize the pretrained model
model = T5ForConditionalGeneration.from_pretrained('t5-large')
tokenizer = T5Tokenizer.from_pretrained('t5-large')
device = torch.device('cpu')
#--------------------------------------------------------------------------
#summarization
def summary(prompt) -> str :
  preprocessed_text : str = prompt.strip().replace('\n','')
  t5_input_text : str = ' summarize:' + preprocessed_text
  tokenized_text = tokenizer.encode(t5_input_text, return_tensors='pt', max_length=512).to(device)
  summary_ids = model.generate(tokenized_text, min_length=30, max_length=120,num_beams=4,early_stopping=True)
  summary  : str = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
  return summary
  pass
#---------------------------------------------------------------------------
# prompot handling 
def prompt_handling(prompt) -> str :
  tool = language_tool_python.LanguageToolPublicAPI('en-US')
  text :str = tool.correct(prompt)
  return text
  pass
#---------------------------------------------------------------------------
#الشتايم
def bad_words_checker(text:str):
  censored = profanity.censor(text)
  return censored
#---------------------------------------------------------------------------
#time 
def show_time():
  now = datetime.datetime.now()
  print("note : the format is in year-month-day hour-minute-second.microsecond")
  return now
#---------------------------------------------------------------------------
# calender
def show_calendar():
  y = 2023
  m = 8
  print(calendar.month(y,m))
#---------------------------------------------------------------------------
# generation photos 
def generate_photo():
  openai.api_key = api_key
  tool_spec = TextToImageToolSpec()
  # OR
  tool_spec = TextToImageToolSpec(api_key=api_key)
  agent = OpenAIAgent.from_tools(tool_spec.to_tool_list())
  text=input(" what is a photo you need to generating : ")
  agent.chat(text)
#---------------------------------------------------------------------------
#continuation
def continuation(response):
  model = pipeline("text-generation", model="gpt2")
  generated_text = model(response['content'], max_length=70, num_return_sequences=1)[0]['generated_text']
  print(generated_text)
#---------------------------------------------------------------------------
#data_science
def data_science():
# Sample DataFrame
  path = input("send a path of your file ")
  df= os.path.realpath(path)
  data = pd.read_csv(df)
# path :str = '' # enter data path here
# df = pd.read_csv(path)
  llm = OpenAI(api_token= api_key)
  pandas_ai = PandasAI(llm,conversational=True)
# df = SmartDataframe(df, config={"llm": llm})
  prompt = str(input("enter your question or what do you want with the dataset.."))
  pandas_ai.run(df,prompt=prompt)
# df.chat(prompt)
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
#report

#---------------------------------------------------------------------------
def chat_bot(mas):
   
  # Swap out your index below for whatever knowledge base you want
  bot = Chatbot(api_key, custom_llm_index)
  bot.load_chat_history("chat_history.json")

  while True:
      prompt = mas
      text = bad_words_checker(prompt)
      user_input = prompt_handling(text)
      user_input = user_input.replace("*","")
     
      if user_input.casefold() in ['show calendar']:
        return(show_calendar())
        continue

      if user_input.casefold() in ['show time',time_intents]:
        return(show_time())
        continue

      if user_input.casefold() in ['summarize']:
        return("Titan: ",summary(response.get('content')))
        continue

      if user_input.lower() in ['generate photo']:
        return(generate_photo())
        continue

      if user_input.lower() in ['continue']:
        return(continuation(response))
        continue

      if user_input.lower() in ['data']:
        return(data_science())
        continue

      if user_input.casefold() in ["bye", "goodbye"]:
        return("Titan: Goodbye!")
        bot.save_chat_history("chat_history.json")
        break

      response = bot.generate_response(user_input)
      return(f"Titan: {response['content']}")
      return("______________ \n")
      tts = gTTS(str(response['content']))
      tts.save("output.mp3")
Chatbot()
from flask import Flask, render_template, request,jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return render_template("home.dart")

@app.route('/api', methods = ['GET'])

def get_bot_reponse():
    d = {}
    userText = request.args.get('msg')
    answer = str(chat_bot(userText))
    d['output'] = answer
    return d

if __name__ == "_main_":
    app.run(debug=True)