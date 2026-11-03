import zipfile 
import xml .etree .ElementTree as ET 

filename ="SA859CMS_Cost Report_WE_30 Oct 2026.xlsx"

with zipfile .ZipFile (filename ,'r')as z :
    wb_rels_xml =z .read ('xl/_rels/workbook.xml.rels')
    root_rels =ET .fromstring (wb_rels_xml )
    rel_map ={rel .attrib .get ('Id'):rel .attrib .get ('Target')for rel in root_rels }

    wb_xml =z .read ('xl/workbook.xml')
    root_wb =ET .fromstring (wb_xml )
    ns ={'ns':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

    sheets_elem =root_wb .find ('ns:sheets',ns )
    for s in sheets_elem .findall ('ns:sheet',ns ):
        name =s .attrib .get ('name')
        rid =s .attrib .get ('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        target =rel_map .get (rid )
        full_path ='xl/'+target if not target .startswith ('/')else target [1 :]


        xml_data =z .read (full_path )
        tree =ET .fromstring (xml_data )
        dim =tree .find ('ns:dimension',ns )
        dim_ref =dim .attrib .get ('ref')if dim is not None else 'N/A'

        sheetData =tree .find ('ns:sheetData',ns )
        row_count =len (sheetData .findall ('ns:row',ns ))if sheetData is not None else 0 

        print (f"{name :30} | Rows: {row_count :6} | Dim: {dim_ref }")

