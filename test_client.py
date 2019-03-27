# Echo client program
import socket
import sys
import os

def remove_prefix(s, prefix):
    return s[len(prefix):] if len(s)-len(prefix)>0 else "/"

def recieve_to_file(filename, s):
    with open(filename, 'wb') as f:
        marker = " "
        while True:            
            # try:
            #     print(marker, "-----", marker[-1], marker[-2])
            # except:
            #     print(marker, "-----", marker[-1])

            if len(marker) == 1 and marker[-1:] == ord('$') or len(marker) > 1 and not marker[-2] == ord('\\') and marker[-1]== ord("$"):                
                break
            # print('reciev')
            data = s.recv(1024)
            # print(data)
            marker = data[-2:]
            if len(marker) == 1 and marker[-1:] == ord("$") or len(marker) > 1 and not marker[-2] == ord('\\') and marker[-1]== ord("$"):
                data = data[:-1]
            if not data: 
                break
            data = data.replace(b'\\\\', b'\\')
            data = data.replace(b"\$", b"$")
            f.write(data)
    f.close()
    print('Successfully get the file')

def send_from_file(filename,s):
    f = open(filename,'rb')
    l = f.read(1024)
    while (l):        
        l = l.replace(b'\\', b'\\\\')
        l = l.replace(b"$", b"\$")        
        s.send(l)
        l = f.read(1024)
    f.close()
    
    s.send(b'$')
    print('Done sending to server')
    

root = os.getcwd()

HOST = sys.argv[1]        # The remote host
PORT = sys.argv[2]        # The same port as used by the server
s = None
for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except OSError as msg:
        s = None
        continue
    try:
        s.connect(sa)
    except OSError as msg:
        s.close()
        s = None
        continue
    break
if s is None:
    print('could not open socket')
    sys.exit(1)
with s:
    while True:
        command = input('$ ')
        tokens = command.split()
        if tokens[0] == "ls":
            # send to server: NLST <>
            server_command = "NLST" + command[2:]
            s.sendall(str.encode(server_command))
            result = s.recv(10000)
            print(result.decode())
            
        elif tokens[0] == "cd":
            # send to server: CWD <>
            server_command = "CWD"+command[2:]
            s.sendall(str.encode(server_command))
            result = s.recv(1024)
            print(result.decode())
        elif tokens[0] == "lcd":
            # no server call
            if len(tokens) == 1:
                os.chdir(root)
                print("/")
            else:
                #check if valid directory
                if os.path.isdir(root+"/"+tokens[1]):
                    os.chdir(root+"/"+tokens[1])
                    full_path = os.getcwd()
                    local_path = remove_prefix(full_path,root)
                    print(local_path)
                else:
                    print(tokens[1], "does not exist.")
        elif tokens[0] == "get":
            
            if len(tokens) > 3:
                print("Invalid Command")
            else:
                #CWD <dirname>
                if len(tokens) == 3:                    
                    server_command = "CWD " + tokens[2]
                    s.sendall(str.encode(server_command))
                    result = s.recv(1024)
                    if result.decode() == "Illegal CWD operation.":
                        #directory DNE
                        print(result.decode())
                        continue
                    else:
                        print("Changed directory to ", result)
                #RETR <filename>
                server_command = "RETR "+ tokens[1]                
                s.sendall(str.encode(server_command))
                # s.sendall(str.encode(command))
                result = s.recv(1024)
                if result.decode() == "1":
                    #FILE NAME OK
                    recieve_to_file(tokens[1],s)
                elif result.decode() == "0":
                    print("File does not exist at server")
                
        elif tokens[0] == "put":
            curr_path = os.getcwd()
                                       
            if not os.path.isfile(curr_path+"/"+tokens[1]):
                print(tokens[1], "does not exist")
                continue 

            if len(tokens) == 2:
                #dirname is not provided
                server_command = "STOR"+ command[3:]
                s.sendall(str.encode(server_command))
                response = s.recv(1024)
                print(response)
                send_from_file(tokens[1], s)
                response = s.recv(1024)
                print(response)

            elif len(tokens) == 3:
                server_command = "CWD " + tokens[2]
                s.sendall(str.encode(server_command))
                response = s.recv(1024)
                print(response.decode())
                if response == b"Illegal CWD operation.":
                    continue
                server_command = "STOR " + tokens[1]
                s.sendall(str.encode(server_command))
                response = s.recv(1024)
                send_from_file(tokens[1], s)
                response = s.recv(1024)
                print(response)

        elif tokens[0] == "pwd":
            dirpath = os.getcwd()
            dirpath = remove_prefix(dirpath, root)
            if len(dirpath) == 0:
                dirpath = "/"
            print("current dir at client:", dirpath)
            server_command = "PWD"
            s.sendall(str.encode(server_command))
            response = s.recv(1024)
            print("Directory at server:", response.decode())
            # print(response.decode())

        elif tokens[0] == "quit":
            print("quiting")
            command = "QUIT"
            s.sendall(str.encode(command))
            s.close()
            sys.exit(1)
                
    data = s.recv(1024)    
