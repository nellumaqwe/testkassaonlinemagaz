from aiogram import Router, types
from aiogram.filters import CommandStart
from email_validator import validate_email
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile 
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext 
from aiogram.fsm.state import StatesGroup, State
from decimal import Decimal
from aiogram import F
from botapp.keyboards import cart_kb, order_kb, payment_kb
from botapp.db.models import Product, Cart, User, Orders
import logging
from dadata import Dadata
import os
import asyncio
from datetime import datetime
from aiogram import Bot
from pathlib import Path
from botapp.config import settings
from tortoise.exceptions import ConfigurationError
import uuid
import requests
from yookassa import Configuration, Payment

Configuration.account_id = '1071512'
Configuration.secret_key = 'test_1m_3nSHnamjHi4BfAhaGRTlF9xpgRb5e9JLPkz3_tro'

orders_router = Router()

TOKEN = settings["TOKEN"]
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Order(StatesGroup):
    order_data=State()
    admin_data=State()

@orders_router.callback_query(F.data.startswith("buy"))
async def buy_handler(callback:CallbackQuery, state:FSMContext):
    user_id=callback.from_user.id
    user_username=callback.from_user.username
    order_type=callback.data.split("/")
    products_list=[]
    u = await User.filter(user_id=user_id).first()
    email = u.email
    address = u.address
    if order_type[1] == "all":
        products_data = await Cart.filter(user_id=user_id)
        for item in products_data:
            p=await Product.filter(id=item.product_name).first()
            products_list.append(
                {"id": p.id,
                "name": p.name,
                "price": p.price}
            )

        price = round(sum(float(product["price"]) for product in products_list), 2)
        products_id=[str(product["id"]) for product in products_list]
        names = [product["name"] for product in products_list]
        await payment_operation(names, products_id, price, email, address, user_id, user_username,  callback, state)
    if order_type[1] != "all":
        p = await Product.filter(id=order_type[1]).first()
        price = round(float(p.price), 2)
        products_id = [p.id]
        await payment_operation(names, products_id, price, email, address, user_id, user_username,  callback, state)
        

async def payment_operation(names, products_id, price, email, address, user_id, user_username, callback:CallbackQuery, state:FSMContext):
    order_time=datetime.now()
    await Orders.create(
        user_id=user_id,
        product_name=products_id,
        address = address,
        order_time=order_time,
        email=email
    )

    payment = Payment.create({
        "amount":{
            "value": f"{price}",
            "currency": "RUB"
        },
        "confirmation":{
            "type": "redirect",
            "return_url": "https://"
        },
        "capture":True,
        "description": f"payment"
    }, uuid.uuid4())

    url = payment.confirmation.confirmation_url
    pay_message  = await callback.message.answer(f"press the button to pay for your products", reply_markup=order_kb(url))
    for i in range(30):
        await asyncio.sleep(10)
        check_payment = Payment.find_one(payment_id=payment.id)
        if check_payment.status == 'succeeded':
            await callback.message.answer("succeed, wait for information from admin")
            await pay_message.delete()
            await Orders.filter(orser_time=order_time).update(status="active")
            await send_order_data_to_admin(names, products_id, user_username, price, address)
            return            
        elif check_payment.status == 'canceled': 
            await callback.message.answer("payment was canceled")
            await Orders.filter(orser_time=order_time).update(status="canceled")
            return


async def send_order_data_to_admin(names, products_id, user_username, price, address):

    if not isinstance(products_id, list):
        products_id = [products_id]
    media = []
    names_str = ', '.join(names)

    for product_id in products_id:
        p = await Product.filter(id=product_id).first()
        if len(media)<1:       
            media.append(InputMediaPhoto(media=FSInputFile(p.picture), caption=f"user @{user_username} ordered {names_str} for {price} rub\nhis address: {address}"))
        else:
            media.append(InputMediaPhoto(media=FSInputFile(p.picture)))

    await bot.send_media_group(chat_id=settings["ADMIN"], media=media)


@orders_router.callback_query(F.data=="watch_orders")
async def watch_orders_handler(callback:CallbackQuery):
    return