from settle import compute_balances, settle

people = ["Eric", "Max", "Andy", "Leo"]
expenses = [("Eric", 30), ("Max", 400), ("Andy", 250), ("Leo", 151), ("Eric", 50)]

balances = compute_balances(people, expenses)
print(balances)
for f, t, a in settle(balances):
    print(f, "->", t, a)
