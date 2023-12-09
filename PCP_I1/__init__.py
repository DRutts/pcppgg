from otree.api import *

import time


doc = """
Your app description
"""

# ======================
#       MODEL PART
# ======================

class C(BaseConstants):
    NAME_IN_URL = 'PCP_I1'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1  

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass



class Player(BasePlayer):
    consent = models.FloatField(
            choices=[[1, 'I consent']],
            label = '',
            widget=widgets.RadioSelect
        )
    keep = models.IntegerField(initial = 0)

    captcha1 = models.StringField(max_length = 200)
    captcha2 = models.StringField(max_length = 200)
    incorrect_attempts_captcha1 = models.IntegerField(initial = 0)
    incorrect_attempts_captcha2 = models.IntegerField(initial = 0)
    TimeoutCapthca1 = models.BooleanField(initial = False)
    TimeoutCapthca2 = models.BooleanField(initial = False)
    Q1_1 = models.IntegerField(
        label = 'Each member of the group has an endowment of 20 tokens. Suppose that you contribute 8 tokens to the project and suppose that the other group members contribute a total of 22 tokens to the project. What is your total income?'
    )
    num_failed_attempts_1 = models.IntegerField(initial=0)







# ======================
#    CALCULATION PART
# ======================




# ======================
#       PAGE PART
# ======================

class Consent(Page):
    form_model = 'player'
    form_fields = ['consent']

    @staticmethod
    def consent_error_message(player: Player, value):
        solutions = dict(consent='I consent')
        errors = {name: '''You must accept the consent form to proceed with the study''' for name in solutions if values[name] != solutions[name]}
        if errors:
            return errors


class Captcha1(Page):
    form_model = 'player'
    form_fields = ['captcha1']   
    timeout_seconds = 90

    @staticmethod
    def error_message(player: Player, values):
        solutions = dict(captcha1='RUNAJIX')
        errors = {name: '''Please type the characters correctly, case sensitive''' for name in solutions if values[name] != solutions[name]}
        if errors:
            player.incorrect_attempts_captcha1 += 1
            if player.incorrect_attempts_captcha1 >= 4:
                player.keep = 1
            else:
                return errors

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.TimeoutCapthca1 = True
            player.keep = 1
        else: 
            player.TimeoutCapthca1 = False
            


class Captcha2(Page):
    form_model = 'player'
    form_fields = ['captcha2']
    timeout_seconds = 90

    @staticmethod
    def is_displayed(player: Player):
        return player.keep == 0

    @staticmethod
    def error_message(player: Player, values):
        solutions = dict(captcha2=["Eps10 vector", 'Eps10 vect0r', "Epslo vector", "Epslo vect0r", 'Eps1o vector', 'Eps1o vect0r'])
        errors = {name: '''Please type the characters correctly, including any numbers, letters, and spaces. Use lowercase.''' for name in solutions if values[name] not in solutions[name]}
        if errors:
            player.incorrect_attempts_captcha2 += 1
            if player.incorrect_attempts_captcha2 >= 4:
                player.keep = 1
            else:
                return errors

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.TimeoutCapthca2 = True
            player.keep = 1
        else: 
            player.TimeoutCapthca2 = False
            
class InstructionsPage1_1(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.keep == 0

class InstructionsPage1_2(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.keep == 0

class InstructionsPage1_3(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.keep == 0

class InstructionsPage1_4(Page):
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
    
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['wait_arrival_time'] = time.time()
        if player.keep == 1:
            player.participant.vars['boot'] = True
        else: 
            player.participant.vars['boot'] = False

class Elimination(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.keep == 1

page_sequence = [Consent,
                 Captcha1,
                 Captcha2,
                 InstructionsPage1_1, 
                 InstructionsPage1_2,
                 InstructionsPage1_3,
                 InstructionsPage1_4,
                 Elimination]
