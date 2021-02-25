def find_in_gazetteers_return_tag(tag_string, gazetteers):
    if tag_string in gazetteers['female_names']:
        tag_level_2 = "given name - female"
    elif tag_string in gazetteers['male_names']:
        tag_level_2 = "given name - male"

    elif tag_string in gazetteers['countries']:
        tag_level_2 = "country"
    elif tag_string in gazetteers['spanish_territories']:
        tag_level_2 = "territory"
    elif tag_string in gazetteers['spanish_cities']:
        tag_level_2 = "city"
    elif tag_string in gazetteers['surnames']:
        tag_level_2 = "family name"
    else:
        tag_level_2 = ""
    return tag_level_2

def process_person_tag(token, last_tag_id, last_tag, gazetteers):
     # Parse one name
    tag_level_1 = "PERSON"
    tag_level_2 = find_in_gazetteers_return_tag(token, gazetteers)
    # if last tag is person
    if "PERSON" in last_tag and last_tag != "_":
        tag_id_1 = "[" + str(last_tag_id - 1) + "]"
        tag_id_2 = "[" + str(last_tag_id + 1) + "]"
        add_tag = 1
    else:
        tag_id_1 = "[" + str(last_tag_id + 1) + "]"
        tag_id_2 = "[" + str(last_tag_id + 2) + "]"
        add_tag = 2
    tag = tag_level_1 + tag_id_1 + "|" + tag_level_2 + tag_id_2
    tag_id = "".join(['*',tag_id_1,'|*',tag_id_2])
    return tag_id, tag, add_tag
    



def process_territory_tag(token, last_tag_id, last_tag, gazetteers):
    # Parse one territory
    tag_level_1 = "ADDRESS"
    tag_level_2 = find_in_gazetteers_return_tag(token, gazetteers)
    tag_id_1 = "[" + str(last_tag_id + 1) + "]"
    tag_id_2 = "[" + str(last_tag_id + 2) + "]"
    tag = tag_level_1 + tag_id_1 + "|" + tag_level_2 + tag_id_2
    tag_id = "".join(['*',tag_id_1,'|*',tag_id_2])
    add_tag = 2
    return tag_id, tag, add_tag