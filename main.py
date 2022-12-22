
import arcade
import os
import math
import _pickle as pickle

import socket
import json
HOST = "192.168.55.103"
PORT = 5555

from network import Network



import threading
file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_path)

SPRITE_SCALING = 0.35
WALL_SCALING = 0.2
SPRITE_SCALING_BULLET = 0.5

SCREEN_WIDTH = 1024
WIDTH = 1024
SCREEN_HEIGHT = 768
HEIGHT = 768
SCREEN_TITLE = "Move Sprite by Angle Example"
data = {
        'p1' :{'posx':100,'posy':200,'speed':0,
            'changeangle':0,'angle':90},
        'p2' : {'posx':200,'posy':300,'speed':0,
            'changeangle':0,'angle':90},
        'p3' :{'posx':300,'posy':400,'speed':0,
            'changeangle':0,'angle':90},
        'p4' : {'posx':400,'posy':500,'speed':0,
            'changeangle':0,'angle':90}
        
        }
currentPlayer =''
players= {}
    
activeplayers = list(data.keys())


cp = {}
MOVEMENT_SPEED = 3
ANGLE_SPEED = 2
BULLET_SPEED = 7

isConnected = True

class Enemy(arcade.Sprite):
    def __init__(self,image,scale):
        super().__init__(image,scale)
        self.speed = 0
    def update(self):
        pass


class Player(arcade.Sprite):
    """ Player class """

    def __init__(self, image, scale):
        """ Set up the player """

        # Call the parent init
        super().__init__(image, scale)

        # Create a variable to hold our speed. 'angle' is created by the parent
        self.speed = 0

    def update(self):
        # Convert angle in degrees to radians.
        global data

        if self.left <0:
            self.left = 0
        elif self.right > SCREEN_WIDTH -1 :
            self.right = SCREEN_WIDTH - 1
        
        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT -1:
            self.top = SCREEN_HEIGHT-1
        
        angle_rad = math.radians(self.angle)
        

        # Rotate the ship
        self.angle += self.change_angle
        

        # Use math to find our change based on our speed and angle
        self.center_x += -self.speed * math.sin(angle_rad)
        self.center_y += self.speed * math.cos(angle_rad)
        

class MenuView(arcade.View):

    def __init__(self):
        super().__init__()
        self.total_time = 5.0
        self.setup()
        self.isConnected = True
        global isConnected

      
    def setup(self):
        """
        Set up the application.
        """
        arcade.set_background_color(arcade.color.WHITE)
        self.total_time = 6.0
        #threading.Thread(target=move_enemies).start()

    def on_draw(self):
       
        arcade.start_render()
        
        # Calculate minutes'
        if(isConnected) :
            arcade.draw_text("TANK WARS", SCREEN_WIDTH/2-120, SCREEN_HEIGHT/2+100, arcade.color.BLACK, 30)
            arcade.draw_text("Click Anywhere to start game"+ currentPlayer, SCREEN_WIDTH/2-200, SCREEN_HEIGHT/2+200, arcade.color.BLACK, 30)

        else:
        
            arcade.draw_text("waiting for connection", SCREEN_WIDTH/2, SCREEN_HEIGHT/2+300, arcade.color.BLACK, 30)
    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        """
        
        self.total_time -= delta_time
   
        if(self.total_time < 0.0):
            game = GameView()
            self.window.show_view(game)

        self.on_draw()
    def on_mouse_press(self, _x, _y, _button, _modifiers):
        Wait = WaitView()
        self.window.show_view(Wait)

class  WaitView(arcade.View):
    def __init__(self):
        super().__init__()
        self.total_time = 5.0
        self.setup()
      
    def setup(self):
        """
        Set up the application.
        """
        arcade.set_background_color(arcade.color.WHITE)
        self.total_time = 6.0

    def on_draw(self):
       
        arcade.start_render()
        
        # Calculate minutes
        minutes = int(self.total_time) // 60

        # Calculate seconds by using a modulus (remainder)
        seconds = int(self.total_time) % 60

        # Figure out our output
        output = f"Game starts in {seconds:01d}"

        # Output the timer text.
        arcade.draw_text(output, SCREEN_WIDTH/2-160, SCREEN_HEIGHT/2, arcade.color.BLACK, 30)
    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        """
        
        self.total_time -= delta_time
   
        if(self.total_time < 0.0):
            game = GameView()
            self.window.show_view(game)

        self.on_draw()
   
    
        

enemies = {}


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        global enemies,cp
        self.player_list = None
        self.wall_list = None
        # Set up the player info
        self.player_sprite = None
        self.bullet_list = None
        self.enemy_list = None
        self.enemy = None
        self.view_bottom = 0
        self.view_left = 0
        self.p1 = None
        self.p2 = None
        self.p3 = None
        self.p4 = None
        self.enemies=[]
        self.score = 0
        self.enemies_bullet = None
        self.bullet = None
        self.server = Network()
        self.players ={}
        # Set the background color
        self.bullet_angle = 0
        
        self.current_id = self.server.connect('TK')
        self.players = self.server.send('get')
     
        self.setup()



    def setup(self):
        """ Set up the game and initialize the variables. """
        global cp
        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.enemies_bullet = arcade.SpriteList()

        # Set up the player
        file_path = "assets/Hull_0"+ str(self.current_id%4+1) +".png"
        print(file_path)
                
        self.player_sprite = Player(file_path, SPRITE_SCALING)
        self.player_sprite.center_x = self.players[self.current_id]['posx']
        self.player_sprite.center_y = self.players[self.current_id]['posy']
        self.player_list.append(self.player_sprite)

        """
        for n in range(3,6):
            self.enemy = Player("assets/Hull_01.png", SPRITE_SCALING)
            self.enemy.center_x = SCREEN_WIDTH / n+1
            self.enemy.center_y = SCREEN_HEIGHT / n+1
            self.enemy_list.append(self.enemy)


        """
        

        for x in range(200, 650, 26):
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", WALL_SCALING)
            wall.center_x = x
            wall.center_y = 200
            self.wall_list.append(wall)


       
        for s in activeplayers:
            if s != currentPlayer:
                file_path = "assets/Hull_0"+ str(self.current_id%4+1) +".png"
          
                self.enemy = Enemy(file_path, SPRITE_SCALING)
                self.enemy.center_x = data[s]['posx']
                self.enemy.center_y = data[s]['posy']
          
                self.enemy_list.append(self.enemy)
                enemies[s] = self.enemy
       
           
            
    
        
        for y in range(0, int((SCREEN_HEIGHT)/4), 26):
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", WALL_SCALING)
            wall.center_x = 110
            wall.center_y = y+100
            self.wall_list.append(wall)

        for y in range(0, int((SCREEN_HEIGHT)/4), 26):
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", WALL_SCALING)
            wall.center_x = 200
            wall.center_y = y+600
            self.wall_list.append(wall)

        """top square"""
        for x in range(470,520,26):
            for y in range(600,700,26):
                wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", WALL_SCALING)
                wall.center_x = x
                wall.center_y = y
                self.wall_list.append(wall)
        
        for y in range(0, int((SCREEN_HEIGHT)/4), 26):
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", WALL_SCALING)
            wall.center_x = 100
            wall.center_y = y+500
            self.wall_list.append(wall)

        """RIght center"""
        for x in range(0, int((SCREEN_HEIGHT)/4), 26):
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", WALL_SCALING)
            wall.center_x = x
            wall.center_y = 360
            self.wall_list.append(wall)

        """SQUARE"""
        for x in range(400,500,26):
            for y in range(300,400,26):
                wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", WALL_SCALING)
                wall.center_x = x
                wall.center_y = y
                self.wall_list.append(wall)


                """top_middle"""
        for x in range(300,900,26):
            for y in range(0,250,26):
                wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", WALL_SCALING)
                if(x>550):
                    wall.center_x = x-200
                    wall.center_y = 520
                else:
                    wall.center_x = 600
                    wall.center_y = y+520

                
                self.wall_list.append(wall)






        for y in range(0, SCREEN_HEIGHT, 26):
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", WALL_SCALING)
            wall.center_x = SCREEN_WIDTH
            wall.center_y = y
            self.wall_list.append(wall)
        for y in range(0, SCREEN_HEIGHT, 26):
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", WALL_SCALING)
            wall.center_x = 0
            wall.center_y = y
            self.wall_list.append(wall)
        for x in range(0, SCREEN_WIDTH+64, 26):
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", WALL_SCALING)
            wall.center_x = x
            wall.center_y = SCREEN_HEIGHT
            self.wall_list.append(wall)

        for x in range(0, SCREEN_WIDTH+64, 26):
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", WALL_SCALING)
            wall.center_x = x
            wall.center_y = 0
            self.wall_list.append(wall)


        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite,
                                                         self.wall_list)
        self.physics  = arcade.PhysicsEngineSimple(self.player_sprite,self.enemy_list)
        self.bullet_physics = arcade.PhysicsEngineSimple(self.player_sprite, self.enemies_bullet)
        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)
        

    def on_draw(self):
        """
        Render the screen.
        """
        global enemies

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.player_list.draw()
        self.wall_list.draw()
        self.bullet_list.draw()
        self.enemy_list.draw()
        self.enemies_bullet.draw()
        
        try:
            score_text = f"Score: {self.score}"
            if self.players[self.current_id]['alive'] == False:
                score_text = f"YOU DIED"
                arcade.draw_text(score_text, SCREEN_WIDTH/2, SCREEN_HEIGHT/2,
                            arcade.csscolor.WHITE, 18)
            else:
                score_text = f"Score: {self.score}"
                arcade.draw_text(score_text, 10+ self.view_left, 10+self.view_bottom,
                            arcade.csscolor.WHITE, 18)

            if self.players != None:
                for n in self.players:
                    score_text = f"Player {self.current_id} : {self.players[n]['score']}"

                    arcade.draw_text(score_text, SCREEN_WIDTH-100,SCREEN_HEIGHT-n*30 ,
                                arcade.csscolor.WHITE, 18)
        except :
            arcade.draw_text("YOU DIED", SCREEN_WIDTH/2, SCREEN_HEIGHT/2,
                            arcade.csscolor.WHITE, 18)


        

    def on_update(self, delta_time):
        """ Movement and game logic """
        
        
            
        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        """
        print(self.player_sprite.center_x,
            self.player_sprite.center_y,
            self.player_sprite.angle,
            self.player_sprite.change_angle,

        )
        
        for s in activeplayers:
          
            if s == 'p1':
                self.p1.center_x = p1[0][s]['posx']
                self.p1.center_y = p1[0][s]['posy']
                self.p1.speed = p1[0][s]['speed']
                self.p1.change_angle = 0
              
            elif s == 'p2':
                self.p2.center_x = p2[0][s]['posx']
                self.p2.center_y = p2[0][s]['posx']
                self.p2.speed = p2[0][s]['speed']
                self.p2.change_angle = p2[0][s]['changeangle']
                self.enemy_list.append(self.p2)
            elif s == 'p3':
                self.enemy.center_x = p3[0][s]['posx']
                self.enemy.center_y = p3[0][s]['posx']
                self.enemy.speed = p3[0][s]['speed']
                self.enemy.change_angle = p3[0][s]['changeangle']
                self.enemy_list.append(self.enemy)
            elif s == 'p4':
                self.enemy.center_x = p4[0][s]['posx']
                self.enemy.center_y = p4[0][s]['posx']
                self.enemy.speed = p4[0][s]['speed']
                self.enemy.change_angle = p4[0][s]['changeangle']
                self.enemy_list.append(self.enemy)
        """
        
        
        self.physics_engine.update()
        self.physics.update()
        self.bullet_physics.update()
        self.player_list.update()
        self.bullet_list.update()
        self.enemy_list.update()
        self.enemies_bullet.update()
        
        send_data = "move "+str(self.player_sprite.center_x)+" "+str(self.player_sprite.center_y)+" "+str(self.player_sprite.angle)+" "+str(self.score)
       

        if len(self.bullet_list) >0 and len(self.bullet_list) <=1 :
            
            send_data = "bullet "+str(self.player_sprite.center_x)+" "+str(self.player_sprite.center_y)+" "+str(self.player_sprite.angle)+" "+str(self.bullet_angle)+" "+str(self.bullet.center_x)+" "+str(self.bullet.center_y)+" "+str(self.score)
      
        self.players = self.server.send(send_data)
       
        
            
        """
        for n in self.players:
            print('player', self.players[n]['id'])
            if int(self.players[n]['id']) != str(self.current_id):
                if len(self.enemies) > self.players[n]['id']:
                    if self.enemies[self.players[n]['id']] != '':
                        self.enemies[n].center_x =  float(self.players[n]['posx'])
                        self.enemies[n].center_y =  float(self.players[n]['posy'])    
                else:
                    self.enemy = Enemy("assets/Hull_01.png", SPRITE_SCALING)
                    self.enemy.center_x = float(self.players[n]['posx'])
                    self.enemy.center_y = float(self.players[n]['posy'])
                    self.enemy_list.append(self.enemy)
                    self.enemies.append(self.enemy)
        """

        for n in self.enemy_list:
            n.remove_from_sprite_lists()
        for n in self.enemies_bullet:
            n.remove_from_sprite_lists()

        

        try:
            for n in self.players:
                
        
                if self.players[n]['id'] != self.current_id:
                    file_path = "assets/Hull_0"+ str(n%4+1) +".png"
                    self.enemy = Enemy(file_path, SPRITE_SCALING)
                    self.enemy.center_x = float(self.players[n]['posx'])
                    self.enemy.center_y = float(self.players[n]['posy'])
                    self.enemy.angle = float(self.players[n]['angle'])
                    self.enemy._id = self.players[n]['id']
                    self.enemy_list.append(self.enemy)

            
                    if str(self.players[n]['shoot']) == str(1):
                        print(self.players[n])
                        bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING_BULLET)
                # The image points to the right, and we want it to point up. So
                # rotate it.

                        
                        angle_rad = math.radians(float(self.players[n]['angle']))
                        bullet.center_x = float(self.players[n]['bx'])
                        bullet.center_y = float(self.players[n]['by'])
                        bullet.angle = float(self.players[n]['bullet_angle'])

                        self.enemies_bullet.append(bullet)

                        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.enemies_bullet)
                        if(len(hit_list)>0):
                            print('hit')
                            self.server.send("desl ")
        except :
            print('You Dies')



                #self.enemies.append(self.enemy)


        
   


        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.wall_list)
            if(len(hit_list)>0):
                bullet.remove_from_sprite_lists()
            

            if bullet.bottom > SCREEN_HEIGHT:
                bullet.remove_from_sprite_lists()
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            if(len(hit_list)>0):
                self.score +=100
                bullet.remove_from_sprite_lists()
            for enemy in hit_list:
                if(enemy in self.enemy_list):
                
                    self.server.send("del "+str(enemy._id))
                    enemy.remove_from_sprite_lists()

                
    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        
        if self.players[self.current_id]['alive'] == True:
            if key == arcade.key.ESCAPE:
                # pass self, the current view, to preserve this view's state
                pause = PauseView(self)
                self.window.show_view(pause)
            # Forward/back
            if key == arcade.key.UP:
                self.player_sprite.speed = MOVEMENT_SPEED
                
            elif key == arcade.key.DOWN:
                self.player_sprite.speed = -MOVEMENT_SPEED
                


            # Rotate left/right
            elif key == arcade.key.LEFT:
                self.player_sprite.change_angle = ANGLE_SPEED
            elif key == arcade.key.RIGHT:
                self.player_sprite.change_angle = -ANGLE_SPEED
            if key == arcade.key.SPACE :

                if len(self.bullet_list) < 1:
                    self.bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING_BULLET)
                # The image points to the right, and we want it to point up. So
                # rotate it.
                    

                    angle_rad = math.radians(self.player_sprite.angle)
                    rotate = self.player_sprite.angle
                    self.bullet.angle = rotate-90
                    
                    self.bullet.center_x = self.player_sprite.center_x 
                    self.bullet.center_y = self.player_sprite.center_y
            
                    rotate = self.player_sprite.angle
                    self.bullet.angle = rotate-90
                    self.bullet_angle = self.bullet.angle
                    self.bullet.change_x = -BULLET_SPEED * math.sin(angle_rad)
                    self.bullet.change_y = BULLET_SPEED * math.cos(angle_rad)


                    # Give the bullet a speed
                
                    # Position the bullet
                    
                
                    # Add the bullet to the appropriate lists
                    self.bullet_list.append(self.bullet)
            
            

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.speed = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_angle = 0

class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

    def on_show(self):
        arcade.set_background_color(arcade.color.ORANGE)

    def on_draw(self):
        arcade.start_render()

        # Draw player, for effect, on pause screen.
        # The previous View (GameView) was passed in
        # and saved in self.game_view.
        player_sprite = self.game_view.player_sprite
        player_sprite.draw()

        # draw an orange filter over him
        arcade.draw_lrtb_rectangle_filled(left=player_sprite.left,
                                          right=player_sprite.right,
                                          top=player_sprite.top,
                                          bottom=player_sprite.bottom,
                                          color=arcade.color.ORANGE + (200,))

        arcade.draw_text("PAUSED", WIDTH/2, HEIGHT/2+50,
                         arcade.color.BLACK, font_size=50, anchor_x="center")

        # Show tip to return or reset
        arcade.draw_text("Press Esc. to return",
                         WIDTH/2,
                         HEIGHT/2,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")
        arcade.draw_text("Press Enter to reset",
                         WIDTH/2,
                         HEIGHT/2-30,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.ESCAPE:   # resume game
            self.window.show_view(self.game_view)
        elif key == arcade.key.ENTER:  # reset game
            game = GameView()
            self.window.show_view(game)

def control_enemies(player):
    global enemies
   
    while player:
        enemies[player].center_x = data[player]['posx']
        enemies[player].center_y = data[player]['posy']
  

    

def move_enemies():
    global socket
    global enemies
    global isConnected
  
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket:
        global data
        global currentPlayer,isConnected

        socket.connect((HOST, PORT))
        currentPlayer = (socket.recv(2048)).decode()
        isConnected = True
        
        
        while True:
            socket.sendall(json.dumps(data[currentPlayer]).encode())
            response = socket.recv(2048)
            if not response:
                break
            
            data = eval(response.decode())
          
            for n in enemies.keys():
                if n == 'p2':
                    pass
                   
                enemies[n].center_x = data[n]['posx']
                enemies[n].center_y = data[n]['posy']
                enemies[n].angle = data[n]['angle']


            
            
        
        socket.close()
        for n in enemies.keys():
            enemies[n].speed = 5
   

def main():
    window = arcade.Window(WIDTH, HEIGHT, "Instruction and Game Over Views Example")
    menu = MenuView()
    window.show_view(menu)
    arcade.run()
   


if __name__ == "__main__":
    main()