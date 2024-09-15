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
    

def search_word_and_compare_tables(word: str, table_names1, table_names2, table_names3, table_names4):
    PROMPT = ""

    prompt1=f"""
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

Table Name: Service_Skill
Column Details:
ID: int, Primary Key, Auto-increment.
Skill_Id: int, Not Null. References Skill(ID).
Service_Id: int, Not Null. References Servie(ID).
Emp_Id: int, Nullable. References Employee(Id).
Acc_Id: int, Nullable. References Accounts(Id).
Project_Id: int, Nullable. References Project(ID).
Region_Id: int, Nullable. References Region(ID).
Allocation_Percentage: varchar(50), Nullable.
Service_Id2: int, Nullable. References Servie(ID).
Created_By: varchar(50), Nullable.
Created_On: datetime, Nullable.
Updated_By: varchar(50), Nullable.
Updated_On: datetime, Nullable.
Indexes:
Primary Key: ID (Clustered)
Foreign Keys:
Acc_Id references Accounts(Id)
Emp_Id references Employee(Id)
Project_Id references Project(ID)
Region_Id references Region(ID)
Service_Id references Servie(ID)
Service_Id2 references Servie(ID)
Skill_Id references Skill(ID)


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
    
Table Name: Allocation_Status
    Columns:
    -ID: Integer, Primary Key, Auto-increment.
    -Label: Varchar(50), Required, Unique.
    -OrderWise: Integer, Required.
    -Is_Active: Bit, Required.
    Constraints:
    -Primary Key on ID.
    -Unique Constraint on Label.
 
 
Table Name: C2C_Con  
Columns:  
- Id: Integer, Primary Key, Auto-increment.  
- Emp_Code: Varchar(50), Required, Unique.  
- Start_Date: Date, Required.  
- Con_End_Date: Date, Required.  
- Is_Bill: Bit, Required.  
- Emp_Type: Integer, Foreign Key to Emp_Work_Type(ID), Nullable.  
- Pat_Comp: Varchar(150), Nullable.  
- Bill_Rate: Bigint, Nullable.  
- Created_By: Varchar(50), Nullable.  
- Created_On: Datetime, Nullable.  
- Updated_By: Varchar(50), Nullable.  
- Updated_On: Datetime, Nullable.  
- Unique Constraint on Emp_Code.
 
 
Table Name: C2C_Req  
Columns:  
- Id: Integer, Foreign Key to C2C_Con(Id), Required.  
- Reason: Varchar(500), Required.  
- Mod_By: Integer, Foreign Key to Employee(Id), Nullable.  
- Mod_On: Date, Nullable.  
- Mod_Ext_Date: Date, Required.  
- Is_Mod_Bill: Bit, Required.  
- C2C_Req_Status: Integer, Foreign Key to Con_Req_Status(ID), Required.  
- Created_By: Varchar(50), Nullable.  
- Created_On: Datetime, Nullable.  
- Updated_By: Varchar(50), Nullable.  
- Updated_On: Datetime, Nullable.  
- Foreign Keys:  
  - C2C_Req_Status to Con_Req_Status(ID).  
  - Id to C2C_Con(Id).  
  - Mod_By to Employee(Id).


Table Name: Con_Req_Status  
Columns:  
- ID: Integer, Primary Key, Auto-increment.  
- Label: Varchar(50), Required.  
- OrderWise: Integer, Required.  
- Is_Active: Bit, Required.
 

 Table Name: Emp_Cert_Status  
Columns:  
- ID: Integer, Primary Key, Auto-increment.  
- Label: Varchar(50), Required.  
- OrderWise: Integer, Required.  
- Is_Active: Bit, Required.
 
 
Table Name: Emp_Type  
Columns:  
- ID: Integer, Primary Key, Auto-increment.  
- Label: Varchar(50), Required.  
- OrderWise: Integer, Required.  
- Is_Active: Bit, Required.
 
Table Name: Emp_Work_Type  
Columns:  
- ID: Integer, Primary Key, Auto-increment.  
- Label: Varchar(50), Required.  
- OrderWise: Integer, Required.  
- Is_Active: Bit, Required.
 
 
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

 
Table Name: Employee_Certification
Columns:
ID: Integer, Primary Key, Auto-increment.
Certificate_Id: Integer, Foreign Key to Certification(ID), Required.
Created_By: Varchar(50), Nullable. The user who created the certification record.
Created_On: DateTime, Nullable. The date and time when the record was created.
Updated_By: Varchar(50), Nullable. The user who last updated the record.
Updated_On: DateTime, Nullable. The date and time when the record was last updated.
Certification_End_Date: Date, Nullable. The end date of the certification.
Date_Of_Certification: Date, Required. The date the certification was awarded.
LevelId: Integer, Foreign Key to Level(ID), Nullable. Represents the level of the certification.
Location_Id: Integer, Foreign Key to Location(ID), Nullable. Represents the location where the certification was awarded.
Emp_Certification_StatusId: Integer, Foreign Key to Emp_Cert_Status(ID), Required. Represents the status of the employee certification.
Emp_Id: Integer, Foreign Key to Employee(Id), Required. References the employee who holds the certification.
Foreign Keys:
Certificate_Id references Certification(ID).
Emp_Certification_StatusId references Emp_Cert_Status(ID).
Emp_Id references Employee(Id).
LevelId references Level(ID).
Location_Id references Location(ID).
 
 
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


Table Name: Manager_Status
Columns:
ID: Integer, Primary Key, Auto-increment.
Label: Varchar(50), Required. Descriptive label for the manager status.
OrderWise: Integer, Required. Defines the order or ranking for the manager status.
Is_Active: Bit, Required. Indicates if the manager status is active.
Constraints:
Primary Key: ID


Table Name: MaternityRequest
Column Details:
ID: int, Primary Key, Auto-increment.
Emp_Code: varchar(50), Required.
Request_Date: date, Required.
Reason: varchar(250), Required.
Modified_By: int, Nullable, Foreign Key to Employee(Id).
Modified_On: date, Nullable.
Manager_Status: int, Required, Foreign Key to Manager_Status(ID).
Created_By: varchar(50), Nullable.
Created_On: datetime, Nullable.
Updated_By: varchar(50), Nullable.
Updated_On: datetime, Nullable.
Foreign Key References:
Manager_Status references Manager_Status(ID).
Modified_By references Employee(Id).
ID references Employee(Id) (This might be incorrect; usually, a different column would be used for this reference).

"""
    
    prompt3=f"""
Table Name: Opp_Status
Column Details:
ID: int, Primary Key, Auto-increment.
Label: varchar(50), Required.
OrderWise: int, Required.
Is_Active: bit, Required.
 
Table Name: Earmark_History  
Columns:  
- ID: Integer, Primary Key, Auto-increment.  
- Emp_Id: Integer, Foreign Key to Employee(Id), Required.  
- Job_Id: Integer, Foreign Key to Job_Requirements(ID), Nullable.  
- ClientInterview: Bit, Nullable.  
- ClientName: Varchar(50), Nullable.  
- L1Interview: Varchar(50), Nullable.  
- IsL1Selected: Bit, Nullable.  
- L1Reason: Varchar(50), Nullable.  
- L2Interview: Varchar(50), Nullable.  
- IsL2Selected: Bit, Nullable.  
- L2Reason: Varchar(50), Nullable.  
- Created_By: Varchar(50), Nullable.  
- Created_On: Datetime, Nullable.  
- Updated_By: Varchar(50), Nullable.  
- Updated_On: Datetime, Nullable.  
- Foreign Keys:  
  - Emp_Id to Employee(Id).  
  - Job_Id to Job_Requirements(ID).

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
 
 
Table Name: Project_Code
Column Details:
ID: int, Primary Key, Auto-increment.
Job_Id: int, Foreign Key to Job_Requirements(ID), Nullable.
Skill_Id: int, Foreign Key to Job_Requirements(ID), Nullable.
Skill_Category_ID: int, Foreign Key to Skill_Category(Id), Nullable.
Experience: int, Nullable.
Skill_Level_ID: int, Foreign Key to Skill_Level(ID), Nullable.
Skil_Type_Id: int, Foreign Key to Skill_Type(ID), Nullable.
Created_By: varchar(50), Nullable.
Created_On: datetime, Nullable.
Updated_By: varchar(50), Nullable.
Updated_On: datetime, Nullable.
 
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
 
 
Table Name: Skill_Map_AllSkills
Columns:
ID (int, Identity, Not Null)
Job_Code (varchar(50), Nullable)
Emp_Id (int, Nullable)
Created_By (varchar(50), Nullable)
Created_On (datetime, Nullable)
Updated_By (varchar(50), Nullable)
Updated_On (datetime, Nullable)
Primary Key: ID
Foreign Key: Emp_Id references Employee (Id)
 

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
 
 
Table Name: Sow_File
Columns:
ID (int, Identity, Not Null)
File_Data (binary(1), Nullable)
File_Extension (varchar(50), Nullable)
Created_By (varchar(50), Nullable)
Created_On (datetime, Nullable)
Updated_By (varchar(50), Nullable)
Updated_On (datetime, Nullable)
Primary Key:ID
Foreign Key:Sow_ID (int, Nullable) references Sow (ID)
 
Table Name: Sow_Role
Columns:
ID (int, Identity, Not Null)
Sow_Id (int, Nullable)
Position (decimal(8, 0), Nullable)
Role (varchar(50), Nullable)
Billing_Rate (decimal(8, 0), Nullable)
Start_Date (date, Nullable)
End_Date (date, Nullable)
Total_Working_HR (int, Nullable)
Value (decimal(8, 0), Nullable)
Created_By (varchar(50), Nullable)
Created_On (datetime, Nullable)
Updated_By (varchar(50), Nullable)
Updated_On (datetime, Nullable)
Primary Key:ID
Foreign Key:Sow_Id (int, Nullable) references Sow (ID)
 
 
Table Name: Sow_Type
Columns:
ID (int, Identity, Not Null)
Label (varchar(50), Not Null)
OrderWise (int, Not Null)
Is_Active (bit, Not Null)
Primary Key:ID

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
 
 
Table Name: Job_Requirements
Columns:
ID: Integer, Primary Key, Auto-increment.
Job_Code: Varchar(20), Required. Unique code for the job requirement.
Job_Name: Varchar(50), Required. Name of the job.
Job_Description: Text, Required. Description of the job role and responsibilities.
Project_Id: Integer, Foreign Key to Project(ID), Required. The project the job is associated with.
Role_Id: Integer, Foreign Key to Role(ID), Required. The role required for the job.
Positions_Required: Integer, Required. Number of positions required for the job.
Skill_Id1: Integer, Foreign Key to Skills(ID), Required. The primary skill required for the job.
Skill_Id2: Integer, Foreign Key to Skills(ID), Nullable. The secondary skill required for the job.
Skill_Level_Id1: Integer, Foreign Key to Skill_Level(ID), Required. The level of the primary skill.
Skill_Level_Id2: Integer, Foreign Key to Skill_Level(ID), Nullable. The level of the secondary skill.
Skill_Code1: Varchar(50), Nullable. Code for the primary skill.
Skill_Code2: Varchar(50), Nullable. Code for the secondary skill.
Job_Status_Id: Integer, Foreign Key to Job_Status(ID), Required. The status of the job requirement.
Experience: Decimal(18, 0), Nullable. Required experience for the job.
Client_Interview: Bit, Nullable. Indicates if a client interview is required.
Week_Id: Integer, Nullable. Week the job is needed.
Created_By: Varchar(50), Nullable. The user who created the job requirement.
Created_On: DateTime, Nullable. Date and time the job was created.
Updated_By: Varchar(50), Nullable. The user who updated the job requirement.
Updated_On: DateTime, Nullable. Date and time the job was updated.
Bu: Integer, Foreign Key to Business_Unit(ID), Nullable. The business unit associated with the job.
Completed_Date: Date, Nullable. The date the job was completed.
Is_External_Job: Bit, Nullable. Indicates if the job is external.
Job_Start_Date: Date, Nullable. The start date of the job.
SOWId: Integer, Foreign Key to Sow(ID), Nullable. Statement of Work associated with the job.
InvoiceReferenceName: Varchar(50), Nullable. Reference name for invoicing.
Foreign Keys:
Job_Status_Id references Job_Status(ID).
Project_Id references Project(ID).
Role_Id references Role(ID).
Skill_Id1 references Skills(ID).
Skill_Id2 references Skills(ID).
Skill_Level_Id1 references Skill_Level(ID).
Skill_Level_Id2 references Skill_Level(ID).
SOWId references Sow(ID).
Bu references Business_Unit(ID).
 
 
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

"""
    prompt4=f"""
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
 
 
  Table Name: Cert_Status  
Columns:  
- ID: Integer, Primary Key, Auto-increment.  
- Label: Varchar(50), Required.  
- OrderWise: Integer, Required.  
- Is_Active: Bit, Required.
 
 
Table Name: Certification  
Columns:  
- ID: Integer, Primary Key, Auto-increment.  
- Name: Varchar(500), Required, Unique.  
- Is_Active: Bit, Required.  
- Skill_Id: Integer, Foreign Key to Skills(ID), Required.  
- Exam_Num: Varchar(150), Nullable.  
- Emp_Type: Integer, Nullable.  
- Job_Start_Date: Date, Nullable.  
- Unique Constraint on Name.
- Foreign Key on Skill_Id to Skills(ID).
 
  Table Name: Emp_Cert_Status  
Columns:  
- ID: Integer, Primary Key, Auto-increment.  
- Label: Varchar(50), Required.  
- OrderWise: Integer, Required.  
- Is_Active: Bit, Required.
 
 
Table Name: Emp_Type  
Columns:  
- ID: Integer, Primary Key, Auto-increment.  
- Label: Varchar(50), Required.  
- OrderWise: Integer, Required.  
- Is_Active: Bit, Required.
 
Table Name: Emp_Work_Type  
Columns:  
- ID: Integer, Primary Key, Auto-increment.  
- Label: Varchar(50), Required.  
- OrderWise: Integer, Required.  
- Is_Active: Bit, Required.
 
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

Table Name: Employee_Certification
Columns:
ID: Integer, Primary Key, Auto-increment.
Certificate_Id: Integer, Foreign Key to Certification(ID), Required.
Created_By: Varchar(50), Nullable. The user who created the certification record.
Created_On: DateTime, Nullable. The date and time when the record was created.
Updated_By: Varchar(50), Nullable. The user who last updated the record.
Updated_On: DateTime, Nullable. The date and time when the record was last updated.
Certification_End_Date: Date, Nullable. The end date of the certification.
Date_Of_Certification: Date, Required. The date the certification was awarded.
LevelId: Integer, Foreign Key to Level(ID), Nullable. Represents the level of the certification.
Location_Id: Integer, Foreign Key to Location(ID), Nullable. Represents the location where the certification was awarded.
Emp_Certification_StatusId: Integer, Foreign Key to Emp_Cert_Status(ID), Required. Represents the status of the employee certification.
Emp_Id: Integer, Foreign Key to Employee(Id), Required. References the employee who holds the certification.
Foreign Keys:
Certificate_Id references Certification(ID).
Emp_Certification_StatusId references Emp_Cert_Status(ID).
Emp_Id references Employee(Id).
LevelId references Level(ID).
Location_Id references Location(ID).
 
 

 

 
Table Name: Location_Type
Columns:
ID: Integer, Primary Key, Auto-increment.
Label: Varchar(50), Required. Descriptive label for the location type.
OrderWise: Integer, Required. Defines the order or ranking for the location type.
Is_Active: Bit, Required. Indicates if the location type is active.
Constraints:
Primary Key: ID
Unique Key: Label
 
 
Table Name: Match_Table
Column Details:
ID: int, Primary Key, Auto-increment.
Emp_Id: int, Nullable, Foreign Key to Employee(Id).
Job_Req_Id: int, Nullable, Foreign Key to Job_Requirements(ID).
Is_Best_Match: bit, Nullable.
Is_Near_Match: bit, Nullable.
Is_Match: bit, Nullable.
Is_No_Match: bit, Nullable.
Rating: int, Nullable.
Created_By: varchar(50), Nullable.
Created_On: datetime, Nullable.
Updated_By: varchar(50), Nullable.
Updated_On: datetime, Nullable.
Foreign Key References:
Emp_Id references Employee(Id).
Job_Req_Id references Job_Requirements(ID).
  

 
Table Name: Training_Details
Columns:
ID (int, Identity, Not Null)
Name (varchar(50), Not Null)
Start_Date (date, Not Null)
End_Date (date, Not Null)
Training_Status (int, Not Null)
Is_Certification (bit, Not Null)
Certification_Id (int, Nullable)
Is_Active (bit, Not Null)
Created_By (varchar(50), Nullable)
Created_On (datetime, Nullable)
Updated_By (varchar(50), Nullable)
Updated_On (datetime, Nullable)
Primary Key:ID
Foreign Keys:
Certification_Id references Certification (ID)
Training_Status references Training_Status (ID)
 
Table Name: Training_Status
Columns:
ID (int, Identity, Not Null)
Label (varchar(50), Not Null)
OrderWise (int, Not Null)
Is_Active (bit, Not Null)
Primary Key:ID
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
    else:
        PROMPT = "No relevant table found."

   
        
        

@app.get("/")
async def get_response(User_Input: str):
    # Define the prompt with dynamic user input
    return "Hello!"
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
    pre=""
    result=search_word_and_compare_tables(User_Input, table_names1, table_names2, table_names3,table_names4)
    return result

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
   
 
    # Define the connection string for local SQL Server
    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=ILDCHNLAP0653\\MSSQLSERVER02;"
        "DATABASE=OMRP;"
        "UID=sa;"
        "PWD=Welcome@1;"
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
   
