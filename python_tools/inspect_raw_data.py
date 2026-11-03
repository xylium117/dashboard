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

def parse_sheet_header_and_sample (z ,sheet_path ,shared_strings ,max_rows =6 ):
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

    sheets_to_inspect =[
    ("Oracle_Combined","xl/worksheets/sheet20.xml"),
    ("WE 30-Oct-26_Time Cost Rev","xl/worksheets/sheet8.xml"),
    ("BL_TaskCode","xl/worksheets/sheet13.xml"),
    ("Staff wise_GM Impact","xl/worksheets/sheet16.xml"),
    ("GM Trend","xl/worksheets/sheet17.xml"),
    ("PU wise split","xl/worksheets/sheet9.xml"),
    ]

    for title ,path in sheets_to_inspect :
        print (f"\n==================== {title } ({path }) ====================")
        rows =parse_sheet_header_and_sample (z ,path ,shared_strings ,max_rows =5 )
        for r_idx ,cols in rows :
            print (f"Row {r_idx }: {list (cols .items ())[:12 ]}")

