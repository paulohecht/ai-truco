import random
import time
import asyncio
from player_gemini import PlayerGemini
from player_gpt import PlayerGpt
from truco_helper import TrucoHelper

players = [PlayerGemini(), PlayerGpt()]
truco_helper = TrucoHelper()
wait_time = 5


async def decide_if_bid(player, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
    result = await players[player].decide_if_bid(log, hand, cards, round, truco_helper.bid_values[current_bid], cards_in_hand, manilha, turned_card)
    return result == 'raise'


async def decide_card(player, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
    decision = await players[player].decide_card(log, hand, cards, round, truco_helper.bid_values[current_bid], cards_in_hand, manilha, turned_card)
    return decision[:2], len(decision) > 2 and "  " in hand


async def decide_bid_answer(player, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
    decision = await players[player].decide_bid_answer(log, hand, cards, round, truco_helper.bid_values[current_bid], cards_in_hand, manilha, turned_card)
    return decision


async def bid(player, hands, cards, round, current_bid, cards_in_hand, manilha, turned_card):
    print_and_log(f"{players[player].name} calls {truco_helper.bids[current_bid]}!")
    return await answer_bid(player ^ 1, hands, cards, round, current_bid, cards_in_hand, manilha, turned_card)


async def answer_bid(player, hands, cards, round, current_bid, cards_in_hand, manilha, turned_card):
    answer = await decide_bid_answer(player, hands[player], cards, round, current_bid, cards_in_hand, manilha, turned_card)
    if answer == 'fold':
        print_and_log(f"{players[player].name} folds!")
        return player ^ 1, current_bid * -1
    elif answer == 'raise' and current_bid < len(truco_helper.bids) - 1:
        return await bid(player, hands, cards, round, current_bid + 1, cards_in_hand, manilha, turned_card)
    print_and_log(f"{players[player].name} accepts!")
    return player ^ 1, current_bid


def shuffle_and_deal(deck):
    random.shuffle(deck)
    player1_hand = deck[:3]
    player2_hand = deck[3:6]
    turned_card = deck[6]
    return [player1_hand, player2_hand], turned_card


def render_table(hands, turned_card, cards=['  ', '  ']):

    print(f" ")
    print(f"{players[0].name}                {players[1].name}")
    print(f"[{hands[0][0]}] | [{cards[0]}]   [{cards[1]}] | [{hands[1][0]}]")
    print(f"[{hands[0][1]}] |             | [{hands[1][1]}]")
    print(f"[{hands[0][2]}] |     [{turned_card}]    | [{hands[1][2]}]")
    print(f"       turned card")
    print(f" ")
    time.sleep(wait_time)

def calculate_hand_winner(round, hand_results):
    if round == 1 and hand_results[0] == 2 and hand_results[1] != 2: return hand_results[1]
    if round == 1 and hand_results[1] == 2 and hand_results[0] != 2: return hand_results[0]
    if round == 1 and hand_results[0] == hand_results[1] and hand_results[1] != 2: return hand_results[1]
    if round == 2 and hand_results[2] == 2: return hand_results[0]
    if round == 2: return hand_results[2]
    return None


def print_and_log(message):
    print(message)
    log.append(message)


def log(message):
    log.append(message)


log = []

async def main():
    print_and_log("Match starts...")
    print("--------------------------------------------------------")
    hand_player = random.randint(0, 1)
    scores = [0, 0]
    hand = 0
    while True:
        hand += 1
        player = hand_player
        hands, turned_card = shuffle_and_deal(truco_helper.deck.copy())
        current_bid = 0
        last_bidder = None
        results = []
        print("Hand ", hand)
        print_and_log(f"{players[player ^ 1].name} deals the cards and flips  {turned_card}")
        cards_in_hand = [turned_card]
        for round in range(3):
            print("---------")
            print("Round ", round + 1)
            render_table(hands, turned_card)
            cards = ['  ', '  ']
            for turn in range(2):
                if truco_helper.bid_values[current_bid] < 12 and last_bidder != player and await decide_if_bid(player, hands[player], cards, round, current_bid, cards_in_hand, truco_helper.manilha(turned_card), turned_card):
                    last_bidder, current_bid = await bid(player, hands, cards, round, current_bid + 1, cards_in_hand, truco_helper.manilha(turned_card), turned_card)
                    if current_bid < 0: break;

                card, hidden = await decide_card(player, hands[player], cards, round, current_bid, cards_in_hand, truco_helper.manilha(turned_card), turned_card)
                if hidden:
                    print_and_log(f"{players[player].name} covers a card")
                    cards[player] = 'XX'
                else:
                    print_and_log(f"{players[player].name} plays {card}")
                    cards[player] = card
                cards_in_hand.append(cards[player])
                hands[player] = list(map(lambda x: "  " if x == card else x, hands[player]))
                render_table(hands, turned_card, cards)
                player = player ^ 1

            if current_bid < 0:
                hand_winner = player
                current_bid = (current_bid * -1) - 1
            else:
                results.append(truco_helper.winner(cards, turned_card))

                if results[round] == 2:
                    print_and_log("Round is a tie!")
                    player = hand_player
                else:
                    print_and_log(f"{players[results[round]].name} won the round!")
                    player = results[round]
                hand_winner = calculate_hand_winner(round, results)

            if hand_winner is not None:
                if hand_winner == 2:
                    print_and_log("Hand is a tie!")
                else:
                    print_and_log(f"{players[hand_winner].name} won the hand! +{truco_helper.bid_values[current_bid]}")
                    scores[hand_winner] += truco_helper.bid_values[current_bid]
                hand_player = hand_player ^ 1
                break

        print_and_log("--------------------------------------------------------")
        print_and_log(f"{players[0].name}: {scores[0]}, {players[1].name}: {scores[1]}")
        print_and_log("--------------------------------------------------------")
        time.sleep(wait_time)

        match_winner = index = next((i for i, x in enumerate(scores) if x >= 12), None)
        if match_winner is not None:
            print(players[match_winner].name, "won the match!")
            break

asyncio.run(main())

print(" ")
# print("LOG --->")
# print(*log, sep="\n")
# exit()
