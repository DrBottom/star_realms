from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
import random


@dataclass
class Card:
    class Type(Enum):
        SHIP = 1
        STATION = 2,
        OUTPOST = 3

    class Faction(Enum):
        FEDERATION = 1
        SLIME = 2
        TECHO = 3
        EMPIRE = 4
        NEUTRAL = 5

    cost: int
    faction: Faction
    name: str
    abilities: 'AbstractAbilityPool'
    delete_abilities: 'AbstractAbilityPool'
    ally_abilities: 'AbstractAbilityPool'
    double_ally_abilities: 'AbstractAbilityPool'
    hp: (int, None)


class CardPile:
    class Orientation(Enum):
        BACK = 1
        FRONT = 2

    def __init__(self, orientation: Orientation, cards: list[Card]):
        self.orientation = orientation
        self.cards = cards

    def draw(self) -> Card:
        return self.cards.pop()

    def shuffle(self):
        random.shuffle(self.cards)

    def put(self, card: Card):
        self.cards.append(card)


class Player:
    def __init__(self, health: int = 50):
        self.draw_pile: CardPile = CardPile(orientation=CardPile.Orientation.BACK, cards=[])
        self.discard_pile: CardPile = CardPile(orientation=CardPile.Orientation.FRONT, cards=[])
        self.hand: list[Card] = []
        self.bases: list[Card] = []
        self.outposts: list[Card] = []
        self.health = health

    def from_draw_pile_to_hand(self):
        self.hand.append(self.draw_pile.cards.pop())

    def from_hand_to_discard(self, card: Card):
        self.discard_pile.put(self.hand.pop(self.hand.index(card)))

    def from_discard_to_draw_pile(self):
        self.discard_pile.shuffle()
        for _ in range(len(self.discard_pile.cards)):
            self.draw_pile.put(self.discard_pile.cards[_])

    def destroy_base(self, card: Card):
        self.discard_pile.put(self.bases.pop(self.bases.index(card)))

    def destroy_outpost(self, card: Card):
        self.discard_pile.put(self.outposts.pop(self.outposts.index(card)))

    def play_hand(self, ctx: 'GameContext'):
        for card in self.hand:
            if card.Type.SHIP:
                card.abilities.apply(ctx)
            else:
                if card.Type.OUTPOST:
                    self.outposts.append(card)
                else:
                    self.bases.append(card)
                self.hand.remove(card)

    def apply_first_base_ability(self, ctx: 'GameContext'):
        selected_base = Selector.select_card(self.bases)
        selected_ability = Selector.select_ability(selected_base.abilities.abilities)
        selected_ability.apply(ctx)

    def apply_ally_ability(self, ctx: 'GameContext'):
        all_players_cards = self.hand + self.bases
        selected_card = Selector.select_card(all_players_cards)
        selected_ability = Selector.select_ability(selected_card.ally_abilities.abilities)
        selected_ability.apply(ctx)

    def apply_double_ally_ability(self, ctx: 'GameContext'):
        all_players_cards = self.hand + self.bases
        selected_card = Selector.select_card(all_players_cards)
        selected_ability = Selector.select_ability(selected_card.double_ally_abilities.abilities)
        selected_ability.apply(ctx)

    def apply_delete_ability(self, ctx: 'GameContext'):
        all_players_cards = self.hand + self.bases
        selected_card = Selector.select_card(all_players_cards)
        selected_ability = Selector.select_ability(selected_card.delete_abilities.abilities)
        selected_ability.apply(ctx)

    def buy_card(self, ctx: 'GameContext'):
        selected_card = Selector.select_card(ctx.shop.current)
        if selected_card.cost <= ctx.pool.money:
            self.discard_pile.put(selected_card)
            ctx.shop.draw_card(selected_card)

    @staticmethod
    def attack_enemy(ctx: 'GameContext'):
        selected_enemy = Selector.select_opponent(ctx.opponents)
        # Нет баз
        # Есть базы
        # Есть аванпосты
        # Есть и базы, и аванпосты
        while any(outpost.hp <= ctx.pool.damage for outpost in selected_enemy.outposts):
            outposts_can_be_destroyed = list(filter(lambda x: x.hp <= ctx.pool.damage, selected_enemy.outposts))
            outpost_to_destroy = Selector.select_card(outposts_can_be_destroyed)
            ctx.pool.damage -= outpost_to_destroy.hp
            selected_enemy.destroy_outpost(outpost_to_destroy)
        if ctx.pool.damage <= 0 or selected_enemy.outposts:
            return

        while selected_enemy.bases and Selector.yes_or_no('Do you want to destroy a base?'):
            bases_can_be_destroyed = list(filter(lambda x: x.hp <= ctx.pool.damage, selected_enemy.bases))
            selected_base = Selector.select_card(bases_can_be_destroyed)
            ctx.pool.damage -= selected_base.hp
            selected_enemy.destroy_base(selected_base)

        selected_enemy.health -= ctx.pool.damage

    def discard_phase(self, ctx: 'GameContext'):
        self.health += ctx.pool.heal
        self.refresh_hand()

    def refresh_hand(self):
        for card in self.hand:
            self.discard_pile.put(card)
        self.hand.clear()
        self.hand = [self.from_draw_pile_to_hand() for _ in range(5)]


class AttributePool:
    damage: int = 0
    heal: int = 0
    money: int = 0


class CardShop:
    def __init__(self, cards: CardPile):
        self.cards = cards
        self.current: list[Card] = [self.cards.draw() for _ in range(5)]

    def draw_card(self, card: Card) -> Card:
        result = self.current.pop(self.current.index(card))
        self.current.append(self.cards.draw())
        return result


class GameContext:
    def __init__(self, current_player: Player, opponents: list[Player], shop: CardShop):
        self.pool = AttributePool()
        self.player = current_player
        self.opponents = opponents
        self.shop = shop


class AbstractAbility(ABC):
    # TODO: make @abstractmethod to force all childs to implement this
    def display(self) -> str:
        return 'sample text'

    @abstractmethod
    def apply(self, context: GameContext):
        pass


class AbstractAbilityPool(ABC):
    def __init__(self, abilities: list[AbstractAbility]):
        self.abilities = abilities

    @abstractmethod
    def apply(self, context: GameContext):
        pass


class Selector:
    @staticmethod
    def select_card(cards: list[Card]) -> Card:
        return cards[0]
        # TODO

    @staticmethod
    def select_ability(abilities: list[AbstractAbility]):
        return abilities[0]
        # TODO

    @staticmethod
    def select_opponent(enemies: list[Player]):
        return enemies[0]
        # TODO

    @staticmethod
    def yes_or_no(msg: str):
        return True
        # TODO
