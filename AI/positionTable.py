import os
import pickle


def update_position_table(path, new_data):
    if not os.path.exists(path):
        data = {}
    else:
        with open(path, "rb") as f:
            data = pickle.load(f)

    for d in new_data:
        for k, v in d.items():
            prev_data = data.get(k)
            if prev_data is None:
                data[k] = (v[0], v[1], v[2], v[3])
            else:
                data[k] = (v[0], prev_data[1] + v[1], prev_data[2] + v[2], prev_data[3] + v[3])

    with open(path, "wb") as f:
        pickle.dump(data, f)


def show_position_table(path):
    with open(path, "rb") as f:
        data = pickle.load(f)
        n = 0
        for k, v in data.items():
            if v[1] + v[2] + v[3] > 1:
                n += 1
        lst = list(data.items())
        lst.sort(key=lambda x: x[1][1] + x[1][2] + x[1][3])
        print(*lst, sep='\n')
        print(f"{len(data)} positions")
        exit(0)
