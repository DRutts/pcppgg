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
    NAME_IN_URL = 'PCP_P'
    MULTIPLIER = 1.6
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 10
    ENDOWMENT_N = 20
    ENDOWMENT_P = 25
    PUNISHMENT_MULTIPLIER = 3
    MAX_PUNISHMENT = 10
    



class Subsession(BaseSubsession):
    def group_by_arrival_time_method(subsession, waiting_players):
        for player in waiting_players: 
            player.Remove = 0
        if len(waiting_players) >= 4:
            return [waiting_players[0], waiting_players[1], waiting_players[2], waiting_players[3]]
        for player in waiting_players:
            if player.waiting_too_long():
                player.Remove = 1
                return[player]


class Group(BaseGroup):
    TotalContribution = models.IntegerField()
    PGEarnings = models.FloatField()
    Rounded_PGEarnings = models.FloatField()

def make_punishment_field(id_in_group):
        return models.IntegerField(
            min=0, max=C.MAX_PUNISHMENT, label="Deduction assigned to Player {}".format(id_in_group)
        )

class Player(BasePlayer):
    Remove = models.IntegerField(initial = 0)
    PID = models.IntegerField()
    DispID = models.IntegerField()
    Timeout_C = models.IntegerField(initial = 0)
    Timeout_P = models.IntegerField(initial = 0)
    Contribution = models.IntegerField(
        min=0, max=20, label="How much will you contribute?"
    )
    ContributionPercentage = models.FloatField()
    RetainedEndowment = models.IntegerField()
    PreliminaryPayoff = models.FloatField()
    PunishmentTo1 = make_punishment_field(1)
    PunishmentTo2 = make_punishment_field(2)
    PunishmentTo3 = make_punishment_field(3)
    PunishmentTo4 = make_punishment_field(4)
    TotalPunishmentsFrom = models.IntegerField()
    TotalPunishmentsTo = models.IntegerField()
    PayoffReduction = models.IntegerField()
    RevisedPayoff = models.FloatField()
    Rounded_RevisedPayoff = models.FloatField()
    Q2_1 = models.IntegerField(
        label = 'Suppose that, in the second phase, you send 9, 5, and 0 deduction points to the other three players, respectively. What is the total cost of the deduction points you sent?'
    )
    Q2_2 = models.IntegerField(
        label = 'Suppose that, in the second phase, you received a total of 4 deduction points from other players. By how many tokens will your earnings decrease?'
    )

    def waiting_too_long(player):
        return time.time() - player.participant.vars['wait_page_arrival_time'] > 15*60



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

def Punishment_Fields(player: Player):
    return ['PunishmentTo{}'.format(p.DispID) for p in player.get_others_in_group()]

def SetPrelimPayoffs_N(group: Group):
    players = group.get_players()
    contributions = [p.Contribution for p in players]
    group.TotalContribution = sum(contributions)
    group.PGEarnings = group.TotalContribution * C.MULTIPLIER / C.PLAYERS_PER_GROUP
    group.Rounded_PGEarnings = round(group.PGEarnings, 2)

    for p in players:

        PID = GetPID(p) 
        p.ContributionPercentage = p.Contribution/C.ENDOWMENT_N * 100
        p.RetainedEndowment = C.ENDOWMENT_N - p.Contribution
        p.PreliminaryPayoff = C.ENDOWMENT_N - p.Contribution + group.Rounded_PGEarnings


def SetPrelimPayoffs_{(group: Group):
    players = group.get_players()
    contributions = [p.Contribution for p in players]
    group.TotalContribution = sum(contributions)
    group.PGEarnings = group.TotalContribution * C.MULTIPLIER / C.PLAYERS_PER_GROUP
    group.Rounded_PGEarnings = round(group.PGEarnings, 2)

    for p in players:

        PID = GetPID(p) 
        p.ContributionPercentage = p.Contribution/C.ENDOWMENT_P * 100
        p.RetainedEndowment = C.ENDOWMENT_P - p.Contribution
        p.PreliminaryPayoff = C.ENDOWMENT_P - p.Contribution + group.Rounded_PGEarnings


def SetRevisedPayoffs(group: Group):
    players = group.get_players()
    for p in players: 
        PID = GetPID(p) 
        punishments_received = [getattr(other, PID) for other in p.get_others_in_group()]
        p.TotalPunishmentsTo = sum(punishments_received)
        punishments_sent = [getattr(p, field) for field in Punishment_Fields(p)]
        p.TotalPunishmentsFrom = sum(punishments_sent)
        p.PayoffReduction = C.PUNISHMENT_MULTIPLIER*p.TotalPunishmentsTo
        p.RevisedPayoff = p.PreliminaryPayoff - p.TotalPunishmentsFrom - p.PayoffReduction
        p.Rounded_RevisedPayoff = round(p.RevisedPayoff, 2)



# ======================
#       PAGE PART
# ======================

class InstructionsPage2_1(Page):
    timeout_seconds = 60 * 2
    
    @staticmethod

    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False


class InstructionsPage2_2(Page):
    form_model = "player"
    form_fields = ["Q2_1", "Q2_2"]
    timeout_seconds = 60 * 3
    
    @staticmethod

    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False

    @staticmethod
    def error_message(player: Player, values):
        solutions = dict(Q2_1=14,
                         Q2_2=12)
        errors = {name: 'Wrong' for name in solutions if values[name] != solutions[name]}
        if errors:
            return errors
class InstructionsWaitPage(WaitPage):
    after_all_players_arrive = ShuffleID
    body_text = "Please wait for the other players to join. The waiting time will take at most 6 minutes."    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False

class Inter_RoundWaitPage(WaitPage):
    after_all_players_arrive = ShuffleID
    body_text = "Please wait for the other players to join. The waiting time will take at most 30 seconds."    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number >= 2 and player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False

class ContributionPage(Page):
    form_model = "player"
    form_fields = ["Contribution"]
    timeout_seconds = 60

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.Contribution = random.randint(0,20)
            player.Timeout_C = 1



class ResultsWaitPage(WaitPage):
    body_text = "Please wait for the other players to join. The waiting time will take at most 1 minute."
    after_all_players_arrive = SetPrelimPayoffs
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False


class PreliminaryResults(Page):
    timeout_seconds = 30
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False
    

class InformationScreen(Page):
    timeout_seconds = 30
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False

    def vars_for_template(player: Player):
        return dict(
            other_players=player.get_others_in_group(),
        )
    

class PunishmentPage(Page):
    form_model = 'player'
    get_form_fields = Punishment_Fields
    timeout_seconds = 60 * 2

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False
    
    def vars_for_template(player: Player):
        return dict(
            other_players=player.get_others_in_group(),
        )

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.PunishmentTo1 = 0
            player.PunishmentTo2 = 0
            player.PunishmentTo3 = 0
            player.PunishmentTo4 = 0
            player.Timeout_P = 1

class PunishmentWaitPage(WaitPage):
    after_all_players_arrive = SetRevisedPayoffs
    body_text = "Please wait for the other players to join. The waiting time will take at most 3 minutes."
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False

class RevisedResults(Page):
    timeout_seconds = 30

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.participant.vars['WTL'] == False




page_sequence = [InstructionsWaitPage,
                 Inter_RoundWaitPage,
                 ContributionPage, 
                 ResultsWaitPage, 
                 PreliminaryResults,
                 InformationScreen,
                 PunishmentPage, 
                 PunishmentWaitPage, 
                 RevisedResults]
