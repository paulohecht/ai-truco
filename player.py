import time

class Player:

    def __base_prompt(self, log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
        return f"""
        You are {self.name}, a `truco paulista` professional player.

        In this game, in each "hand", each player gets 3 cards to play 3 rounds.
        In each round, each player show a card and the highest card wins.
        Who wins more rounds, wins the hand. Who wins 12 hands first wins the match.
        
        Before playing his turn, the player can raise the bet, increasing the potential points for the hand.
        The other player can `accept`, `fold` or `raise` the bet. 
        The sequence is `truco` (3 points), 6, 9, 12.

        Except in the first round, you can cover your card (play it face down) if you want to ensure that the 
        other player doesn't know what card you had (for example, if you’re going to lose anyway or if you want 
        to lose a round on purpose to trick your opponent into accepting a bet later).
        Note: Covering cards is not allowed in the first round of the hand! When you cover a card, 
        you are deliberately choosing to lose that round. Think carefully.

        These are the cards values from lowest to highest in this hand, considering the turned card id `{turned_card}`:
        ```
        Covered: `XX = 1` (covered cards always lose) 
        Non-manilhas (any suit): `{"`, `".join([f"{card} = {index + 1}" for index, card in enumerate(filter(lambda x: x != manilha, ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']))])}` 
        Manilhas: `{manilha}♦ = 10`, `{manilha}♤ = 11`, `{manilha}♥ = 12`, `{manilha}♧ = 13`
        ```

        You must follow these rules:
         - Prioritize winning every round and every hand.
         - When winning a round, use the lowest card higher than the opponent's.           
         - If you can't win, cover your lowest card instead of showing it.
         - When you have a strong hand and the odds are in your favor, raise the bet.

        These are the cards in your hand (your opponent can't see them):
        ```
        `{"`, `".join(hand)}`
        ```

        These are the cards on the table in this round (if none, you are the first to play):
        ```
        `{"`, `".join(cards)}`
        ```
        
        This hand is worth `{current_bid}` points.
        This is round `{round + 1}`
        
        These are the cards that have already been played in this hand (so you know your opponent doesn't have them):
        ```
        `{turned_card}`, `{"`, `".join(cards_in_hand)}`
        ```
        """

    def _card_prompt(self, log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
        return f"""
        {self.__base_prompt(log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card)}
        Decide which card to play and whether to cover it or not.
            Give your response only in the format: `A♦` or, if you want to cover it, `A♦X` .
            Use only one card from your hand, and add the `X` if you want to cover it.
            No quotes or other signs.
        """

    def _bid_prompt(self, log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
        return f"""
        {self.__base_prompt(log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card)}
        Decide whether to raise the next bet (truco, 6, 9, or 12).
        Your response must contain ONLY one of the following words:
            `raise` if you want to raise the bet
            `continue` if you don't want to raise the bet.
        """

    def _bid_answer_prompt(self, log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
        return f"""
        {self.__base_prompt(log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card)}
        You need to decide whether to accept, fold, or raise the bet.
        Your response must contain ONLY one of the following words:
            `accept` to accept the last request.
            `raise` if raising is an option (the maximum is 12).
            `fold` to concede and give the points from the last bet to your opponent.
        """

    @property
    def name(self):
        raise NotImplementedError("This property should be overridden by subclasses")

    async def __prompt(self, prompt):
        time.sleep(1)
        return (await self._request(prompt)).strip('\'`" ')

    async def _request(self, prompt):
        raise NotImplementedError("This method should be overridden by subclasses")


    async def decide_if_bid(self, log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
        return (await self.__prompt(self._bid_prompt(log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card)))


    async def decide_card(self, log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
        return await self.__prompt(self._card_prompt(log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card))


    async def decide_bid_answer(self, log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
        return await self.__prompt(self._bid_answer_prompt(log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card))
