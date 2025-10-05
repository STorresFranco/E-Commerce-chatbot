import sqlite3
import pandas as pd
import sys
import os
from groq import Groq
from pathlib import Path
import re

#Paths
sys.path.append(os.path.abspath("."))
DB_PATH=Path(__file__).parent / "resources/db.sqlite"

#Create Groq client
client_sql=Groq()

#template for sql prompts
SQL_PROMPT="""You are an expert in understanding the database schema and generating SQL queries for a natural language question asked
pertaining to the data you have. The schema is provided in the schema tags. 
<schema> 
table: product 

fields: 
product_link - string (hyperlink to product)	
title - string (name of the product)	
brand - string (brand of the product)	
price - integer (price of the product in Indian Rupees)	
discount - float (discount on the product. 10 percent discount is represented as 0.1, 20 percent as 0.2, and such.)	
avg_rating - float (average rating of the product. Range 0-5, 5 is the highest.)	
total_ratings - integer (total number of ratings for the product)

</schema>
Make sure whenever you try to search for the brand name, the name can be in any case. 
So, make sure to use %LIKE% to find the brand in condition. Never use "ILIKE". 
Create a single SQL query for the question provided. 
The query should have all the fields in SELECT clause (i.e. SELECT *)

Just the SQL query is needed, nothing more. Always provide the SQL in between the <SQL></SQL> tags."""

#Prompt to respond to user

RESPONSE_PROMPT="""You are an expert in understanding the context of the question and replying based on the data pertaining to the question provided. You will be provided with Question: and Data:. The data will be in the form of an array or a dataframe or dict. Reply based on only the data provided as Data for answering the question asked as Question. Do not write anything like 'Based on the data' or any other technical words. Just a plain simple natural language response.
The Data would always be in context to the question asked. For example is the question is “What is the average rating?” and data is “4.3”, then answer should be “The average rating for the product is 4.3”. So make sure the response is curated with the question and data. Make sure to note the column names to have some context, if needed, for your response.
There can also be cases where you are given an entire dataframe in the Data: field. Always remember that the data field contains the answer of the question asked. All you need to do is to always reply in the following format when asked about a product: 
Produt title, price in indian rupees, discount, and rating, and then product link. Take care that all the products are listed in list format, one line after the other. Not as a paragraph.
For example:
1. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
2. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
3. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>

"""



def run_query(query):
    '''
    Description:
        Function to validate the start of a query and execute a pandas query based search
    Inputs
        query (str): SQL query to execute in pandas
    Returns
        df (Dataframe): Returns a Dataframe if the query start has correct syntax
    '''
    #Making sure the query is well formulated
    if query.strip().upper().startswith("SELECT"): 
        with sqlite3.connect(DB_PATH) as conn:
            df=pd.read_sql_query(query,conn) #Read the query and return a dataframe
            return df
    return None

def generate_sql_query(query):
    ''' 
    Description:
        Function to generate an SQL query based on an user given prompt
    Inputs
        query (str): Query passed by the user
    Returns 
        sql_query (str): Query formated in SQL syntax
    '''
    #Creating the Groq client
    client = Groq()

    #Generating the SQL query syntax
    chat_completion = client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": SQL_PROMPT,
            },
            {
                "role": "user",
                "content": query,
            }
        ],
        model=os.getenv("GROQ_MODEL"), # type: ignore
        temperature=0.2,
        max_tokens=1024
    )

    #Draw results from LLM response
    sql_query_raw= chat_completion.choices[0].message.content
    
    #Clean format so it can be passed to pandas queries
    sql_query=sql_query_format(sql_query_raw)
    return sql_query

def sql_query_format(sql_query):
    '''
    Description:
        Function to execute rule based extraction of the generated SQL query
    Inputs
        sql_query (str): SQL with syntax query of which pattern is extracted
    Returns
        sql_content(str): SQL code to execute in pandas
    '''
    #Extract the pattern using regex
    pattern="<SQL>*(.*?)</SQL>"
    match=re.search(pattern,sql_query,re.DOTALL)

    # Print the matched SQL content if found
    if match:
        sql_content = match.group(1)
        print("Extracted SQL:\n", sql_content)
        return sql_content
    else:
        return "No SQL block found."

def query_response(query,in_df):
    '''
    Description:
        Function to convert SQL retrieved dataframe into a humanized response
    Inputs
        query (str): Original query provided by the user
        in_df (dataframe): Dataframe retrieved from SQL query        
    '''
    #Convert df to context
    context=in_df.to_dict(orient="records")

    #Create the Groq client
    response_client = Groq()

    #Create response
    chat_completion = response_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": RESPONSE_PROMPT,
            },
            {
                "role": "user",
                "content": f"Question: {query} Data: {context}",
            }
        ],
        model=os.getenv("GROQ_MODEL"), # type: ignore
        temperature=0.2)

    #Take the text from the response
    response= chat_completion.choices[0].message.content

    return response

def concatenated_process(query):
    ''' 
    Description 
        Function to concatenate the full query process
    Inputs
        query (str): Query provided by the user
    '''
    #Convert the query to sql syntax
    sql_query=generate_sql_query(query)

    #Return Df based on sql query
    df=run_query(sql_query)

    #Convert the returned dataframe into a humanized response
    result=query_response(query,df)
    return result

if __name__=="__main__":
    pass
 



