from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext 
from aiogram.fsm.state import StatesGroup, State
from decimal import Decimal
from aiogram import F
from botapp.keyboards import cart_kb, admin_kb, start_kb
from botapp.db.models import Product, Cart, User, Orders
import logging
import os
from aiogram import Bot
from pathlib import Path
from botapp.config import settings
from tortoise.exceptions import ConfigurationError

user_router = Router()

class Users(StatesGroup):
    user_data = State()

TOKEN = settings["TOKEN"]
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@user_router.message(CommandStart())
async def start_reg_user(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not await User.filter(user_id=user_id).exists():
        await message.answer("Send your address and email, use '/' between them")
        await state.set_state(Users.user_data)
        print("123")
    else:
        if user_id == settings["ADMIN"]:
            await message.answer("Hello admin", reply_markup=admin_kb())
        else:   
            await message.answer("Hello and welcome to nell/store/bot", reply_markup=start_kb())

@user_router.message(Users.user_data)
async def reg_user(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if await User.filter(user_id=user_id).exists():
        await message.answer("You are already registered!", reply_markup=start_kb())
        await state.clear()
        return
    
    data = message.text.split("/")
    
    if len(data) == 2:
        address = data[0].strip()
        email = data[1].strip()
        
        if "@" not in email or "." not in email:
            await message.answer("Please enter a valid email address")
            return
        
        try:
            await User.create(
                user_id=user_id,
                user_username=message.from_user.username,
                email=email,
                address=address
            )
            await message.answer("Successfully registered!", reply_markup=start_kb())
            await state.clear()
        except Exception as e:
            await message.answer("Registration error. Please try again.")
            logger.error(f"Registration error: {e}")
    else:
        await message.answer("Please use format: Address / email\nExample: 123 Main St / user@example.com")

@user_router.message(F.text == "🧔 nellProfile")
async def main_profile_handler(message: Message):
    user_id = message.from_user.id
    user_data = await User.filter(user_id=user_id).first()
    active_orders_data = await Orders.filter(user_id=user_id, status="active")
    done_users_data = await Orders.filter(user_id=user_id, status="done")
    await message.answer(f"hello, {user_data.user_username}\n\nyour orders:\nactive orders: {len(active_orders_data)}\ndone orders: {len(done_users_data)}")