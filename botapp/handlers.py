from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext 
from aiogram.fsm.state import StatesGroup, State
from decimal import Decimal
from aiogram import F
import time
from botapp.keyboards import start_kb, collections_kb, admin_kb, admin_kb_2, admin_collections_kb, collection_kb
from botapp.db.models import Product, Cart, User
import logging
import os
from aiogram import Bot
from pathlib import Path
from botapp.config import settings
from tortoise.exceptions import ConfigurationError

router = Router()
TOKEN = settings["TOKEN"]
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

class Products(StatesGroup):
    product = State()

class Seecol(StatesGroup):
    collection = State()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
IMAGES_DIR = BASE_DIR / "botapp/images"

# Создаем папку для изображений, если ее нет
if not IMAGES_DIR.exists():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Создана папка {IMAGES_DIR}")

PAGES = [
    {
        "link": ["Open", "colec_firstcol"],
        "image": IMAGES_DIR / "rb3.jpg",
        "caption": "sematary`s 1colection"
    },
    {
        "link": ["Open", "colec_secondcol"],
        "image": IMAGES_DIR / "rb1.jpg",
        "caption": "sematary`s 2colection"
    },
    {
        "link": ["Open", "colec_oldcol"],
        "image": IMAGES_DIR / "rb2.jpg",
        "caption": "sematary`s oldcolection"
    }
]

user_pages = {}

async def verify_image(image_path: Path) -> bool:
    """Проверяет доступность изображения"""
    try:
        return image_path.exists() and image_path.is_file()
    except Exception as e:
        logger.error(f"Ошибка проверки изображения: {e}")
        return False

@router.message(F.text=="🧔 nellProfile")
async def profile_handler(message: Message):
    await message.answer("Cdelai profil pzh")

@router.message(F.text=="📂 nellColections")
async def collections_handler(message: Message):
    user_id = message.from_user.id
    user_pages[user_id] = 0
    
    page_data = PAGES[0]
    
    if not await verify_image(page_data["image"]):
        await message.answer("Изображение недоступно")
        return
    
    try:
        keyboard = collections_kb(
            items=page_data["link"],
            current_page=0,
            total_pages=len(PAGES))
        
        photo = FSInputFile(page_data["image"])
        await message.answer_photo(
            photo=photo,
            caption=page_data["caption"],
            reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка при отправке коллекции: {e}")
        await message.answer("Произошла ошибка при загрузке коллекции")

@router.callback_query(F.data.startswith("col_"))
async def pages_handlers(callback: CallbackQuery):
    user_id = callback.from_user.id
    current_page = user_pages.get(user_id, 0)
    
    if callback.data == "col_prev_page" and current_page > 0:
        new_page = current_page - 1
    elif callback.data == "col_next_page" and current_page < len(PAGES) - 1:
        new_page = current_page + 1
    else:
        await callback.answer()
        return
    
    user_pages[user_id] = new_page
    page_data = PAGES[new_page]
    
    if not await verify_image(page_data["image"]):
        await callback.answer("Изображение недоступно", show_alert=True)
        return
    
    try:
        media = InputMediaPhoto(
            media=FSInputFile(page_data["image"]),
            caption=page_data["caption"])
        
        keyboard = collections_kb(
            items=page_data["link"],
            current_page=new_page,
            total_pages=len(PAGES))
        
        await callback.message.edit_media(
            media=media,
            reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка при обновлении страницы: {e}")
        await callback.answer("Произошла ошибка при загрузке страницы", show_alert=True)
    
    await callback.answer()

@router.message(F.text=="⚙️ nellAdmin")
async def admin_handler(message:Message):
    await message.answer("Choose what to do", reply_markup=admin_kb_2())

@router.callback_query(F.data=="add")
async def add_product(callback:CallbackQuery, state:FSMContext):
    await callback.message.answer("Write type, name, price cherez '/'")
    await state.set_state(Products.product)

@router.message(Products.product)
async def add_product_2(message: Message, state: FSMContext):
    data = await state.get_data()
    is_description = data.get("is_description", False)
    
    if not is_description:
        parts = [part.strip() for part in message.text.split("/")]
        if len(parts) != 3:
            await message.answer("Write type, name, price cherez '/'")
            return
        
        try:
            price = Decimal(parts[2])
        except:
            await message.answer("Цена должна быть числом (например: 1000 или 999.99)")
            return
        
        await state.update_data(
            product_type=parts[0],
            product_name=parts[1],
            price=str(price),
            is_description=True)
        await message.answer("Choose collection:", reply_markup=admin_collections_kb())
    else:
        if not message.photo:
            await message.answer("Put cloth photo")
            return
            
        timestamp = int(time.time() * 1000)
        
        try:
            photo = message.photo[-1]
            file_id = photo.file_id
            file = await bot.get_file(file_id)
            file_ext = file.file_path.split('.')[-1].lower() if '.' in file.file_path else 'jpg'
            file_name = f"{data['collection']}_{timestamp}.{file_ext}"
            destination = os.path.join(IMAGES_DIR, file_name)
            
            await bot.download_file(file.file_path, destination)
            
            collection = data.get("collection")
            if not collection:
                await message.answer("Ошибка: коллекция не выбрана")
                return
            
            await Product.create(
                collection=collection,
                type=data["product_type"],
                name=data["product_name"],
                price=Decimal(data["price"]),
                picture=str(destination))
            
            await message.answer("✅ Succesfully added")
            await state.clear()
        except ConfigurationError as e:
            await message.answer("⚠️ Database configuration error. Please contact admin.")
            logger.error(f"Database error: {e}")
        except Exception as e:
            error_msg = f"⚠️ Error occurred: {str(e)}"
            error_msg = error_msg.replace("<", "&lt;").replace(">", "&gt;")
            await message.answer(error_msg)
            logger.exception("Error in add_product_2")

@router.callback_query(F.data == "1collection")
async def add_1col(callback: CallbackQuery, state: FSMContext):
    await state.update_data(collection="1collection", is_description=True)
    await callback.message.answer("Put cloth photo")
    await callback.answer()

col_pages={}

async def send_collection(callback:CallbackQuery, state:FSMContext):
    data = await state.get_data()
    collection = data.get("collection", "")
    collection_data = await Product.filter(collection=collection)
    products_list = [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "type": p.type,
            "picture": p.picture
        }
        for p in collection_data
    ]
    await state.update_data(products_list=products_list)
    user_id = callback.message.from_user.id
    col_pages[user_id] = 0

    page_data = products_list[0]

    keyboard = collection_kb(
        id=page_data["id"],
        current_page=0,
        total_pages=len(products_list))
        
    photo = FSInputFile(page_data["picture"])
    await callback.message.answer_photo(
        photo=photo,
        caption=f"{page_data["type"]}\n\n{page_data["name"]}\n\nprice: {float(page_data["price"])}",
        reply_markup=keyboard)

@router.callback_query(F.data.startswith("colec_"))
async def get_collection(callback:CallbackQuery, state: FSMContext):
    await state.set_state(Seecol.collection)
    if callback.data=="colec_firstcol":
        await state.update_data(collection="1collection")
        await send_collection(callback, state)
    elif callback.data=="colec_secondcol":
        await state.update_data(collection="2collection")
        await send_collection(callback, state)
    elif callback.data=="colec_oldcol":
        await state.update_data(collection="oldcollection")
        await send_collection(callback, state)
        
@router.callback_query(F.data.startswith("col2_"))
async def pages_handlers(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    current_page = col_pages.get(user_id, 0)
    
    # Получаем данные из состояния
    data = await state.get_data()
    products_list = data.get("products_list", [])
    
    if not products_list:
        await callback.answer("Нет данных о продуктах", show_alert=True)
        return

    if callback.data == "col2_prev_page" and current_page > 0:
        new_page = current_page - 1
    elif callback.data == "col2_next_page" and current_page < len(products_list) - 1:
        new_page = current_page + 1
    else:
        await callback.answer()
        return
    
    col_pages[user_id] = new_page
    page_data = products_list[new_page]
    
    try:
        # Формируем медиа с правильными полями
        media = InputMediaPhoto(
            media=FSInputFile(page_data["picture"]),
            caption=f"{page_data['type']}\n\n{page_data['name']}\n\nprice: {float(page_data['price'])}"
        )
        
        # Используем ту же клавиатуру, что и в первом обработчике
        keyboard = collection_kb(
            id=page_data["id"],
            current_page=new_page,
            total_pages=len(products_list))
        
        await callback.message.edit_media(
            media=media,
            reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка при обновлении страницы: {e}")
        await callback.answer("Произошла ошибка при загрузке страницы", show_alert=True)
    
    await callback.answer()
        






    
       
