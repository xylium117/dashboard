import zipfile 
import xml .etree .ElementTree as ET 

filename ="SA859CMS_Cost Report_WE_30 Oct 2026.xlsx"

with zipfile .ZipFile (filename ,'r')as z :
    strings =[]
    if 'xl/sharedStrings.xml'in z .namelist ():
        tree =ET .fromstring (z .read ('xl/sharedStrings.xml'))
        ns ={'ns':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        for si in tree .findall ('ns:si',ns ):
            strings .append (''.join (t .text or ''for t in si .findall ('.//ns:t',ns )))

    def print_sheet (name ,path ,max_r =15 ):
        print (f"\n--- {name } ({path }) ---")
        xml =z .read (path )
        tree =ET .fromstring (xml )
        ns ={'ns':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        for r in tree .findall ('.//ns:row',ns )[:max_r ]:
            r_idx =r .attrib .get ('r')
            cells ={}
            for c in r .findall ('ns:c',ns ):
                ref =c .attrib .get ('r')
                t =c .attrib .get ('t')
                v =c .find ('ns:v',ns )
                val =v .text if v is not None else ''
                if t =='s'and val .isdigit ():
                    val =strings [int (val )]
                cells [ref ]=val 
            print (f"R{r_idx }: {list (cells .items ())[:8 ]}")

    print_sheet ("Contract Sum Breakdown","xl/worksheets/sheet6.xml")
    print_sheet ("Task Codes","xl/worksheets/sheet2.xml",max_r =10 )
    print_sheet ("Regionwise Split","xl/worksheets/sheet10.xml",max_r =10 )

