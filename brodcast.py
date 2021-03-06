import zeroconf
import socket
 
server = zeroconf.Zeroconf()
 
# Get local IP address
local_ip = socket.gethostbyname(socket.gethostname())
local_ip = socket.inet_aton(local_ip)
 
svc1 = zeroconf.ServiceInfo('_http._tcp.local.',
                              'bottle 1._http._tcp.local.',
                              address = local_ip,
                              port = 2972,
                              weight = 0, priority=0,
                              properties = {'description':
                                            'Departmental server'}
                             )
server.register_service(svc1)
