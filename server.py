import socket
from _thread import *
import sys
import json
server = "ip_address"
port = 5555
currentPlayer = 1
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
import _pickle as pickle
try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(1)
print("Waiting for a connection, Server Started")

connected = []

players = {}
died = []
connections = 0

data = {
        'p1' :{'posx':100,'posy':200,'speed':0,
            'changeangle':1,'angle':90},
        'p2' : {'posx':200,'posy':300,'speed':0,
            'changeangle':2,'angle':90},
        'p3' :{'posx':300,'posy':400,'speed':0,
            'changeangle':1,'angle':90},
        'p4' : {'posx':400,'posy':500,'speed':0,
            'changeangle':2,'angle':90}
        
        }

def threaded_client(conn, player):
    global data, players, connections, died



    current_id = player
    players[current_id] = {'id':current_id, 'posx':100,'posy':100,
    'angle':90, 'shoot':0,'bx':0,'by':0,'bullet_angle':0,'alive': True,'score':0
    }
    
    
    
    conn.send(str.encode(str(current_id)))
    while True:
    
        try:
            
       
            received_data = conn.recv(1024)
            players[current_id]['shoot'] = 0
            
            if not received_data:
                print("Disconnected")
                break
            
            received_data = received_data.decode('utf-8')



            if players[current_id]['alive'] == True:
    
                try:
                    if received_data.split(" ")[0] == 'move':
                        
                        players[current_id]['posx'] = received_data.split(" ")[1]
                        players[current_id]['posy'] = received_data.split(" ")[2]
                        players[current_id]['angle'] = received_data.split(" ")[3]
                        players[current_id]['score'] = received_data.split(" ")[4]
        
                except  Exception as e:
                    print('sss', e)
                    
                if received_data.split(" ")[0] == 'bullet':
                    players[current_id]['shoot'] = 1
                    players[current_id]['bullet_angle'] = received_data.split(" ")[4]
                    players[current_id]['posx'] = received_data.split(" ")[1]
                    players[current_id]['posy'] = received_data.split(" ")[2]
                    players[current_id]['angle'] = received_data.split(" ")[3]
                    players[current_id]['bx'] = received_data.split(" ")[5]
                    players[current_id]['by'] = received_data.split(" ")[6]
                    players[current_id]['score'] = received_data.split(" ")[7]
                
                if received_data.split(" ")[0] == 'del':
                    enemy_id = received_data.split(" ")[1]
                    players[int(enemy_id)]['alive'] = False



            
            send_data = pickle.dumps((players))
            #data[player] = received_data
    
          

            conn.send(send_data)
        
           
        except Exception as e:
            print('server error', e)
            break

    print("Lost connection")
    connections -=1
    try:
        del players[current_id]
    except :
        pass


    conn.close()


while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    connections +=1
    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1
