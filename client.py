class Client():
    def __init__(self, parameter_list):
        self.name = "Client"
    
    def if_exists_client(self, filename):
        #check if file exists in client directory
        pass

    def if_exists_server(self, filename):
        #check if file exists in client directory
        pass

    def get(self, filename, dirname = ""):
        if len(dirname) == 0:
            if(if_exists_server(filename)):
                #retrieve the file
            else:
                print("File does not exist in server.")
        else:
            


    def put(self, filename, dirname = ""):
        if len(dirname) == 0:
            if(if_exists_client(filename)):
                #store in current directory at server
                #Retrieve the specified file, if it exists at the server.
                # !!!!!!!!!!!!!!!!!!!!!!                 
            else:
                print("File does not exist at client directory.")
        else:

        pass

    def pwd(self):
        #print current directory
        pass
    
    def quit(self):
        #close files and socket
        pass