# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
import pyodbc
import re

app = FastAPI()

def matches_any(word: str, table_names: list) -> bool:
    # Split the word into individual words
   words = word.lower().split(" ")  # Split the input into individual words
    
    # Check for exact word matches
   return any(w == table_name.lower() for table_name in table_names for w in words)
    

def search_word_and_compare_tables(word: str, table_names1, table_names2, table_names3, table_names4,table_names5):
    PROMPT = ""

    prompt1=f"""
    
 
Table Name: Business_Unit
Columns:
-ID: Integer, Primary Key, Auto-increment.
-Name: Varchar(250), Required, Unique.
-Is_Active: Bit, Required.
-Created_By: Varchar(50), Nullable.
-Created_On: Datetime, Nullable.
-Updated_By: Varchar(50), Nullable.
-Updated_On: Datetime, Nullable.
-Constraints:
-Primary Key on ID.
-Unique Constraint on Name (Note: There is a redundant unique constraint on Name).

Table Name: Desigination  
Columns:  
- ID: Integer, Primary Key, Auto-increment.  
- Name: Varchar(50), Required, Unique.  
- Is_Active: Bit, Required.  
- Created_By: Varchar(50), Nullable.  
- Created_On: Datetime, Nullable.  
- Updated_By: Varchar(50), Nullable.  
- Updated_On: Datetime, Nullable.  
- Unique Constraint on Name.


Table Name: Location
Columns:
ID: Integer, Primary Key, Auto-increment.
Name: Varchar(250), Required. The name of the location.
Is_Active: Bit, Required. Indicates if the location is active.
Created_By: Varchar(50), Nullable. The user who created the location.
Created_On: Datetime, Nullable. The date the location was created.
Updated_By: Varchar(50), Nullable. The user who last updated the location.
Updated_On: Datetime, Nullable. The date the location was last updated.
Constraints:
Primary Key: ID
Unique Key: Name



Table Name: Region
Column Details:
ID: int, Primary Key, Auto-increment.
Name: varchar(250), Not Null.
Is_Active: bit, Not Null.
Created_By: varchar(50), Nullable.
Created_On: datetime, Nullable.
Updated_By: varchar(50), Nullable.
Updated_On: datetime, Nullable.
Indexes:
Primary Key: ID (Clustered)


Table Name: Role
Column Details:
ID: int, Primary Key, Auto-increment.
Skill_Type_Id: int, Not Null.
Name: varchar(250), Not Null.
Is_Active: bit, Not Null.
Created_By: varchar(50), Nullable.
Created_On: datetime, Nullable.
Updated_By: varchar(50), Nullable.
Updated_On: datetime, Nullable.
Indexes:
Primary Key: ID (Clustered)
Unique Index: Name (Nonclustered)


Table Name: Employee
Columns:
Id: Integer, Primary Key, Auto-increment.
Employee_Code: Varchar(20), Required, Unique.
First_Name: Varchar(50), Required.
Middle_Name: Varchar(50), Nullable.
Last_Name: Varchar(50), Required.
Email: Varchar(50), Required, Unique.
Mobile_Number: Integer, Required, Unique.
Date_Of_Joining: Date, Required.
Total_Experience: Decimal(18, 2), Required.
ILink_Experience: Decimal(18, 2), Required.
Age: Integer, Nullable.
Designation_Id: Integer, Foreign Key to Desigination(ID), Required.
Role_Id: Integer, Foreign Key to Role(ID), Nullable.
BU_Id: Integer, Foreign Key to Business_Unit(ID), Nullable.
Location_Id: Integer, Foreign Key to Location(ID), Required.
Reporting_To_Id: Integer, Foreign Key to Employee(Id), Nullable.
Is_Active: Bit, Required.
Notice_Period: Bit, Nullable.
Last_Working_Date: Date, Nullable.
Current_Allocation_Status: Integer, Foreign Key to Allocation_Status(ID), Nullable.
Allocation_Percentage: Integer, Nullable.
Location_Type: Integer, Foreign Key to Location_Type(ID), Nullable.
Emp_Type: Integer, Foreign Key to Emp_Type(ID), Nullable.
Is_Bill: Bit, Nullable.
Unique Constraints:
Employee_Code
Email
Mobile_Number
Foreign Keys:
BU_Id to Business_Unit(ID)
Current_Allocation_Status to Allocation_Status(ID)
Designation_Id to Desigination(ID)
Emp_Type to Emp_Type(ID)
Location_Id to Location(ID)
Location_Type to Location_Type(ID)
Reporting_To_Id to Employee(Id)
Role_Id to Role(ID)


 
Table Name: Technology
Columns:
ID (int, Identity, Not Null)
Name (varchar(150), Not Null)
Is_Active (bit, Not Null)
Created_By (varchar(50), Nullable)
Created_On (datetime, Nullable)
Updated_By (varchar(50), Nullable)
Updated_On (datetime, Nullable)
Primary Key:ID
Unique Constraints:Name (Unique)

 """
    prompt2=f"""
    
Table Name: Servie
Column Details:
ID: int, Primary Key, Auto-increment.
Name: varchar(250), Not Null.
Is_Active: bit, Not Null.
Created_By: varchar(50), Nullable.
Created_On: datetime, Nullable.
Updated_By: varchar(50), Nullable.
Updated_On: datetime, Nullable.
Indexes:
Primary Key: ID (Clustered)


Table Name: Employee_Skills

Columns:
ID (int, PK): Unique record identifier.
Employee_Id (int, FK): Links to Employee table.
Skill_Category_ID (int, FK): Links to Skill_Category table.
Skill_Id1 (int, FK): Primary skill from Skills table.
Skill_Level_Id1 (int, FK): Proficiency level for Skill_Id1.
Skill_Id2 (int, FK, Nullable): Secondary skill from Skills.
Skill_Level_Id2 (int, FK, Nullable): Proficiency for Skill_Id2.
Skill_Code1 (varchar(20)): Code for primary skill.
Skill_Code2 (varchar(20), Nullable): Code for secondary skill.
Created_By (varchar(50), Nullable): Record creator.
Created_On (datetime, Nullable): Creation timestamp.
Updated_By (varchar(50), Nullable): Last updater.
Updated_On (datetime, Nullable): Last update timestamp.
Skill1Proficiency (decimal(8, 0), Nullable): Proficiency level for primary skill.
Is_Certified (bit, Nullable): Certification status.
Service_Id (int, FK, Nullable): Links to Service table.
Relationships
Employee_Id (FK)
References: Employee table (Id)
Skill_Category_ID (FK)
References: Skill_Category table (Id)
Skill_Id1 (FK)
References: Skills table (Id)
Skill_Level_Id1 (FK)
References: Skill_Level table (Id)
Skill_Id2 (FK, Nullable)
References: Skills table (Id)
Skill_Level_Id2 (FK, Nullable)
References: Skill_Level table (Id)


    Table Name: Employee
Columns:
Id: Integer, Primary Key, Auto-increment.
Employee_Code: Varchar(20), Required, Unique.
First_Name: Varchar(50), Required.
Middle_Name: Varchar(50), Nullable.
Last_Name: Varchar(50), Required.
Email: Varchar(50), Required, Unique.
Mobile_Number: Integer, Required, Unique.
Date_Of_Joining: Date, Required.
Total_Experience: Decimal(18, 2), Required.
ILink_Experience: Decimal(18, 2), Required.
Age: Integer, Nullable.
Designation_Id: Integer, Foreign Key to Desigination(ID), Required.
Role_Id: Integer, Foreign Key to Role(ID), Nullable.
BU_Id: Integer, Foreign Key to Business_Unit(ID), Nullable.
Location_Id: Integer, Foreign Key to Location(ID), Required.
Reporting_To_Id: Integer, Foreign Key to Employee(Id), Nullable.
Is_Active: Bit, Required.
Notice_Period: Bit, Nullable.
Last_Working_Date: Date, Nullable.
Current_Allocation_Status: Integer, Foreign Key to Allocation_Status(ID), Nullable.
Allocation_Percentage: Integer, Nullable.
Location_Type: Integer, Foreign Key to Location_Type(ID), Nullable.
Emp_Type: Integer, Foreign Key to Emp_Type(ID), Nullable.
Is_Bill: Bit, Nullable.
Unique Constraints:
Employee_Code
Email
Mobile_Number
Foreign Keys:
BU_Id to Business_Unit(ID)
Current_Allocation_Status to Allocation_Status(ID)
Designation_Id to Desigination(ID)
Emp_Type to Emp_Type(ID)
Location_Id to Location(ID)
Location_Type to Location_Type(ID)
Reporting_To_Id to Employee(Id)
Role_Id to Role(ID)


Table Name: Allocation_Status
    Columns:
    -ID: Integer, Primary Key, Auto-increment.
    -Label: Varchar(50), Required, Unique.
    -OrderWise: Integer, Required.
    -Is_Active: Bit, Required.
    Constraints:
    -Primary Key on ID.
    -Unique Constraint on Label.

 

 
 
Table Name: Employee_Type  
Columns:  
- ID: Integer, Primary Key, Auto-increment.  
- Label: Varchar(50), Required.  
- OrderWise: Integer, Required.  
- Is_Active: Bit, Required.
 
Table Name: Employee_Work_Type  
Columns:  
- ID: Integer, Primary Key, Auto-increment.  
- Label: Varchar(50), Required.  
- OrderWise: Integer, Required.  
- Is_Active: Bit, Required.
 


Table Name :Employee_Allocated_Project
columns: 
ID: Integer, Primary Key, Auto-increment.
Employee_Id: Integer, Foreign Key to Employee(Id), Required.
Allocation_Date: DateTime, Required. This indicates when the allocation started.
End_Date: DateTime, Required. This indicates when the allocation ends.
Job_Requirement_Id: Integer, Foreign Key to Job_Requirements(ID), Nullable.
Allocation_Percentage: Integer, Required. Percentage of time the employee is allocated to the project.
Is_Billable: Bit, Nullable. Indicates whether the allocation is billable.
Project_Id: Integer, Foreign Key to Project(ID), Nullable. References the associated project.
Created_By: Varchar(50), Nullable. The user who created the allocation record.
Created_On: DateTime, Nullable. The date and time when the allocation was created.
Updated_By: Varchar(50), Nullable. The user who last updated the allocation record.
Updated_On: DateTime, Nullable. The date and time when the allocation was last updated.
Emp_Type: Integer, Foreign Key to Emp_Type(ID), Nullable. Indicates the type of employee.
Job_Start_Date: Date, Nullable. The start date of the job requirement.
Emp_Alloc_Status: Integer, Foreign Key to Allocation_Status(ID), Nullable. Indicates the allocation status of the employee.
Additionally, the table includes the following constraints:
Primary Key on ID.
Foreign Keys on Emp_Alloc_Status (Allocation_Status(ID)), Emp_Type (Emp_Type(ID)), Employee_Id (Employee(Id)), Job_Requirement_Id (Job_Requirements(ID)), and Project_Id (Project(ID)).

  
Table Name: Job_Requirement_Allocation
Columns:
ID: Integer, Primary Key, Auto-increment.
Employee_Id: Integer, Foreign Key to Employee(Id), Nullable. Represents the employee allocated to the job requirement.
Job_Requirement_Id: Integer, Foreign Key to Job_Requirements(ID), Required. Represents the job requirement being allocated.
Allocation_Status_Id: Integer, Foreign Key to Allocation_Status(ID), Nullable. Represents the status of the allocation.
End_Date: Date, Nullable. The end date of the job allocation.
Created_By: Varchar(50), Nullable. The user who created the job requirement allocation record.
Created_On: DateTime, Nullable. The date and time the record was created.
Updated_By: Varchar(50), Nullable. The user who last updated the record.
Updated_On: DateTime, Nullable. The date and time when the record was last updated.
Allocation_Date: Date, Nullable. The date the employee was allocated to the job requirement.
JobStart_Date: Date, Nullable. The date the job started.
Is_External: Bit, Nullable. Indicates whether the job allocation is external.
Foreign Keys:
Employee_Id references Employee(Id).
Job_Requirement_Id references Job_Requirements(ID).
Allocation_Status_Id references Allocation_Status(ID).


Table Name: Project
Column Details:
ID: int, Primary Key, Auto-increment.
Name: varchar(250), Required, Unique.
Project_Code: varchar(100), Nullable.
Start_Date: date, Required.
End_Date: date, Required.
Description: text, Required.
Team_Size: int, Nullable.
Account_Id: int, Foreign Key to Accounts(Id), Required.
Project_Status_Id: int, Foreign Key to Project_Status(ID), Nullable.
Project_Manager_Id: int, Foreign Key to Employee(Id), Nullable.
Location_Id: int, Foreign Key to Location(ID), Nullable.
Created_By: varchar(50), Nullable.
Created_On: datetime, Nullable.
Updated_By: varchar(50), Nullable.
Updated_On: datetime, Nullable.
Service_Id: int, Foreign Key to Service(ID), Nullable.
Modified_By: int, Foreign Key to Employee(Id), Nullable.
Modified_On: datetime, Nullable.
Is_Active: bit, Nullable.
Is_Multiple_Invoice: bit, Nullable.


Table Name: Project_Status
Column Details:
ID: int, Primary Key, Auto-increment.
Label: varchar(50), Unique, Not Null.
OrderWise: int, Not Null.
Is_Active: bit, Not Null.
Indexes:
Primary Key: ID (Clustered)
Unique Nonclustered Index: Label
 

Table Name: Skill_Category
Columns:
Id (int, Identity, Not Null) - Primary Key
Label (varchar(50), Not Null) - Unique Label for the Skill Category
OrderWise (int, Not Null) - Integer for Sorting or Ordering
Is_Active (bit, Not Null) - Status Indicator for Activity
 
Table Name: Skill_Level
Columns:
ID (int, Identity, Not Null)
Label (varchar(150), Not Null)
OrderWise (int, Not Null)
Is_Active (bit, Not Null)
Primary Key: ID
Unique Index: Label

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
 
 Table Name: Project_Type
Column Details:
ID: int, Primary Key, Auto-increment.
Label: varchar(50), Not Null.
OrderWise: int, Not Null.
Is_Active: bit, Not Null.
Indexes:
Primary Key: ID (Clustered)



 


"""
    
    prompt3=f"""
Table Name: Opp_Status
Column Details:
ID: int, Primary Key, Auto-increment.
Label: varchar(50), Required.
OrderWise: int, Required.
Is_Active: bit, Required.
 

Table Name: Opportunity
Column Details:
ID: int, Primary Key, Auto-increment.
Region: int, Foreign Key to Region(ID), Required.
Opp_Code: varchar(50), Required.
Name: varchar(150), Required.
Account: varchar(100), Required.
Stage: int, Foreign Key to Stage_Probability(ID), Required.
Probability: int, Nullable.
Status: int, Foreign Key to Opp_Status(ID), Required.
Revenue: decimal(20, 2), Required.
Planned_Start_Date: date, Nullable.
Service_Line: int, Foreign Key to Service(ID), Nullable.
Is_Active: bit, Required.
Created_By: varchar(50), Nullable.
Created_On: datetime, Nullable.
Updated_By: varchar(50), Nullable.
Updated_On: datetime, Nullable
 

 Table Name: Region
Column Details:
ID: int, Primary Key, Auto-increment.
Name: varchar(250), Not Null.
Is_Active: bit, Not Null.
Created_By: varchar(50), Nullable.
Created_On: datetime, Nullable.
Updated_By: varchar(50), Nullable.
Updated_On: datetime, Nullable.
Indexes:
Primary Key: ID (Clustered)


Table Name: Servie
Column Details:
ID: int, Primary Key, Auto-increment.
Name: varchar(250), Not Null.
Is_Active: bit, Not Null.
Created_By: varchar(50), Nullable.
Created_On: datetime, Nullable.
Updated_By: varchar(50), Nullable.
Updated_On: datetime, Nullable.
Indexes:
Primary Key: ID (Clustered)


Table Name: Employee
Columns:
Id: Integer, Primary Key, Auto-increment.
Employee_Code: Varchar(20), Required, Unique.
First_Name: Varchar(50), Required.
Middle_Name: Varchar(50), Nullable.
Last_Name: Varchar(50), Required.
Email: Varchar(50), Required, Unique.
Mobile_Number: Integer, Required, Unique.
Date_Of_Joining: Date, Required.
Total_Experience: Decimal(18, 2), Required.
ILink_Experience: Decimal(18, 2), Required.
Age: Integer, Nullable.
Designation_Id: Integer, Foreign Key to Desigination(ID), Required.
Role_Id: Integer, Foreign Key to Role(ID), Nullable.
BU_Id: Integer, Foreign Key to Business_Unit(ID), Nullable.
Location_Id: Integer, Foreign Key to Location(ID), Required.
Reporting_To_Id: Integer, Foreign Key to Employee(Id), Nullable.
Is_Active: Bit, Required.
Notice_Period: Bit, Nullable.
Last_Working_Date: Date, Nullable.
Current_Allocation_Status: Integer, Foreign Key to Allocation_Status(ID), Nullable.
Allocation_Percentage: Integer, Nullable.
Location_Type: Integer, Foreign Key to Location_Type(ID), Nullable.
Emp_Type: Integer, Foreign Key to Emp_Type(ID), Nullable.
Is_Bill: Bit, Nullable.
Unique Constraints:
Employee_Code
Email
Mobile_Number
Foreign Keys:
BU_Id to Business_Unit(ID)
Current_Allocation_Status to Allocation_Status(ID)
Designation_Id to Desigination(ID)
Emp_Type to Emp_Type(ID)
Location_Id to Location(ID)
Location_Type to Location_Type(ID)
Reporting_To_Id to Employee(Id)
Role_Id to Role(ID)

Table Name: Stage_Probability
Columns:
ID (int, PK): Unique identifier for each record.
Stage (varchar(50), Nullable): Name of the stage.
Probability (int, Nullable): Probability percentage associated with the stage.
Created_By (varchar(50), Nullable): User who created the record.
Created_On (datetime, Nullable): Timestamp of record creation.
Updated_By (varchar(50), Nullable): User who last updated the record.
Updated_On (datetime, Nullable): Timestamp of last update.

"""
    prompt4=f"""

Table Name: Sow
Columns:
ID (int, Identity, Not Null)
Name (varchar(50), Not Null)
Opp_Id (int, Not Null)
Acc_Id (int, Nullable)
Project_Id (int, Nullable)
Project_Type (int, Nullable)
Value (bigint, Nullable)
Sow_Signed (bit, Not Null)
Signed_Date (datetime, Nullable)
Region_Id (int, Not Null)
Sow_Start_Date (date, Not Null)
Sow_End_Date (date, Not Null)
Project_Name (varchar(50), Nullable)
Acc_Name (varchar(50), Nullable)
Is_Active (bit, Nullable)
Created_By (varchar(50), Nullable)
Created_On (datetime, Nullable)
Updated_By (varchar(50), Nullable)
Updated_On (datetime, Nullable)
Primary Key: ID
Foreign Keys:
Acc_Id references Accounts (Id)
Opp_Id references Opportunity (ID)
Project_Id references Project (ID)
Project_Type references Project_Type (ID)
Region_Id references Region (ID)
 
Table Name: Accounts
     Columns:
    -Id: Integer, Primary Key, Auto-increment.
    -Name: Varchar(250), Required, Unique.
    -Is_Active: Bit, Required.
    -Created_By: Varchar(50), Nullable.
    -Created_On: Datetime, Nullable.
    -Updated_By: Varchar(50), Nullable.
    -Updated_On: Datetime, Nullable.
    -Primary Key on Id.
    -Unique Constraint on Name (Note: There is a redundant unique constraint on Name).


Table Name: Project
Column Details:
ID: int, Primary Key, Auto-increment.
Name: varchar(250), Required, Unique.
Project_Code: varchar(100), Nullable.
Start_Date: date, Required.
End_Date: date, Required.
Description: text, Required.
Team_Size: int, Nullable.
Account_Id: int, Foreign Key to Accounts(Id), Required.
Project_Status_Id: int, Foreign Key to Project_Status(ID), Nullable.
Project_Manager_Id: int, Foreign Key to Employee(Id), Nullable.
Location_Id: int, Foreign Key to Location(ID), Nullable.
Created_By: varchar(50), Nullable.
Created_On: datetime, Nullable.
Updated_By: varchar(50), Nullable.
Updated_On: datetime, Nullable.
Service_Id: int, Foreign Key to Service(ID), Nullable.
Modified_By: int, Foreign Key to Employee(Id), Nullable.
Modified_On: datetime, Nullable.
Is_Active: bit, Nullable.
Is_Multiple_Invoice: bit, Nullable.


Table Name: Region
Column Details:
ID: int, Primary Key, Auto-increment.
Name: varchar(250), Not Null.
Is_Active: bit, Not Null.
Created_By: varchar(50), Nullable.
Created_On: datetime, Nullable.
Updated_By: varchar(50), Nullable.
Updated_On: datetime, Nullable.
Indexes:
Primary Key: ID (Clustered)

 
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

 
 

"""
    
    prompt5=f"""

Table Name :Employee_Allocated_Project
columns: 
ID: Integer, Primary Key, Auto-increment.
Employee_Id: Integer, Foreign Key to Employee(Id), Required.
Allocation_Date: DateTime, Required. This indicates when the allocation started.
End_Date: DateTime, Required. This indicates when the allocation ends.
Job_Requirement_Id: Integer, Foreign Key to Job_Requirements(ID), Nullable.
Allocation_Percentage: Integer, Required. Percentage of time the employee is allocated to the project.
Is_Billable: Bit, Nullable. Indicates whether the allocation is billable.
Project_Id: Integer, Foreign Key to Project(ID), Nullable. References the associated project.
Created_By: Varchar(50), Nullable. The user who created the allocation record.
Created_On: DateTime, Nullable. The date and time when the allocation was created.
Updated_By: Varchar(50), Nullable. The user who last updated the allocation record.
Updated_On: DateTime, Nullable. The date and time when the allocation was last updated.
Emp_Type: Integer, Foreign Key to Emp_Type(ID), Nullable. Indicates the type of employee.
Job_Start_Date: Date, Nullable. The start date of the job requirement.
Emp_Alloc_Status: Integer, Foreign Key to Allocation_Status(ID), Nullable. Indicates the allocation status of the employee.
Additionally, the table includes the following constraints:
Primary Key on ID.
Foreign Keys on Emp_Alloc_Status (Allocation_Status(ID)), Emp_Type (Emp_Type(ID)), Employee_Id (Employee(Id)), Job_Requirement_Id (Job_Requirements(ID)), and Project_Id (Project(ID)).

Table Name: Service
Column Details:
ID: int, Primary Key, Auto-increment.
Name: varchar(250), Not Null.
Is_Active: bit, Not Null.
Created_By: varchar(50), Nullable.
Created_On: datetime, Nullable.
Updated_By: varchar(50), Nullable.
Updated_On: datetime, Nullable.
Indexes:
Primary Key: ID (Clustered)


  Table Name: Project_Status
Column Details:
ID: int, Primary Key, Auto-increment.
Label: varchar(50), Unique, Not Null.
OrderWise: int, Not Null.
Is_Active: bit, Not Null.
Indexes:
Primary Key: ID (Clustered)
Unique Nonclustered Index: Label


Table Name: Job_Requirement_Allocation
Columns:
ID: Integer, Primary Key, Auto-increment.
Employee_Id: Integer, Foreign Key to Employee(Id), Nullable. Represents the employee allocated to the job requirement.
Job_Requirement_Id: Integer, Foreign Key to Job_Requirements(ID), Required. Represents the job requirement being allocated.
Allocation_Status_Id: Integer, Foreign Key to Allocation_Status(ID), Nullable. Represents the status of the allocation.
End_Date: Date, Nullable. The end date of the job allocation.
Created_By: Varchar(50), Nullable. The user who created the job requirement allocation record.
Created_On: DateTime, Nullable. The date and time the record was created.
Updated_By: Varchar(50), Nullable. The user who last updated the record.
Updated_On: DateTime, Nullable. The date and time when the record was last updated.
Allocation_Date: Date, Nullable. The date the employee was allocated to the job requirement.
JobStart_Date: Date, Nullable. The date the job started.
Is_External: Bit, Nullable. Indicates whether the job allocation is external.
Foreign Keys:
Employee_Id references Employee(Id).
Job_Requirement_Id references Job_Requirements(ID).
Allocation_Status_Id references Allocation_Status(ID).



Table Name: project
Column Details:
ID: int, Primary Key, Auto-increment.
Name: varchar(250), Required, Unique.
Project_Code: varchar(100), Nullable.
Start_Date: date, Required.
End_Date: date, Required.
Description: text, Required.
Team_Size: int, Nullable.
Account_Id: int, Foreign Key to Accounts(Id), Required.
Project_Status_Id: int, Foreign Key to Project_Status(ID), Nullable.
Project_Manager_Id: int, Foreign Key to Employee(Id), Nullable.
Location_Id: int, Foreign Key to Location(ID), Nullable.
Created_By: varchar(50), Nullable.
Created_On: datetime, Nullable.
Updated_By: varchar(50), Nullable.
Updated_On: datetime, Nullable.
Service_Id: int, Foreign Key to Service(ID), Nullable.
Modified_By: int, Foreign Key to Employee(Id), Nullable.
Modified_On: datetime, Nullable.
Is_Active: bit, Nullable.
Is_Multiple_Invoice: bit, Nullable.

 
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



"""
    
   

     # Search for the word in each list of table names
    if matches_any(word, table_names1):
        return prompt1
    elif matches_any(word, table_names2):
        return  prompt2
    elif matches_any(word, table_names3):
        return  prompt3
    elif matches_any(word, table_names4):
        return prompt4
    elif matches_any(word, table_names5):
        return prompt5
    else:
        PROMPT = "No relevant table found."

   
        
        

@app.get("/getresponse/{User_Input}")
async def get_response(User_Input: str):
    # Define the prompt with dynamic user input
    table_names1 = [
    'Business Units',
    'Desigination',
    'Location',
    'Locations',
    'Region',
    'Regions',
    'Role',
    'Roles',
    'Technology',
    'Technologies',
    'BU',
    'employee type',
    'Employee Type',
    'Location Type',
    'Allocation Status',
    'Employees',
    'Employee'
]

    table_names2 = [
    'Job requirement',
    'job requirements',
    'job requirement allocation',
    'job requirement allocations',
    'Allocation',
    'Allocations',
    'employee allocation',
    'employee allocations',
    'pending allocation',
    'pending allocations',
    'employee skill',
    'employee skills',
    'skill',
    'skills',
    'Billable employee',
    'Billable employees',
    'Skill level',
    'employee work type',
    'skill type'
]
    
    table_names3 = [
    'Opportunity',
    'Opportunitites',
    'Stages',
    'Stage propability',
    'Stage propabilities',
    'Opportunity status',
    'Stage'
]
    
    table_names4 = [
    'Sow',
    'sow project',
    'projecttype',
    'Accounts',
    'Account',
    'Sow''s',
    'sow projects',
]
  
    table_names5 = [
    'Projects',
    'projectStatus',
    'project status',
    'service line',
    'project'
    'Services',
    'Service'
]
   
    pre=""
    result=search_word_and_compare_tables(User_Input, table_names1, table_names2, table_names3,table_names4,table_names5)
    
    prompt_content=f"""
   

    {result}
   
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
   
    return sql_query
    
   
    def is_db_related_query(sql_query: str) -> bool:
    # Simple keyword-based check for now. You can expand this as needed.
     db_related_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'FROM', 'JOIN', 'WHERE', '*', 'IS_ACTIVE',' ']
     return any(keyword in sql_query.upper() for keyword in db_related_keywords)
   
    if not is_db_related_query(User_Input):
        return {"response": "Sorry, I cannot process this request. Please check your question and try again."}
   
    return sql_query
 
    


@app.get("/generate-response/{user_question}/{Query_Result}")
async def generate_response(Query_Result: str, user_question: str):

    prompt_content1 = f"""
    You are given a question and an answer. Your task is to generate a human-readable response based on the provided information.
    You need to generate response based on {user_question} and  {Query_Result} , not an  Ai generated  {Query_Result}.
       
    Question: {user_question}
    Answer: {Query_Result}
    
    Response:    
   
    """


    client = Groq(api_key="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")
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
   
