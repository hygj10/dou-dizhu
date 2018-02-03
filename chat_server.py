import time
import socket
import select
import sys
import string
import indexer
import pickle as pkl
from chat_utils import *
import chat_group as grp
import random
import Doudizhu_Roles

class Server:
    def __init__(self):
        self.new_clients = [] #list of new sockets of which the user id is not known
        self.logged_name2sock = {} #dictionary mapping username to socket
        self.logged_sock2name = {} # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        self.ddz = Doudizhu_Roles
        self.turn = []
        #start server
        self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        #initialize past chat indices
        self.indices={}
        # sonnet
        self.sonnet_f = open('AllSonnets.txt.idx', 'rb')
        self.sonnet = pkl.load(self.sonnet_f)
        self.sonnet_f.close()
        
    def new_client(self, sock):
        #add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        #read the msg that should have login code plus username
        msg = myrecv(sock)
        if len(msg) > 0:
            code = msg[0]

            if code == M_LOGIN:
                name = msg[1:]
                if self.group.is_member(name) != True:
                    #move socket from new clients list to logged clients
                    self.new_clients.remove(sock)
                    #add into the name to sock mapping
                    self.logged_name2sock[name] = sock
                    self.logged_sock2name[sock] = name
                    #load chat history of that user
                    if name not in self.indices.keys():
                        try:
                            self.indices[name]=pkl.load(open(name+'.idx','rb'))
                        except IOError: #chat index does not exist, then create one
                            self.indices[name] = indexer.Index(name)
                    print(name + ' logged in')
                    self.group.join(name)
                    mysend(sock, M_LOGIN + 'ok')
                else: #a client under this name has already logged in
                    mysend(sock, M_LOGIN + 'duplicate')
                    print(name + ' duplicate login attempt')
            else:
                print ('wrong code received')
        else: #client died unexpectedly
            self.logout(sock)

    def logout(self, sock):
        #remove sock from all lists
        name = self.logged_sock2name[sock]
        pkl.dump(self.indices[name], open(name + '.idx','wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

#==============================================================================
# main command switchboard
#==============================================================================
    def handle_msg(self, from_sock):
        #read msg code 
        msg = myrecv(from_sock)
        if len(msg) > 0:
            print("Server is here! ")
            code = msg[0]           
#==============================================================================
# handle connect request
#==============================================================================
            if code == M_CONNECT:
                to_name = msg[1:]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = M_CONNECT + 'hey you'
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = M_CONNECT + 'ok'
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, M_CONNECT + from_name)
                else:
                    msg = M_CONNECT + 'no_user'
                mysend(from_sock, msg)
#==============================================================================
# handle message exchange   
#==============================================================================
            elif code == M_EXCHANGE:
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                said = msg[1:]
                said2 = text_proc(said, from_name)
                self.indices[from_name].add_msg_and_index(said2)
                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]
                    self.indices[g].add_msg_and_index(said2)                
                    mysend(to_sock, msg)
                    
            ###############################
            elif code == M_CARDS:
                from_name = self.logged_sock2name[from_sock]
                whoseturn = self.turn[len(self.group.card_on_table) % 3]
                n_of_guys = len(self.group.list_me(from_name))
                
                # Check there are excatly 3 people in the group
                if n_of_guys != 3:
                    mysend(from_sock, " You need 3 members!")
                else:
                    
                # Check Whose turn this is
                    if from_name != whoseturn:
                        mysend(from_sock, " It's not your turn")
                    else:
                        the_guys = self.group.list_me(from_name)
#                        print(msg[-4:])
#                        print(str(msg[-4:]) == "pass") 

                # If the player choose to pass                           
                        if str(msg[-4:]) == "pass":
                            if len(self.group.card_on_table) == 0:
                                mysend(from_sock, " You can NOT play this!")
                            else:
                                self.group.card_on_table.append([])
                                for g in the_guys[1:]:
                                    to_sock = self.logged_name2sock[g]            
                                    mysend(to_sock, msg)
                                                                
                        else:
                            try:                           
                                said = msg[1:]
                                print(said)
                                saidcopy = said[:]
                                list1 = saidcopy.split(" ")
                                del list1[0]
                                cardlist = list1
                                print(cardlist)
                                
                                #newlist has JQKA2
                                newlist = []
                                for i in cardlist:
                                    if i == "11":
                                        newlist.append("J")
                                    elif i == "12":
                                        newlist.append("Q")
                                    elif i == "13":
                                        newlist.append("K")
                                    elif i == "14":
                                        newlist.append("A")
                                    elif i == "15":
                                        newlist.append("TWO")
                                    elif i == "16":
                                        newlist.append("BlackJoker")
                                    elif i == "17":
                                        newlist.append("RedJoker")
                                    else:
                                        newlist.append(int(i))
                                
                                print(newlist)
                                
                                output = ""
                                for i in newlist:
                                    output += str(i) + " "
                                
                                int_cardlist = []
                                for i in cardlist:
                                    int_cardlist.append(int(i))
                                
                                # If he is the first one to play
                                if len(self.group.card_on_table) == 0:
#                                    print("This is condition1.")
#                                    print(int_cardlist)
                                    ok = self.ddz.isAplay(int_cardlist)
                                    print(ok)
                                    if ok:
                                        said2 = from_name + "played:" + text_proc(said, from_name)
                                        self.group.play_card(int_cardlist)
                                        for a in newlist:
                                            print(self.group.card_decks[from_name])
                                            self.group.card_decks[from_name].remove(a)
                                        mysend(from_sock, M_CARDS + " ".join(str(e) for e in self.group.card_decks[from_name]))
                                        for g in the_guys[1:]:
                                            to_sock = self.logged_name2sock[g]            
                                            mysend(to_sock, " " + "[" + from_name + "] " + output)
                                    else:
                                        mysend(from_sock, " You can NOT play this!")
                                
                                # If the former player has played
                                elif self.group.card_on_table[-1] != []:
#                                    print("This is condition2.")
                                    ok = self.ddz.validplay(int_cardlist, self.group.card_on_table[-1])                                              
                                    if ok:
                                        said2 = from_name + "played:" + text_proc(said, from_name)
                                        self.group.play_card(int_cardlist)
                                        for a in newlist:
                                            print(self.group.card_decks[from_name])
                                            self.group.card_decks[from_name].remove(a)
                                        mysend(from_sock, M_CARDS + " ".join(str(e) for e in self.group.card_decks[from_name]))
                                        for g in the_guys[1:]:
                                            to_sock = self.logged_name2sock[g]            
                                            mysend(to_sock, " " + "[" + from_name + "] " + output)
                                    else:
                                        mysend(from_sock, " You can NOT play this!")
                                
                                # If the former player passed and the one former that played
                                elif len(self.group.card_on_table) > 1 and self.group.card_on_table[-2] != []:
#                                    print("This is condition3.")
                                    ok2 = self.ddz.validplay(int_cardlist, self.group.card_on_table[-2])
                                    if ok2:
                                        said2 = from_name + "played:" + text_proc(said, from_name)
                                        self.group.play_card(int_cardlist)
                                        for a in newlist:
                                            print(self.group.card_decks[from_name])
                                            self.group.card_decks[from_name].remove(a)
                                        mysend(from_sock, M_CARDS + " ".join(str(e) for e in self.group.card_decks[from_name]))
                                        for g in the_guys[1:]:
                                            to_sock = self.logged_name2sock[g]            
                                            mysend(to_sock, " " + "[" + from_name + "] " + output)
                                    else:
                                        mysend(from_sock, " You can NOT play this!")
                                
                                # If the former player and the one before him neither played
                                elif len(self.group.card_on_table) > 1 and self.group.card_on_table[-2] == [] and self.group.card_on_table[-1] == []:
                                    ok = self.ddz.isAplay(int_cardlist)
                                    if ok:
#                                        print("This is condition4.")
                                        said2 = from_name + "played:" + text_proc(said, from_name)
                                        self.group.play_card(int_cardlist)
                                        for a in newlist:
                                            print(self.group.card_decks[from_name])
                                            self.group.card_decks[from_name].remove(a)
                                        mysend(from_sock, M_CARDS + " ".join(str(e) for e in self.group.card_decks[from_name]))
                                        for g in the_guys[1:]:
                                            to_sock = self.logged_name2sock[g]            
                                            mysend(to_sock, " " + "[" + from_name + "] " + output)
                                    else:
                                        mysend(from_sock, " You can NOT play this!")
                            
                            
                            except:
                                mysend(from_sock, " You can NOT play this!")
                                
                if len(self.group.card_decks[from_name]) == 0:
                    mysend(from_sock, " You Win!")
                    the_guys = self.group.list_me(from_name)
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]            
                        mysend(to_sock, " You Lose!")                                            

                        
            elif code == M_PLAY:
#                print("where are you")
                to_name = msg[1:]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = M_PLAY + 'hey you'
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.game_connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = M_PLAY + 'ok'
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, M_PLAY + from_name)
                else:
                    msg = M_PLAY + 'no_user'
                    
                from_name = self.logged_sock2name[from_sock]
                n_of_guys = len(self.group.list_me(from_name))
                if n_of_guys == 3:
                    deck = []
                    the_guys = self.group.list_me(from_name)
                    quarter_deck = [3,4,5,6,7,8,9,10,11,12,13,14,15]
                    for card in quarter_deck:
                        for i in range(4):
                            deck.append(card)
                    deck.append(17)
                    deck.append(16)
                    random.shuffle(deck)
                    hand1 = deck[0:17]
                    hand2 = deck[17:34]
                    hand_lord = deck[34:]
                    hand1.sort();hand2.sort();hand_lord.sort()                    
#                    print(hand1, hand2, hand_lord)
                    self.group.set_card_decks(the_guys[0], hand1)
                    self.group.set_card_decks(the_guys[1], hand2)
                    self.group.set_card_decks(the_guys[2], hand_lord)
                    self.turn.append(the_guys[2]); self.turn.append(the_guys[0]); self.turn.append(the_guys[1]);                    
                    cardlist = self.group.card_decks
                    for i in cardlist.values():
                        for n, e in enumerate(i):
                            print("this is e: ", i[n])
                            if e == 11:
                                i[n] = "J"
                            elif e == 12:
                                i[n] = "Q"
                            elif e == 13:
                                i[n] = "K"
                            elif e == 14:
                                i[n] = "A"
                            elif e == 15:
                                i[n] = "TWO"
                            elif e == 16:
                                i[n] = "BlackJoker"
                            elif e == 17:
                                i[n] = "RedJoker"
                            print("this is e: ", i[n])
                        
                    for g in the_guys:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, M_CARDS + " ".join(str(e) for e in cardlist[g]))
                    
                mysend(from_sock, msg)
                    
            
            ###############################
#==============================================================================
#listing available peers
#==============================================================================
            elif code == M_LIST:
                from_name = self.logged_sock2name[from_sock]
                msg = self.group.list_all()
                mysend(from_sock, msg)
#==============================================================================
#retrieve a sonnet
#==============================================================================
            elif code == M_POEM:
                poem_indx = int(msg[1:])
                from_name = self.logged_sock2name[from_sock]
                print(from_name + ' asks for ', poem_indx)
                poem = self.sonnet.get_sect(poem_indx)
                print('here:\n', poem)
                mysend(from_sock, M_POEM + poem)
#==============================================================================
#time
#==============================================================================
            elif code == M_TIME:
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, ctime)
#==============================================================================
#search
#==============================================================================
            elif code == M_SEARCH:
                term = msg[1:]
                from_name = self.logged_sock2name[from_sock]
                print('search for ' + from_name + ' for ' + term)
                search_rslt = (self.indices[from_name].search(term)).strip()
                print('server side search: ' + search_rslt)
                mysend(from_sock, M_SEARCH + search_rslt)
#==============================================================================
# the "from" guy has had enough (talking to "to")!
#==============================================================================
            elif code == M_DISCONNECT:
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, M_DISCONNECT)
                    

#==============================================================================
#the "from" guy really, really has had enough
#==============================================================================
            elif code == M_LOGOUT:
                self.logout(from_sock)
        else:
            #client died unexpectedly
            self.logout(from_sock)   

#==============================================================================
# main loop, loops *forever*
#==============================================================================
    def run(self):
        print ('starting server...')
        while(1):
           read,write,error=select.select(self.all_sockets,[],[])
           print('checking logged clients..')
           for logc in list(self.logged_name2sock.values()):
               if logc in read:
                   self.handle_msg(logc)
           print('checking new clients..')
           for newc in self.new_clients[:]:
               if newc in read:
                   self.login(newc)
           print('checking for new connections..')
           if self.server in read :
               #new client request
               sock, address=self.server.accept()
               self.new_client(sock)
           
def main():
    server=Server()
    server.run()

main()
