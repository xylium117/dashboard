import zipfile 
import re 
import os 
import time 

src ="SA859CMS_Cost Report_WE_30 Oct 2026.xlsx"
dst ="SA859CMS_Cost_Report_Cleaned.xlsx"
tmp ="SA859CMS_Cost_Report_Cleaned.tmp"

try :
    with zipfile .ZipFile (src ,'r')as zin :
        with zipfile .ZipFile (tmp ,'w',zipfile .ZIP_DEFLATED )as zout :
            for item in zin .infolist ():
                data =zin .read (item .filename )
                if item .filename =='xl/workbook.xml':
                    xml_str =data .decode ('utf-8',errors ='ignore')
                    xml_cleaned =re .sub (r'<definedNames>.*?</definedNames>','<definedNames/>',xml_str ,flags =re .DOTALL )
                    print (f"workbook.xml reduced from {len (data ):,} bytes to {len (xml_cleaned ):,} bytes")
                    zout .writestr (item ,xml_cleaned .encode ('utf-8'))
                else :
                    zout .writestr (item ,data )


    for attempt in range (5 ):
        try :
            if os .path .exists (dst ):
                os .remove (dst )
            os .replace (tmp ,dst )
            break 
        except OSError :
            time .sleep (0.5 )

    print (f"Cleaned workbook ready: {dst if os .path .exists (dst )else tmp }")
except Exception as e :
    print (f"Notice: {e }")
