import zipfile 
import xml .etree .ElementTree as ET 
from datetime import datetime ,timedelta 

def excel_date (serial ):
    try :
        s =float (serial )
        base =datetime (1899 ,12 ,30 )
        return (base +timedelta (days =s )).strftime ('%Y-%m-%d')
    except :
        return str (serial )

filename ="SA859CMS_Cost Report_WE_30 Oct 2026.xlsx"
with zipfile .ZipFile (filename ,'r')as z :
    strings =[]
    if 'xl/sharedStrings.xml'in z .namelist ():
        tree =ET .fromstring (z .read ('xl/sharedStrings.xml'))
        ns ={'ns':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        for si in tree .findall ('ns:si',ns ):
            strings .append (''.join (t .text or ''for t in si .findall ('.//ns:t',ns )))

    xml =z .read ('xl/worksheets/sheet17.xml')
    tree =ET .fromstring (xml )
    ns ={'ns':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

    for r in tree .findall ('.//ns:row',ns ):
        row_idx =r .attrib .get ('r')
        cells ={}
        for c in r .findall ('ns:c',ns ):
            ref =c .attrib .get ('r')
            t =c .attrib .get ('t')
            v =c .find ('ns:v',ns )
            val =v .text if v is not None else None 
            if t =='s'and val and val .isdigit ():
                val =strings [int (val )]
            cells [ref ]=val 
        print (f"R{row_idx }: {list (cells .items ())[:15 ]}")

