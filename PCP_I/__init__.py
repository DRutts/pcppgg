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
    NAME_IN_URL = 'PCP_I'
    MULTIPLIER = 1.6
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 20
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
    TypeMarker = models.IntegerField()
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
    RandomRound = models.IntegerField()
    ElicitedDispID = models.IntegerField()
    ElicitedCont1 = models.IntegerField()
    ElicitedCont2 = models.IntegerField()
    ElicitedCont3 = models.IntegerField()
    ElicitedCont4 = models.IntegerField()
    OppASP1 = models.IntegerField(initial = 0)
    OppASP2 = models.IntegerField(initial = 0)
    OppASP3 = models.IntegerField(initial = 0)
    OppASP4 = models.IntegerField(initial = 0)
    OccASP1 = models.IntegerField(initial = 0)
    OccASP2 = models.IntegerField(initial = 0)
    OccASP3 = models.IntegerField(initial = 0)
    OccASP4 = models.IntegerField(initial = 0)
    TotalOccASP = models.IntegerField(initial = 0)
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

def SetID(group: Group):
    players = group.get_players()
    IDList = [1, 2, 3, 4]
    P1id = IDList.pop(random.randint(0,3))
    P2id = IDList.pop(random.randint(0,2))
    P3id = IDList.pop(random.randint(0,1))
    P4id = IDList[0]
    DispIDList = [P1id, P2id, P3id, P4id]
    
    for p in players:
        p.DispID = DispIDList[p.id_in_group - 1]
        p.RandomRound = random.randint(11,20)
        p.TypeMarker = random.randint(1,5)


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




def SetPrelimPayoffs_P(group: Group):
    players = group.get_players()
    contributions = [p.Contribution for p in players]
    DispIDs = [p.DispID for p in players]
    group.TotalContribution = sum(contributions)
    group.PGEarnings = group.TotalContribution * C.MULTIPLIER / C.PLAYERS_PER_GROUP
    group.Rounded_PGEarnings = round(group.PGEarnings, 2)

    for p in players:
        PID = GetPID(p) 
        p.ContributionPercentage = p.Contribution/C.ENDOWMENT_P * 100
        p.RetainedEndowment = C.ENDOWMENT_P - p.Contribution
        p.PreliminaryPayoff = C.ENDOWMENT_P - p.Contribution + group.Rounded_PGEarnings
        p.ElicitedCont1 = contributions[DispIDs.index(1)]
        p.ElicitedCont2 = contributions[DispIDs.index(2)]
        p.ElicitedCont3 = contributions[DispIDs.index(3)]
        p.ElicitedCont4 = contributions[DispIDs.index(4)]


    for p in players:
        if p.DispID != 1 and p.Contribution <= contributions[0]:
            p.OppASP1 = 1
        if p.DispID != 2 and p.Contribution <= contributions[1]:
            p.OppASP2 = 1
        if p.DispID != 3 and p.Contribution <= contributions[2]:
            p.OppASP3 = 1
        if p.DispID != 4 and p.Contribution <= contributions[2]:
            p.OppASP2 = 1



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

    for p in players:
        if p.DispID != 1:
            if p.OppASP1 == 1 and p.PunishmentTo1 > 0:
                p.OccASP1 = 1
        if p.DispID != 2:
            if p.OppASP2 == 1 and p.PunishmentTo2 > 0:
                p.OccASP2 = 1
        if p.DispID != 3:
            if p.OppASP3 == 1 and p.PunishmentTo3 > 0:
                p.OccASP3 = 1
        if p.DispID != 4:
            if p.OppASP4 == 1 and p.PunishmentTo4 > 0:
                p.OccASP4 = 1
                
    for p in players:
        p.TotalOccASP = p.OccASP1 + p.OccASP2 + p.OccASP3 + p.OccASP4



# ======================
#       PAGE PART
# ======================

class GroupingWaitPage(WaitPage):
    group_by_arrival_time = True

    after_all_players_arrive = SetID
    body_text = "Please wait for the other players to join. You will be organized into a group of 4 once enough players have arrived. This may take several minutes. If you have been on the page for more than 5 minutes, refresh the page. Once you have been on the page for 15 minutes, you will be asked to return the study."
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.participant.vars['boot'] == False

    

class InstructionsPage2_1(Page):
    timeout_seconds = 1
    #timeout_seconds = 60 * 2
    
    @staticmethod

    def is_displayed(player: Player):
        return player.round_number == 11 and player.participant.vars['boot'] == False and player.Remove == 0
        
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['MaxASP'] = 0

class InstructionsPage2_2(Page):
    form_model = "player"
    form_fields = ["Q2_1", "Q2_2"]
    timeout_seconds = 1
    #timeout_seconds = 60 * 3
    
    @staticmethod

    def is_displayed(player: Player):
        return player.round_number == 11 and player.participant.vars['boot'] == False and player.Remove == 0

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
        return player.round_number == 11 and player.participant.vars['boot'] == False and player.Remove == 0



class Inter_RoundWaitPage_N(WaitPage):
    after_all_players_arrive = ShuffleID
    body_text = "Please wait for the other players to join. The waiting time will take at most 1 minute."    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number >= 2 and player.round_number <=10 and player.participant.vars['boot'] == False and player.Remove == 0



class Inter_RoundWaitPage_P(WaitPage):
    after_all_players_arrive = ShuffleID
    body_text = "Please wait for the other players to join. The waiting time will take at most 30 seconds."    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number >= 12 and player.participant.vars['boot'] == False and player.Remove == 0



class ContributionPage_N(Page):
    form_model = "player"
    form_fields = ["Contribution"]
    timeout_seconds = 1
    #timeout_seconds = 60

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number <= 10 and player.participant.vars['boot'] == False and player.Remove == 0
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.Contribution = random.randint(0,20)
            player.Timeout_C = 1



class ContributionPage_P(Page):
    form_model = "player"
    form_fields = ["Contribution"]
    timeout_seconds = 1
    #timeout_seconds = 60

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number >= 11 and player.participant.vars['boot'] == False and player.Remove == 0
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.Contribution = random.randint(0,20)
            player.Timeout_C = 1



class ResultsWaitPage_N(WaitPage):
    body_text = "Please wait for the other players to join. The waiting time will take at most 1 minute."
    after_all_players_arrive = SetPrelimPayoffs_N
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number <= 10 and player.participant.vars['boot'] == False and player.Remove == 0



class ResultsWaitPage_P(WaitPage):
    body_text = "Please wait for the other players to join. The waiting time will take at most 1 minute."
    after_all_players_arrive = SetPrelimPayoffs_P
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number >= 11 and player.participant.vars['boot'] == False and player.Remove == 0



class PreliminaryResults(Page):
    timeout_seconds = 1
    #timeout_seconds = 30
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.vars['boot'] == False and player.Remove == 0
    def before_next_page(player, timeout_happened):
        if player.round_number == 1:
            player.participant.vars['randomround'] = player.RandomRound


class InformationScreen_N(Page):
    timeout_seconds = 1
    #timeout_seconds = 30
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number <= 10 and player.participant.vars['boot'] == False and player.Remove == 0

    def vars_for_template(player: Player):
        return dict(
            other_players=player.get_others_in_group(),
        )
    def before_next_page(player: Player, timeout_happened):
        if player.round_number == 1:
            if player.TypeMarker == 1:
                player.participant.vars['type'] = 0
            else: 
                player.participant.vars['type'] = 1


class InformationScreen_P(Page):
    timeout_seconds = 1
    #timeout_seconds = 30
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number >= 11 and player.participant.vars['boot'] == False and player.Remove == 0

    def vars_for_template(player: Player):
        return dict(
            other_players=player.get_others_in_group(),
        )

    def before_next_page(player: Player, timeout_happened):
        if player.Remove == 0:
            player.participant.vars['WTL'] = False
        else: 
            player.participant.vars['WTL'] = True



class PunishmentPage(Page):
    form_model = 'player'
    get_form_fields = Punishment_Fields
    timeout_seconds = 1
    #timeout_seconds = 60 * 2

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number >= 11 and player.participant.vars['boot'] == False and player.Remove == 0
    
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
            #player.PunishmentTo1 = random.randint(0, 1)
            #player.PunishmentTo2 = random.randint(0, 1)
            #player.PunishmentTo3 = random.randint(0, 1)
            #player.PunishmentTo4 = random.randint(0, 1)
            player.Timeout_P = 1



class PunishmentWaitPage(WaitPage):
    after_all_players_arrive = SetRevisedPayoffs
    body_text = "Please wait for the other players to join. The waiting time will take at most 3 minutes."
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number >= 11 and player.participant.vars['boot'] == False and player.Remove == 0



class RevisedResults(Page):
    timeout_seconds = 1
    #timeout_seconds = 30

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number >= 11 and player.participant.vars['boot'] == False and player.Remove == 0

    def before_next_page(player, timeout_happened):
        if player.TotalOccASP > player.participant.vars['MaxASP'] and player.participant.vars['type'] == 1:
            player.participant.vars['MaxASP'] = player.TotalOccASP
            player.participant.vars['randomround'] = player.round_number
            player.participant.vars['EDispID'] = player.DispID
            player.participant.vars['ECont1'] = player.ElicitedCont1
            player.participant.vars['ECont2'] = player.ElicitedCont2
            player.participant.vars['ECont3'] = player.ElicitedCont3
            player.participant.vars['ECont4'] = player.ElicitedCont4
            
            if player.DispID != 1:
                player.participant.vars['EPun1'] = player.PunishmentTo1
            else:
                player.participant.vars['EPun1'] = 0
                
            if player.DispID != 2:
                player.participant.vars['EPun2'] = player.PunishmentTo2
            else:
                player.participant.vars['EPun2'] = 0
                
            if player.DispID != 3:
                player.participant.vars['EPun3'] = player.PunishmentTo3
            else:
                player.participant.vars['EPun3'] = 0

            if player.DispID != 4:
                player.participant.vars['EPun4'] = player.PunishmentTo4
            else:
                player.participant.vars['EPun4'] = 0
            
        if player.round_number == player.participant.vars['randomround'] and player.participant.vars['type'] == 0:
            player.participant.vars['EDispID'] = player.DispID
            player.participant.vars['ECont1'] = player.ElicitedCont1
            player.participant.vars['ECont2'] = player.ElicitedCont2
            player.participant.vars['ECont3'] = player.ElicitedCont3
            player.participant.vars['ECont4'] = player.ElicitedCont4
            
            if player.DispID != 1:
                player.participant.vars['EPun1'] = player.PunishmentTo1
            else:
                player.participant.vars['EPun1'] = 0
                
            if player.DispID != 2:
                player.participant.vars['EPun2'] = player.PunishmentTo2
            else:
                player.participant.vars['EPun2'] = 0
                
            if player.DispID != 3:
                player.participant.vars['EPun3'] = player.PunishmentTo3
            else:
                player.participant.vars['EPun3'] = 0

            if player.DispID != 4:
                player.participant.vars['EPun4'] = player.PunishmentTo4
            else:
                player.participant.vars['EPun4'] = 0

        if player.round_number == player.participant.vars['randomround'] and player.TotalOccASP == 0:
            player.participant.vars['EDispID'] = player.DispID
            player.participant.vars['ECont1'] = player.ElicitedCont1
            player.participant.vars['ECont2'] = player.ElicitedCont2
            player.participant.vars['ECont3'] = player.ElicitedCont3
            player.participant.vars['ECont4'] = player.ElicitedCont4
            
            if player.DispID != 1:
                player.participant.vars['EPun1'] = player.PunishmentTo1
            else:
                player.participant.vars['EPun1'] = 0
                
            if player.DispID != 2:
                player.participant.vars['EPun2'] = player.PunishmentTo2
            else:
                player.participant.vars['EPun2'] = 0
                
            if player.DispID != 3:
                player.participant.vars['EPun3'] = player.PunishmentTo3
            else:
                player.participant.vars['EPun3'] = 0

            if player.DispID != 4:
                player.participant.vars['EPun4'] = player.PunishmentTo4
            else:
                player.participant.vars['EPun4'] = 0
            


class PunishmentReason(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 20 and player.participant.vars['boot'] == False and player.Remove == 0


class WaitTooLong(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.Remove == 1


page_sequence = [GroupingWaitPage,
                 InstructionsPage2_1,
                 InstructionsPage2_2,
                 InstructionsWaitPage,
                 Inter_RoundWaitPage_N,
                 Inter_RoundWaitPage_P,
                 ContributionPage_N, 
                 ContributionPage_P,
                 ResultsWaitPage_N, 
                 ResultsWaitPage_P, 
                 PreliminaryResults,
                 InformationScreen_N,
                 InformationScreen_P,
                 PunishmentPage, 
                 PunishmentWaitPage, 
                 RevisedResults,
                 WaitTooLong]
