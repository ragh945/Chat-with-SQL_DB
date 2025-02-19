import streamlit as st
from PIL import Image
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
#rom langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import sqlite3

st.set_page_config(page_title="Chat with SQL DB", page_icon="🔗")
st.title("Talk2SQL: Natural Language Chat with Your Database")
image=Image.open("mysql.png")
st.image(image,use_container_width=False)

# Database options
local_db = "Use_Localdb"
mysql = "mysql"
radio_opt = ["Use SQLite 3 Database - Student.db", "Connect to your SQL Database"]
selected_opt = st.sidebar.radio(label="Choose the DB to chat with", options=radio_opt)

if radio_opt.index(selected_opt) == 1:
    db_uri = mysql
    mysql_host = st.sidebar.text_input("Provide MySQL Host", value="localhost")  # Default host
    mysql_port = st.sidebar.text_input("Provide MySQL Port", value="3306")  # Separate port
    mysql_user = st.sidebar.text_input("MySQL User")
    mysql_password = st.sidebar.text_input("MySQL Password", type="password")
    mysql_db = st.sidebar.text_input("MySQL Database")
else:
    db_uri = local_db

api_key = st.sidebar.text_input(label="Enter your API key",type="password")

if not api_key:
    st.info("Please add your API Key")

llm = ChatOpenAI(model="gpt-3.5-turbo")

@st.cache_resource(ttl="2h")
def configure(db_uri, mysql_host=None, mysql_port=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri == local_db:
        db_filepath = (Path(__file__).parent / "Student.db").absolute()
        creator = lambda: sqlite3.connect(f"file:{db_filepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite://", creator=creator))
    
    elif db_uri == mysql:
        if not (mysql_host and mysql_port and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details")
            st.stop()

        db_url = URL.create(
            drivername="mysql+mysqlconnector",
            username=mysql_user,
            password=mysql_password,
            host=mysql_host,
            port=int(mysql_port),  # Convert port to integer
            database=mysql_db
        )
        engine = create_engine(db_url)
        return SQLDatabase(engine)

if db_uri == mysql:
    db = configure(db_uri, mysql_host, mysql_port, mysql_user, mysql_password, mysql_db)
else:
    db = configure(db_uri)

# Toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# SQL Agent
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

# Chat history
if "messages" not in st.session_state or st.sidebar.button("Clear Chat History"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input
user_query = st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks=[streamlit_callback])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
