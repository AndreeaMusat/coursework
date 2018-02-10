# Tudor Berariu, 2017
from argparse import ArgumentParser, Namespace
import os
INF = 99999999999999

def read_input_file(in_file):
    tasks = {}

    with open(in_file) as f:
        n, p = map(int, f.readline().strip().split(","))
        for _ in range(n):
            task_info = list(map(int, f.readline().strip().split(",")))
            i, di, ti = task_info[0:3]
            tasks[i] = Namespace(di=di, ti=ti, conds=task_info[3:])
    return n, p, tasks


def eval_solution(out_file, n, p, tasks):
    if os.stat(out_file).st_size == 0:
        return INF

    cost, started_at, ended_at = 0, {}, {}
    with open(out_file) as f:
        for _ in range(p):
            n_p = int(f.readline().strip())
            proc_free_at = 0
            for _ in range(n_p):
                i, si = map(int, f.readline().strip().split(","))
                assert i not in started_at, "Task already scheduled!"
                assert si >= proc_free_at, "Processor was not ready!"
                started_at[i] = si
                ended_at[i] = proc_free_at = si + tasks[i].di
                cost += max(0, ended_at[i] - tasks[i].ti)

    for i, info in tasks.items():
        assert i in started_at, "All tasks need to be scheduled!"
        si = started_at[i]
        for j in info.conds:
            assert j in ended_at and ended_at[j] <= si, "Constraint fail!"

    return cost


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("in_file", help="Problem file")
    arg_parser.add_argument("out_file", help="Path to solution file")
    args = arg_parser.parse_args()

    n, p, tasks = read_input_file(args.in_file)
    cost = eval_solution(args.out_file, n, p, tasks)

    if cost == INF:
	print("No solution found")
    else:
        print("%d" % cost)


if __name__ == "__main__":
    main()
    # read_input_file("data")
