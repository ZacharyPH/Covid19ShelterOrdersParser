import requests
from datetime import datetime
from bs4 import BeautifulSoup
from StateCodes import state_abrv


def get_order(place) -> dict:
    """Returns a dict containing the order for a state"""
    # order = place.contents[1].contents[0]
    when = (place.contents[1].contents[1].contents[0].split(" ") + ["0"])[2:4]
    date_str = " ".join(str(i) for i in when[:2] + ["2020"])
    date = datetime.strptime(date_str, "%B %d %Y").strftime("%m/%d/%Y")
    return {"date": date}   # {"order": order, "date": date}


def get_counties(state) -> list:
    """Returns a list of dicts of orders by county for a state"""
    orders = []
    for county in state.find_all(attrs={"class": "place-wrap"}):
        name = county.contents[1].contents[0].strip(" ").split(" ")
        if name[-1] == "County":
            name = " ".join(name[:-1]).upper()
        else:
            name = " ".join(name).upper()
        pop = populations(county.contents[1].contents[1].contents[0].replace(",", "").split(" ")[1:-1])
        # order = county.contents[3].contents[0].strip(" ")
        when = county.contents[3].contents[1].contents[0].split(" ")[2:4]
        date_str = " ".join(str(i) for i in when[:2]) + " 2020"
        date = datetime.strptime(date_str, "%B %d %Y").strftime("%m/%d/%Y")
        # [{"county": name, "order": order, "date": date, "pop": pop}]
        orders += [{"county": name, "date": date, "pop": pop}]
    return orders


def populations(pop) -> int:
    """Converts a list containing population information into an int"""
    if len(pop) == 1:
        return int(pop[0])
    text2num = {"thousand": 1000,
                "million": 1000000}
    return int(float(pop[0]) * text2num[pop[1]])


def get_state_wraps():
    """Parses the NTY article for a list of state and county orders, returns bs4.element.ResultSet"""
    try:
        r = requests.get('https://www.nytimes.com/interactive/2020/us/coronavirus-stay-at-home-order.html')
    except requests.exceptions.MissingSchema:
        print("The supplied URL is invalid. Please update and run again.")
        raise Exception("InvalidURL")
    soup = BeautifulSoup(r.text, 'html.parser')
    date = soup.find(attrs={"class": "css-wcxsge"}).contents[2].replace(",", "")
    return soup.find_all(attrs={"class": "state-wrap"}), date


def populate_states(state_wraps, date, rebuild=False) -> dict:
    """
    Attempts to retrieve state and county orders
    :param state_wraps: bs4.element.ResultSet of state data
    :param date: date NYT article was last updated
    :param rebuild: (T) fetch website data and update files. (F) retrieve local data from previous fetch
    :return:
    """
    datafile = "Covid19ShelterOrders.csv"
    if not rebuild:
        try:
            return parse_data(datafile)
        except FileNotFoundError:
            print("Stored data cannot be found.", end=" ")

    print("Rebuilding...")

    states = {"State": [{"county": "County", "order": "Order", "date": "Date", "pop": "Population"}]}
    for state_wrap in state_wraps:
        st = state_abrv(state_wrap.contents[1].next.strip(" "))
        if len(state_wrap.attrs["class"]) == 2:
            order = get_order(state_wrap.contents[5])
            order["pop"] = populations(state_wrap.contents[1].contents[1].contents[0].replace(",", "").split(" ")[1:-1])
            order["county"] = "STATEWIDE"
            order = [order]
        else:
            order = get_counties(state_wrap)

        states[st] = order

    if rebuild:
        with open(datafile, "w") as orders:
            # orders.write("State, County, Population, Order, Date\n")
            for state, counties in states.items():
                for county in counties:
                    orders.write(state + "," + county["county"] + "," + str(county["pop"]) + ","
                                 + county["date"] + "\n")  # county["order"]
            today = datetime.now().strftime("%m/%d/%Y")
            date = datetime.strptime(date, "%B %d %Y").strftime("%m/%d/%Y")
            orders.write(",,,\nScript last run:," + today + ", Data from:," + date)
        print("Data written to", datafile)
    return states


def parse_data(filename) -> dict:
    """Retrieve order information from local 'Covid19ShelterOrders.csv' and return as dict"""
    states = {}
    orders = open(filename, "r")
    for line in orders.readlines()[:-2]:    # The final two lines reference update data and are not needed
        st, county, pop, order, date = line.split(", ")
        try:
            pop = int(pop)
        except ValueError:
            pass
        new_county = [{"county": county, "date": date.strip("\n"), "pop": pop}]  # "order": order,
        try:
            states[st] += new_county
        except KeyError:
            states[st] = new_county
    orders.close()
    return states


def main() -> dict:
    rebuild = True
    state_wraps, date = "", ""
    if rebuild:
        state_wraps, date = get_state_wraps()
    states = populate_states(state_wraps, date, rebuild=rebuild)

    return states


if __name__ == "__main__":
    main()
