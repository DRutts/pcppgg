from otree.api import (

    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)

import time

from django.forms.widgets import CheckboxSelectMultiple
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
    consent = models.BooleanField(widget=djforms.CheckboxInput,
                                  initial=False
                                  )

    incorrect_attempts1= models.IntegerField(initial = 0)
    bot_num = models.IntegerField(initial = 0)

    captcha1 = models.StringField(max_length = 200)
    captcha2 = models.StringField(max_length = 200)
    incorrect_attempts_captcha1 = models.IntegerField(initial = 0)
    incorrect_attempts_captcha2 = models.IntegerField(initial = 0)
    TimeoutCapthca1 = models.BooleanField(initial = False)
    TimeoutCapthca2 = models.BooleanField(initial = False)

    num_failed_attempts_1 = models.IntegerField(initial=0)
    num_failed_attempts_2 = models.IntegerField(initial=0)
    failed_too_many = models.BooleanField(initial=False)
    TimeoutQ1 = models.BooleanField(initial = False)
    TimeoutQ2 = models.BooleanField(initial = False)

    Q1a = models.IntegerField(
        label = "a) What is your income?"
    )
    Q1b = models.IntegerField(
        label = "b) What is the income of the other group members?"
    )
    Q2a = models.IntegerField(
        label = "a) What is your income?"
    )
    Q2b = models.IntegerField(
        label = "b) What is the income of the other group members?"
    )
    Q3a = models.IntegerField(
        label = "a) What is your income if you contribute 0 tokens to the project?"
    )
    Q3b = models.IntegerField(
        label = "b) What is your income if you contribute 15 tokens to the project?"
    )
    Q4a = models.IntegerField(
        label = "a) What is your income if the other group members together contribute a total of 7 tokens to the project?"
    )
    Q4b = models.IntegerField(
        label = "b) What is your income if the other group members together contribute a total of 22 tokens to the project"
    )

    Q5 = models.IntegerField(
        min=-50, max=50,
        label='5) Suppose at the second stage you assign the following deduction points to your three other group members:-9,-5,0. What are the total costs of your assigned deduction points?'
    )
    Q6 = models.IntegerField(
        min=-50, max=50,
        label='6) What are your costs if you assign a total of 0 points?'
    )
    Q7 = models.IntegerField(
        min=-50, max=50,
        label='7) By how many Guilders will your income from the first stage be changed if you receive a total of 0 deduction points from the other group members?'
    )
    Q8 = models.IntegerField(
        min=-50, max=50,
        label='8) By how many Guilders will your income from the first stage be changed if you receive a total of 4 deduction points from the other group members?'
    )
    Q9 = models.IntegerField(
        min=-50, max=50,
        label='9) By how many Guilders will your income from the first stage be changed if you receive a total of 15 deduction points from the other group members?'
    )




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
        if not value:
            return 'You must accept the consent form in order to proceed with the study!'

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
            return errors

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.TimeoutCapthca1 = True
            player.participant.vars['boot'] = True
        if player.incorrect_attempts_captcha1 >= 3:
                player.participant.vars['boot'] = True
        else: 
            player.TimeoutCapthca1 = False
            player.participant.vars['boot'] = False


class Captcha2(Page):
    form_model = 'player'
    form_fields = ['captcha2']
    timeout_seconds = 90

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False

    @staticmethod
    def error_message(player: Player, values):
        solutions = dict(captcha2=["eps10 vector", 'eps10 vect0r', "epsio vector", "epsio vect0r", 'eps1o vector', 'eps1o vect0r'])
        errors = {name: '''Please type the characters correctly, including any numbers, letters, and spaces. Use lowercase.''' for name in solutions if values[name] not in solutions[name]}
        if errors:
            player.incorrect_attempts_captcha2 += 1
            return errors

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.TimeoutCapthca2 = True
            player.participant.vars['boot'] = True
        if player.incorrect_attempts_captcha2 >= 3:
                player.participant.vars['boot'] = True
        else: 
            player.TimeoutCapthca2 = False
            player.participant.vars['boot'] = False


class Instructions1(Page):

    form_model = "player"
    form_fields = ["Q1a", "Q1b", "Q2a", "Q2b", "Q3a", "Q3b", "Q4a", "Q4b"]
    
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False

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
                player.failed_too_many = True
                
            else:
                return errors

    def before_next_page(player: Player, timeout_happened):
        if player.failed_too_many == True:
            player.participant.vars['boot'] = True
        else: 
            player.participant.vars['boot'] = False
    
    
class Instructions2(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False
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
                player.participant.vars['boot'] = True
            else:
                return errors
    
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['wait_arrival_time'] = time.time()
        if player.failed_too_many == True:
            player.participant.vars['boot'] = True
        else: 
            player.participant.vars['boot'] = False

class Elimination(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == True

page_sequence = [Consent,
                 Captcha1,
                 Captcha2,
                 Instructions1, 
                 Instructions2,
                 Elimination]
