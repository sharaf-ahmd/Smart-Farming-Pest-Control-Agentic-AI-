import os
import numpy as np
import warnings
from ultralytics import YOLO
from collections import Counter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

from dotenv import load_dotenv


load_dotenv()
groq_api_key=os.getenv('GROQ_API_KEY')


__model = None
chain=None
vector_db =None
vector_db2 =None
doc_chain=None
doc_chain2=None
llm=None
embeddings = OllamaEmbeddings(model="nomic-embed-text")


def load_saved_artifacts():
    global __model
    __model = YOLO("best.pt")
    print('loading complete....')  

    global llm
    llm = ChatGroq(api_key=groq_api_key,model="Gemma2-9b-It")

    
    '''--------------Impact analyzer--------------'''
    
    global vector_db
    db = FAISS.load_local('../Model/ImpactAnalyzer/faiss_index', embeddings,allow_dangerous_deserialization=True)
    vector_db=db.as_retriever()   

    prompt= ChatPromptTemplate.from_messages([
    ("system","You are an impact analyzer agent for a smart farming system," 
     "use the context below to provide accurate and precise impact prediction based on the user input."
     "provide the user with Risk Level, Avg Damage, Predicted Yield Loss."
     "always provide the values for 'Risk Level, Avg Damage, Predicted Yield Loss' seperateley even if they are the same."
     "also provide an overall description"
     "if the user propmt is out of context find solutions from online resources and provide them(indicate out of context)"),
     ("system","<context>\n{context}\n</context>"),
     ("human", "Question:{input} and {croptype}")])

    global doc_chain
    doc_chain=create_stuff_documents_chain(llm,prompt)
    global chain
    chain=create_retrieval_chain(vector_db,doc_chain)

    '''----------------------------------------------'''
    
    
    '''--------------Treatement Reccomender--------------'''

    global vector_db2
    db2 = FAISS.load_local('../Model/treament_reccomender/faiss_index', embeddings,allow_dangerous_deserialization=True)
    vector_db2=db2.as_retriever()

    prompt2 = ChatPromptTemplate.from_messages([
    ("system","You are an Treatement reccomender agent for a smart farming system," 
     "use the context below to provide accurate and precise treatement for the relevant pest and crop on the user input."
     "provide the user with a detailed description of the treatment."),
     ("system","<context>\n{context}\n</context>"),
     ("human", "Question:{input} and {croptype}")
])
    
    global doc_chain2
    doc_chain2=create_stuff_documents_chain(llm,prompt2)
    global chain2
    chain2=create_retrieval_chain(vector_db2,doc_chain2)

    '''--------------------------------------------'''


def get_prediction(img):
    if __model is None:
        raise Exception("Model not loaded. Call load_saved_artifacts() first.")

    results = __model.predict(img, imgsz=640, conf=0.25)[0]  # first (and only) image
    labels = []

    # collect all detected pest names
    for box in results.boxes:
        cls_id = int(box.cls[0])
        label = results.names[cls_id]
        labels.append(label)

    # count how many of each pest
    pest_counts = dict(Counter(labels))
    return pest_counts


def analyze(pest:str, crop:str):
    if chain is None:
        raise Exception("Chain not loaded. Call load_saved_artifacts() first.")
    result = chain.invoke({"input": pest, "croptype": crop})
    return result['answer']


def reccomend(pest:str, crop:str):
    if chain2 is None:
        raise Exception("Chain not loaded. Call load_saved_artifacts() first.")
    result = chain2.invoke({"input": pest, "croptype": crop})
    return result['answer']