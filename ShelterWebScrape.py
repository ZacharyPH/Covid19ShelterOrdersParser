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
    when = place.contents[1].contents[1].contents[0].split(" ")[1:]
    date = [" ".join(str(i) for i in when[:2]), " ".join(str(i) for i in when[3:5])]
    return {"order": order, "date": date}


def get_counties(state) -> dict:    # TODO: Implement
    orders = {}
    for county in state.find_all(attrs={"class": "place-wrap"}):
        name = county.contents[1].contents[0]
        pop = county.contents[1].contents[1].contents[0].replace(",", "").split(" ")[1:-1]
        order = county.contents[3].contents[0]
        when = county.contents[3].contents[1].contents[0].split(" ")[2:]
        date = [" ".join(str(i) for i in when[:2]), " ".join(str(i) for i in when[3:5])]
        orders[name] = {"order": order, "date": date, "pop": pop}
    return orders


def populations(pop):   # TODO: Implement (converts 'millions' into actual number)
    pass


def dates(date):    # TODO: Implement (converts words 'March 25' into actual date)
    pass


def main():
    try:
        r = requests.get('https://www.nytimes.com/interactive/2020/us/coronavirus-stay-at-home-order.html')
    except requests.exceptions.MissingSchema:
        print("The supplied URL is invalid. Please update and run again.")
        raise Exception("InvalidURL")
    soup = BeautifulSoup(r.text, 'html.parser')

    state_wraps = soup.find_all(attrs={"class": "state-wrap"})
    states = {}
    orders = open("Stay At Home Orders.csv", "w")
    for state_wrap in state_wraps:
        st = state_wrap.contents[1].next.strip(" ")
        if len(state_wrap.attrs["class"]) == 2:
            order = get_order(state_wrap.contents[5])
            order["pop"] = state_wrap.contents[1].contents[1].contents[0].replace(",", "").split(" ")[1:-1]
        else:
            order = get_counties(state_wrap)

        states[st] = order

    with open("Stay At Home Orders.csv", "w") as orders:
        orders.write("\n".join(str(state) + " - " + str(data) for state, data in states.items()))


if __name__ == "__main__":
    main()
