import telebot
import os
import logging
import configt
import datetime

from markups import *
from database import *
from addition import *

from random import sample
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputMediaPhoto 
from json import load

logging.basicConfig(format='%(sctime)s - %(levelname)s - %(message)s',
					level=logging.INFO,
					filename='bot.log'
					)

with open('config.json', 'r', encoding='utf-8') as fp:
	config = load(fp)

with open("cocktails.json", 'r', encoding='utf-8') as fp:
	cocktails_info = load(fp)

bot = telebot.TeleBot(configt.TOKEN)

name = ""
cocktails_for_party = {}

party_for_delete = ""

party_data_for_edit = {}
cocktail_to_edit_id = -1


@bot.message_handler(commands = ["start"])
def start_bot(message):

	user_id = message.from_user.id
	username = message.from_user.username
	first_name = message.from_user.first_name
	last_name = message.from_user.last_name

	result = check_user(user_id)

	if not result:
		insert_user(user_id, username, first_name, last_name, datetime.date.today())

	markup = create_main_keyboard(config)
	bot.send_message(message.chat.id, config["start_command"], reply_markup = markup)


@bot.message_handler(func = lambda message: message.text == config["main_menu_button"], content_types = ["text"])
def main_menu(message):

	activity_tracking(datetime.date.today(), message.from_user.id)

	global name
	global cocktails_for_party
	global party_for_delete
	global party_data_for_edit
	global cocktail_to_edit_id

	name = ''
	cocktails_for_party = {}
	party_data_for_edit = {}
	cocktail_to_edit_id = -1
	party_for_delete = -1

	bot.send_message(message.chat.id, config["main_menu"], reply_markup = create_main_keyboard(config))


@bot.message_handler(func = lambda message: message.text in config["cocktails_list_buttons"].values(), content_types = ["text"])
def cocktails_work(message):

	activity_tracking(datetime.date.today(), message.from_user.id)
	
	markup = create_main_keyboard(config)
	bot.send_message(message.chat.id, config["wait_command"], reply_markup = markup)
	
	collection_name = ""

	for name, button_text in config["cocktails_list_buttons"].items():
		if button_text == message.text:
			collection_name = name[:-7]

	description = config["cocktails_list_buttons"][collection_name + "_button"]
	cocktails_state = config["collections_info"][collection_name]["photos"]

	if len(cocktails_state) == 0:
		cocktails_state = sample(list(range(50)), k=5)

	media_groups = prepare_media_group(cocktails_state, description)
	
	for media_group in media_groups:
		bot.send_media_group(message.chat.id, media_group, timeout = 10)

@bot.message_handler(func = lambda message: message.text == config["show_cocktails_list_button"], content_types = ["text"])
def show_cocktails_list(message):
	activity_tracking(datetime.date.today(), message.from_user.id)

	bot.send_message(message.chat.id, config["show_cocktails_list"],reply_markup = create_cocktails_collections_keyboard(config))

@bot.message_handler(func = lambda message: message.text == config["choose_party_button"], content_types = ["text"])
def choose_party(message):
	activity_tracking(datetime.date.today(), message.from_user.id)

	partys = select_partys_by_user_and_master(message.from_user.id)
	bot.send_message(message.chat.id, config["choose_party"], reply_markup = create_party_keyboard(config, partys))

@bot.message_handler(func = lambda message: message.text == config["remove_party_button"], content_types = ["text"])
def delete_party_start(message):
	activity_tracking(datetime.date.today(), message.from_user.id)

	data = select_partys_by_user(message.from_user.id)
	markup = create_partys_by_data_keyboard(data)

	if len(data) == 0:
		bot.send_message(message.chat.id, config["not_enougth_partys"])
		main_menu(message)
	else:
		bot.send_message(message.chat.id, config["choose_party_for_delete"], reply_markup = markup)
		bot.register_next_step_handler(message, choose_party_for_delete)

def choose_party_for_delete(message):

	global party_for_delete
	party_for_delete = message.text

	markup = ReplyKeyboardMarkup()
	markup.add(KeyboardButton("Да"))
	markup.add(KeyboardButton("Нет"))

	bot.send_message(message.chat.id, config["delete_confirm"] + message.text + "?", reply_markup = markup)
	bot.register_next_step_handler(message, delete_party)

def delete_party(message):

	if message.text == "Да":
		delete_party_by_name(message.from_user.id, party_for_delete)
		bot.send_message(message.chat.id, config["delete_ended"])
	main_menu(message)

@bot.message_handler(func = lambda message: message.text == config["edit_party_button"],content_types = ["text"])
def choose_party(message):
	activity_tracking(datetime.date.today(), message.from_user.id)

	data = select_partys_by_user_and_master(message.from_user.id)
	markup = create_partys_by_data_keyboard(data)

	bot.send_message(message.chat.id, config["choose_party_for_edit"], reply_markup = markup)
	bot.register_next_step_handler(message, choose_coctail_to_edit)

def choose_coctail_to_edit(message):

	global party_data_for_edit

	if party_data_for_edit.get("name") == None:
		party_data = select_party_by_name_and_user(message.text, message.from_user.id)

		party_data_for_edit["name"] = party_data[3].strip()
		party_data_for_edit["cocktails"] = {}

		cocktails_name = [cocktails_info[str(cocktail_id)]["name"] for cocktail_id in party_data[1]]
		cocktails_count = party_data[2]

		for name, id, count in zip(cocktails_name, party_data[1], party_data[2]):
			party_data_for_edit["cocktails"][name] = {"id" : id, "count" : count}


	text = config["cocktail_in_party_template"] + "\n"
	cocktails_state = [id["id"] for id in party_data_for_edit["cocktails"].values()]

	media_groups = prepare_media_group(cocktails_state)

	for name, cocktail_data in party_data_for_edit["cocktails"].items():
		count = cocktail_data["count"]
		text = text + f" {name} : {count}\n"

	data = [name for name in party_data_for_edit["cocktails"]]

	markup = create_cocktails_by_data_keyboard(config, data)

	for media_group in media_groups:
		bot.send_media_group(message.chat.id, media_group, timeout = 10)
	bot.send_message(message.chat.id, text)
	bot.send_message(message.chat.id, config["choose_cocktail_to_edit"], reply_markup = markup)
	bot.register_next_step_handler(message, choose_count)

def choose_count(message):
	global cocktail_to_edit_id

	count = []
	cocks = []

	if message.text == config["editing_party_end_button"]:
		check = select_masters_partys(party_data_for_edit["name"])
		if len(check) != 0:

			check_tmp = select_party_by_name_and_user(party_data_for_edit["name"] + "(ред)", message.from_user.id)

			for cock in party_data_for_edit["cocktails"].values():
				count.append(cock["count"])
				cocks.append(cock["id"])
			if check_tmp != None:
				print(count)
				update_party(count, party_data_for_edit["name"] + "(ред)", message.from_user.id)
			else:
				insert_party(message.from_user.id, cocks, count, party_data_for_edit["name"]+"(ред)", "Ваша вечеринка")
		else:
			for cock in party_data_for_edit["cocktails"].values():
				count.append(cock["count"])
			name = party_data_for_edit["name"]

			update_party(count, name, message.from_user.id)

		bot.send_message(message.chat.id, config["editing_party_end"])
		main_menu(message)

	else:

		for name, id in party_data_for_edit["cocktails"].items():
			if name == message.text:
				cocktail_to_edit_id = id["id"]

		bot.send_message(message.chat.id, config["enter_count"], reply_markup = ReplyKeyboardRemove())
		bot.register_next_step_handler(message, get_count)

def get_count(message):

	global party_data_for_edit

	try:
		count = int(message.text)
		text = config["cocktail_in_party_template"] + "\n"

		if count < 0:
			bot.send_message(message.chat.id, config["choose_correct_count"])
			bot.register_next_step_handler(message, get_count)
		else:

			for name, cocktail_data in party_data_for_edit["cocktails"].items():
				if cocktail_data["id"] == cocktail_to_edit_id:
					cocktail_data["count"] = count

				count_text = cocktail_data["count"]
				text = text + f" {name} : {count_text}\n"

			data = [name for name in party_data_for_edit["cocktails"]]
			markup = create_cocktails_by_data_keyboard(config, data)


			cocktails_state = [id["id"] for id in party_data_for_edit["cocktails"].values()]
			media_groups = prepare_media_group(cocktails_state)
			for media_group in media_groups:
				bot.send_media_group(message.chat.id, media_group, timeout = 10)

			bot.send_message(message.chat.id, text)
			bot.send_message(message.chat.id, config["choose_cocktail_to_edit"], reply_markup = markup)

			bot.send_message(message.chat.id, config["coctail_count_changed"])
			bot.register_next_step_handler(message, choose_count)
	except ValueError:
		bot.send_message(message.chat.id, config["value_error"])
		bot.register_next_step_handler(message, get_count)


@bot.message_handler(func = lambda message: True, content_types = ["text"])
def party_case(message):
	activity_tracking(datetime.date.today(), message.from_user.id)

	if message.text.split(":")[0] == config["u-drink_party"][:-2] or message.text.split(":")[0] == config["user_party"][:-2]:
		name = message.text.split(":")[1].lstrip()

		party_data = select_party_by_name_and_user(name, message.from_user.id)

		cocktails_count = party_data[2]
		cocktails_state = party_data[1]

		cocktails_names = [cocktails_info[str(id)]["name"] for id in cocktails_state]
		text_count = config["cocktail_in_party_template"] + '\n'

		for cock_name, count in zip(cocktails_names, cocktails_count):
			text_count += f'{cock_name} : {count} \n'

		ingridients = count_ingridients(cocktails_info, cocktails_state, cocktails_count)
		result = f""" *{name.upper()}* \n*Необходимые ингридиенты: *\n"""
		for k, v in ingridients.items():
			if v != 0:
				result += f"""_{k}_ : {v}мл \n"""

		description = party_data[4]

		media_groups = prepare_media_group(cocktails_state, description)
		for media_group in media_groups:
			bot.send_media_group(message.chat.id, media_group, timeout = 10)
		bot.send_message(message.chat.id, text_count)
		bot.send_message(message.chat.id, result, parse_mode="Markdown")

	if message.text == config["create_new_party_button"]:
		bot.send_message(message.chat.id, config["create_new_party_step_1"], reply_markup=ReplyKeyboardRemove())
		bot.register_next_step_handler(message, get_party_name)

def get_party_name(message):
	global name
	if message.text == None:
		bot.send_message(message.chat.id, config["empty_text_error"])
		bot.register_next_step_handler(message, get_party_name)
	else:
		name  = message.text
		markup = create_cocktails_collections_keyboard(config)
		bot.send_message(message.chat.id, config["create_new_party_step_2"], reply_markup = markup)
		bot.register_next_step_handler(message, get_cocktails_by_collection)

def get_cocktails_by_collection(message):
	collection_name = ""

	for k, v in config["cocktails_list_buttons"].items():
		if v == message.text:
			collection_name = k

	description = config["collections_info"][collection_name[:-7]]["description"]
	cocktails_state = config["collections_info"][collection_name[:-7]]["photos"]

	if len(cocktails_state) == 0:
		cocktails_state = sample(list(range(50)), k=5)

	markup = create_cocktails_keyboard(config, cocktails_info, cocktails_state)

	media_groups = prepare_media_group(cocktails_state, description)

	for media_group in media_groups:
		bot.send_media_group(message.chat.id, media_group, timeout = 10)
	bot.send_message(message.chat.id, "Просто нажми на название если хочешь добавить", reply_markup = markup)
	bot.register_next_step_handler(message, get_cocktail)

def get_cocktail(message):

	global cocktails_for_party

	if message.text == config["choose_another_collection_button"]:
		markup = create_cocktails_collections_keyboard(config)
		bot.send_message(message.chat.id, config["choose_another_collection"], reply_markup = markup)
		bot.register_next_step_handler(message, get_cocktails_by_collection)
	elif message.text == config["complete_cocktail_selection_button"]:
		if len(cocktails_for_party) == 0:
			main_menu(message)

		markup = ReplyKeyboardMarkup()
		markup.add(KeyboardButton(config["drinkers_per_party_button"]))
		markup.add(KeyboardButton(config["drinkers_per_cocktail_button"]))


		bot.send_message(message.chat.id, config["types_of_drinkers_count"], reply_markup = markup)
		bot.register_next_step_handler(message, get_drinkers)
	else:
		for id, cocktail in cocktails_info.items():
			if message.text == cocktail["name"]:
				cocktails_for_party[id] = 1
				bot.send_message(message.chat.id, config["cocktail_successfully_aded"])
		bot.register_next_step_handler(message, get_cocktail)

def get_drinkers(message):
	global cocktails_for_party
	global name

	if  message.text == config["drinkers_per_party_button"]:
		bot.send_message(message.chat.id, config["complete_cocktail_selection"], reply_markup = ReplyKeyboardRemove())
		bot.register_next_step_handler(message, get_all_drinkers)
	if message.text == config["drinkers_per_cocktail_button"]:
		cocktails = [int(k) for k in cocktails_for_party]
		quantity = [v for v in cocktails_for_party.values()]

		insert_party(message.from_user.id, cocktails, quantity, name, "Ваша вечеринка")
		message.text = name
		name = ""
		cocktails_for_party = {}
		choose_coctail_to_edit(message)

		

def get_all_drinkers(message):

	global cocktails_for_party
	global name

	try:
		drinkers = int(message.text)

		if drinkers < 1:
			bot.send_message(message.chat.id, config["choose_correct_count"])
			bot.register_next_step_handler(message, get_drinkers_count)
		else:

			for k in cocktails_for_party:
				cocktails_for_party[k] = cocktails_for_party[k] * drinkers
			cocktails = [int(k) for k in cocktails_for_party]
			quantity = [v for v in cocktails_for_party.values()]

			insert_party(message.from_user.id, cocktails, quantity, name, "Ваша вечеринка")
			name = ""
			cocktails_for_party = {}
			bot.send_message(message.chat.id, config["party_creating_end"], reply_markup = create_main_keyboard(config))
	except ValueError:
		bot.send_message(message.chat.id, config["value_error"])
		bot.register_next_step_handler(message, get_drinkers_count)



if __name__ == '__main__':
	bot.polling(none_stop=True)