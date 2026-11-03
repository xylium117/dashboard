import zipfile 
import xml .etree .ElementTree as ET 

filename ="SA859CMS_Cost Report_WE_30 Oct 2026.xlsx"

with zipfile .ZipFile (filename ,'r')as z :
    wb_xml =z .read ('xl/workbook.xml')
    root =ET .fromstring (wb_xml )


    ns ={'ns':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

    sheets =[]
    sheets_elem =root .find ('ns:sheets',ns )
    if sheets_elem is not None :
        for s in sheets_elem .findall ('ns:sheet',ns ):
            sheet_id =s .attrib .get ('sheetId')
            name =s .attrib .get ('name')
            r_id =s .attrib .get ('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            sheets .append ((sheet_id ,name ,r_id ))

    print (f"Total sheets found: {len (sheets )}")
    for sid ,name ,rid in sheets :
        print (f"  SheetId: {sid }, Name: {name }, RelId: {rid }")


    defined_names =root .findall ('.//ns:definedName',ns )
    print (f"Total defined names: {len (defined_names )}")

