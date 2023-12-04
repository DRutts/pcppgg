from otree.api import *
import time

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

def make_punishment_field(id_in_group):
        return models.IntegerField(
            min=C.MAX_PUNISHMENT, max=0, label="Deduction assigned to Player {}".format(id_in_group)
        )

class Player(BasePlayer):
    PID = models.IntegerField()
    Contribution = models.IntegerField(
        min=0, max=C.ENDOWMENT, label="How much will you contribute?"
    )
    RetainedEndowment = models.IntegerField()
    incomplete = models.IntegerField(initial = 0)
    PreliminaryPayoff = models.FloatField()
    ContributionPercentage = models.FloatField()
    PunishmentTo1 = make_punishment_field(1)
    PunishmentTo2 = make_punishment_field(2)
    PunishmentTo3 = make_punishment_field(3)
    PunishmentTo4 = make_punishment_field(4)
    TotalPunishmentsFrom = models.IntegerField()
    TotalPunishmentsTo = models.IntegerField()
    PayoffReduction = models.IntegerField()
    RevisedPayoff = models.FloatField()

    def waiting_too_long(player):
        return time.time() - player.participant.vars['wait_arrival_time'] > 30*60

    def SetRevisedPayoffs(group: Group):
        players = group.get_players()
        for p in players:
            PID = GetPID(p)   
            punishments_received = [getattr(other, PID) for other in p.get_others_in_group()]
            p.TotalPunishmentsTo = -1*sum(punishments_received)
            punishments_sent = [getattr(p, field) for field in Punishment_Fields(p)]
            p.TotalPunishmentsFrom = -1*sum(punishments_sent)
            p.PayoffReduction = C.PUNISHMENT_MULTIPLIER*p.TotalPunishmentsTo
            p.RevisedPayoff = p.PreliminaryPayoff - p.TotalPunishmentsFrom - p.PayoffReduction  




# ======================
#    CALCULATION PART
# ======================

def GetPID(player: Player):
    return 'PunishmentTo{}'.format(player.id_in_group)

def Punishment_Fields(player: Player):
    return ['PunishmentTo{}'.format(p.id_in_group) for p in player.get_others_in_group()]

def SetPrelimPayoffs(group: Group):
    players = group.get_players()
    contributions = [p.Contribution for p in players]
    group.TotalContribution = sum(contributions)
    group.PGEarnings = group.TotalContribution * C.MULTIPLIER / C.PLAYERS_PER_GROUP

    for p in players:
        PID = GetPID(p) 
        p.ContributionPercentage = p.Contribution/C.ENDOWMENT * 100
        p.RetainedEndowment = C.ENDOWMENT - p.Contribution
        p.PreliminaryPayoff = C.ENDOWMENT - p.Contribution + group.PGEarnings


def SetRevisedPayoffs(group: Group):
    players = group.get_players()
    for p in players:
        PID = GetPID(p)   
        punishments_received = [getattr(other, PID) for other in p.get_others_in_group()]
        p.TotalPunishmentsTo = -1*sum(punishments_received)
        punishments_sent = [getattr(p, field) for field in Punishment_Fields(p)]
        p.TotalPunishmentsFrom = -1*sum(punishments_sent)
        p.PayoffReduction = C.PUNISHMENT_MULTIPLIER*p.TotalPunishmentsTo
        p.RevisedPayoff = p.PreliminaryPayoff - p.TotalPunishmentsFrom - p.PayoffReduction


# ======================
#       PAGE PART
# ======================

class ShuffleWaitPage(WaitPage):
    group_by_arrival_time = True
    body_text = "Please wait for the other players to join. The waiting time will take at most 20 minutes."
    
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False

class ContributionPage(Page):
    form_model = "player"
    form_fields = ["Contribution"]
    timeout_seconds = 90

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
    timeout_seconds = 45
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False

    

class InformationScreen(Page):
    timeout_seconds = 45
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False
    

    def vars_for_template(player: Player):
        return dict(
            other_players=player.get_others_in_group(), contributions = [p.Contribution for p in player.get_players_in_group()],
        )


page_sequence = [ShuffleWaitPage,
                 ContributionPage, 
                 ResultsWaitPage, 
                 PreliminaryResults,
                 InformationScreen
                ]
