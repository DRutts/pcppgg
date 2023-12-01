from otree.api import *


doc = """
Your app description
"""

# ======================
#       MODEL PART
# ======================

class C(BaseConstants):
    NAME_IN_URL = 'PCP.P'
    MULTIPLIER = 1.6
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 10
    ENDOWMENT = 25
    PUNISHMENT_MULTIPLIER = 3
    MAX_PUNISHMENT = 10
    



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    TotalContribution = models.IntegerField()
    PGEarnings = models.FloatField()

def make_punishment_field(id_in_group):
        return models.IntegerField(
            min=0, max=C.MAX_PUNISHMENT, label="Deduction assigned to Player {}".format(id_in_group)
        )

class Player(BasePlayer):
    Contribution = models.IntegerField(
        min=0, max=C.ENDOWMENT, label="How much will you contribute?"
    )
    RetainedEndowment = models.IntegerField()
    PreliminaryPayoff = models.FloatField()
    PunishmentTo1 = make_punishment_field(1)
    PunishmentTo2 = make_punishment_field(2)
    PunishmentTo3 = make_punishment_field(3)
    PunishmentTo4 = make_punishment_field(4)
    TotalPunishmentsFrom = models.IntegerField()
    TotalPunishmentsTo = models.IntegerField()
    PayoffReduction = models.IntegerField()
    RevivsedPayoff = models.FloatField()
    



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
        p.RetainedEndowment = C.ENDOWMENT - p.Contribution
        p.PreliminaryPayoff = C.ENDOWMENT - p.Contribution + group.PGEarnings


def SetRevisedPayoffs(group: Group):
    players = group.get_players()
    for p in players:
        PID = GetPID(p)   
        punishments_received = [getattr(other, PID) for other in p.get_others_in_group()]
        p.TotalPunishmentsTo = sum(punishments_received)
        punishments_sent = [getattr(p, field) for field in Punishment_Fields(p)]
        p.TotalPunishmentsFrom = sum(punishments_sent)
        p.PayoffReduction = C.PUNISHMENT_MULTIPLIER*p.TotalPunishmentsTo
        p.RevisedPayoff = max(p.PreliminaryPayoff - p.TotalPunishmentsFrom - p.PayoffReduction, 0)



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
    
    # def before_next_page(player, timeout_happened):
    #     if timeout_happened:
    #         player.Contribution = 0



class ResultsWaitPage(WaitPage):
    after_all_players_arrive = SetPrelimPayoffs
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False


class PreliminaryResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False
    timeout_seconds = 30

class InformationPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False
    timeout_seconds = 30

    def vars_for_template(player: Player):
        return dict(
            other_players=player.get_others_in_group(), contributions = [p.Contribution for p in player.get_players_in_group()],
        )
    

class PunishmentPage(Page):
    form_model = 'player'
    get_form_fields = Punishment_Fields
    timeout_seconds = 60 * 2

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False
    
    def vars_for_template(player: Player):
        return dict(
            other_players=player.get_others_in_group(), multiplier = C.PUNISHMENT_MULTIPLIER,
        )

    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.PunishmentTo1 = 0
            player.PunishmentTo2 = 0
            player.PunishmentTo3 = 0
            player.PunishmentTo4 = 0

class PunishmentWaitPage(WaitPage):
    after_all_players_arrive = SetRevisedPayoffs

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False

class RevisedResults(Page):
    timeout_seconds = 30

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False




page_sequence = [ContributionPage, 
                 ResultsWaitPage, 
                 PreliminaryResults,
                 PunishmentPage, 
                 PunishmentWaitPage, 
                 RevisedResults]
