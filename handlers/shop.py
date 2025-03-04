async def shop_menu(message: types.Message):
    await message.answer("В нашем магазине вы можете приобрести аксессуары и корм для вашего питомца. Выберите товар из каталога.")

def register_shop_handlers(dp: Dispatcher):
    dp.register_message_handler(shop_menu, lambda message: message.text == "Магазин")