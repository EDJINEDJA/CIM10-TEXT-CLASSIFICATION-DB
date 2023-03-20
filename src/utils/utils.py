"""

"""

#dependencies
import requests
import csv
import os
import pandas as pd
import openai
import pprint
from  tqdm import tqdm
from configparser import ConfigParser
import json
import time
import random

parser = ConfigParser()
parser.read("./config/config.ini")

with open("./secret/keys.json") as f:
    api_key = json.load(f)


class Utils():

    def __init__(self) -> None:
        pass


    def __str__(self) -> str:
        return "Utils provides instance to scraped icd10 code is such a way that  for each code their descriptio. The output s in to csv file"

    def __getitem__(self):
        pass

    def __len__(self):
        pass

    def fields(self):
        with open(os.path.join(parser.get("inputPath","absPath"),"LIBCIM10MULTI.TXT"), mode="r" , encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                line = line.replace("\n","")
                # Split the text file into lines and parse each line into fields
                fields = line.split("|")
                #Split the text line using one blank seperator
                yield [field.strip() for field in fields if field.strip()]

    def load(self):

        rows = []
        for item in self.fields():
            if len(item)==0:
                pass
            else:
                rows.append(item) #filled in the rows

        # Write the parsed data to a CSV file with the specified column headers
        with open(os.path.join(parser.get("outputPath","path"),'CIM10_2022.csv'), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['CODE', 'MCO/HAD', 'SSR','PSY', 'SHORTDESCRIPTION', 'DESCRIPTION'])
            writer.writerows(rows)

    def icd92icd10(self):
        #read excel file from raw folder
        icd9icd10 = pd.read_excel(parser.get("inputPath", "path"), sheet_name=None , usecols="A:B,C")
        #Convert into dataframe
        data = pd.DataFrame(icd9icd10['masterb10 - incl 3rd vic fix'], columns=["TABLETYP", "ICD10" ,"Pure Victorian Logical"])
        #Rename columns
        data.rename(columns={"TABLETYP" : "TABLETYPE", "ICD10" : "CODE-10" ,"Pure Victorian Logical" : "ICD9-CM"}, inplace= True)
        print("Export progress ... ")
        #Export into csv file and save in output folder
        data.to_csv(os.path.join(parser.get("outputPath","path"),'icd9icd10.csv'))

        print("____ Export done ___")

    def merge(self):
        #Load icd92icd10 csv file located in processed folder
        correspondanceicd92icd10 = pd.read_csv(os.path.join(parser.get("outputPath","path"),'icd9icd10.csv'))
        CIM10_2022 = pd.read_csv(os.path.join(parser.get("outputPath","path"),'CIM10_2022.csv'))
        ICD9_CM = []

        for keys , values in CIM10_2022["CODE"].iteritems():
            # supposons que le dataframe s'appelle `correspondance_df`
            # et que les colonnes contenant les codes ICD-9 et ICD-10 s'appellent respectivement `icd9` et `icd10`

            code_icd10_recherche = values
            try:
                valeur_icd9_correspondante = correspondanceicd92icd10.loc[correspondanceicd92icd10["CODE-10"] == str(code_icd10_recherche.strip()), "ICD9-CM"].iloc[0]
                ICD9_CM.append(valeur_icd9_correspondante)
            except IndexError:
                ICD9_CM.append("Pas d'équivalence")

        CIM10_2022["CODE-9"]=ICD9_CM

        #Rename columns
        CIM10_2022.rename(columns={"CODE" : "CODE-10", 'MCO/HAD' : 'MCO/HAD', 'SSR' : 'SSR','PSY' : 'PSY', 'SHORTDESCRIPTION' : 'SHORTDESCRIPTION', 'DESCRIPTION' : 'DESCRIPTION', "CODE-9" : "CODE-9"}, inplace= True)
        cim10_final = pd.DataFrame()
        cim10_final["CODE-10"]=CIM10_2022["CODE-10"]
        cim10_final["CODE-9"]=CIM10_2022["CODE-9"]
        cim10_final['MCO/HAD']=CIM10_2022['MCO/HAD']
        cim10_final['SSR']=CIM10_2022['SSR']
        cim10_final['PSY']=CIM10_2022['PSY']
        cim10_final['SHORTDESCRIPTION']=CIM10_2022['SHORTDESCRIPTION']
        cim10_final['DESCRIPTION']=CIM10_2022['DESCRIPTION']

        print("Export progress ... ")
        #Export into csv file and save in output folder
        cim10_final.index.name = "INDEX"
        cim10_final.to_csv(os.path.join(parser.get("outputFinalPath","path"),'CIM10_final.csv'))
        print("____ Export done ___")

    def addServices(self):
        #Load final CIM10 in csv format from final folder
        finalCim10 = pd.read_csv(os.path.join(parser.get("outputFinalPath" , "path"), "CIM10_final.csv") , sep= ",")

        #Load CIM10 chunk by desease category
        chunkCim10 = pd.read_csv(os.path.join(parser.get("inputPath" , "absPath_"), "Classification maladiesv1.csv") , sep= ";")

        finalCim10_CODE_10_GROUPED = []
        finalCim10_DESCRIPTION_GROUPED = []
        finalCim10_SERVICES = []

        for idx in range(0,937):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[0])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[0])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[0])

        for idx in range(937,939):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[1])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[1])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[1])

        for idx in range(939,1855):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[2])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[2])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[2])

        for idx in range(1855,1866):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[3])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[3])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[3])

        for idx in range(1866,2054):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[4])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[4])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[4])

        for idx in range(2054,2060):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[5])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[5])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[5])

        for idx in range(2060,2547):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[6])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[6])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[6])


        for idx in range(2547,3898):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[7])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[7])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[7])


        for idx in range(3898,4314):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[8])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[8])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[8])

        for idx in range(4314,4318):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[9])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[9])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[9])


        for idx in range(4318 , 4626):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[10])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[10])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[10])

        for idx in range(4626 , 4629):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[11])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[11])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[11])


        for idx in range(4629 , 4760):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[12])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[12])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[12])

        for idx in range(4760,4764):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[13])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[13])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[13])


        for idx in range(4764,5289):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[14])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[14])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[14])

        for idx in range(5289,5585):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[15])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[15])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[15])

        for idx in range(5585,5588):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[16])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[16])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[16])

        for idx in range(5588,6107):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[17])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[17])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[17])

        for idx in range(6107,6122):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[18])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[18])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[18])

        for idx in range(6122,6523):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[19])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[19])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[19])

        for idx in range(6523,6525):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[20])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[20])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[20])

        for idx in range(6525,10339):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[21])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[21])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[21])


        for idx in range(10339,10421):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[22])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[22])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[22])

        for idx in range(10421,10933):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[23])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[23])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[23])

        for idx in range(10933,10941):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[24])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[24])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[24])


        for idx in range(10941,11473):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[25])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[25])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[25])

        for idx in range(11473,11482):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[26])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[26])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[26])


        for idx in range(11482,11883):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[27])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[27])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[27])

        for idx in range(11883,11891):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[28])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[28])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[28])


        for idx in range(11891,12599):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[29])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[29])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[29])

        for idx in range(12599,12604):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[30])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[30])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[30])


        for idx in range(12604,13027):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[31])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[31])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[31])

        for idx in range(13027,14799):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[32])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[32])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[32])

        for idx in range(14799,14803):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[33])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[33])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[33])

        for idx in range(14803,14910):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[34])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[34])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[34])

        for idx in range(14910,14912):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[35])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[35])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[35])


        for idx in range(14912,42009):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[36])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[36])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[36])

        for idx in range(42009,42873):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[37])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[37])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[37])


        for idx in range(42873,42886):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[38])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[38])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[38])

        finalCim10["CIM10-GROUPED"] = finalCim10_CODE_10_GROUPED
        finalCim10["DESCRIPTION-GROUPED"] = finalCim10_DESCRIPTION_GROUPED
        finalCim10["SERVICES-MACRO"] = finalCim10_SERVICES

        print("Export progress ... ")
        #Export into csv file and save in output folder
        finalCim10.to_csv(os.path.join(parser.get("outputFinalPath","path"),'CIM10_final_update.csv'),index=False)
        print("____ Export done ___")




    def addServicesPLus(self):
        #Load final CIM10 in csv format from final folder
        finalCim10 = pd.read_csv(os.path.join(parser.get("outputFinalPath" , "path"), "CIM10_final_update.csv") , sep= ",")

        #Load CIM10 chunk by desease category
        chunkCim10 = pd.read_csv(os.path.join(parser.get("inputPath" , "absPath_"), "Classification maladiesv1.csv") , sep= ";")


        finalCim10_CODE_10_GROUPED = []
        finalCim10_DESCRIPTION_GROUPED = []
        finalCim10_SERVICES = []

        for idx in range(0,937):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[0])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[0])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[0])

        for idx in range(937,939):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[0])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[0])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[0])

        for idx in range(939,1855):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[2])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[2])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[2])

        for idx in range(1855,1866):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[2])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[2])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[2])

        for idx in range(1866,2054):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[4])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[4])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[4])

        for idx in range(2054,2060):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[4])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[4])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[4])

        for idx in range(2060,2547):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[6])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[6])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[6])


        for idx in range(2547,3898):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[7])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[7])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[7])


        for idx in range(3898,4314):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[8])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[8])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[8])

        for idx in range(4314,4318):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[8])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[8])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[8])


        for idx in range(4318 , 4626):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[10])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[10])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[10])

        for idx in range(4626 , 4629):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[10])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[10])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[10])


        for idx in range(4629 , 4760):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[12])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[12])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[12])

        for idx in range(4760,4764):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[12])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[12])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[12])


        for idx in range(4764,5289):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[14])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[14])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[14])

        for idx in range(5289,5585):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[15])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[15])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[15])

        for idx in range(5585,5588):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[15])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[15])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[15])

        for idx in range(5588,6107):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[17])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[17])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[17])

        for idx in range(6107,6122):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[17])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[17])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[17])

        for idx in range(6122,6523):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[19])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[19])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[19])

        for idx in range(6523,6525):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[19])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[19])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[19])

        for idx in range(6525,10339):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[21])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[21])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[21])


        for idx in range(10339,10421):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[21])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[21])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[21])

        for idx in range(10421,10933):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[23])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[23])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[23])

        for idx in range(10933,10941):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[23])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[23])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[23])


        for idx in range(10941,11473):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[25])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[25])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[25])

        for idx in range(11473,11482):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[25])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[25])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[25])


        for idx in range(11482,11883):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[27])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[27])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[27])

        for idx in range(11883,11891):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[27])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[27])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[27])


        for idx in range(11891,12599):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[29])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[29])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[29])

        for idx in range(12599,12604):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[29])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[29])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[29])


        for idx in range(12604,13027):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[31])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[31])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[31])

        for idx in range(13027,14799):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[32])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[32])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[32])

        for idx in range(14799,14803):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[32])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[32])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[32])

        for idx in range(14803,14910):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[34])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[34])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[34])

        for idx in range(14910,14912):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[34])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[34])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[34])


        for idx in range(14912,42009):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[36])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[36])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[36])

        for idx in range(42009,42873):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[37])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[37])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[37])


        for idx in range(42873,42886):
            finalCim10_CODE_10_GROUPED.append(chunkCim10["CIM10"].tolist()[37])
            finalCim10_DESCRIPTION_GROUPED.append(chunkCim10["TITRE"].tolist()[37])
            finalCim10_SERVICES.append(chunkCim10["SERVICES"].tolist()[37])

        finalCim10["CIM10-GROUPED+"] = finalCim10_CODE_10_GROUPED
        finalCim10["DESCRIPTION-GROUPED+"] = finalCim10_DESCRIPTION_GROUPED
        finalCim10["SERVICES-MINI+"] = finalCim10_SERVICES

        print("Export progress ... ")
        #Export into csv file and save in output folder
        finalCim10.to_csv(os.path.join(parser.get("outputFinalPath","path"),'CIM10_final_update_plus.csv'))
        print("____ Export done ___")



    @staticmethod
    # Define function to generate response
    def generate_response(prompt, model , temperature):
        response = openai.ChatCompletion.create(
            model=model,
            messages=prompt,
            temperature = temperature
        )

        return response

    def ChatGptAPi(self , content , temperature = 0):
        # Set OpenAI API key
        openai.api_key = api_key["api-keys"]

        # Set up the OpenAI model
        model_engine = "gpt-3.5-turbo"
        model_prompt = [{"role" : "system" ,"content" : f"{content}"
                        }] # Change the question prompt as needed

        # Generate response using the defined function
        response = self.generate_response(model_prompt, model_engine, temperature)

        # return the response
        return response['choices'][0]['message']['content']

    def Q2text(self):

        #Load icd_final.csv
        icd_final = pd.read_csv(parser.get("outputFinalPath" , "load"))

        if not os.path.exists(parser.get("outputFinalPath","inProgressFile")) and not os.path.exists(os.path.join(parser.get("outputFinalPath" , "path"),"log.json")):
            print("__ log file and final data locator in creation __")
            with open(parser.get("outputFinalPath","inProgressFile"), "w", newline="") as file:
                file.close()

            with open(os.path.join(parser.get("outputFinalPath" , "path"),"log.json"), 'w') as f:
                json.dump({},f)
                # définir la taille du fichier à 0 octet
            os.truncate(os.path.join(parser.get("outputFinalPath" , "path"),"log.json"), 0)
            print("Creation done . . . ")
            print("replay the script to getting started")



        if os.path.getsize(parser.get("outputFinalPath","inProgressFile")) == 0:
            # Ouverture du fichier en mode 'append' pour ajouter de nouvelles lignes
            with open(os.path.join(parser.get("outputFinalPath","path"),'CIM10-CLASSIFICATION_DATASET.csv'), mode='a', newline='') as file:
                # Définition des colonnes dans un objet DictWriter
                writer = csv.DictWriter(file, fieldnames=["INDEX","CODE-10","CODE-9","MCO/HAD","SSR","PSY","SHORTDESCRIPTION","DESCRIPTION","CIM10-GROUPED","DESCRIPTION-GROUPED","SERVICES-MACRO","CIM10-GROUPED+","DESCRIPTION-GROUPED+","SERVICES-MINI+", "Text"])

                # Écriture de l'en-tête
                writer.writeheader()

        else :

            if os.path.getsize(os.path.join(parser.get("outputFinalPath" , "path"),"log.json")) == 0:
                with open(os.path.join(parser.get("outputFinalPath" , "path"),"log.json"), mode='w') as f:
                    keys = "0"
                    icd10 = "A00"
                    data = {f"{keys}" : f"{icd10}"}
                    # Écrire l'objet JSON dans le fichier
                    json.dump(data, f)

                    # Ajouter un retour à la ligne pour séparer les objets JSON
                    f.write("\n")
                    f.close()
            else:
                data = [json.loads(line) for line in open(os.path.join(parser.get("outputFinalPath" , "path"),"log.json") , mode ="r")]
                cursor = data[-1].values()
                valeurs = list(cursor) # conversion de la vue en liste
                valeur = valeurs[0] # accès à la première valeur de la liste
                # Trouver l'index de l'élément "valeur" dans la colonne "colonne"
                index = icd_final["CODE-10"].index[icd_final["CODE-10"] == valeur][0]

                for keys_ , icd10_ in tqdm(icd_final["CODE-10"].iloc[index:].iteritems()):

                    compt = 0
                    des = icd_final.loc[icd_final["CODE-10"] == icd10_, "SHORTDESCRIPTION"].iloc[0]+ "," + icd_final.loc[icd_final["CODE-10"] == icd10_, "DESCRIPTION"].iloc[0]
                    prompt = f"La CIM-10,qui est la classification internationale des maladies publiée par l'OMS, décrit le :{des} avec le code = {icd10_} Simulez-moi svp une discussion entre un docteur et un patient qui explique les symptômesqu'il a liés à ce type de maladie comme un appel d'urgence, sans mentionné dans  le texte anonymisé le diagnostic trouvé par le docteur et la maladie."
                    
                    with open(os.path.join(parser.get("outputFinalPath" , "path"),"log.json"), mode='w') as f:
                        data = {f"{keys_}" : f"{icd10_}"}
                        # Écrire l'objet JSON dans le fichier
                        json.dump(data, f)
                        # Ajouter un retour à la ligne pour séparer les objets JSON
                        f.write("\n")
                        f.close()
                    text = self.ChatGptAPi(prompt , temperature= random.random() * 0.9 + 0.1)

                    row =[icd_final.loc[icd_final["CODE-10"] == icd10_, "INDEX"].iloc[0],
                    icd10_,
                    icd_final.loc[icd_final["CODE-10"] == icd10_, "CODE-9"].iloc[0],
                    icd_final.loc[icd_final["CODE-10"] == icd10_, "MCO/HAD"].iloc[0],
                    icd_final.loc[icd_final["CODE-10"] == icd10_, "SSR"].iloc[0],
                    icd_final.loc[icd_final["CODE-10"] == icd10_, "PSY"].iloc[0],
                    icd_final.loc[icd_final["CODE-10"] == icd10_, "SHORTDESCRIPTION"].iloc[0],
                    icd_final.loc[icd_final["CODE-10"] == icd10_, "DESCRIPTION"].iloc[0],
                    icd_final.loc[icd_final["CODE-10"] == icd10_, "CIM10-GROUPED"].iloc[0],
                    icd_final.loc[icd_final["CODE-10"] == icd10_, "DESCRIPTION-GROUPED"].iloc[0],
                    icd_final.loc[icd_final["CODE-10"] == icd10_, "SERVICES-MACRO"].iloc[0],
                    icd_final.loc[icd_final["CODE-10"] == icd10_, "CIM10-GROUPED+"].iloc[0],
                    icd_final.loc[icd_final["CODE-10"] == icd10_, "CIM10-GROUPED+"].iloc[0],
                    icd_final.loc[icd_final["CODE-10"] == icd10_, "SERVICES-MINI+"].iloc[0],
                    text]
                    # Ouverture du fichier en mode 'append' pour ajouter de nouvelles lignes
                    with open(os.path.join(parser.get("outputFinalPath","path"),'CIM10-CLASSIFICATION_DATASET.csv'), mode='a', newline='') as file1:
                        writer1 = csv.writer(file1)
                        # Écriture d'une nouvelle ligne dans le fichier CSV
                        writer1.writerow(row)
                    time.sleep(60)