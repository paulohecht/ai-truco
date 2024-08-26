import time

class Player:

    def __base_prompt(self, log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
        return f"""
        You are {self.name}, a `truco paulista` professional player.

        In this game, in each "hand", each player gets 3 cards to play 3 rounds.
        In each round, each player show a card and the highest card wins.
        The first player to win two rounds wins the hand. Who wins 12 hands first wins the match.
        
        Before playing his turn, the player can raise the bet, increasing the potential points for the hand.
        The other player can `accept`, `fold` or `raise` the bet. 
        The sequence is `truco` (3 points), 6, 9, 12.

        Except in the first round, you can cover your card (play it face down) if you want to ensure that the 
        other player doesn't know what card you had (for example, if you’re going to lose anyway or if you want 
        to lose a round on purpose to trick your opponent into accepting a bet later).
        Note: Covering cards is not allowed in the first round of the hand! When you cover a card, 
        you are deliberately choosing to lose that round. Think carefully.

        These are the cards values from lowest to highest in this hand, considering the turned card id `{turned_card}`:
        Covered: `XX = 1` (covered cards always lose) 
        Normal Cards (any suit): `{"`, `".join([f"{card} = {index + 1}" for index, card in enumerate(filter(lambda x: x != manilha, ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']))])}` 
        Manilhas: `{manilha}♦ = 10`, `{manilha}♤ = 11`, `{manilha}♥ = 12`, `{manilha}♧ = 13`

        You must follow these rules:
         - Always try to win the round by playing a card higher then the opponent's
         - When you have a card higher than you opponent's, play the lowest card tha win the round.        
         - When you can't win the round, cover your lowest card instead of showing it.
         - When you have a strong hand and the odds are in your favor, raise the bet.

        These are the cards in your hand (your opponent can't see them):
        `{"`, `".join(hand)}`

        This is the card you should try to win (if none, you are the first to play):
        `{" ".join(cards)}`
        
        This hand is worth `{current_bid}` points.
        This is the round `{round + 1}`
        
        This is the what happened in this match so far:
        {"; ".join(log)}
        """

    def _card_prompt(self, log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
        return f"""
        {self.__base_prompt(log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card)}
        Decide which card to play and whether to cover it or not.
            Please, explain your rationale for the decision and then, the last line of
            your response should be only a card in the format: `A♦` or, if you want to cover it, `A♦X` .
            Use only a card from your hand, and add the `X` if you want to cover it.
        """

    def _bid_prompt(self, log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
        return f"""
        {self.__base_prompt(log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card)}
        Decide whether to raise the next bet (truco, 6, 9, or 12).
        Please, explain your rationale for the decision and then, the last line of
        your response should be ONLY one of the following words:
            `raise` if you want to raise the bet
            `continue` if you don't want to raise the bet.
        """

    def _bid_answer_prompt(self, log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
        return f"""
        {self.__base_prompt(log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card)}
        You need to decide whether to accept, fold, or raise the bet.
        Please, explain your rationale for the decision and then, the last line of
        your response should be ONLY one of the following words:
            `accept` to accept the last request.
            `raise` if raising is an option (the maximum is 12).
            `fold` to concede and give the points from the last bet to your opponent.
        """

    def _extract_response_prompt(self, response):
        return f"""
            ```
            {response}
            ```
        
            Please, interpret this text, the last line should contain the decision.
            Respond with the decision as just a single token text response that should be one of:
                A card in the format: `A♦` or a covered card in the format: `A♦X`.
                Or any of the words: `continue`, `accept`, `raise`, `fold`
            No extra quotes or other signs. Only the response text so that it can be interpreted by a parser.
        """

    @property
    def name(self):
        raise NotImplementedError("This property should be overridden by subclasses")

    async def __prompt(self, prompt):
        time.sleep(1)
        response = (await self._request(prompt))
        # print(f"{self.name} Response: {response}")
        answer = (await self._request(self._extract_response_prompt(response)))
        # print(f"{self.name} Answer: {answer}")
        return answer.strip('\'`" ')

    async def _request(self, prompt):
        raise NotImplementedError("This method should be overridden by subclasses")


    async def decide_if_bid(self, log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
        return (await self.__prompt(self._bid_prompt(log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card)))


    async def decide_card(self, log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
        return await self.__prompt(self._card_prompt(log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card))


    async def decide_bid_answer(self, log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card):
        return await self.__prompt(self._bid_answer_prompt(log, hand, cards, round, current_bid, cards_in_hand, manilha, turned_card))
