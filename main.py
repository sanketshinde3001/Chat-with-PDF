import openai
import streamlit as st
from dotenv import load_dotenv
import pickle
from PyPDF2 import PdfReader
from streamlit_extras.add_vertical_space import add_vertical_space
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import os

st.title(':card_file_box: PDF-GPT')

def main():
      st.header("Chat with PDF 💬")
      pdf = st.file_uploader("Upload your PDF", type='pdf')
      if pdf is not None:
         pdf_reader = PdfReader(pdf)
         text = ""
         for page in pdf_reader.pages:
            text += page.extract_text()
 
         text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
            )
         chunks = text_splitter.split_text(text=text)
         store_name = pdf.name[:-4]
         st.write(f'{store_name}')

         if os.path.exists(f"{store_name}.pkl"):
            with open(f"{store_name}.pkl", "rb") as f:
               VectorStore = pickle.load(f)

         else:
            embeddings = OpenAIEmbeddings()
            VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
            with open(f"{store_name}.pkl", "wb") as f:
               pickle.dump(VectorStore, f)
         
         query = st.text_input("Ask questions about your PDF file:")   
         if query:
            docs = VectorStore.similarity_search(query=query, k=3)
 
            llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
            chain = load_qa_chain(llm=llm, chain_type="stuff")
            with get_openai_callback() as cb:
               global response
               response = chain.run(input_documents=docs, question=query)
               print(cb)
               st.write(response)

with st.container():

    openai_api_key = st.text_input("OpenAI API Key", type="password")
    os.environ["OPENAI_API_KEY"]= openai_api_key
    openai.api_key = openai_api_key
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")   

    if __name__ == '__main__':
        main() 


