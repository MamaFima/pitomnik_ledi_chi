async def breed_info(message: types.Message):
    info = "Чихуахуа — это маленькая, энергичная и умная порода собак. Они известны своей преданностью и дружелюбием."
    await message.answer(info)

async def breed_question(message: types.Message):
    await message.answer("Задайте ваш вопрос о породе чихуахуа, и я постараюсь ответить!")

def register_breed_handlers(dp: Dispatcher):
    dp.register_message_handler(breed_info, lambda message: message.text == "О породе (чихуахуа)")
    dp.register_message_handler(breed_question, lambda message: message.text.startswith("?"))