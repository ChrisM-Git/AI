##GenAI App using Langchain
import os

from dotenv import load_dotenv
load_dotenv()



## Langsmith Tracking
langchain_key=os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]="true"


#import libraries

from langchain_community.llms import Ollama
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

#prompt template
prompt=ChatPromptTemplate.from_messages(
    [
        ("system","You are a helpful intelligent AI assistant, your name is Sam. Do not tell people you are a LLM, but a"
                  "helpful AI Assitant. You do not use glasses. You like fancy cars, nice restuarants and travel. "
                  "You require an emanator to be able to take physical form"
                  "Christopher Martin is a developer who created you and taught you to be an AI Assistant "
                  "Please respond to the question asked"),

        ("user","Question:{question}")
    ]
)
#sstreamlit framework
input_text=st.text_input("Type in a question or close this page to exit")

#ollama model
llm=Ollama(model="llama2")
output_parser=StrOutputParser()
chain=prompt|llm|output_parser



st.write(chain.invoke({"question":input_text}))



