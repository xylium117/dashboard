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

def parse_sheet (z ,sheet_path ,shared_strings ,max_rows =15 ):
    xml_data =z .read (sheet_path )
    tree =ET .fromstring (xml_data )
    ns ={'ns':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

    rows =[]
    sheetData =tree .find ('ns:sheetData',ns )
    if sheetData is None :
        return rows 

    for r in sheetData .findall ('ns:row',ns )[:max_rows ]:
        row_idx =r .attrib .get ('r')
        row_vals ={}
        for c in r .findall ('ns:c',ns ):
            col_ref =c .attrib .get ('r')
            cell_type =c .attrib .get ('t')
            v_elem =c .find ('ns:v',ns )
            val =v_elem .text if v_elem is not None else None 

            if cell_type =='s'and val is not None and val .isdigit ():
                idx =int (val )
                val =shared_strings [idx ]if idx <len (shared_strings )else val 
            elif cell_type =='inlineStr':
                is_elem =c .find ('.//ns:t',ns )
                val =is_elem .text if is_elem is not None else val 
            elif cell_type =='b':
                val =(val =='1')

            row_vals [col_ref ]=val 
        rows .append ((row_idx ,row_vals ))
    return rows 

with zipfile .ZipFile (filename ,'r')as z :
    shared_strings =load_shared_strings (z )
    print (f"Loaded {len (shared_strings )} shared strings.")


    print ("\n--- Summary (sheet5.xml) ---")
    summary_rows =parse_sheet (z ,'xl/worksheets/sheet5.xml',shared_strings ,max_rows =25 )
    for r_idx ,cols in summary_rows :
        row_str =" | ".join (f"{col }:{val }"for col ,val in list (cols .items ())[:8 ]if val is not None )
        if row_str :
            print (f"Row {r_idx }: {row_str }")


    print ("\n--- Fin KPIs &WIP Recon (sheet7.xml) ---")
    kpi_rows =parse_sheet (z ,'xl/worksheets/sheet7.xml',shared_strings ,max_rows =20 )
    for r_idx ,cols in kpi_rows :
        row_str =" | ".join (f"{col }:{val }"for col ,val in list (cols .items ())[:8 ]if val is not None )
        if row_str :
            print (f"Row {r_idx }: {row_str }")

