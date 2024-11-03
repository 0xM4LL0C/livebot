from helpers.enums import ItemRarity, ItemType
from helpers.datatypes import Item

rarity_weights = {
    ItemRarity.COMMON: 6,
    ItemRarity.UNCOMMON: 5,
    ItemRarity.RARE: 3,
    ItemRarity.EPIC: 2,
    ItemRarity.LEGENDARY: 1,
}

ITEMS = [
    Item(
        name="бабло",
        emoji="🪙",
        desc="Игровая валюта",
        rarity=ItemRarity.COMMON,
    ),
    Item(
        name="буханка",
        emoji="🍞",
        desc="-10 голода, используется в крафтах",
        craft={"мука": 3, "вода": 5},
        effect=10,
        price=100,
        is_consumable=True,
        rarity=ItemRarity.COMMON,
        is_task_item=True,
        task_coin=(50, 150),
        can_exchange=True,
        exchange_price=(70, 100),
    ),
    Item(
        name="сэндвич",
        emoji="🥪",
        desc="-30 голода",
        craft={"буханка": 2, "помидор": 3, "сыр": 4},
        effect=30,
        price=250,
        is_consumable=True,
        rarity=ItemRarity.COMMON,
        is_task_item=True,
        task_coin=(100, 300),
        can_exchange=True,
        exchange_price=(70, 250),
        altnames=["сендвич"],
    ),
    Item(
        name="пицца",
        emoji="🍕",
        desc="-50 голода",
        craft={"буханка": 5, "сыр": 4},
        effect=50,
        price=380,
        is_consumable=True,
        rarity=ItemRarity.COMMON,
        is_task_item=True,
        task_coin=(300, 450),
        can_exchange=True,
        exchange_price=(200, 380),
    ),
    Item(
        name="тако",
        emoji="🌮",
        desc="-70 голода",
        craft={"буханка": 1, "помидор": 8, "сыр": 6},
        effect=70,
        price=530,
        is_consumable=True,
        rarity=ItemRarity.COMMON,
        is_task_item=True,
        task_coin=(350, 600),
        can_exchange=True,
        exchange_price=(400, 530),
    ),
    Item(
        name="суп",
        emoji="🍲",
        desc="-100 голода",
        craft={
            "вода": 10,
            "помидор": 5,
            "морковка": 4,
            "мясо": 7,
            "трава": 3,
            "гриб": 2,
        },
        effect=100,
        price=700,
        is_consumable=True,
        rarity=ItemRarity.UNCOMMON,
        can_exchange=True,
        exchange_price=(500, 700),
    ),
    Item(
        name="мука",
        emoji="🥣",
        desc="Используется в крафтах",
        price=100,
        rarity=ItemRarity.COMMON,
        can_exchange=True,
        exchange_price=(70, 100),
    ),
    Item(
        name="вода",
        emoji="💦",
        desc="Используется в крафтах",
        price=80,
        rarity=ItemRarity.COMMON,
        is_task_item=True,
        task_coin=(50, 120),
        can_exchange=True,
        exchange_price=(40, 80),
    ),
    Item(
        name="помидор",
        emoji="🍅",
        desc="Используется в крафах",
        price=83,
        rarity=ItemRarity.COMMON,
        is_task_item=True,
        task_coin=(50, 150),
        can_exchange=True,
        exchange_price=(70, 83),
    ),
    Item(
        name="сыр",
        emoji="🧀",
        desc="Используется в крафтах",
        price=75,
        rarity=ItemRarity.COMMON,
        is_task_item=True,
        task_coin=(40, 110),
        can_exchange=True,
        exchange_price=(60, 75),
    ),
    Item(
        name="морковка",
        emoji="🥕",
        desc="Используется в крафтах",
        price=60,
        rarity=ItemRarity.COMMON,
        is_task_item=True,
        task_coin=(30, 100),
        can_exchange=True,
        exchange_price=(30, 60),
        altnames=["морковь"],
    ),
    Item(
        name="мясо",
        emoji="🥩",
        desc="Используется в крафтах",
        price=350,
        rarity=ItemRarity.COMMON,
        can_exchange=True,
        exchange_price=(250, 350),
    ),
    Item(
        name="буст",
        emoji="⚡",
        desc="При использовании добавляет от 100 до 500 опыта",
        price=75000,
        is_consumable=True,
        rarity=ItemRarity.RARE,
        can_exchange=True,
        exchange_price=(60000, 75000),
    ),
    Item(
        name="бокс",
        emoji="📦",
        desc="При открытии падают 3 предмета",
        price=35000,
        is_consumable=True,
        rarity=ItemRarity.LEGENDARY,
        can_exchange=True,
        exchange_price=(25000, 35000),
    ),
    Item(
        name="кость",
        emoji="🦴",
        desc="Нужен для того, чтобы подружиться с псиной",
        rarity=ItemRarity.UNCOMMON,
        can_exchange=True,
        exchange_price=(200, 500),
    ),
    Item(
        name="энергос",
        emoji="🔋",
        desc="Выпей, чтобы быстро восстановить силы",
        effect=100,
        price=5000,
        is_consumable=True,
        craft={"химоза": 4, "вода": 3},
        rarity=ItemRarity.UNCOMMON,
        can_exchange=True,
        exchange_price=(4000, 5000),
        altnames=["енергос"],
    ),
    Item(
        name="химоза",
        emoji="🧪",
        desc="Используется в крафтах",
        price=2310,
        rarity=ItemRarity.UNCOMMON,
        can_exchange=True,
        exchange_price=(1000, 2310),
    ),
    Item(
        name="пилюля",
        emoji="💊",
        desc="Принимай эти пилюли, чтобы быстрее выздороветь",
        is_consumable=True,
        rarity=ItemRarity.RARE,
        can_exchange=True,
        exchange_price=(1000, 2000),
    ),
    Item(
        name="хелп",
        emoji="💉",
        desc="Используй, если не хочешь лечь в больницу, сразу восстанавливается все здоровье",
        effect=100,
        is_consumable=True,
        rarity=ItemRarity.RARE,
        can_exchange=True,
        exchange_price=(10000, 20000),
    ),
    Item(
        name="трава",
        emoji="🌿",
        desc="-5 к сытости, используется в крафтах",
        effect=5,
        is_consumable=True,
        price=60,
        rarity=ItemRarity.COMMON,
        is_task_item=True,
        task_coin=(20, 80),
        can_exchange=True,
        exchange_price=(40, 60),
    ),
    Item(
        name="гриб",
        emoji="🍄",
        desc="Используется в крафтах",
        price=63,
        rarity=ItemRarity.COMMON,
        is_task_item=True,
        task_coin=(20, 80),
        can_exchange=True,
        exchange_price=(40, 63),
    ),
    Item(
        name="свисток",
        emoji="🪈",
        desc="Можно взять у псины, если с ней подружиться",
        rarity=ItemRarity.UNCOMMON,
        can_exchange=True,
        exchange_price=(500, 1600),
    ),
    Item(
        name="фиксоманчик",
        emoji="👾",
        desc="Чини предметы на изи, восстанавливает 50-100% предмета",
        type=ItemType.USABLE,
        is_consumable=True,
        rarity=ItemRarity.LEGENDARY,
        can_exchange=True,
        exchange_price=(800000, 1500000),
    ),
    Item(
        name="снеговик",
        emoji="⛄",
        desc="Ивентовый предмет",
        craft={"снежок": 10},
        rarity=ItemRarity.UNCOMMON,
        is_task_item=False,
        task_coin=(500, 1000),
        can_exchange=True,
        exchange_price=(500, 1000),
    ),
    Item(
        name="снежок",
        emoji="❄",
        desc="Используется в крафте снеговика",
        rarity=ItemRarity.COMMON,
        is_task_item=False,
        task_coin=(70, 100),
        can_exchange=True,
        exchange_price=(60, 170),
    ),
    Item(
        name="водка",
        emoji="🍾",
        desc="Выпей, чтобы быстро восстановить усталость, но потеряешь здоровье",
        effect=40,
        is_consumable=True,
        rarity=ItemRarity.EPIC,
        can_exchange=True,
        exchange_price=(200000, 300000),
    ),
    Item(
        name="билет",
        emoji="🎟",
        desc="Нужен чтобы играть в казино",
        price=70,
        rarity=ItemRarity.UNCOMMON,
        is_task_item=True,
        task_coin=(35, 100),
        can_exchange=True,
        exchange_price=(60, 70),
    ),
    Item(
        name="велик",
        emoji="🚲",
        desc="Лень ждать когда вернешься с прогулки? юзай велик и сократи время от 10 до 45 минут",
        price=25000,
        is_consumable=True,
        rarity=ItemRarity.RARE,
        can_exchange=True,
        exchange_price=(10000, 25000),
    ),
    Item(
        name="чаинка",
        emoji="🍃",
        desc="Используется в крафте чая",
        price=52,
        rarity=ItemRarity.COMMON,
        is_task_item=True,
        task_coin=(15, 60),
        can_exchange=True,
        exchange_price=(20, 52),
    ),
    Item(
        name="чай",
        emoji="🍵",
        desc="Попей чтобы уменьшить усталость",
        price=90,
        craft={"вода": 3, "чаинка": 1},
        effect=7,
        is_consumable=True,
        rarity=ItemRarity.COMMON,
        is_task_item=True,
        task_coin=(50, 130),
        can_exchange=True,
        exchange_price=(60, 90),
    ),
    Item(
        name="ключ",
        emoji="🗝️",
        desc="Нужен чтобы открыть сундук",
        price=5691,
        rarity=ItemRarity.RARE,
        can_exchange=True,
        exchange_price=(4000, 5800),
    ),
    Item(
        name="бабочка",
        emoji="🦋",
        desc="Ивентовый предмет",
        rarity=ItemRarity.UNCOMMON,
        can_exchange=True,
        exchange_price=(2000, 3000),
    ),
    Item(
        name="клевер-удачи",
        emoji="🍀",
        desc="Увеличивает удачу на 1",
        rarity=ItemRarity.LEGENDARY,
        is_consumable=True,
        effect=1,
    ),
    Item(
        name="конфета",
        emoji="🍬",
        desc="Уменьшает голод и усталость",
        rarity=ItemRarity.EPIC,
        is_task_item=True,
        task_coin=(300, 500),
        can_exchange=True,
        exchange_price=(150, 300),
        effect=40,
    ),
    Item(
        name="тыква",
        emoji="🎃",
        desc="Ивентовый предмет",
        rarity=ItemRarity.LEGENDARY,
    ),
]
