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

def col_letter_to_index (col_str ):
    exp =0 
    val =0 
    for char in reversed (col_str ):
        val +=(ord (char )-ord ('A')+1 )*(26 **exp )
        exp +=1 
    return val -1 

def parse_cell_ref (ref ):
    col ="".join (filter (str .isalpha ,ref ))
    row =int ("".join (filter (str .isdigit ,ref )))
    return col ,row 

with zipfile .ZipFile (filename ,'r')as z :
    shared_strings =load_shared_strings (z )

    xml_data =z .read ('xl/worksheets/sheet20.xml')
    tree =ET .fromstring (xml_data )
    ns ={'ns':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

    sheetData =tree .find ('ns:sheetData',ns )
    rows =sheetData .findall ('ns:row',ns )


    header_row =rows [0 ]
    headers ={}
    for c in header_row .findall ('ns:c',ns ):
        ref =c .attrib .get ('r')
        col ,_ =parse_cell_ref (ref )
        t =c .attrib .get ('t')
        v =c .find ('ns:v',ns )
        val =v .text if v is not None else ''
        if t =='s'and val .isdigit ():
            val =shared_strings [int (val )]
        headers [col ]=val 

    print (f"Total columns in Oracle_Combined: {len (headers )}")
    for col ,h in headers .items ():
        print (f"  {col }: {h }")

    print (f"\nTotal transaction rows: {len (rows )-1 }")

