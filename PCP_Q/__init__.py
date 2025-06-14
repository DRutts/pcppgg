from otree.api import *


doc = """
Your app description
"""

# ======================
#       MODEL PART
# ======================

class C(BaseConstants):
    NAME_IN_URL = 'PCP_Q'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    RandomRound = models.IntegerField()
    EDispID = models.IntegerField()
    ECont1 = models.IntegerField()
    ECont2 = models.IntegerField()
    ECont3 = models.IntegerField()
    ECont4 = models.IntegerField()
    EPun1 = models.IntegerField()
    EPun2 = models.IntegerField()
    EPun3 = models.IntegerField()
    EPun4 = models.IntegerField()
    Deserved1 = models.StringField(
        label='To what extent do you agree that Player 1 deserved to receive deduction points?',
        choices=[[0, 'Disagree'], 
                 [1, 'Somewhat disagree'], 
                 [2, 'Somewhat agree'], 
                 [3, 'Agree']],
        widget=widgets.RadioSelect
    )
    Deserved2 = models.StringField(
        label='To what extent do you agree that Player 2 deserved to receive deduction points?',
        choices=[[0, 'Disagree'], 
                 [1, 'Somewhat disagree'], 
                 [2, 'Somewhat agree'], 
                 [3, 'Agree']],
        widget=widgets.RadioSelect
    )
    Deserved3 = models.StringField(
        label='To what extent do you agree that Player 3 deserved to receive deduction points?',
        choices=[[0, 'Disagree'], 
                 [1, 'Somewhat disagree'], 
                 [2, 'Somewhat agree'], 
                 [3, 'Agree']],
        widget=widgets.RadioSelect
    )
    Deserved4 = models.StringField(
        label='To what extent do you agree that Player 4 deserved to receive deduction points?',
        choices=[[0, 'Disagree'], 
                 [1, 'Somewhat disagree'], 
                 [2, 'Somewhat agree'], 
                 [3, 'Agree']],
        widget=widgets.RadioSelect
    )
    PunishmentReason1 = models.StringField(min_length = 10, max_length = 300,
                                          label = '')
    PunishmentReason2 = models.StringField(min_length = 10, max_length = 300,
                                          label = '')
    PunishmentReason3 = models.StringField(min_length = 10, max_length = 300,
                                          label = '')
    PunishmentReason4 = models.StringField(min_length = 10, max_length = 300,
                                          label = '')
    
    QQ1 = models.IntegerField(
        min=0, label='1) What is your age?'
    )
    QQ2 = models.StringField(
        label='2) What is your gender?',
        choices=[[0, 'Male'], 
                 [1, 'Female'], 
                 [2, 'Other'], 
                 [3, 'Prefer not to say']]
    )
    QQ3 = models.BooleanField(
        label='3) Were you born in your current country of residence?'
    )
    QQ4 = models.IntegerField(
        min=0, label='4) How many years have you lived in your current country of residence?'
    )
    QQ5 = models.StringField(
        label='5) What is the size of the city in which you have spent most of your life?',
        choices=[[0, 'Up to 2,000 inhabitants'], 
                 [1, 'Between 2,000 and 10,000 inhabitants'], 
                 [2, 'Between 10,000 and 100,000 inhabitants'], 
                 [3, 'More than 100,000 inhabitants']]
    )
    QQ6 = models.StringField(
        label='6) Based on your personal judgement, which of the following best describes your family income?', 
        choices=[[0, 'Substantially below average'],
                 [1, 'Somewhat below average'],
                 [2, 'Average'],
                 [3, 'Somewhat above average'],
                 [4, 'Above avrage']]
    )
    QQ7 = models.IntegerField(
        min=0, label='7) How many siblings do you have?'
    )
    QQ8 = models.BooleanField(
        label='8) Are you a member of any voluntary associations (political groups, interest groups, cultural groups, sports, nonprofits, etc.)'
    )
    QQ9a = models.IntegerField(
        min=1, max=10, label='a) Claiming government benefits to which you are not entitled'
    )
    QQ9b = models.IntegerField(
        min=1, max=10, label='b) Avoiding a fare on public transportation'
    )
    QQ9c = models.IntegerField(
        min=1, max=10, label='c) Cheating on taxes if you have a chance'
    )




# ======================
#    CALCULATION PART
# ======================





# ======================
#       PAGE PART
# ======================

class Transition(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False
        
    def before_next_page(player, timeout_happened):
        player.RandomRound = player.participant.vars['randomround']
        player.EDispID = player.participant.vars['EDispID']
        player.ECont1 = player.participant.vars['ECont1']
        player.ECont2 = player.participant.vars['ECont2']
        player.ECont3 = player.participant.vars['ECont3']
        player.ECont4 = player.participant.vars['ECont4']
        player.EPun1 = player.participant.vars['EPun1']
        player.EPun2 = player.participant.vars['EPun2']
        player.EPun3 = player.participant.vars['EPun3']
        player.EPun4 = player.participant.vars['EPun4']


class PunishmentReasonP1(Page):
    form_model = 'player'
    form_fields = ['Deserved2', 'Deserved3', 'Deserved4', 'PunishmentReason2', 'PunishmentReason3', 'PunishmentReason4']
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False and player.EDispID == 1

class PunishmentReasonP2(Page):
    form_model = 'player'
    form_fields = ['Deserved1', 'Deserved3', 'Deserved4', 'PunishmentReason1', 'PunishmentReason3', 'PunishmentReason4']
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False and player.EDispID == 2

class PunishmentReasonP3(Page):
    form_model = 'player'
    form_fields = ['Deserved1', 'Deserved2', 'Deserved4', 'PunishmentReason1', 'PunishmentReason2', 'PunishmentReason4']
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False and player.EDispID == 3

class PunishmentReasonP4(Page):
    form_model = 'player'
    form_fields = ['Deserved1', 'Deserved2', 'Deserved3', 'PunishmentReason1', 'PunishmentReason2', 'PunishmentReason3']
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False and player.EDispID == 4


class Questionnaire(Page):
    form_model = 'player'
    form_fields = ['QQ1', 'QQ2', 'QQ3', 'QQ4', 'QQ5', 'QQ6', 'QQ7', 'QQ8']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False


class Questionnaire2(Page):
    form_model = 'player'
    form_fields = ['QQ9a', 'QQ9b', 'QQ9c']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False


class Completion(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False
    

page_sequence = [Transition,
                 PunishmentReasonP1,
                 PunishmentReasonP2,
                 PunishmentReasonP3,
                 PunishmentReasonP4,
                 Questionnaire,
                 Questionnaire2,
                 Completion]
