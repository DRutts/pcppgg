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
    ENDOWMENT = 25
    PUNISHMENT_MULTIPLIER = 3
    MAX_PUNISHMENT = 10
    



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    TotalContribution = models.IntegerField()
    PGEarnings = models.FloatField()
    Rounded_PGEarnings = models.FloatField()

def make_punishment_field(id_in_group):
        return models.IntegerField(
            min=0, max=C.MAX_PUNISHMENT, label="Deduction assigned to Player {}".format(id_in_group)
        )

class Player(BasePlayer):
    PID = models.IntegerField()
    DispID = models.IntegerField()
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
    return 'PunishmentTo{}'.format(player.id_in_group)

def Punishment_Fields(player: Player):
    return ['PunishmentTo{}'.format(p.id_in_group) for p in player.get_others_in_group()]

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

class InstructionsWaitPage(WaitPage):
    after_all_players_arrive = ShuffleID
    #body_text = print(f"{len(waiting_players)} of 4 players ready. Please wait for the other players to join. The waiting time will take at most 5 minutes.") 
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class Inter_RoundWaitPage(WaitPage):
    after_all_players_arrive = ShuffleID
    #body_text = print(f"{len(waiting_players)} of 4 players ready. Please wait for the other players to join. The waiting time will take at most 30 seconds.")
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number >= 2

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



class ResultsWaitPage(WaitPage):
    #body_text = print(f"{len(waiting_players)} of 4 players ready. Please wait for the other players to join. The waiting time will take at most 1 minute.")
    after_all_players_arrive = SetPrelimPayoffs
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False


class PreliminaryResults(Page):
    timeout_seconds = 30
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False
    

class InformationScreen(Page):
    timeout_seconds = 30
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False

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
        return player.participant.vars['boot'] == False
    
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

class PunishmentWaitPage(WaitPage):
    after_all_players_arrive = SetRevisedPayoffs
    #body_text = print(f"{len(waiting_players)} of 4 players ready. Please wait for the other players to join. The waiting time will take at most 3 minutes.")

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False

class RevisedResults(Page):
    timeout_seconds = 30

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False




page_sequence = [InstructionsWaitPage,
                 Inter_RoundWaitPage,
                 ContributionPage, 
                 ResultsWaitPage, 
                 PreliminaryResults,
                 InformationScreen,
                 PunishmentPage, 
                 PunishmentWaitPage, 
                 RevisedResults]
