def find_index_by_entry0(my_list, value):
    try:
        index = next(i for i, tpl in enumerate(my_list) if tpl[0] == value)
        return index
    except StopIteration:
        return None