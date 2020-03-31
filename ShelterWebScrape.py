import requests
from bs4 import BeautifulSoup


def get_state(state):
    state_info = str(state).split("<span")
    if len(state_info) == 1:
        return state_info[0][4:-5]
    else:
        return state_info[0][4:-1]


def get_order(place) -> dict:
    order = place.contents[1].contents[0]
    date = place.contents[1].contents[1].contents[0][2:]
    pop = 0
    return {"order": order, "date": date, "pop": pop}


def get_counties(state) -> dict:    # TODO: Implement
    return {"order": "order", "date": "date"}


def main():
    r = requests.get('https://www.nytimes.com/interactive/2020/us/coronavirus-stay-at-home-order.html')
    soup = BeautifulSoup(r.text, 'html.parser')

    state_wraps = soup.find_all(attrs={"class": "state-wrap"})
    states = {}
    for state_wrap in state_wraps:
        st = state_wrap.contents[1].next
        if len(state_wrap.attrs["class"]) == 2:
            print("Statewide state!", end=" ")
            order = get_order(state_wrap.contents[5])
            order["pop"] = 1    # TODO: Implement
        else:
            print("State:", st)
            order = get_counties(state_wrap.contents)

        states[st] = order
        print(states)
        with open("Stay At Home Orders.csv", "w") as f:
            f.write("\n".join(str(state) + str(data) for state, data in states.items()))


if __name__ == "__main__":
    main()