'''
@author Bailey Freund RPG
@date 3/21/18
'''

import random

'''
    Observable class. Inherited by game objects to be observed by observer objects
'''
class Observable(object):

    '''
    initialize the observable object
    '''
    def __init__(self):    
        self.observers = []

    '''
    Adds a new observer to the list of observers
    @param observer the observer be added to the list
    '''
    def add_observer(self, observer):
        if not observer in self.observers:
            self.observers.append(observer)

    '''
    removes an observer from the list
    @param observer the observer to be removed
    '''
    def remove_observe(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)

    '''
    removes all observers from the list
    '''
    def remove_all_observers(self):
        self.observers = []

    '''
    function called when the object changes data that the observers need to know about
    '''
    # @abstractmethod
    def on_change(self):
        pass

'''
an object which observes other objects
'''
class Observer(object):
    '''
    this is called when the object being observed changes state
    @param observable_obj the object being observed
    '''
    # @abstractmethod
    def update(self, observable_obj):
        pass


'''
Neighborhood stores the map and the game state
'''
class Neighborhood(Observer):
    '''
    initialize neighborhood with a number of rows and cols
    @param rows
    @param cols
    '''
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.houses = [[0 for x in range(cols)] for y in range(rows)] # https://snakify.org/lessons/two_dimensional_lists_arrays/ 

        for i in range(cols):
            for j in range(rows):
                self.houses[i][j] = House(random.randint(1,4), self) #init houses with between 1 and 4 monsters
    

    '''
    Implement the update method of observable. 
    @param who_is_calling which object is calling. May be of type 'player' or 'house'
    '''
    def update(self, who_is_calling):
        if who_is_calling == 'player':
            print('You have died. Game Over.')
            exit()
        elif who_is_calling == 'house':
            for i in range(self.cols):
                for j in range(self.rows):
                    if self.houses[i][j].cleared:
                        continue
                    else: # if house isn't cleared
                        print("Nice job clearing that house, but there's more work to be done..")
                        return 0
            print('All houses cleared! You win the game!')
            exit() # exit the game

    '''
    Loop through all the monsters who have been turned into people and 
    give the player health regen candy every turn
    @player the player to give health to
    '''
    def get_candy(self, player):
        for i in range(self.cols):
            for j in range(self.rows):
                for monster in self.houses[i][j].monsters:
                    if not monster.is_monster:
                        monster.give_candy(player) # get candy from every person who was transformed every turn



'''
There is 1 house in every tile of the game.
Each house contains 1 to 4 monsters.
Houses observe their monsters and are observed by the neighborhood.
'''
class House(Observer, Observable):
    '''
    initialize the house with a number of monsters, and in a specific neighborhood
    @param num_monsters the number of monsters in the house
    @param neighborhood the neighborhood the house is in
    '''
    def __init__(self, num_monsters, neighborhood): #must be passed a map of neighbors
        self.type = 'house'
        self.observers = []
        self.cleared = False
        self.monsters = [0 for i in range(num_monsters)]
        self.num_monsters = num_monsters
        monster_types = {
            0: 'zombie',
            1: 'vampire',
            2: 'ghoul',
            3: 'werewolf'
        }

        for i in range(len(self.monsters)): #init monsters
            monster_type = monster_types[random.randint(0,3)]
            monster_name = monster_type +  str(i)
            self.monsters[i] = Monster( self, monster_type, monster_name )

        self.add_observer(neighborhood)
    

    '''
    Implement the update method of the observer class. 
    Called when a monster is transformed to a person.
    '''
    def update(self):
        for monster in self.monsters:
            if monster.is_monster == False:
                continue
            else: # if there is still a monster in the house
                print('There are still monsters in the house!')
                return 0
        print('No more monsters in the house.')
        self.cleared = True
        self.on_change() #notify the neighborhood that the house is cleared
        return 1

    '''
    Implement the observable on_change function.
    Called once the house has been completely cleared of monsters.
    '''
    def on_change(self):
        for observer in self.observers:
            observer.update(self.type)


'''
Monster class. 
Observed by house.
'''
class Monster(Observable):

    '''
    Initialize monster.
    @param house the house the monster is in
    @param monster_type the type of monster it is
    @monster_name the name of the monster
    '''
    def __init__(self, house, monster_type, monster_name):
        super(Monster, self).__init__()
        self.add_observer( house )
        self.name = monster_name

        self.monster_type = monster_type
        monster_hp = {
            'zombie': random.randint(50,100),
            'vampire': random.randint(100,200),
            'ghoul': random.randint(40,80),
            'werewolf': 200
        }
        self.hp = monster_hp[self.monster_type]
        self.is_monster = True

    '''
    Called once per turn.
    All monsters in the house that the player is in attack if able. 
    @param player the player being attacked
    '''
    def attack(self, player):
        monster_type = self.monster_type
        monster_attack = {
            'zombie': random.randint(0,10),
            'vampire': random.randint(10,20),
            'ghoul': random.randint(15,30),
            'werewolf': random.randint(0,40)
        }
        dmg = monster_attack[monster_type]
        print('%s does %s damage' % (self.name, dmg) )
        player.hp = player.hp - dmg # do the actual damage
        print('You now have %s hp' % player.hp)
        player.on_attacked()

    '''
    Called when the monster is attacked. 
    Checks if the monster has been transformed yet.
    @param player the player attacking the monster
    '''
    def on_attacked(self, player):
        if self.hp <= 0:
            self.is_monster = False
            self.give_candy(player) # give the player candy because you are human now
            self.on_change()
    
    '''
    Implementation of the observer on_change function. 
    Called when the monster transforms.
    Notifies the house the monster is in that the monster is no longer a monster.
    '''
    def on_change(self):
        for observer in self.observers:
            observer.update()
    
    '''
    Give the player 1 candy which regens 1 health.
    @param player the player to give health.
    '''
    def give_candy(self, player):
        player.hp = player.hp + 1

'''
The player of the game.
'''
class Player(Observable):

    '''
    Initialize the player. 
    Observed by neighborhood.
    @param game_map instance of Neighborhood. Used for tracking position. 
    Player starts at [0,0]
    '''
    def __init__(self, game_map):
        super(Player, self).__init__()
        self.type = 'player'
        self.add_observer(game_map)
        self.alive = True
        self.hp = random.randint(100,125)
        print('You have %s hp' % self.hp)
        first_weapon = Weapon('kiss', 'kiss') #every player gets a weapon
        self.weapons = {
            first_weapon.name: first_weapon #generate 1st weapon
        }

        potential_weapons = {
            1: 'sourstraw',
            2: 'chocolate',
            3: 'nerd'
        }

        for i in range(9): #generate the rest of the weapons randomly
            this_weapon = potential_weapons[random.randint(1,3)]
            weapon_name = this_weapon + str(i)
            w = Weapon( weapon_name, this_weapon )

            self.weapons[weapon_name] = w #put into map

        self.x_pos = 0 #player always starts at the northwest corner of the map (that's where their house is :D )
        self.y_pos = 0

    
    '''
    Attack a monster with a weapon
    @param weapon being used to attack
    @param monster being attack
    '''
    def attack(self, weapon, monster):
        dmg = random.uniform(10,20) * weapon.modifier # attack is between 0 and 40 times the damage modifier
        monster.hp = monster.hp - dmg
        monster.on_attacked(self)
        weapon.decrement(self)
        print('You attack %s with %s and do %s damage' % (monster.name, weapon.name, dmg ))
        print('%s has %s hp remaining' %(monster.name, monster.hp))

    '''
    Checks if move is valid, then moves player if it is.
    @param direction north south east or west
    @param game_map instance of Neighborhood
    '''
    def move(self, direction, game_map):
        directions = {
            'north': -1,
            'south': 1,
            'east': 1,
            'west': -1
        }
        try:
            if direction == 'north' or direction == 'south':
                if self.y_pos + directions.get(direction) >= 0 and self.y_pos + directions.get(direction) < game_map.rows:
                    self.y_pos = self.y_pos + directions.get(direction)
                else: 
                    print("You can't go that way!")
                    new_direction = input('Where would you like to go (north, south, east, or west)?')
                    self.move(new_direction, game_map)
            if direction == 'east' or direction == 'west':
                if self.x_pos + directions.get(direction) >= 0 and self.x_pos + directions.get(direction) < game_map.cols:
                    self.x_pos = self.x_pos + directions.get(direction)
                else: 
                    print("You can't go that way!")
                    new_direction = input('Where would you like to go (north, south, east, or west)?')
                    self.move(new_direction, game_map)

        except:
            print("You can't go that way!")
            new_direction = input('Where would you like to go (north, south, east, or west)?')
            self.move(new_direction, game_map)  

    '''
    Called whenever the player is attacked to check if they are still alive or not.
    '''
    def on_attacked(self):
        if self.hp <= 0:
            self.alive = False
            self.on_change()
        else:
            return
    
    '''
    Implement Observer on_change function.
    Called when the player is no longer alive. 
    Triggers 'Game Over' :'(
    '''
    def on_change(self):
        for observer in self.observers:
            observer.update(self.type)


'''
Weapon class
'''
class Weapon():
    '''
    Initialize weapon
    @param name of the weapon
    @param weapon_type which type of weapon is it (kiss, sourstraw, chocolate, or nerd)
    '''
    def __init__(self, name, weapon_type):
        self.name = name
        self.weapon_type = weapon_type
        modifiers = {
            'kiss': 1,
            'sourstraw': random.uniform(1,1.75),
            'chocolate': random.uniform(2,2.4),
            'nerd': random.uniform(3.5,5)
        }
        self.modifier = modifiers.get(self.weapon_type)
        uses = {
            'kiss': 1000000000000, # effectively infinite
            'sourstraw': 2,
            'chocolate': 4,
            'nerd': 1
        }
        self.uses = uses.get(self.weapon_type)

    '''
    Decrements the number of uses for the weapon.
    @param player the player who owns the weapon
    '''
    def decrement(self, player):
        self.uses = self.uses - 1
        if self.uses <= 0:
            self.on_change(player)
        else:
            return
    
    '''
    Called when the weapon no longer has any uses
    @param player the owner of the weapon
    '''
    def on_change(self, player):
        player.weapons.pop(self.name, 0) # https://docs.python.org/2/library/stdtypes.html


'''
Main method
Sets up game and has game looping logic.
'''
if __name__ == '__main__':
    game_map = Neighborhood(3,3) # set up neighborhood
    me = Player(game_map)

    while (True):
        current_house = game_map.houses[me.x_pos][me.y_pos]
        if current_house.cleared:
            direction = input('Where would you like to go (north, south, east, or west)?')
            me.move(direction, game_map)
        elif (current_house.cleared == False): # then the house has monsters!
            print('You are in house at %s, %s' % (me.x_pos, me.y_pos)) # https://stackoverflow.com/questions/15286401/print-multiple-arguments-in-python
            print('You see monsters ' )
            for monster in current_house.monsters:
                if monster.is_monster: #only print the monsters that haven't been beaten yet
                    print(monster.name)

            print('You have weapons: %s' % me.weapons.keys())
            attack_weapon_str = input('Which weapon would you like to attack with?\n')
            attack_weapon = me.weapons.get(attack_weapon_str)
            for m in current_house.monsters:
                me.attack(attack_weapon, m)
                if(m.is_monster): #only attack the player if you haven't been turned yet
                    m.attack(me)
            


        else: 
            cmd = input('House cleared, where would you like to go next? \n')
        
        game_map.get_candy(me)
        


