import zipfile 
import xml .etree .ElementTree as ET 

filename ="SA859CMS_Cost Report_WE_30 Oct 2026.xlsx"

def load_shared_strings (z ):
    strings =[]
    if 'xl/sharedStrings.xml'in z .namelist ():
        tree =ET .fromstring (z .read ('xl/sharedStrings.xml'))
        ns ={'ns':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        for si in tree .findall ('ns:si',ns ):
            texts =[t .text or ''for t in si .findall ('.//ns:t',ns )]
            strings .append (''.join (texts ))
    return strings 

with zipfile .ZipFile (filename ,'r')as z :
    shared_strings =load_shared_strings (z )

    xml_data =z .read ('xl/worksheets/sheet5.xml')
    tree =ET .fromstring (xml_data )
    ns ={'ns':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    sheetData =tree .find ('ns:sheetData',ns )

    for r in sheetData .findall ('ns:row',ns ):
        row_idx =r .attrib .get ('r')
        row_vals ={}
        for c in r .findall ('ns:c',ns ):
            col_ref =c .attrib .get ('r')
            cell_type =c .attrib .get ('t')
            v_elem =c .find ('ns:v',ns )
            val =v_elem .text if v_elem is not None else None 
            if cell_type =='s'and val is not None and val .isdigit ():
                val =shared_strings [int (val )]
            row_vals [col_ref ]=val 
        line =" | ".join (f"{k }:{v }"for k ,v in row_vals .items ()if v is not None )
        if line :
            print (f"R{row_idx :2}: {line }")

