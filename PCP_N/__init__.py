from otree.api import *
import time
import random

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
    def group_by_arrival_time_method(subsession, waiting_players):
        for player in waiting_players: 
            player.incomplete = 0
        if len(waiting_players) >= 4:
            return [waiting_players[0], waiting_players[1], waiting_players[2], waiting_players[3]]
        for player in waiting_players:
            if player.waiting_too_long():
                player.incomplete = 1
                return[player]


class Group(BaseGroup):
    TotalContribution = models.IntegerField()
    PGEarnings = models.FloatField()
    Rounded_PGEarnings = models.FloatField()
    



class Player(BasePlayer):
    Remove = models.IntegerField(initial = 0)
    PID = models.IntegerField()
    DispID = models.IntegerField()
    Timeout_C = models.IntegerField(initial = 0)
    Contribution = models.IntegerField(
        min=0, max=C.ENDOWMENT, label="How much will you contribute?"
    )
    RetainedEndowment = models.IntegerField()
    incomplete = models.IntegerField(initial = 0)
    PreliminaryPayoff = models.FloatField()
    ContributionPercentage = models.FloatField()


    def waiting_too_long(player):
        return time.time() - player.participant.vars['wait_arrival_time'] > 30




# ======================
#    CALCULATION PART
# ======================

def ShuffleID(group: Group):
    players = group.get_players()
    IDList = [1, 2, 3, 4]
    P1id = IDList.pop(random.randint(0,3))
    P2id = IDList.pop(random.randint(0,2))
    P3id = IDList.pop(random.randint(0,1))
    P4id = IDList[0]
    DispIDList = [P1id, P2id, P3id, P4id]
    
    for p in players:
        p.DispID = DispIDList[p.id_in_group - 1]

    


def GetPID(player: Player):
    return 'PunishmentTo{}'.format(player.DispID)



def SetPrelimPayoffs(group: Group):
    players = group.get_players()
    contributions = [p.Contribution for p in players]
    group.TotalContribution = sum(contributions)
    group.PGEarnings = group.TotalContribution * C.MULTIPLIER / C.PLAYERS_PER_GROUP
    group.Rounded_PGEarnings = round(group.PGEarnings, 2)


    for p in players:
        PID = GetPID(p) 
        p.ContributionPercentage = p.Contribution/C.ENDOWMENT * 100
        p.RetainedEndowment = C.ENDOWMENT - p.Contribution
        p.PreliminaryPayoff = C.ENDOWMENT - p.Contribution + group.Rounded_PGEarnings


    



# ======================
#       PAGE PART
# ======================

class GroupingWaitPage(WaitPage):
    group_by_arrival_time = True

    def group_by_arrival_time_method(subsession, waiting_players):
        if len(waiting_players) >= 4:
            return waiting_players[:4]
        for player in waiting_players:
            if waiting_too_long(player):
                player.Remove = 1
                return [player]
    after_all_players_arrive = ShuffleID
    body_text = "Please wait for the other players to join. You will be organized into a group of 4 once enough players have arrived. This may take several minutes. If you have been on the page for more than 5 minutes, refresh the page. Once you have been on the page for 15 minutes, you will be asked to return the study."


    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.participant.vars['boot'] == False

    

class Inter_RoundWaitPage(WaitPage):
    after_all_players_arrive = ShuffleID
    body_text = "Please wait for the other players to join. The waiting time will take at most 1 minute."

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number >= 2 and player.participant.vars['boot'] == False and player.Remove == 0

class ContributionPage(Page):
    form_model = "player"
    form_fields = ["Contribution"]
    timeout_seconds = 60

    @staticmethod

    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.Contribution = random.randint(0,20)
            player.Timeout_C = 1



class ResultsWaitPage(WaitPage):
    body_text = "Please wait for the other players to join. The waiting time will take at most 1 minute."
    @staticmethod

    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.Remove == 0
    
    after_all_players_arrive = SetPrelimPayoffs


class PreliminaryResults(Page):
    timeout_seconds = 30
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.Remove == 0

    

class InformationScreen(Page):
    timeout_seconds = 30
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.Remove == 0

    def vars_for_template(player: Player):
        return dict(
            other_players=player.get_others_in_group()
        )

    def before_next_page(player: Player, timeout_happened):
        if player.Remove == 0:
            player.participant.vars['WTL'] = False
        else: 
            player.participant.vars['WTL'] = True
    
class WaitTooLong(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.Remove == 1


page_sequence = [GroupingWaitPage,
                 Inter_RoundWaitPage,
                 ContributionPage, 
                 ResultsWaitPage, 
                 PreliminaryResults,
                 InformationScreen,
                 WaitTooLong
                ]
