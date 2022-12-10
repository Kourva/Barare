#!/usr/bin/env python3

# Barare By Izolabela
# Github: https://github.com/Izolabela

# Imports
import random
from sys import exit
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious

# KIVY config file
with open("main.kv") as kv:
    Builder.load_string(kv.read())

# Login menu screens class
class LoginMenuScreen(Screen):

    # Check login password
    def login(self, username, errorlable):
        if username == "admin":
            self.manager.current = 'MainMenu'
        else:
            errorlable.text = "[b][color=#FF0000][font=RobotoMono-Regular]Login Failed! Try Again[/font][/color][/b]"

# Main menu screen class
class MainMenuScreen(Screen):
    pass

# Profile screen class
class ProfileScreen(Screen):
    pass

# About menu screen class
class AboutMenuScreen(Screen):
    pass

# guest menu screen class
class GuestMenuScreen(Screen):
    pass

class QMCSolverScreen(Screen):
    
    # Solver
    def solve(self, minterms, dontcares, qmcresult):
        try:
            # This function will remove repeated minterms 
            def Remove_repeated(_chart, terms):
                for i in terms:
                    for j in find_minterms(i):
                        try:
                            del _chart[j]
                        except KeyError:
                            pass

            # This function will find EPI's from PI's
            def find_EPI(x):
                output = []
                for i in x:
                    if len(x[i]) == 1:
                        output.append(x[i][0]) if x[i][0] not in output else None
                return output

            # This function will multiply 2 minterms
            def Miltiply_2_Minterm(x, y): 
                output = []
                for i in x:
                    if i + "'" in y or (len(i) == 2 and i[0] in y):
                        return []
                    else:
                        output.append(i)
                for i in y:
                    if i not in output:
                        output.append(i)
                return output

            # This function will remove don't care terms from a given list
            def Remove_Dont_cares(main_list, dont_care_list): 
                output = []
                for i in main_list:
                    if int(i) not in dont_care_list:
                        output.append(i)
                return output

            # This function will multiply 2 expressions
            def Multiply_2_Expressions(x, y): 
                output = []
                for i in x:
                    for j in y:
                        val = Miltiply_2_Minterm(i,j)
                        output.append(val) if len(val) != 0 else None
                return output

            # This function will find variables in a meanterm.
            def find_Variables(x):
                output = []
                for i in range(len(x)):
                    if x[i] == '0':
                        output.append(chr(i + 65) + "'")
                    elif x[i] == '1':
                        output.append(chr(i + 65))
                return output

            # This function is for flattens a list
            def flatten(x):
                output = []
                for i in x:
                    output.extend(x[i])
                return output

            # This function will find which minterms are merged. 
            def find_minterms(val):
                temp = val.count('-')
                if temp == 0:
                    return [str(int(val,2))]
                x = [bin(i)[2:].zfill(temp) for i in range(pow(2, temp))]
                output = []
                for i in range(pow(2,temp)):
                    output2 = val[:]
                    index = -1
                    for j in x[0]:
                        if index != -1:
                            index = index + output2[index + 1:].find('-') + 1
                        else:
                            index = output2[index + 1:].find('-')
                        output2 = output2[:index] + j + output2[index + 1:]
                    output.append(str(int(output2, 2)))
                    x.pop(0)
                return output

            # This function will check if 2 minterms differ by 1 bit only
            def compare(a, b):
                c = 0
                for i in range(len(a)):
                    if a[i] != b[i]:
                        index = i
                        c += 1
                        if c > 1:
                            return (False, None)
                return (True, index)

            # Take minterms - Add them to list and sort them
            temp1 = minterms.text.strip().split()

            mintems_list = []
            for i in temp1:
                mintems_list.append(int(i))
            mintems_list.sort()

            # Take don't cares - Add them to list
            temp2 = dontcares.text
            temp2.strip()
            temp2.split()

            dont_cares_list = []
            for i in temp2:
                dont_cares_list.append(int(i))

            # Combine minterms and don't cares
            minterms = mintems_list + dont_cares_list
            minterms.sort()

            # Take size of minterms
            size = len(bin(minterms[-1])) -2
            groups = {}
            all_pi = set()

            # Primary grouping
            for minterm in minterms:
                try:
                    groups[bin(minterm).count('1')].append(bin(minterm)[2:].zfill(size))
                except KeyError:
                    groups[bin(minterm).count('1')] = [bin(minterm)[2:].zfill(size)]

            # Creating tables and finding PI's
            while True:
                temp3 = groups.copy()
                groups = {}
                index = 0
                marked = set()
                should_stop = True

                l = sorted(list(temp3.keys()))

                for i in range(len(l) - 1):

                    # Loop which iterates through current group elements
                    for j in temp3[l[i]]:

                        # Loop which iterates through next group elements
                        for k in temp3[l[i+1]]: 

                            # Compare the minterms
                            res = compare(j, k) 

                            # If the minterms differ by 1 bit only
                            if res[0]: 
                                try:
                                    # Put a '-' in the changing bit and add it to corresponding group
                                    groups[index].append(j[:res[1]] + '-' + j[res[1] + 1:]) if j[:res[1]] + '-' + j[res[1] + 1:] not in groups[index] else None 
                                    
                                except KeyError:
                                    # If the group doesn't exist, create the group at first and then put a '-' in the changing bit and add it to the newly created group
                                    groups[index] = [j[:res[1]]+'-'+j[res[1]+1:]]
                                    
                                should_stop = False
                                marked.add(j) # Mark element j
                                marked.add(k) # Mark element k

                    index += 1

                # Unmarked elements of each table
                local_unmarked = set(flatten(temp3)).difference(marked)

                # Adding Prime Implicants to global list (PI)
                all_pi = all_pi.union(local_unmarked) 

                if should_stop:
                    # Print all prime implicants if should_stop is True
                    All_PIS = None if len(all_pi) == 0 else f', '.join(all_pi)
                    break

            # Generating PI chart 
            sz = len(str(mintems_list[-1])) # The number of digits of the largest minterm
            chart = {}
                         
            for i in all_pi:
                merged_minterms = find_minterms(i)
                y = 0

                for j in Remove_Dont_cares(merged_minterms, dont_cares_list):
                    x = mintems_list.index(int(j)) * (sz + 1) # The position where we should put '*'
                        
                    y = x + sz
                    try:
                        # Add minterm in chart
                        chart[j].append(i) if i not in chart[j] else None 
                        
                    except KeyError:
                        chart[j] = [i]

            # Find EIP from given chart
            EPI = find_EPI(chart) 
             
            # Remove repeated EPI from chart
            Remove_repeated(chart,EPI) 

            # If no repeated minterms
            if(len(chart) == 0): 
                # Final result with only EPIs
                final_result = [find_Variables(i) for i in EPI] 

            else:
                P = [[find_Variables(j) for j in chart[i]] for i in chart]
                    
                # Keep multiplying until we get the SOP form of P
                while len(P)>1: 
                    P[1] = Multiply_2_Expressions(P[0],P[1])
                    P.pop(0)

                # Choosing the term with minimum variables from P    
                final_result = [min(P[0],key=len)] 

                # Adding the EPIs to final solution
                final_result.extend(find_Variables(i) for i in EPI)

            Final_Output =(f'F = ' + ' + '.join(''.join(i) for i in final_result))
            qmcresult.text = Final_Output

        except IndexError as ie:
            qmcresult.text = f"[b][color=#FF0000]Error[/color]!\n\n{ie}\nEnter at least one minterm[/b]"
        except ValueError as ve:
            qmcresult.text = f"[b][color=#FF0000]Error[/color]!\n\n{ve}\nEnter valid numbers[/b]"

# Main class
class BarareApp(App):

    # Build function
    def build(self):

        # root screen manager
        self.root = ScreenManager()
        
        # Login menu screen
        self.LoginMenuScreen = LoginMenuScreen(name='LoginMenu')
        self.root.add_widget(self.LoginMenuScreen)

        # Main menu screen
        self.MainMenuScreen = MainMenuScreen(name='MainMenu')
        self.root.add_widget(self.MainMenuScreen)

        # About menu screen
        self.AboutMenuScreen = AboutMenuScreen(name='AboutMenu')
        self.root.add_widget(self.AboutMenuScreen)

        # Profile screen
        self.ProfileScreen = ProfileScreen(name='Profile')
        self.root.add_widget(self.ProfileScreen)

        # Guest menu screen
        self.GuestMenuScreen = GuestMenuScreen(name='GuestMenu')
        self.root.add_widget(self.GuestMenuScreen)

        # QMC solver screen
        self.QMCSolverScreen = QMCSolverScreen(name='QMCsolver')
        self.root.add_widget(self.QMCSolverScreen)

        # Set current screen to Login menu and return root   
        self.root.current = 'LoginMenu'
        return self.root

# run the class
BarareApp().run()