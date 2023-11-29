from otree.api import *


doc = """
Your app description
"""

# ======================
#       MODEL PART
# ======================

class C(BaseConstants):
    NAME_IN_URL = 'PCP_N'
    MULTIPLIER = 1.6
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 10
    ENDOWMENT = 20


    


class Subsession(BaseSubsession):
    def group_by_arrival_time_method(waiting_players):
        grouped_players = [p for p in waiting_players]
        for player in waiting_players: 
            player.incomplete = 0
        if len(grouped_players) >= 1:
            return [player[1], player[2], player[3], player[4]]
        for player in waiting_players:
            if player.waiting_too_long():
                player.incomplete = 1
                return[player]


class Group(BaseGroup):
    
    TotalContribution = models.IntegerField()
    PGEarnings = models.FloatField()


class Player(BasePlayer):
    PID = models.IntegerField()
    Contribution = models.IntegerField(
        min=0, max=C.ENDOWMENT, label="How much will you contribute?"
    )






# ======================
#    CALCULATION PART
# ======================

def GetPID(player: Player):
    return 'PunishmentTo{}'.format(player.id_in_group)



def SetPrelimPayoffs(group: Group):
    players = group.get_players()
    contributions = [p.Contribution for p in players]
    group.TotalContribution = sum(contributions)
    group.PGEarnings = group.TotalContribution * C.MULTIPLIER / C.PLAYERS_PER_GROUP

    for p in players:
        PID = GetPID(p)  
        p.PreliminaryPayoff = C.ENDOWMENT - p.Contribution + group.PGEarnings




# ======================
#       PAGE PART
# ======================


class ContributionPage(Page):
    form_model = "player"
    form_fields = ["Contribution"]
    timeout_seconds = 60

    @staticmethod

    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.Contribution = 0



class ResultsWaitPage(WaitPage):
    @staticmethod

    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False
    
    after_all_players_arrive = SetPrelimPayoffs


class PreliminaryResults(Page):
    @staticmethod

    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False

    timeout_seconds = 30

class ShuffleWaitPage(WaitPage):
    group_by_arrival_time = True
    body_text = "Please wait for the other player to join. The waiting time will take at most 20 minutes."
    
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False


page_sequence = [ShuffleWaitPage,
                 ContributionPage, 
                 ResultsWaitPage, 
                 PreliminaryResults,
                 ]
