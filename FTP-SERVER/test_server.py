# Echo server program
import socket
import sys
import os

def remove_prefix(s, prefix):
    return s[len(prefix):] if len(s)-len(prefix)>0 else "/"
#print(os.path.exists("/home/el/myfile.txt"))

def read_from_file(filename, s):
    
    f = open(filename,'rb')
    l = f.read(1024)
    while (l):
        l = l.decode()
        l = l.replace('\\', '\\\\')
        l = l.replace("$", r"\$")
        l = str.encode(l)
        conn.send(l)
        print('Sent ',repr(l))
        l = f.read(1024)
    f.close()
    
    conn.send(b'')
    print('Done sending')
    
def write_to_file(filename, conn):
    with open(tokens[1], 'wb') as f:
        print('file opened')
        marker = ""
        while True:
            # print('receiving data...')
            if len(marker) > 1 and not marker[-2] == '\\':
                break
            if len(marker) == 1 and marker[-1:] == "$":
                break
            data = s.recv(1024)
            marker = data[-2:]
            # write data to a file
            data = data.decode()
            data = data.replace('\\\\', '\\')
            data = data.replace(r"\$", "$")
            data = str.encode(data)
            f.write(data)
    f.close()

root = os.getcwd()

HOST = None               # Symbolic name meaning all available interfaces
PORT = sys.argv[1]              # Arbitrary non-privileged port
s = None
for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
                              socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except OSError as msg:
        s = None
        continue
    try:
        s.bind(sa)
        s.listen(1)
    except OSError as msg:
        s.close()
        s = None
        continue
    break
if s is None:
    print('could not open socket')
    sys.exit(1)
conn, addr = s.accept()

with conn:
    print('Connected by', addr)
    while True:
        data_b = conn.recv(1024)
        data = data_b.decode()
        tokens = data.split()
        if len(tokens) == 0: break
        # print(tokens[0])
        if tokens[0] == "NLST":
            print("ls server")
            if len(tokens) == 1:
                path = os.getcwd()                
            else:
                path = root+"/"+tokens[1]
                if not os.path.isdir(path):
                    print("Invalid directory name.", path)
                    result = "Invalid directory name."
                    conn.send(str.encode(result))
                    continue

            files = os.listdir(path)
            result = ""
            for name in files:
                result = result +"\n"+ name
            
            conn.send(str.encode(result))

        elif tokens[0] == "CWD":
            print("CWD server")
            if len(tokens) == 1:
                path = root
            else:
                path = root+"/"+tokens[1]

            print(path)
            local_path = ""
            if not os.path.isdir(path):
                print("Invalid directory name.", path)
                local_path = "Illegal CWD operation."                                
            else:
                os.chdir(path)
                local_path = remove_prefix(path,root)
                # if len(local_path) == 0:
                #     local_path = "/"
            conn.send(str.encode(local_path))

        elif tokens[0] == "RETR":
            print("getting server")
            curr_path = os.getcwd()
            
            #dirname is not provided
            if os.path.exists(curr_path+"/"+tokens[1]):
                conn.send(b'1')     #file exist                
                # read_from_file(tokens[1],s)
                    
                f = open(tokens[1],'rb')
                l = f.read(1024)
                while (l):
                    l = l.decode()
                    l = l.replace('\\', '\\\\')
                    l = l.replace("$", r"\$")
                    l = str.encode(l)
                    conn.send(l)
                    print('Sent ',repr(l))
                    l = f.read(1024)
                f.close()
                
                conn.send(b'')
                print('Done sending')
                                                
            else:
                conn.send(b'0')
                #file DNE
                print(remove_prefix(curr_path+"/"+tokens[1],root), "does not exist")             
            
        elif tokens[0] == "STOR":
            conn.send(b"OK to SEND file")
            print("OK")
            # write_to_file(tokens[1],conn)
            with open(tokens[1], 'wb') as f:
                print('file opened')
                marker = " "
                while True:
                    print('receiving data...', marker, len(marker), str(marker[-1]))
                    if len(marker) > 1 and not marker[-2] == 92:
                        break
                    if len(marker) == 1 and marker[-1] == 36:
                        break
                    data = conn.recv(1024)
                    marker = data[-2:]
                    # write data to a file
                    data = data.decode()
                    data = data.replace('\\\\', '\\')
                    data = data.replace(r"\$", "$")
                    data = str.encode(data)
                    f.write(data)
            f.close()

            print("written")
            conn.send(b"File Recieved")
            print('Successfully get the file')

        elif tokens[0] == "PWD":
            print("server pwd")
            res = os.getcwd()
            res = remove_prefix(res, root)
            conn.send(str.encode(res))
            print("sendnig", res)
        elif tokens[0] == "QUIT":
            conn.close()