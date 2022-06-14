from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputMediaPhoto

def resize_keyboard(data):

	result = [data[2*i : 2*(i+1)] for i in range(len(data) // 2)]
	if len(data) % 2 != 0:
		result.append([data[-1]])

	return result

def create_main_keyboard(config):
	markup = ReplyKeyboardMarkup()
	markup.add(KeyboardButton(config["choose_party_button"]))
	markup.add(KeyboardButton(config["show_cocktails_list_button"]))
	return markup

def create_cocktails_collections_keyboard(config):
	markup = ReplyKeyboardMarkup()
	buttons = []
	for name in config["cocktails_list_buttons"].values():
		buttons.append(name)

	if len(buttons) > 6:
		buttons = resize_keyboard(buttons)

		for cocktails in buttons:
			markup.add(*cocktails)
	else:
		markup.add(*buttons)

	return markup

def create_party_keyboard(config, data):
	markup = ReplyKeyboardMarkup()
	buttons = []
	for party in data:
		button_name = config["u-drink_party"] + party[3].strip() if party[0] == -1 else config["user_party"] + party[3].strip()
		buttons.append(button_name)

	if len(buttons) > 6:
		buttons = resize_keyboard(buttons)
		for cocktails in buttons:
			markup.add(*cocktails)
	else:
		markup.add(*buttons)


	markup.add(KeyboardButton(config["main_menu_button"]))
	markup.add(KeyboardButton(config["create_new_party_button"]))
	markup.add(KeyboardButton(config["remove_party_button"]))
	markup.add(KeyboardButton(config["edit_party_button"]))
	return markup

def create_partys_by_data_keyboard(data):
	markup = ReplyKeyboardMarkup()
	buttons = []

	for party in data:
		buttons.append(party[3].strip())

	if len(buttons) > 6:
		buttons = resize_keyboard(buttons)

		for cocktails in buttons:
			markup.add(*cocktails)
	else:
		markup.add(*buttons)

	return markup

def create_cocktails_keyboard(config, cocktails_info, data):
	markup = ReplyKeyboardMarkup()
	buttons = []
	for id in data:
		buttons.append((cocktails_info[str(id)]["name"]))

	if len(buttons) > 6:
		buttons = resize_keyboard(buttons)
		for cocktails in buttons:
			markup.add(*cocktails)
	else:
		markup.add(*buttons)

	markup.add(KeyboardButton(config["choose_another_collection_button"]))
	markup.add(KeyboardButton(config["complete_cocktail_selection_button"]))
	return markup

def create_cocktails_by_data_keyboard(config, data):
	markup = ReplyKeyboardMarkup()
	buttons = []

	for name in data:
		buttons.append(name)

	if len(buttons) > 6:
		buttons = resize_keyboard(buttons)

		for cocktails in buttons:
			markup.add(*cocktails)
	else:
		markup.add(*buttons)


	markup.add(KeyboardButton(config["editing_party_end_button"]))

	return markup
