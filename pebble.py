#the message client 'pebble.py'
import sys, time, json, pika, threading, shelve, socket, uuid
from zeroconf import ServiceBrowser, Zeroconf

#get arguments from function call
args = sys.argv
print str(args)

#default parameters for this client
client_author = "Ben Kaija"
client_age = 22

#global config_found
config_found = False

#the zeroconf listener on the network
class MyListener(object):  
    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        try:
            info = zeroconf.get_service_info(type, name)
        except:
            print "ZeroConfig error"
        
        #wait until it finds
        if  'TEAM_38_BOTTLE' in name:
            print name
            global server_host
            global config_found
            
            server_host = socket.inet_ntoa(info.address)
            #allow spinning loop to exit
            config_found= True

zeroconf = Zeroconf()  
listener = MyListener()  
browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)  

#wait untill the device parameter have been disocvered
while(config_found == False):
    time.sleep(1)
    pass

#end the zeroconf communication
zeroconf.close()

print 'raspberrypi server found! establishing connection to: '+server_host

#connection to rabbitMQ callback function

#my_q = 'team_38_bottle'

class RpcClient(object):
    def __init__(self, address):
        self.creds = pika.credentials.PlainCredentials('team_38_user', 'micro')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=address, virtual_host='team_38', credentials=self.creds))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)
        print "connected to server located at: "+address

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='team_38_bottle',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=n)
        while self.response is None:
            self.connection.process_data_events()
        return self.response

pebble_rpc = RpcClient(server_host)


def consume_callback(ch, method, properties, body):
    print body
    response = json.loads(body)
    print response
    connection.close()


#function to push message to the server queue
def send_push_req(subject, text):
    print 'pushing message --> '+subject+': '+text
    new_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
    pebble = {'Action':'push',
              'Author':client_author,
              'Age':client_age,
              'MsgID':'Team38_'+new_id,
              'Subject':subject,
              'Message':text
              }
    json_pebble = json.dumps(pebble)
    #shelve the new pebble with the key being the timestamped id
    datastore = shelve.open('local_datastore.dat')
    datastore[new_id]=pebble
    datastore.close()
    #now push the new message
    resp = pebble_rpc.call(json_pebble)
    print "Response: "+ resp

#pull
def send_pull_req(age, author, msg, sub):
    print 'Sending pull request to find: '+age+' '+author+' '+msg+' '+sub
    pebble = {'Action':'pull',
              'Age':age,
              'Author':author,
              'Subject':sub,
              'Message':msg
              }
    json_pebble = json.dumps(pebble)
    resp = pebble_rpc.call(json_pebble)
    print "Response: "+ resp

#pullr
def send_pullr_req(age, author, msg, sub):
    print 'Sending pullr request to find: '+age+' '+author+' '+msg+' '+sub
    pebble = {'Action':'pullr',
              'Age':age,
              'Author':author,
              'Subject':sub,
              'Message':msg
              }
    json_pebble = json.dumps(pebble)
    resp = pebble_rpc.call(json_pebble)
    print "Response: "+ resp

#main
if len(args) < 3:
    print 'no action requested'
else:
    if(args[1] == '-a'):
        if(args[2]=='push'):
            #print 'do push action'	
            if(len(args) == 7 and args[3]=='-s' and args[5]=='-m'):
                send_push_req(args[4], args[6])
            else:
                print 'incorrect number of arguments'
                
        elif(args[2]=='pull' or args[2]=='pullr'):
            #print 'do pull/pullr action'
            #parse quereies
            age_req = ''
            author_req = ''
            mesg_req = ''
            sub_req = ''

            for i in range(3, len(args)):
                # print args[i]
                #age
                if(args[i]=='-Qa'):
                    age_req = args[i+1]
                #author
                elif(args[i]=='-QA'):
                    author_req = args[i+1]
                #message
                elif(args[i]=='-Qm'):
                    mesg_req = args[i+1]
                #subject
                elif(args[i]=='-Qs'):
                    sub_req = args[i+1]
            
            if(args[2]=='pull'):
                send_pull_req(age_req, author_req, mesg_req, sub_req)
            else:
                send_pullr_req(age_req, author_req, mesg_req, sub_req)
        else:
            print 'the requested operation is not available'
 
#end
