from database import *
import os
from telebot.types import InputMediaPhoto 

def count_ingridients(cocktails_info, cocktails_state, cocktails_count):

	result = {}

	for id, count in zip(cocktails_state, cocktails_count):
		for k, v in cocktails_info[str(id)].items():
			if k != "name":
				if result.get(k) != None:
					result[k] += v * count
				else:
					result[k] = v * count

	return result

def activity_tracking(date, user_id):
	update_activity(date, user_id)

def prepare_media_group(cocktails_state, description = ""):

	media_group = []
	media_group_result = []

	for id in cocktails_state:
		media_group.append(InputMediaPhoto(open(os.path.join('img', f'main_information-{id}.png'), 'rb')))

	if description != "":
		media_group[-1].caption = description

	if len(media_group) > 10:

		media_group_length = len(media_group)
		media_group_slices = len(media_group) // 5

		media_group_result = [media_group[5 * i: 5 * (i + 1)] for i in range(media_group_slices)]
		media_group_result[-1].extend(media_group[5 * media_group_slices:])
	else:
		media_group_result = [media_group]

	return media_group_result