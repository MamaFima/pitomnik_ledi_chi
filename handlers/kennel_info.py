async def kennel_info(message: types.Message):
    info = "Наш питомник специализируется на разведении чихуахуа. Мы заботимся о каждом щенке и обеспечиваем им лучшие условия."
    await message.answer(info)

async def kennel_question(message: types.Message):
    await message.answer("Задайте ваш вопрос о питомнике, и я постараюсь ответить!")

def register_kennel_handlers(dp: Dispatcher):
    dp.register_message_handler(kennel_info, lambda message: message.text == "О питомнике")
    dp.register_message_handler(kennel_question, lambda message: message.text.startswith("?"))