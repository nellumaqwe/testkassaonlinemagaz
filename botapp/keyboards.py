from aiogram.types import KeyboardButton, InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def admin_kb():
    kb=[
        [
            KeyboardButton(text="🧔 nellProfile"),
            KeyboardButton(text="📂 nellColections")
        ],
        [
            KeyboardButton(text="📝 nellTypes"),
            KeyboardButton(text="🛒 nellCart")
        ],
        [
            KeyboardButton(text="🔍 nellSearch"),
            KeyboardButton(text="⚙️ nellAdmin")
        ],
        

    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def start_kb():
    kb=[
        [
            KeyboardButton(text="🧔 nellProfile"),
            KeyboardButton(text="📂 nellColections")
        ],
        [
            KeyboardButton(text="📝 nellTypes"),
            KeyboardButton(text="🛒 nellCart")
        ],
        [
            KeyboardButton(text="🔍 nellSearch")
        ],
    ]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb, one_time_keyboard=False)

def collections_kb(items: list[str], current_page: int, total_pages: int):
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(text=items[0],callback_data=f"{items[1]}"))

    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Previous",callback_data="col_prev_page"))
     
    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️",callback_data="col_next_page"))

    builder.row(*nav_buttons)
    return builder.as_markup()

def collection_kb(id: int, current_page: int, total_pages: int):
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(text="Add to cart",callback_data=f"add_to_cart/{id}"))

    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Previous",callback_data="col2_prev_page"))
     
    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️",callback_data="col2_next_page"))

    builder.row(*nav_buttons)
    return builder.as_markup()

def admin_kb_2():
    kb=[
        [
            InlineKeyboardButton(text="➕ Add product", callback_data="add"),
            InlineKeyboardButton(text="✏️ Edit collections", callback_data="edit")
        ],
        [
            InlineKeyboardButton(text="Watch orders", callback_data="watch_orders")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def admin_collections_kb():
    kb=[
        [
            InlineKeyboardButton(text="sematary`s 1colection", callback_data="1collection")
        ],
        [
            InlineKeyboardButton(text="sematary`s 2colection", callback_data="2collection")
        ],
        [
            InlineKeyboardButton(text="sematary`s oldcolection", callback_data="oldcollection")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def cart_kb(name: int, current_page: int, total_pages: int):
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="Buy all",callback_data=f"buy/all"))

    builder.add(InlineKeyboardButton(text="Buy this",callback_data=f"buy/{name}"), InlineKeyboardButton(text="Delete from cart", callback_data=f"delete_from_cart/{name}"))

    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Previous",callback_data="cart_prev_page"))
     
    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️",callback_data="cart_next_page"))

    builder.row(*nav_buttons)
    builder.adjust(2,1,1)
    return builder.as_markup()

def order_kb(url:str):
    kb=[
        [InlineKeyboardButton(text="Pay", url=url)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def payment_kb():
    kb=[
        [InlineKeyboardButton(text="go to payment", callback_data="goto_payment")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def choose_order_type():
    kb=[
        [
            [InlineKeyboardButton(text="Active orders", callback_data="active_orders")],
            [InlineKeyboardButton(text="Canceled orders", callback_data="canceled_orders")]
        ],
        [
            InlineKeyboardButton(text="Done orders", callback_data="done_orders")
        ]      
    ]

def admin_orders_kb(order_id: int, current_page: int, total_pages: int):
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="Mark as done",callback_data=f"done/{order_id}"))

    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Previous",callback_data="order_prev_page"))
     
    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️",callback_data="order_next_page"))

    builder.row(*nav_buttons)
    return builder.as_markup()


    