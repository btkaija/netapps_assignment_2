#the message client 'pebble.py'
import sys, time
args = sys.argv
print str(args)

client_authot = "Ben Kaija"
client_age = 22

def push_mesg(subject, text):
    print 'pushing message --> '+subject+': '+text
    new_id = time.strftime("%Y%m%d%H%M%S", time.localtime())

if len(args) < 3:
    print 'no action requested'
else:

    if(args[1] == '-a'):
        if(args[2]=='push'):
            print 'do push action'	
            if(len(args) == 7 and args[3]=='-s' and args[5]=='-m'):
                push_mesg(args[4], args[6])
            else:
                print 'incorrect number of arguments'
                
        elif(args[2]=='pull'):
            print 'do pull action'
		
        elif(args[2]=='pullr'):
            print 'do pullr action'

        else:
            print 'The requested operation is not available'
 
