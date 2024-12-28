import subprocess
import threading
import sys

def read_server_output(server_process):
    while True:
        output = server_process.stdout.readline()
        if output == '' and server_process.poll() is not None:
            break
        if output:
            print(f"{output.strip()}")

def interact_with_server(server_process):
    while True:

        user_input = input("")
        if user_input.strip().lower() == "exit":
            print("Fermeture du serveur...")
            server_process.stdin.write("exit\n")
            server_process.stdin.flush()
            break
        server_process.stdin.write(user_input + "\n")
        server_process.stdin.flush()

server_process = subprocess.Popen(['java', '-jar', 'server.jar'], 
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

subprocess.Popen(['python', 'Bubble.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
subprocess.Popen(['python', 'WonderGUI.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

output_thread = threading.Thread(target=read_server_output, args=(server_process,))
output_thread.daemon = True  
output_thread.start()

interact_with_server(server_process)