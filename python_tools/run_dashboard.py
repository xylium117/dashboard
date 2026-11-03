import http .server 
import socketserver 
import webbrowser 
import os 
import sys 

PORT =8050 

class QuietHandler (http .server .SimpleHTTPRequestHandler ):
    def log_message (self ,format ,*args ):

        sys .stderr .write (f"[{self .log_date_time_string ()}] {format %args }\n")

def main ():
    os .chdir (os .path .dirname (os .path .abspath (__file__ )))


    port =PORT 
    server =None 
    for p in range (PORT ,PORT +20 ):
        try :
            server =socketserver .TCPServer (("",p ),QuietHandler )
            port =p 
            break 
        except OSError :
            continue 

    if not server :
        print ("Error: Could not bind to any open port between 8050 and 8070.")
        return 

    url =f"http://localhost:{port }/dashboard.html"
    print ("="*70 )
    print ("  SA859CMS COST REPORT - INTERACTIVE VISUALIZATION DASHBOARD")
    print ("="*70 )
    print (f" Dashboard URL: {url }")
    print (" Opening dashboard in your default browser...")
    print (" Press Ctrl+C in this terminal to stop the server.")
    print ("="*70 )

    webbrowser .open (url )

    try :
        server .serve_forever ()
    except KeyboardInterrupt :
        print ("\nStopping dashboard server. Goodbye!")
        server .server_close ()

if __name__ =='__main__':
    main ()

