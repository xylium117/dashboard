import os 
import csv 
import json 
import zipfile 
import xml .etree .ElementTree as ET 
from datetime import datetime ,timedelta 
from collections import defaultdict 

def excel_date_to_iso (serial ):
    if not serial :
        return ""
    try :
        s =float (serial )
        base =datetime (1899 ,12 ,30 )
        return (base +timedelta (days =s )).strftime ('%Y-%m-%d')
    except Exception :
        return str (serial )

def parse_cell_ref (ref ):
    col ="".join (filter (str .isalpha ,ref ))
    row =int ("".join (filter (str .isdigit ,ref )))
    return col ,row 

def safe_float (val ,default =0.0 ):
    if val is None or val =='':
        return default 
    try :
        return float (val )
    except (ValueError ,TypeError ):
        return default 

def main ():
    excel_path ="SA859CMS_Cost Report_WE_30 Oct 2026.xlsx"
    print (f"Loading and processing {excel_path }...")

    with zipfile .ZipFile (excel_path ,'r')as z :

        strings =[]
        if 'xl/sharedStrings.xml'in z .namelist ():
            tree =ET .fromstring (z .read ('xl/sharedStrings.xml'))
            ns ={'ns':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for si in tree .findall ('ns:si',ns ):
                strings .append (''.join (t .text or ''for t in si .findall ('.//ns:t',ns )))
        print (f"Loaded {len (strings )} shared strings.")

        ns ={'ns':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

        def get_sheet_cells (sheet_path ):
            xml_data =z .read (sheet_path )
            tree =ET .fromstring (xml_data )
            rows ={}
            for r in tree .findall ('.//ns:row',ns ):
                r_idx =int (r .attrib .get ('r'))
                row_cells ={}
                for c in r .findall ('ns:c',ns ):
                    ref =c .attrib .get ('r')
                    col ,_ =parse_cell_ref (ref )
                    t =c .attrib .get ('t')
                    v =c .find ('ns:v',ns )
                    val =v .text if v is not None else None 
                    if t =='s'and val is not None and val .isdigit ():
                        idx =int (val )
                        val =strings [idx ]if idx <len (strings )else val 
                    elif t =='inlineStr':
                        elem =c .find ('.//ns:t',ns )
                        val =elem .text if elem is not None else val 
                    row_cells [col ]=val 
                rows [r_idx ]=row_cells 
            return rows 


        print ("Parsing Task Codes...")
        task_rows =get_sheet_cells ('xl/worksheets/sheet2.xml')
        task_map ={}
        for r_idx in range (2 ,max (task_rows .keys ())+1 ):
            row =task_rows .get (r_idx ,{})
            wbs =row .get ('B')
            if wbs :
                task_map [wbs ]={
                'code':wbs ,
                'category':row .get ('A',''),
                'short_name':row .get ('C',''),
                'description':row .get ('D',''),
                'monthly_rate':safe_float (row .get ('F')),
                'hourly_rate':safe_float (row .get ('H'))
                }
        print (f"Loaded {len (task_map )} task codes.")


        print ("Parsing Executive Summary...")
        sum_rows =get_sheet_cells ('xl/worksheets/sheet5.xml')


        project_title =sum_rows .get (2 ,{}).get ('E','50MW Humain Campus Data Center CS')
        as_of_date_serial =sum_rows .get (4 ,{}).get ('E')
        as_of_date =excel_date_to_iso (as_of_date_serial )
        currency ="SAR"
        usd_fx_rate =safe_float (sum_rows .get (48 ,{}).get ('F'),0.2666 )

        kpis ={
        'project_title':project_title ,
        'as_of_date':as_of_date ,
        'week_number':int (safe_float (sum_rows .get (8 ,{}).get ('S'),13 )),
        'currency':currency ,
        'usd_fx_rate':usd_fx_rate ,
        'weekly_burn_hours':safe_float (sum_rows .get (9 ,{}).get ('S')),
        'weekly_burn_cost':safe_float (sum_rows .get (10 ,{}).get ('S')),
        'personnel_deployed':int (safe_float (sum_rows .get (11 ,{}).get ('S'),11 )),
        'baseline':{
        'revenue':safe_float (sum_rows .get (9 ,{}).get ('F')),
        'cost':safe_float (sum_rows .get (10 ,{}).get ('F')),
        'hours':safe_float (sum_rows .get (11 ,{}).get ('F')),
        'gm':safe_float (sum_rows .get (12 ,{}).get ('F')),
        'gm_pct':safe_float (sum_rows .get (13 ,{}).get ('F'))*100 ,
        'gm_hr':safe_float (sum_rows .get (14 ,{}).get ('F'))
        },
        'pjtd':{
        'revenue':safe_float (sum_rows .get (9 ,{}).get ('G')),
        'cost':safe_float (sum_rows .get (10 ,{}).get ('G')),
        'hours':safe_float (sum_rows .get (11 ,{}).get ('G')),
        'gm':safe_float (sum_rows .get (12 ,{}).get ('G')),
        'gm_pct':safe_float (sum_rows .get (13 ,{}).get ('G'))*100 ,
        'gm_hr':safe_float (sum_rows .get (14 ,{}).get ('G'))
        },
        'etc':{
        'revenue':safe_float (sum_rows .get (9 ,{}).get ('H')),
        'cost':safe_float (sum_rows .get (10 ,{}).get ('H')),
        'hours':safe_float (sum_rows .get (11 ,{}).get ('H'))
        },
        'working_capital':{
        'unbilled':safe_float (sum_rows .get (35 ,{}).get ('F')),
        'wip':safe_float (sum_rows .get (35 ,{}).get ('G')),
        'ar':safe_float (sum_rows .get (35 ,{}).get ('H')),
        'wwoa_approved':safe_float (sum_rows .get (38 ,{}).get ('F')),
        'wwoa_spent':safe_float (sum_rows .get (38 ,{}).get ('G')),
        'wwoa_utilization_pct':safe_float (sum_rows .get (38 ,{}).get ('H'))*100 
        },
        'contingency':{
        'total_sar':safe_float (sum_rows .get (55 ,{}).get ('G')),
        'total_usd':safe_float (sum_rows .get (55 ,{}).get ('H')),
        'pm_contingency_sar':safe_float (sum_rows .get (52 ,{}).get ('G')),
        'controlled_1_sar':safe_float (sum_rows .get (53 ,{}).get ('G')),
        'controlled_2_sar':safe_float (sum_rows .get (54 ,{}).get ('G'))
        }
        }


        scope_items =[]
        scope_rows_map =[
        (20 ,'1-CS-On-Site','Labor - On-Site'),
        (21 ,'2-CS-OffSite','Labor - Off-Site'),
        (24 ,'3-HO Support','HO Support Labor'),
        (27 ,'4-Expense','Project Expenses'),
        (28 ,'5-NES','NES Labor'),
        (29 ,'6-TASC','TASC Labor'),
        (30 ,'7-Contingency','Contingency Reserve'),
        (31 ,'8-Tax & Accrual','Taxes & Accruals'),
        ]
        for r_num ,code ,name in scope_rows_map :
            row =sum_rows .get (r_num ,{})
            b_rev =safe_float (row .get ('G'))
            b_cost =safe_float (row .get ('H'))
            b_gm =safe_float (row .get ('I'))
            b_gm_pct =safe_float (row .get ('J'))*100 
            p_rev =safe_float (row .get ('K'))
            p_cost =safe_float (row .get ('L'))
            p_gm =safe_float (row .get ('M'))
            p_gm_pct =safe_float (row .get ('N'))*100 

            scope_items .append ({
            'code':code ,
            'name':name ,
            'baseline_revenue':b_rev ,
            'baseline_cost':b_cost ,
            'baseline_gm':b_gm ,
            'baseline_gm_pct':b_gm_pct ,
            'pjtd_revenue':p_rev ,
            'pjtd_cost':p_cost ,
            'pjtd_gm':p_gm ,
            'pjtd_gm_pct':p_gm_pct 
            })


        print ("Parsing GM Trend...")
        gm_rows =get_sheet_cells ('xl/worksheets/sheet17.xml')
        gm_trend =[]
        date_row =gm_rows .get (20 ,{})
        budget_row =gm_rows .get (21 ,{})
        actual_row =gm_rows .get (22 ,{})


        cols =['B','C','D','E','F','G','H','I','J','K','L','M','N']
        for idx ,col in enumerate (cols ,start =1 ):
            d_serial =date_row .get (col )
            b_val =budget_row .get (col )
            a_val =actual_row .get (col )
            if d_serial :
                date_str =excel_date_to_iso (d_serial )
                b_num =safe_float (b_val )*100 if b_val is not None else None 
                a_num =safe_float (a_val )*100 if a_val is not None else None 
                gm_trend .append ({
                'week':idx ,
                'date':date_str ,
                'budget_gm_pct':b_num ,
                'actual_gm_pct':a_num 
                })


        print ("Parsing Regional Split...")
        reg_rows =get_sheet_cells ('xl/worksheets/sheet10.xml')
        regional_split =[]
        for r_idx in [10 ,11 ,12 ]:
            row =reg_rows .get (r_idx ,{})
            source =row .get ('A')
            qty =safe_float (row .get ('B'))
            cost =safe_float (row .get ('C'))
            if source :
                regional_split .append ({
                'source':source ,
                'hours':qty ,
                'cost':cost 
                })


        print ("Parsing 4,095 Oracle Combined Transactions...")
        xml_data =z .read ('xl/worksheets/sheet20.xml')
        tree =ET .fromstring (xml_data )
        rows_elem =tree .findall ('.//ns:row',ns )


        header_row =rows_elem [0 ]
        col_names ={}
        for c in header_row .findall ('ns:c',ns ):
            ref =c .attrib .get ('r')
            col ,_ =parse_cell_ref (ref )
            t =c .attrib .get ('t')
            v =c .find ('ns:v',ns )
            val =v .text if v is not None else ''
            if t =='s'and val .isdigit ():
                val =strings [int (val )]
            col_names [col ]=val 

        transactions =[]
        staff_agg =defaultdict (lambda :{
        'name':'',
        'emp_id':'',
        'total_hours':0.0 ,
        'raw_cost':0.0 ,
        'burdened_cost':0.0 ,
        'revenue':0.0 ,
        'tasks':set (),
        'exp_types':set (),
        'projects':set (),
        'tx_count':0 
        })

        task_agg =defaultdict (lambda :{
        'task_code':'',
        'description':'',
        'category':'',
        'total_hours':0.0 ,
        'raw_cost':0.0 ,
        'burdened_cost':0.0 ,
        'revenue':0.0 ,
        'tx_count':0 ,
        'staff':set ()
        })

        exp_agg =defaultdict (lambda :{
        'exp_type':'',
        'total_hours':0.0 ,
        'burdened_cost':0.0 ,
        'revenue':0.0 ,
        'tx_count':0 
        })

        weekly_agg =defaultdict (lambda :{
        'hours':0.0 ,
        'cost':0.0 ,
        'revenue':0.0 ,
        'tx_count':0 
        })

        for r in rows_elem [1 :]:
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

            project =row_dict .get ('A','')
            task =row_dict .get ('B','')
            employee =row_dict .get ('C','')
            emp_id =row_dict .get ('D','')
            exp_type =row_dict .get ('E','')
            item_date_raw =row_dict .get ('F','')
            item_date =excel_date_to_iso (item_date_raw )
            qty =safe_float (row_dict .get ('G'))
            trans_curr =row_dict .get ('H','')
            trans_cost =safe_float (row_dict .get ('I'))
            proj_raw_cost =safe_float (row_dict .get ('K'))
            proj_burd_cost =safe_float (row_dict .get ('L'))
            accr_rev =safe_float (row_dict .get ('M'))
            bill_rate =safe_float (row_dict .get ('N'))
            bill_amt =safe_float (row_dict .get ('O'))
            billable =row_dict .get ('R','')
            pa_date =excel_date_to_iso (row_dict .get ('S',''))
            org =row_dict .get ('AK','')or row_dict .get ('AL','')


            eff_rev =accr_rev if accr_rev !=0 else bill_amt 

            tx_record ={
            'id':len (transactions )+1 ,
            'project':project ,
            'task':task ,
            'task_desc':task_map .get (task ,{}).get ('description',''),
            'employee':employee ,
            'emp_id':emp_id ,
            'exp_type':exp_type ,
            'item_date':item_date ,
            'qty':round (qty ,2 ),
            'trans_curr':trans_curr ,
            'trans_cost':round (trans_cost ,2 ),
            'raw_cost':round (proj_raw_cost ,2 ),
            'burdened_cost':round (proj_burd_cost ,2 ),
            'revenue':round (eff_rev ,2 ),
            'margin':round (eff_rev -proj_burd_cost ,2 ),
            'bill_rate':round (bill_rate ,2 ),
            'billable':billable ,
            'pa_date':pa_date ,
            'org':org 
            }
            transactions .append (tx_record )


            s =staff_agg [employee ]
            s ['name']=employee 
            s ['emp_id']=emp_id 
            s ['total_hours']+=qty 
            s ['raw_cost']+=proj_raw_cost 
            s ['burdened_cost']+=proj_burd_cost 
            s ['revenue']+=eff_rev 
            s ['tasks'].add (task )
            s ['exp_types'].add (exp_type )
            s ['projects'].add (project )
            s ['tx_count']+=1 

            t =task_agg [task ]
            t ['task_code']=task 
            t ['description']=task_map .get (task ,{}).get ('description','Other Support')
            t ['category']=task_map .get (task ,{}).get ('category','Supervision')
            t ['total_hours']+=qty 
            t ['raw_cost']+=proj_raw_cost 
            t ['burdened_cost']+=proj_burd_cost 
            t ['revenue']+=eff_rev 
            t ['tx_count']+=1 
            t ['staff'].add (employee )

            e =exp_agg [exp_type ]
            e ['exp_type']=exp_type 
            e ['total_hours']+=qty 
            e ['burdened_cost']+=proj_burd_cost 
            e ['revenue']+=eff_rev 
            e ['tx_count']+=1 

            if item_date :

                try :
                    dt =datetime .strptime (item_date ,'%Y-%m-%d')

                    week_start =(dt -timedelta (days =dt .weekday ())).strftime ('%Y-%m-%d')
                    w =weekly_agg [week_start ]
                    w ['hours']+=qty 
                    w ['cost']+=proj_burd_cost 
                    w ['revenue']+=eff_rev 
                    w ['tx_count']+=1 
                except Exception :
                    pass 


        staff_list =[]
        for emp ,s in staff_agg .items ():
            cost =round (s ['burdened_cost'],2 )
            rev =round (s ['revenue'],2 )
            margin =round (rev -cost ,2 )
            margin_pct =round ((margin /rev *100 ),1 )if rev !=0 else (0.0 if cost ==0 else -100.0 )
            avg_hourly_cost =round (cost /s ['total_hours'],2 )if s ['total_hours']>0 else 0.0 
            avg_hourly_rev =round (rev /s ['total_hours'],2 )if s ['total_hours']>0 else 0.0 

            staff_list .append ({
            'name':emp ,
            'emp_id':s ['emp_id'],
            'total_hours':round (s ['total_hours'],1 ),
            'raw_cost':round (s ['raw_cost'],2 ),
            'burdened_cost':cost ,
            'revenue':rev ,
            'margin':margin ,
            'margin_pct':margin_pct ,
            'avg_hourly_cost':avg_hourly_cost ,
            'avg_hourly_rev':avg_hourly_rev ,
            'tx_count':s ['tx_count'],
            'tasks_count':len (s ['tasks']),
            'tasks':list (s ['tasks']),
            'exp_types':list (s ['exp_types']),
            'is_negative_margin':margin <-100.0 
            })
        staff_list .sort (key =lambda x :x ['burdened_cost'],reverse =True )


        task_list =[]
        for code ,t in task_agg .items ():
            cost =round (t ['burdened_cost'],2 )
            rev =round (t ['revenue'],2 )
            margin =round (rev -cost ,2 )
            margin_pct =round ((margin /rev *100 ),1 )if rev !=0 else 0.0 
            task_list .append ({
            'task_code':code ,
            'description':t ['description'],
            'category':t ['category'],
            'total_hours':round (t ['total_hours'],1 ),
            'burdened_cost':cost ,
            'revenue':rev ,
            'margin':margin ,
            'margin_pct':margin_pct ,
            'staff_count':len (t ['staff']),
            'tx_count':t ['tx_count']
            })
        task_list .sort (key =lambda x :x ['burdened_cost'],reverse =True )


        exp_list =[]
        for exp ,e in exp_agg .items ():
            cost =round (e ['burdened_cost'],2 )
            rev =round (e ['revenue'],2 )
            margin =round (rev -cost ,2 )
            margin_pct =round ((margin /rev *100 ),1 )if rev !=0 else 0.0 
            exp_list .append ({
            'exp_type':exp ,
            'total_hours':round (e ['total_hours'],1 ),
            'burdened_cost':cost ,
            'revenue':rev ,
            'margin':margin ,
            'margin_pct':margin_pct ,
            'tx_count':e ['tx_count']
            })
        exp_list .sort (key =lambda x :x ['burdened_cost'],reverse =True )


        weekly_series =[]
        for week_date ,w in sorted (weekly_agg .items ()):
            margin =round (w ['revenue']-w ['cost'],2 )
            margin_pct =round ((margin /w ['revenue']*100 ),1 )if w ['revenue']!=0 else 0.0 
            weekly_series .append ({
            'week_start':week_date ,
            'hours':round (w ['hours'],1 ),
            'cost':round (w ['cost'],2 ),
            'revenue':round (w ['revenue'],2 ),
            'margin':margin ,
            'margin_pct':margin_pct ,
            'tx_count':w ['tx_count']
            })


    os .makedirs ('data',exist_ok =True )


    dashboard_payload ={
    'generated_at':datetime .now ().isoformat (),
    'kpis':kpis ,
    'scope_items':scope_items ,
    'gm_trend':gm_trend ,
    'regional_split':regional_split ,
    'staff_analytics':staff_list ,
    'task_analytics':task_list ,
    'exp_analytics':exp_list ,
    'weekly_series':weekly_series ,
    'transactions':transactions 
    }


    json_path ='data/dashboard_data.json'
    json_tmp ='data/dashboard_data.json.tmp'
    with open (json_tmp ,'w',encoding ='utf-8')as f :
        json .dump (dashboard_payload ,f ,indent =2 )

    for _ in range (5 ):
        try :
            if os .path .exists (json_path ):
                os .remove (json_path )
            os .replace (json_tmp ,json_path )
            break 
        except OSError :
            import time ;time .sleep (0.5 )
    print ("Saved data/dashboard_data.json")


    csv_file ='data/transactions.csv'
    csv_tmp ='data/transactions.csv.tmp'
    if transactions :
        keys =list (transactions [0 ].keys ())
        with open (csv_tmp ,'w',newline ='',encoding ='utf-8')as f :
            writer =csv .DictWriter (f ,fieldnames =keys )
            writer .writeheader ()
            writer .writerows (transactions )
        for _ in range (5 ):
            try :
                if os .path .exists (csv_file ):
                    os .remove (csv_file )
                os .replace (csv_tmp ,csv_file )
                break 
            except OSError :
                import time ;time .sleep (0.5 )
        print (f"Exported {len (transactions )} rows to {csv_file }")

    print ("Data extraction complete!")

if __name__ =='__main__':
    main ()
