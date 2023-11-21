import basics
# TODO: файл с картами


def on_wish(func):
    if not basics.Selector.yes_or_no('Do you want to use this ability?'):
        return
    return func()


class AllAbilityPool(basics.AbstractAbilityPool):
    def apply(self, context: basics.GameContext):
        for a in self.abilities:
            a.apply(context)


class ChoiceAbilityPool(basics.AbstractAbilityPool):
    def apply(self, context: basics.GameContext):
        ability_to_apply = basics.Selector.select_ability(self.abilities)
        ability_to_apply.apply(context)


class PoolDamageAbility(basics.AbstractAbility):
    def __init__(self, damage: int):
        self.damage = damage

    def apply(self, context: basics.GameContext):
        context.pool.damage += self.damage


class PoolHealAbility(basics.AbstractAbility):
    def __init__(self, heal: int):
        self.heal = heal

    def apply(self, context: basics.GameContext):
        context.pool.heal += self.heal


class PoolMoneyAbility(basics.AbstractAbility):
    def __init__(self, money: int):
        self.money = money

    def apply(self, context: basics.GameContext):
        context.pool.money += self.money


class ShopDeleteAbility(basics.AbstractAbility):
    @on_wish
    def apply(self, context: basics.GameContext):
        context.shop.draw_card(basics.Selector.select_card(context.shop.current))


class ShopBuyAbility(basics.AbstractAbility):
    def __init__(self, max_price):
        self.max_price = max_price

    @on_wish
    def apply(self, context: basics.GameContext):
        if basics.Selector.select_card(context.shop.current).cost > self.max_price:
            raise AttributeError('Price too high')
        context.player.discard_pile.put(context.shop.draw_card(basics.Selector.select_card(cards=context.shop.current)))


class ShopDiscardAndDamageAbility(basics.AbstractAbility):
    def apply(self, context: basics.GameContext):
        context.pool.damage += context.shop.draw_card(basics.Selector.select_card(cards=context.shop.current)).cost


class OpponentDiscardCard(basics.AbstractAbility):
    def apply(self, context: basics.GameContext):
        selected_enemy = basics.Selector.select_opponent(context.opponents)
        selected_enemy.from_hand_to_discard()


class TakeAndDiscardCard(basics.AbstractAbility):
    def apply(self, context: basics.GameContext):
        context.player.draw_pile.draw()
        context.player.discard_pile.put(basics.Selector.select_card(cards=context.player.hand))
