# Echo server program
import socket
import sys
import os

def remove_prefix(s, prefix):
    return s[len(prefix):] if len(s)-len(prefix)>0 else "/"
def valid_path(s,pre):
    return s.startswith(pre)

root = os.getcwd()

HOST = None                     # Symbolic name meaning all available interfaces
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
while True:
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data_b = conn.recv(1024)
            data = data_b.decode()
            tokens = data.split()
            if len(tokens) == 0: break
            if tokens[0] == "NLST":
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
                current_path = os.getcwd()
                
                if len(tokens) == 1:
                    path = root                    
                else:
                    path = current_path+"/"+tokens[1]

                local_path = ""
                if not os.path.isdir(path):
                    print("Invalid directory name.", path)
                    local_path = "Illegal CWD operation."                                
                else:                    
                    os.chdir(path)                    
                    if not os.getcwd().startswith(root):
                        conn.send(b'Illegal operation')
                        os.chdir(current_path)
                        continue
                    local_path = remove_prefix(os.getcwd(),root)                
                    # if len(local_path) == 0:
                    #     local_path = "/"
                conn.send(str.encode(local_path))

            elif tokens[0] == "RETR":
                curr_path = os.getcwd()
                
                #dirname is not provided
                if os.path.isfile(curr_path+"/"+tokens[1]):
                    conn.send(b'1')     #file exist                
                    # read_from_file(tokens[1],s)
                    
                    f = open(tokens[1],'rb')
                    l = f.read(1024)
                    while (l):
                        # print("")
                        
                        # print(l)
                        if not l:
                            break
                        l = l.replace(b'\\', b'\\\\')
                        l = l.replace(b"$", b"\$")
                        # l = str.encode(l)
                        conn.send(l)
                        l = f.read(1024)

                    f.close()
                    # print('send EOF')
                    conn.send(b'$')
                                                    
                else:
                    conn.send(b'0')
                    #file DNE
                    print(remove_prefix(curr_path+"/"+tokens[1],root), "does not exist")             
                
            elif tokens[0] == "STOR":
                conn.send(b"OK to SEND file")
                print("Client receiving file")
                # write_to_file(tokens[1],conn)
                with open(tokens[1], 'wb') as f:
                    marker = " "
                    while True:
                        flag = False
                        # print(marker)
                        if len(marker) == 1 and marker[-1:] == b'$' or len(marker) > 1 and not marker[-2] == b'\\' and marker[-1]==b"$":
                            flag = True
                            break
                        # print('rec')
                        data = conn.recv(1024)
                        # print(data)
                        marker = data[-2:]
                        if flag:
                            data = data[:-1]
                        if not data: 
                            break
                        # write data to a file
                        # data = data.decode()
                        data = data.replace(b'\\\\', b'\\')
                        data = data.replace(b"\$", b"$")
                        # data = str.encode(data)
                        f.write(data)
                f.close()

                conn.send(b"File Recieved")

            elif tokens[0] == "PWD":
                res = os.getcwd()
                res = remove_prefix(res, root)
                conn.send(str.encode(res))
            elif tokens[0] == "QUIT":
                path = root
                os.chdir(root)
                conn.close()
                break