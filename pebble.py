#the message client 'pebble.py'
import sys, time, pika, threading, shelve
from zeroconf import ServiceBrowser, Zeroconf

#get arguments from function call
args = sys.argv
print str(args)

#default parameters for this client
client_author = "Ben Kaija"
client_age = 22


#the zeroconf listener on the network
class MyListener(object):  
    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        # print name, info.get_name(), info.server,
        print name, info


#zeroconf = Zeroconf()  
#listener = MyListener()  
#browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)  

#try:  
#    input("Press enter when connection is found...\n\n")
#finally:  
#    zeroconf.close()


#connection to rabbitMQ callback function
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
my_q = 'hello'
channel.queue_declare(queue=my_q)

def consume_callback(ch, method, properties, body):
    print body
    connection.close()


#function to push message to the server queue
def push_mesg(subject, text):
    print 'pushing message --> '+subject+': '+text
    new_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
    pebble = {'Action':'push',
              'Author':client_author,
              'Age':client_age,
              'MsgID':'Team38_'+new_id,
              'Subject':subject,
              'Message':text
              }
    #shelve the new pebble with the key being the timestamped id
    datastore = shelve.open('local_datastore.dat')
    datastore[new_id]=pebble
    datastore.close()
    #now push the new message
    channel.basic_publish(exchange='',
                          routing_key=my_q,
                          body = pebble)
    print 'sent new pebble to queue '+my_q
    print 'waiting for response... (CTRL-C to exit)'
    channel.basic_consume(consume_callback, queue = my_q, no_ack=True)
    channel.start_consuming()


#main
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
 
