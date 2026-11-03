import zipfile 
import xml .etree .ElementTree as ET 
from datetime import datetime ,timedelta 
from collections import defaultdict 

def excel_date (serial ):
    try :
        s =float (serial )
        base =datetime (1899 ,12 ,30 )
        return (base +timedelta (days =s )).strftime ('%Y-%m-%d')
    except :
        return str (serial )

def parse_cell_ref (ref ):
    col ="".join (filter (str .isalpha ,ref ))
    row =int ("".join (filter (str .isdigit ,ref )))
    return col ,row 

filename ="SA859CMS_Cost Report_WE_30 Oct 2026.xlsx"

with zipfile .ZipFile (filename ,'r')as z :
    strings =[]
    if 'xl/sharedStrings.xml'in z .namelist ():
        tree =ET .fromstring (z .read ('xl/sharedStrings.xml'))
        ns ={'ns':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        for si in tree .findall ('ns:si',ns ):
            strings .append (''.join (t .text or ''for t in si .findall ('.//ns:t',ns )))

    xml =z .read ('xl/worksheets/sheet20.xml')
    tree =ET .fromstring (xml )
    ns ={'ns':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

    rows =tree .findall ('.//ns:row',ns )
    header_row =rows [0 ]
    col_map ={}
    for c in header_row .findall ('ns:c',ns ):
        ref =c .attrib .get ('r')
        col ,_ =parse_cell_ref (ref )
        t =c .attrib .get ('t')
        v =c .find ('ns:v',ns )
        val =v .text if v is not None else ''
        if t =='s'and val .isdigit ():
            val =strings [int (val )]
        col_map [col ]=val 

    print ("Header mapped. Extracting rows...")
    by_staff =defaultdict (lambda :{'hours':0.0 ,'burdened_cost':0.0 ,'raw_cost':0.0 ,'revenue':0.0 ,'tx_count':0 ,'tasks':set ()})
    by_task =defaultdict (lambda :{'hours':0.0 ,'burdened_cost':0.0 ,'revenue':0.0 ,'tx_count':0 })
    by_expnd_type =defaultdict (lambda :{'hours':0.0 ,'burdened_cost':0.0 ,'revenue':0.0 ,'tx_count':0 })











    for r in rows [1 :]:
        row_dict ={}
        for c in r .findall ('ns:c',ns ):
            ref =c .attrib .get ('r')
            col ,_ =parse_cell_ref (ref )
            t =c .attrib .get ('t')
            v =c .find ('ns:v',ns )
            val =v .text if v is not None else ''
            if t =='s'and val .isdigit ():
                val =strings [int (val )]
            row_dict [col ]=val 

        emp =row_dict .get ('C','Unknown')
        task =row_dict .get ('B','Unknown')
        exp_type =row_dict .get ('E','Unknown')

        try :
            qty =float (row_dict .get ('G',0 )or 0 )
        except :
            qty =0.0 
        try :
            raw_c =float (row_dict .get ('K',0 )or 0 )
        except :
            raw_c =0.0 
        try :
            burd_c =float (row_dict .get ('L',0 )or 0 )
        except :
            burd_c =0.0 
        try :
            rev =float (row_dict .get ('M',0 )or row_dict .get ('O',0 )or 0 )
        except :
            rev =0.0 

        by_staff [emp ]['hours']+=qty 
        by_staff [emp ]['raw_cost']+=raw_c 
        by_staff [emp ]['burdened_cost']+=burd_c 
        by_staff [emp ]['revenue']+=rev 
        by_staff [emp ]['tx_count']+=1 
        by_staff [emp ]['tasks'].add (task )

        by_task [task ]['hours']+=qty 
        by_task [task ]['burdened_cost']+=burd_c 
        by_task [task ]['revenue']+=rev 
        by_task [task ]['tx_count']+=1 

        by_expnd_type [exp_type ]['hours']+=qty 
        by_expnd_type [exp_type ]['burdened_cost']+=burd_c 
        by_expnd_type [exp_type ]['revenue']+=rev 
        by_expnd_type [exp_type ]['tx_count']+=1 

    print ("\n--- TOP STAFF / SUPPLIERS BY BURDENED COST ---")
    sorted_staff =sorted (by_staff .items (),key =lambda x :x [1 ]['burdened_cost'],reverse =True )
    for emp ,d in sorted_staff [:15 ]:
        gm =d ['revenue']-d ['burdened_cost']
        gm_pct =(gm /d ['revenue']*100 )if d ['revenue']!=0 else 0 
        print (f"{emp [:35 ]:35} | Hrs: {d ['hours']:8.1f} | Cost: SAR {d ['burdened_cost']:10.2f} | Rev: SAR {d ['revenue']:10.2f} | GM: {gm_pct :5.1f}%")

    print ("\n--- BY EXPENDITURE TYPE ---")
    for exp ,d in sorted (by_expnd_type .items (),key =lambda x :x [1 ]['burdened_cost'],reverse =True ):
        print (f"{exp :30} | Hrs: {d ['hours']:8.1f} | Cost: SAR {d ['burdened_cost']:10.2f} | Rev: SAR {d ['revenue']:10.2f}")

