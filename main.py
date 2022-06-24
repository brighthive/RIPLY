import pandas as pd
import os
from pii_detect import detection


# os.environ['CLASSPATH']="./stanford-corenlp-full-2018-02-27/*"
# print(os.getenv('CLASSPATH'))

import csv
import re
import sys
import yaml
from datetime import datetime
from dateutil import parser as date_parser

def identify_header(path,n=5,th=0.9):
    df1=pd.read_csv(path,header='infer',nrows=n)
    df2=pd.read_csv(path,header=None,nrows=n)
    compare=(df1.dtypes.values==df2.dtypes.values).mean()
    return True if compare <th else False
def get_encoding(path):
    with open(path) as f:
        info=str(f)
        info=info.split(" ")[-1]
    return info.replace("=",":").replace(">","").replace("'","").replace("encoding:","")
def attract_delimiter(path):
    with open(path,newline='') as f:
        dialect=csv.Sniffer().sniff(f.read(4000))
    return (dialect.delimiter)
def hash_check(array_input):
    HASH_TYPE_REGEX = {
    re.compile(r"^[a-f0-9]{32}(:.+)?$", re.IGNORECASE):  ["MD5", "MD4", "MD2", "Double MD5",
                                                          "LM", "RIPEMD-128", "Haval-128",
                                                          "Tiger-128", "Skein-256(128)", "Skein-512(128",
                                                          "Lotus Notes/Domino 5", "Skype", "ZipMonster",
                                                          "PrestaShop"],
    re.compile(r"^[a-f0-9]{64}(:.+)?$", re.IGNORECASE):  ["SHA-256", "RIPEMD-256", "SHA3-256", "Haval-256",
                                                          "GOST R 34.11-94", "GOST CryptoPro S-Box",
                                                          "Skein-256", "Skein-512(256)", "Ventrilo"],
    re.compile(r"^[a-f0-9]{128}(:.+)?$", re.IGNORECASE): ["SHA-512", "Whirlpool", "Salsa10",
                                                          "Salsa20", "SHA3-512", "Skein-512",
                                                          "Skein-1024(512)"],
    re.compile(r"^[a-f0-9]{56}$", re.IGNORECASE):        ["SHA-224", "Haval-224", "SHA3-224",
                                                          "Skein-256(224)", "Skein-512(224)"],
    re.compile(r"^[a-f0-9]{40}(:.+)?$", re.IGNORECASE):  ["SHA-1", "Double SHA-1", "RIPEMD-160",
                                                          "Haval-160", "Tiger-160", "HAS-160",
                                                          "LinkedIn", "Skein-256(160)", "Skein-512(160)",
                                                          "MangoWeb Enhanced CMS"],
    re.compile(r"^[a-f0-9]{96}$", re.IGNORECASE):        ["SHA-384", "SHA3-384", "Skein-512(384)",
                                                          "Skein-1024(384)"],
    re.compile(r"^[a-f0-9]{16}$", re.IGNORECASE):        ["MySQL323", "DES(Oracle)", "Half MD5",
                                                          "Oracle 7-10g", "FNV-164", "CRC-64"],
    re.compile(r"^\*[a-f0-9]{40}$", re.IGNORECASE):      ["MySQL5.x", "MySQL4.1"],
    re.compile(r"^[a-f0-9]{48}$", re.IGNORECASE):        ["Haval-192", "Tiger-192", "SHA-1(Oracle)",
                                                          "XSHA (v10.4 - v10.6)"]
    } 
    
    
    return_array=[]
    for value in array_input:
        match=False
        for algorithm in HASH_TYPE_REGEX:
            if algorithm.match(str(value)):
                return_array.append(1)
                match=True
        if match==False:
           return_array.append(0)
    ### return probability of the return array
    return_array_length=len(return_array)
    probability=sum(return_array)/return_array_length
    return True if probability > 0.9 else False 
             
def get_df_info(path,header=True):
     if header==True:
         df1=pd.read_csv(path,header='infer')
         columns=df1.columns.tolist()
         dtyp=pd.DataFrame(df1.dtypes)
         return (df1,columns)
     else:
         df1=pd.read_csv(path,header=None)
         columns=df1.columns.tolist()
         return (df1,columns)
def date_validate(input_array):
    array_store=[]
    for input in input_array:
        try:
            bool(date_parser.parse(str(input)))
            array_store.append(1)
        except ValueError:
            array_store.append(0)
    length_array_store=len(array_store)
    probability=sum(array_store)/length_array_store
    return True if probability>0.95 else False 
def determine_date_format(input_value):
    formats=["%Y-%m-%d","%m/%d/%Y","%d/%m/%Y","%d.%m.%Y","%d %B %Y","%m %d %Y","%a %b %d %H:%M:%S %Y","%I:%M %p","%H:%M:%S"]
    for format_val in formats:
        try:
            bool_val=bool(datetime.strptime(str(input_value),format_val))
            return format_val
        except ValueError:
            pass
    return "couln't find correct format"

def pii_analyzer(columns,df):

    json_score={}
    pii_detection = detection()
    for column_name in columns:
        array=df[column_name]
        analysis = pii_detection.analyze(array)
        json_score[column_name]=analysis
    return json_score

file_name= sys.argv[1]
yaml_format={}



get_encoding=get_encoding(file_name)

delimiter=attract_delimiter(file_name)
yaml_format["source"]=file_name
yaml_format["encoding"]=get_encoding
yaml_format["delimiter"]='{}'.format(delimiter)
type_value=file_name.split(".")[-1]
yaml_format["type"]=type_value
file_name_csv=pd.read_csv(file_name,delimiter=delimiter)
file_name_csv=file_name_csv.to_csv(file_name.replace(type_value,"csv"),index=None)
file_name_clean=file_name.replace(type_value,"csv")
header=identify_header(file_name_clean)

yaml_format["header"]=header





full_array=[]
if header==True:
   df, column_names = get_df_info(file_name_clean)
   pii_field=pii_analyzer(column_names,df)
   for column_name in column_names:
       combine_json={}
       column_value=df[column_name].tolist()
       check_hash=hash_check(column_value)
       if check_hash== True:
           combine_json["hash"]=check_hash
       if pii_field[column_name]>0.9:
           combine_json["pii"]=column_name
       column_json={}
       column_json[column_name]=combine_json
       full_array.append(column_json)
       if date_validate(column_value)== True:
           combine_json["type"]="date"
           ## just choose one of out manyls
           format_date=determine_date_format(column_value[0])
           combine_json["format"]=format_date
   yaml_format["fields"]=full_array
else:
    df, column_names = get_df_info(file_name_clean)
    pii_field = pii_analyzer(column_names,df)
    for column_name in column_names:
        combine_json = {}
        column_value = df[column_name].tolist()
        check_hash = hash_check(column_value)
        if check_hash == True:
            combine_json["hash"] = check_hash
        if pii_field[column_name] > 0.9:
            combine_json["pii"] = column_name
        column_json = {}
        column_json[column_name] = combine_json
        full_array.append(column_json)
        if date_validate(column_value) == True:
            combine_json["type"] = "date"
            ## just choose one of out many
            format_date = determine_date_format(column_value[0])
            combine_json["format"] = format_date
    yaml_format["fields"] = full_array



   




with open("./Test.yaml","w") as f:
    yaml.dump(yaml_format,f,sort_keys=False, default_flow_style=False)




        
#value=["e10adc3949ba59abbe56e057f20f883e","e10adc3949ba59abbe56e057f20f883e","e10adc3949ba59abbe56e057f20f883e","e10adc3949ba59abbe56e057f20f883e","e10adc3949ba59abbe56e057f20f883e","e10adc3949ba59abbe56e057f20f883e","e10adc3949ba59abbe56e057f20f883e","e10adc3949ba59abbe56e057f20f883e","e10adc3949ba59abbe56e057f20f883e"]


#path='./VA2_Earning.csv'
#print(hash_test(value))
