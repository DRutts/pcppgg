from otree.api import *

import time


doc = """
Your app description
"""

# ======================
#       MODEL PART
# ======================

class C(BaseConstants):
    NAME_IN_URL = 'PCP_I'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1  

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass



class Player(BasePlayer):
    Q2_2 = models.IntegerField()





# ======================
#    CALCULATION PART
# ======================




# ======================
#       PAGE PART
# ======================

class InstructionsPage2_1(Page):
    form_model = "player"
    form_fields = ["Q1_1"]
    
    @staticmethod
    def is_displayed(player: Player):
        return player.keep == 0

    @staticmethod
    def error_message(player: Player, values):
        solutions = dict(Q1_1=24)
        errors = {name: 'Wrong' for name in solutions if values[name] != solutions[name]}
        if errors:
            player.num_failed_attempts_1 += 1
            if player.num_failed_attempts_1 >= 10:
                player.keep = 1
            else:
                return errors

class Instructions1(Page):

    form_model = "player"
    form_fields = ["Q1a", "Q1b", "Q2a", "Q2b", "Q3a", "Q3b", "Q4a", "Q4b"]
    
    @staticmethod
    def is_displayed(player: Player):
        return player.keep == 0

    @staticmethod
    def error_message(player: Player, values):
        solutions = dict(Q1a=20,
                         Q1b=20,
                         Q2a=32,
                         Q2b=32,
                         Q3a=32,
                         Q3b=23,
                         Q4a=18,
                         Q4b=24)
        errors = {name: 'Wrong' for name in solutions if values[name] != solutions[name]}
        if errors:
            player.num_failed_attempts_1 += 1
            if player.num_failed_attempts_1 >= 10:
                player.keep = 1
            else:
                return errors

    
    
class Instructions2(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.keep == 0
    form_model = "player"
    form_fields = ["Q5", "Q6", "Q7", "Q8", "Q9"]
    @staticmethod
    def error_message(player: Player, values):
        solutions = dict(Q5=14,
                         Q6=0,
                         Q7=0,
                         Q8=-12,
                         Q9=-45)
        errors = {name: 'Wrong' for name in solutions if values[name] != solutions[name]}
        if errors:
            player.num_failed_attempts_2 += 1
            if player.num_failed_attempts_2 >= 10:
                player.keep = 1
            else:
                return errors
    
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['wait_arrival_time'] = time.time()
        if player.keep == 1:
            player.participant.vars['boot'] = True
        else: 
            player.participant.vars['boot'] = False



page_sequence = [InstructionsPage2_1,
                 InstructionsPage2_2
                ]
