from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext 
from aiogram.fsm.state import StatesGroup, State
from decimal import Decimal
from aiogram import F
from botapp.keyboards import cart_kb
from botapp.db.models import Product, Cart
import logging
import os
from aiogram import Bot
from pathlib import Path
from botapp.config import settings
from tortoise.exceptions import ConfigurationError

cart_router = Router()

router = Router()
TOKEN = settings["TOKEN"]
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Cart_items(StatesGroup):
    cart_product=State()

@cart_router.callback_query(F.data.startswith("add_to_cart"))
async def add_to_cart(callback:CallbackQuery):
    id=callback.data.split("/")
    user_id=callback.from_user.id
    print(int(id[1]))
    if await Cart.filter(user_id=user_id, product_name=int(id[1])).exists():
        await callback.message.answer("Product is alredy in your cart")
    else:
        await Cart.create(
            user_id=user_id,
            product_name=int(id[1]))
        await callback.message.answer("Successfully added")

cart_pages={}

@cart_router.message(F.text=="🛒 nellCart")
async def send_cart(message:Message, state:FSMContext):
    await state.set_state(Cart_items.cart_product)
    user_id=message.from_user.id

    cart_list=[]
    in_cart_data = await Cart.filter(user_id=user_id)
    
    for item in in_cart_data:
        p=await Product.filter(id=item.product_name).first()
        cart_list.append(
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "type": p.type,
                "picture": p.picture
            }
        )
    if not cart_list:
        await message.answer("Cart is empty")
        return
    
    await state.update_data(cart_list=cart_list)
    cart_pages[user_id] = 0

    page_data = cart_list[0]

    keyboard = cart_kb(
        name=page_data["id"],
        current_page=0,
        total_pages=len(cart_list))
        
    photo = FSInputFile(page_data["picture"])
    await message.answer_photo(
        photo=photo,
        caption=f"{page_data["type"]}\n\n{page_data["name"]}\n\nprice: {float(page_data["price"])}",
        reply_markup=keyboard)

@cart_router.callback_query(F.data.startswith("cart_"))
async def pages_handlers(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    current_page = cart_pages.get(user_id, 0)
    
    # Получаем данные из состояния
    data = await state.get_data()
    products_list = data.get("cart_list", [])
    
    if not products_list:
        await callback.answer("Нет данных о товарах", show_alert=True)
        return

    if callback.data == "cart_prev_page" and current_page > 0:
        new_page = current_page - 1
    elif callback.data == "cart_next_page" and current_page < len(products_list) - 1:
        new_page = current_page + 1
    else:
        await callback.answer()
        return
    
    cart_pages[user_id] = new_page
    page_data = products_list[new_page]
    
    try:
        # Формируем медиа с правильными полями
        media = InputMediaPhoto(
            media=FSInputFile(page_data["picture"]),
            caption=f"{page_data['type']}\n\n{page_data['name']}\n\nprice: {float(page_data['price'])}"
        )
        
        # Используем ту же клавиатуру, что и в первом обработчике
        keyboard = cart_kb(
            name=page_data["id"],
            current_page=new_page,
            total_pages=len(products_list))
        
        await callback.message.edit_media(
            media=media,
            reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка при обновлении страницы: {e}")
        await callback.answer("Произошла ошибка при загрузке страницы", show_alert=True)
    
    await callback.answer()

@cart_router.callback_query(F.data.startswith("delete_from_cart"))
async def delete_from_cart(callback: CallbackQuery, state: FSMContext):
    name = callback.data.split("/")
    user_id = callback.from_user.id
    
    # Удаляем товар из корзины
    await Cart.filter(user_id=user_id, product_name=name[1]).delete()
    
    # Получаем обновленный список товаров
    in_cart_data = await Cart.filter(user_id=user_id)
    cart_list = []
    
    for item in in_cart_data:
        p = await Product.filter(id=item.product_name).first()
        cart_list.append({
            "name": p.name,
            "price": p.price,
            "type": p.type,
            "picture": p.picture
        })
    
    await state.update_data(cart_list=cart_list)
    
    if not cart_list:
        # Если корзина пуста, удаляем сообщение с корзиной и показываем сообщение
        await callback.message.delete()
        await callback.message.answer("Your cart is now empty")
        return
    
    # Обновляем текущую страницу (если удаленный товар был не на текущей странице)
    current_page = cart_pages.get(user_id, 0)
    if current_page >= len(cart_list):
        current_page = len(cart_list) - 1
        cart_pages[user_id] = current_page
    
    # Получаем данные для текущей страницы
    page_data = cart_list[current_page]
    
    # Создаем новую клавиатуру
    keyboard = cart_kb(
        name=page_data["name"],
        current_page=current_page,
        total_pages=len(cart_list))
    
    # Обновляем сообщение с корзиной
    try:
        media = InputMediaPhoto(
            media=FSInputFile(page_data["picture"]),
            caption=f"{page_data['type']}\n\n{page_data['name']}\n\nprice: {float(page_data['price'])}"
        )
        await callback.message.edit_media(
            media=media,
            reply_markup=keyboard)
        await callback.answer("Product removed from cart")
    except Exception as e:
        logger.error(f"Error updating cart: {e}")
        await callback.answer("Product removed", show_alert=True)
