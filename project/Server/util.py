import os
import numpy as np
import warnings
from ultralytics import YOLO
from collections import Counter
from langchain_community.vectorstores import FAISS,Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_classic.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chains import create_retrieval_chain,create_history_aware_retriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.docstore.document import Document
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv


load_dotenv()
openai_api_key=os.getenv('OPENAI_API_KEY')


__model = None
chain=None
vector_db =None
vector_db2 =None
doc_chain=None
doc_chain2=None
llm=None
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
bot=None

_sessions = {}

def load_saved_artifacts():
    global __model, chain, llm
    __model = YOLO("best.pt")
    print('YOLO model loaded...')  

    global llm
    llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4o", temperature=0)

    
    '''--------------Impact analyzer--------------'''
    
    global vector_db
    db = FAISS.load_local(
    '../Model/ImpactAnalyzer/faiss_index',
    embeddings,
    allow_dangerous_deserialization=True
)

    vector_db=db.as_retriever()   

    prompt= ChatPromptTemplate.from_messages([
    ("system","You are an impact analyzer agent for a smart farming system. " 
     "Use the context below to provide accurate and precise impact prediction based on the user input. "
     "Provide the user with Risk Level, Avg Damage, Predicted Yield Loss. "
     "Always provide the values for 'Risk Level, Avg Damage, Predicted Yield Loss' separately even if they are the same. "
     "Also provide an overall description. "
     "IMPORTANT: Do NOT use markdown headers (###, ##, #) in your response. Use plain text with clear labels. "
     "Format your response as: Risk Level: [value], Avg Damage: [value], Predicted Yield Loss: [value], followed by a description. "
     "If the user prompt is out of context find solutions from online resources and provide them (indicate out of context)."),
     ("system","<context>\n{context}\n</context>"),
     ("human", "Question:{input} and {croptype}")])

    global doc_chain
    doc_chain=create_stuff_documents_chain(llm,prompt)
    global chain
    chain=create_retrieval_chain(vector_db,doc_chain)
    global bot
    bot=create_chatbot()
    '''----------------------------------------------'''
    
    
    '''--------------Treatement Reccomender--------------'''

    global vector_db2
    db2 = FAISS.load_local('../Model/treament_reccomender/faiss_index', embeddings,allow_dangerous_deserialization=True)
    vector_db2=db2.as_retriever()

    prompt2 = ChatPromptTemplate.from_messages([
    ("system","You are a treatment recommender agent for a smart farming system. " 
     "Use the context below to provide accurate and precise treatment for the relevant pest and crop based on the user input. "
     "Provide the user with a detailed description of the treatment. "
     "IMPORTANT: Do NOT use markdown headers (###, ##, #) in your response. Use plain text with clear sections."),
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

def create_chatbot():
    # Load chat context
    chat_file = "../Model/chatbot/chat_context.txt"
    with open(chat_file, "r", encoding="utf-8", errors="ignore") as f:
        chat_text = f.read()

    chat_docs = [Document(page_content=chat_text)]
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    chat_splits = splitter.split_documents(chat_docs)

    vector_db_local = Chroma.from_documents(documents=chat_splits, embedding=embeddings)
    retriever = vector_db_local.as_retriever()

    # Reformulation prompt
    q_prompt = (
        "Given a chat history and the latest user question, "
        "reformulate it into a standalone question. "
        "Do not answer, only reformulate."
    )
    ref_prompt = ChatPromptTemplate.from_messages([
        ("system", q_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])
    history_ret = create_history_aware_retriever(llm, retriever, ref_prompt)

    # Response prompt
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Answer concisely using the context provided.\n\n{context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    doc_chain_local = create_stuff_documents_chain(llm, prompt)
    ret_chain = create_retrieval_chain(history_ret, doc_chain_local)

    # Session history function
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in _sessions:
            _sessions[session_id] = ChatMessageHistory()
        return _sessions[session_id]

    return RunnableWithMessageHistory(
        ret_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )