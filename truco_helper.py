class TrucoHelper:

    def __init__(self):
        self.ranking = ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']
        self.suits = ['♦', '♤', '♥', '♧']
        self.deck = [f'{rank}{suit}' for rank in self.ranking for suit in self.suits]
        self.bids = ['none', 'truco', '6', '9', '12']
        self.bid_values = [1, 3, 6, 9, 12]

    def manilha(self, turned_card):
        return self.ranking[(self.ranking.index(turned_card[0]) + 1) % len(self.ranking)]

    def power(self, card, turned_card):
        if card == 'XX': return -1
        if card[0] == self.manilha(turned_card):
            return 10 + self.suits.index(card[1])
        return self.ranking.index(card[0])

    def winner(self, cards, turned_card):
        if self.power(cards[0], turned_card) > self.power(cards[1], turned_card):
            return 0
        elif self.power(cards[0], turned_card) < self.power(cards[1], turned_card):
            return 1
        else:
            return 2
