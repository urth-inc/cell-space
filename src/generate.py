#!/usr/bin/env python3
import csv
import datetime as dt
import argparse

import rule


def _calc_p_init(graph, init_v):
    init_v_dgree = len(graph[init_v])
    return init_v_dgree / (init_v_dgree + 1)


def _calc_p_diff(graph, init_v):
    all_v_size = len(graph.keys())
    p_init = _calc_p_init(graph, init_v=init_v)
    p_diff = p_init / all_v_size
    return p_diff


def _read_results(graph, result_path, init_v):
    with open(result_path) as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        results = [{k: v for k, v in row.items()} for row in reader]
    visited = set()
    frontier = set([init_v])
    if len(results) == 0:
        return frontier, visited, 1, _calc_p_init(graph, init_v)
    for result in results:
        cell_id = result["cell_id"]
        if not cell_id:
            continue
        v = int(cell_id)
        visited.add(v)
        for adj in graph[v]:
            if adj not in visited:
                frontier.add(adj)
        frontier.remove(v)
    cur_week = int(results[-1]["week"]) + 1
    cur_p = float(results[-1]["next_p"])
    return frontier, visited, cur_week, cur_p


def _write_result(result_path, cur_week, cur_date, new_v, cur_p, next_p):
    fields = [cur_week, cur_date.isoformat(), new_v, f"{cur_p:.4f}", f"{next_p:.4f}"]
    with open(result_path, "a") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(fields)
    return ",".join(map(str, fields))


def _tweet(population, seed, new_v, cur_p):
    if new_v is None:
        tweet_str = "セルは生成されませんでした。\n" f"今回の生成結果 : {cur_p:.1%}"
    else:
        tweet_str = (
            "セルが生成されました。"
            f"世界人口 : {population}人\n"
            f"選定乱数 : {seed}\n"
            f"抽出結果 : {new_v:02}番\n"
            f"今回の生成結果 : {cur_p:.1%}"
        )
    tweet_str = "(テストです。)" + tweet_str
    today = dt.datetime.now().strftime("%Y-%m-%d")
    tweet_file_path = f"../tweets/{today}-result.tweet"
    with open(tweet_file_path, "w") as f:
        f.write(tweet_str)


def generate_cell(graph_path, result_path, init_v=1):
    graph = rule.get_graph(graph_path)
    frontier, visited, cur_week, cur_p = _read_results(graph, result_path, init_v)
    print("frontier:", frontier)
    if len(frontier) == 0:
        print("no frontier")
        exit(1)
    today = dt.datetime.today()
    new_v, p, seed, population = rule.generage_cell(cur_p, frontier, today)
    p_diff = _calc_p_diff(graph, init_v)
    if new_v is None:
        next_p = cur_p
    else:
        next_p = cur_p - p_diff
    result = _write_result(result_path, cur_week, today, new_v, cur_p, next_p)
    print(f"result: {result}")
    _tweet(population, seed, new_v, p)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--graph", help="graph file path", default="./graph.txt")
    parser.add_argument(
        "-r", "--result", help="result file path", default="../results.csv"
    )
    args = parser.parse_args()
    graph_path = args.graph
    result_path = args.result
    generate_cell(graph_path, result_path)
