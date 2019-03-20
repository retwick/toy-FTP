# Echo server program
import socket
import sys
import os

def remove_prefix(s, prefix):
    return s[len(prefix):] if s.startswith(prefix) else s
#print(os.path.exists("/home/el/myfile.txt"))

root = os.getcwd()

HOST = None               # Symbolic name meaning all available interfaces
PORT = 50005              # Arbitrary non-privileged port
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

        if tokens[0] == "ls":
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
            # print(result)
            # print("end")
            conn.send(str.encode(result))
        elif tokens[0] == "cd":
            print("cd server")
            if len(tokens) == 1:
                path = root
            else:
                path = root+"/"+tokens[1]
            print(path)
            local_path = ""
            if not os.path.isdir(path):
                print("Invalid directory name.", path)
                local_path = "Invalid directory name."
                conn.send(str.encode(local_path))
                # continue
            else:
                os.chdir(path)
                local_path = remove_prefix(path,root)            
            conn.send(str.encode(local_path))
        elif tokens[0] == "get":
            print("getting server")
            curr_path = os.getcwd()
            if len(tokens) == 2:
                #dirname is not provided
                if os.path.exists(curr_path+"/"+tokens[1]):
                    conn.send(b'1')
                    # print("file exists.")
                    #file exists
                    filename=tokens[1]
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
                    # conn.send('Thank you for connecting')
                else:
                    conn.send(b'0')
                    #file DNE
                    print(remove_prefix(curr_path+"/"+tokens[1],root), "does not exist") 
            elif len(tokens) == 3:
                #dirname and filename provided
                if os.path.isdir(root+"/"+tokens[2]):
                    os.chdir(root+"/"+tokens[2])                
                    local = os.getcwd()
                    if os.path.exists(local+"/"+tokens[1]):
                        conn.send(b'1') #file exists                    
                        filename=tokens[1]
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
                        
                    else:
                        conn.send(b'0') #file DNE
                else:
                    conn.send(b'2')     #directory doesnt exist at server


        elif tokens[0] == "put":
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
            print('Successfully get the file')


            # with open('received_file', 'wb') as f:
            #         print 'file opened'
            #         while True:
            #             print('receiving data...')
            #             data = s.recv(1024)
            #             print('data=%s', (data))
            #             if not data:
            #                 break
            #             # write data to a file
            #             f.write(data)
            pass
        # if not data_b: break
        # conn.send(data_b)