from info import ActionType

n_directions = 6
max_armies = 12

move_action_list = [(ActionType.PASS, None, None)]  # PASS
move_actions_codes = {(ActionType.PASS, None, None): 0}

for army_id in range(max_armies):
    for dirc in range(n_directions):
        a = (ActionType.MOVE, army_id, dirc)
        move_actions_codes[a] = len(move_action_list)
        move_action_list.append(a)
