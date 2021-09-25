#!/usr/bin/env python3
import datetime as dt
import random


def get_population(date):
    # http://arkot.com/
    myD = date
    myseiki = 1533049200000
    myls = (myD.timestamp() * 1e3 - myseiki) + 32400000
    mylj = (myls * 2.598478) / 1000
    myjinko = round(mylj) + 7594270360
    return myjinko


def get_seed(date):
    population = get_population(date)
    p_under8_5 = population % int(1e8) // int(1e4)
    p_under4 = population % int(1e4)
    seed = random.randrange(min(p_under8_5, p_under4), max(p_under8_5, p_under4))
    return seed


def get_graph(path):
    with open(path) as f:
        edges = [list(map(int, row.split())) for row in f.readlines()]
    vertices = sorted(list(set(sum(edges, []))))  # flatten
    g = {v: [] for v in vertices}
    for edge in edges:
        u, v = edge
        g[u].append(v)
        g[v].append(u)
    return g


def get_next_monday(date):
    utc_tz = dt.timezone.utc
    diff_monday = (7 - date.weekday()) % 7
    nm = date + dt.timedelta(days=diff_monday)
    next_monday_noon = dt.datetime(nm.year, nm.month, nm.day, 12, 0, 0, tzinfo=utc_tz)
    return next_monday_noon


def _print_result(week, date, selected_cell, p):
    str_date = date.strftime("%Y-%m-%d")
    if selected_cell is None:
        str_selected = "not selected"
    else:
        str_selected = f"{selected_cell} selected"
    print(f"week {week:>3}, date {str_date}, {str_selected:>12}, p={p:.3f}")


def _choose_cell(frontier, cur_date):
    seed = get_seed(cur_date)
    idx = seed % len(frontier)
    sorted_frontier = sorted(list(frontier))
    v = sorted_frontier[idx]
    return v


def generage_cell(p, frontier, cur_date):
    q = random.uniform(0, 1)
    if q > p:
        return None
    v = _choose_cell(frontier, cur_date)
    return v


def simulate(graph_path, start_date=dt.datetime.today()):
    graph = get_graph(graph_path)
    all_v_size = len(graph.keys())
    p = 5 / 6
    p_diff = p / all_v_size
    print(p_diff)
    week = 0
    cur_date = get_next_monday(start_date)
    visited = set()
    frontier = set([1])
    for adj in graph[1]:
        frontier.add(adj)
    while len(visited) < all_v_size:
        week += 1
        cur_date += dt.timedelta(weeks=1)
        v = generage_cell(p, frontier, cur_date)
        if v is None:
            _print_result(week, cur_date, None, p)
            continue
        visited.add(v)
        _print_result(week, cur_date, v, p)
        for adj in graph[v]:
            if adj not in visited:
                frontier.add(adj)
        frontier.remove(v)
        p -= p_diff


if __name__ == "__main__":
    graph_path = "./graph.txt"
    simulate(graph_path)
