##GenAI App using Langchain
import os
from dotenv import load_dotenv
load_dotenv()

## Langsmith Tracking
langchain_key=os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_PROJECT"]=os.getenv("LANGCHAIN_PROJECT")

#import libraries

from langchain_community.llms import Ollama
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

#prompt template
prompt=ChatPromptTemplate.from_messages(
    [
        ("system","You are a helpful AI assistant. Please respond to the question asked"),
        ("user","Question:{question}")
    ]
)
#sstreamlit framework

st.title("I'm Luna, your AI Assistant")

#ollama model
llm=Ollama(model="llama2")
output_parser=StrOutputParser()
chain=prompt|llm|output_parser

input_text=st.text_input("Type in a question or exit to stop")
st.write(chain.invoke({"question":input_text}))


