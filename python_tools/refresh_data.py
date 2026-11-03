import os 
import sys 
import subprocess 

def run_step (desc ,script_name ,*args ):
    print (f"\n[+] {desc }...")
    cmd =[sys .executable ,script_name ]+list (args )
    res =subprocess .run (cmd ,capture_output =True ,text =True )
    if res .returncode !=0 :
        print (f"Error in {script_name }:\n{res .stderr }")
        return False 
    print (res .stdout .strip ())
    return True 

def main ():
    print ("="*65 )
    print ("  SA859CMS Cost Report Data Processing & Dashboard Pipeline")
    print ("="*65 )


    if not run_step ("Cleaning Excel workbook (removing defined names bloat)","clean_excel_names.py"):
        return 


    if not run_step ("Extracting transactions, KPIs, and scope analytics","export_dashboard_data.py"):
        return 


    if not run_step ("Re-compiling interactive dashboard.html","build_dashboard.py"):
        return 

    print ("\n"+"="*65 )
    print ("  Pipeline complete! You can view the dashboard by:")
    print ("   1. Double-clicking 'dashboard.html' in Windows Explorer, OR")
    print ("   2. Running: python run_dashboard.py")
    print ("="*65 )

if __name__ =='__main__':
    main ()

