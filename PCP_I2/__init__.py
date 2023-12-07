from otree.api import *

import time


doc = """
Your app description
"""

# ======================
#       MODEL PART
# ======================

class C(BaseConstants):
    NAME_IN_URL = 'PCP_I2'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1  

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass



class Player(BasePlayer):
    Q2_1 = models.IntegerField(
        label = 'Suppose that, in the second phase, you send 9, 5, and 0 deduction points to the other three players, respectively. What is the total cost of the deduction points you sent?'
    )
    Q2_2 = models.IntegerField()





# ======================
#    CALCULATION PART
# ======================




# ======================
#       PAGE PART
# ======================

class InstructionsPage2_1(Page):
    timeout_seconds = 60 * 2
    
    @staticmethod

    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False 


class InstructionsPage2_2(Page):
    form_model = "player"
    form_fields = ["Q2_1", "Q2_2"]
    timeout_seconds = 60 * 3
    
    @staticmethod

    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False

    @staticmethod
    def error_message(player: Player, values):
        solutions = dict(Q2_1=14,
                         Q2_2=12)
        errors = {name: 'Wrong' for name in solutions if values[name] != solutions[name]}
        if errors:
            return errors
        



page_sequence = [InstructionsPage2_1,
                 InstructionsPage2_2
                ]
