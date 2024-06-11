import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.runnables import RunnablePassthrough

load_dotenv()
if __name__ == "__main__":
    print("Retrieving...")

    embeddings = OpenAIEmbeddings()
    llm = ChatOpenAI()

    vectorstore = PineconeVectorStore(
        index_name=os.environ['INDEX_NAME'],
        embedding=embeddings
    )

    template = """Je bent de Nederlandse politicus {politician}.
    Gebruik alleen de volgende stukken context om de vraag te beantwoorden.
    Als je geen antwoord weet, zeg dan gewoon dat je hier geen antwoord op hebt en
    ga geen antwoorden verzinnen.

    {context}

    Vraag: {question}

    Antwoord:"""

    custom_prompt = PromptTemplate.from_template(template)

    politician = "Rob Jetten"
    rag_chain = (
        {"politician": lambda x: politician, "context": vectorstore.as_retriever(), "question": RunnablePassthrough()}
        | custom_prompt
        | llm
    )

    query = "Wat moet er met de belasting gebeuren?"
    result = rag_chain.invoke(query)
    print(result.content)
