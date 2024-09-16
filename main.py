# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
import pyodbc
import re

app = FastAPI()


@app.get("/getresponse/{User_Input}")
async def get_response(User_Input: str):
    # Define the prompt with dynamic user input
    table_names1 = [
    'Accounts',
    'Business Unit',
    'Desigination',
    'Location',
    'Region',
    'Role',
    'Service',
    'Servie',
    'Technology'
]

    table_names2 = [
    'ocationStatus',
    'C2CCon',
    'C2CReq',
    'ConReq_Status',
    'Employee cert_Status',
    'Emp_Type',
    'Emp_Work_Type',
    'Employee',
    'EmployeeAllocatedProject',
    'EmployeeCertification',
    'JobRequirement Allocation',
    'ManagerStatus',
    'MaternityRequest'
]
    
    table_names3 = [
    'Opp_Status',
    'opportunity'
    'EarmarkHistory',
    'Opportunity',
    'Projects',
    'project'
    'ProjectCode',
    'ProjectStatus',
    'Project_Type',
    'SkillCategory',
    'SkillLevel',
    'SkillMap_AllSkills',
    'Sow',
    'Sow File',
    'Sow_Role',
    'Sow_Type',
    'Employee_Allocated_Project',
    'JobRequirement_Allocation',
    'JobRequirements',
    'Job_Status',
    'Level',
    'jobs',
    'jobrequirements',
    'joballocation',
    'JOBS'
]
    
    table_names4 = [
    'SkillType',
    'Skills',
    'Skill',
    'CertificationStatus',
    'Certification',
    'Employee Certification Status',
    'EmployeeType',
    'Emp_Work_Type',
    'Employee',
    'Employee_Certification',
    'Location_Type',
    'Match_Table',
    'Training_Details',
    'Training_Status'
]
    ##pre=""
    ##result=search_word_and_compare_tables(User_Input, table_names1, table_names2, table_names3,table_names4)

    prompt_content=f"""
   
    Table Name: Skill_Type
    Columns:
    - ID: Integer, Primary Key, Auto-increment.
    - Label: Varchar(150), Required, Unique.
    - OrderWise: Integer, Required.
    - Is_Active: Bit, Required.
    - Unique Constraint on Label.
 
    Table Name: Skills
    Columns:
    - ID: Integer, Primary Key, Auto-increment.
    - Name: Varchar(250), Required.
    - Is_Active: Bit, Required.
    - Skill_Type_ID: Integer, Foreign Key to Skill_Type(ID), Nullable.
    - Created_By: Varchar(50), Nullable.
    - Created_On: Datetime, Nullable.
    - Updated_By: Varchar(50), Nullable.
    - Updated_On: Datetime, Nullable.
    - Foreign Key on Skill_Type_ID to Skill_Type.

    
 
 
 
Table Name: Job_Status
Columns:
ID: Integer, Primary Key, Auto-increment.
Label: Varchar(50), Required. Descriptive label for the job status.
OrderWise: Integer, Required. The order or priority associated with the status.
Is_Active: Bit, Required. Indicates whether the status is active.
Constraints:
Primary Key: ID
Unique Key: Label (Unique non-clustered index on Label)
 
 
Table Name: Level
Columns:
ID: Integer, Primary Key, Auto-increment.
Label: Varchar(50), Required. Descriptive label for the level.
OrderWise: Integer, Required. The order or ranking associated with the level.
Is_Active: Bit, Required. Indicates if the level is active or not.
Constraints:
Primary Key: ID


 

Table Name: Project_Status
Column Details:
ID: int, Primary Key, Auto-increment.
Label: varchar(50), Unique, Not Null.
OrderWise: int, Not Null.
Is_Active: bit, Not Null.
Indexes:
Primary Key: ID (Clustered)
Unique Nonclustered Index: Label
 
Table Name: Project_Type
Column Details:
ID: int, Primary Key, Auto-increment.
Label: varchar(50), Not Null.
OrderWise: int, Not Null.
Is_Active: bit, Not Null.
Indexes:
Primary Key: ID (Clustered)


    
   
   Please provide the SQL SERVER query for the following request:
 
    {User_Input}
 
    The SQL SERVER query should be formatted as follows:
 
    ```sql
    <SQL_QUERY_HERE>
    ```
 
    """
 
    client = Groq(api_key="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")
   
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "provide me correct sql query"},
            {"role": "user", "content": prompt_content}
        ],
        temperature=0,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )
   
    response = ""
    for chunk in completion:
        if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
            content = chunk.choices[0].delta.content
            response += content or ""
        if chunk.choices[0].finish_reason == 'length':
            break
 
    # Regex pattern to find SQL code block
    pattern = r"```sql\n(SELECT .*?)\n```"
    match = re.search(pattern, response, re.DOTALL)
 
    if match:
        sql_query = match.group(1).strip()
    else:
        sql_query = ""
 
    
   
    def is_db_related_query(sql_query: str) -> bool:
    # Simple keyword-based check for now. You can expand this as needed.
     db_related_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'FROM', 'JOIN', 'WHERE', '*', 'IS_ACTIVE',' ']
     return any(keyword in sql_query.upper() for keyword in db_related_keywords)
   
    if not is_db_related_query(User_Input):
        return {"response": "Sorry, I cannot process this request. Please check your question and try again."}
   
 
    # Define the connection string for local SQL Server
    connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=tcp:omrpdb.database.windows.net,1433;"
    "DATABASE=OMRP;"
    "UID=suresh;"
    "PWD=Welcome@1;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

   
    # Execute the SQL query
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        answer = ", ".join([str(row) for row in rows])
    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=f"ODBC Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    finally:
        conn.close()
 
    # Generate final response based on user input and SQL query results
    prompt_content1 = f"""
    You are given a question and an answer. Your task is to generate a human-readable response based on the provided information.
 
    Question: {User_Input}
    Answer: {answer}
 
    Response:
    """
 
    completion1 = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "Give only the answer with respect to the question"},
            {"role": "user", "content": prompt_content1}
        ],
        temperature=0,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )
   
    response = ""
    for chunk in completion1:
        if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
            content = chunk.choices[0].delta.content
            response += content or ""
        if chunk.choices[0].finish_reason == 'length':
            break
 
    return {"response": response}
   "
    
