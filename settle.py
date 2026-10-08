def compute_balances(people, expenses):
    balances = {person: 0 for person in people}
    for payer, amount in expenses:
        # computes the share for each individual payment
        share = amount / len(people)
        # deducts each share in balance
        for person in people:
            balances[person] -= share
        # adds total amount of this payment to the balance of who paid for it
        balances[payer] += amount
    rounded_balances = {person: round(balance, 2) for person, balance in balances.items()}
    return rounded_balances


def settle(balances):
    # collects and sorts the people with a positive balance (to receive money), largest creditor first 
    creditors = sorted(
        [p for p, b in balances.items() if b > 0],
        key=lambda p: -balances[p],
    )
    # collects and sorts the people with a negative balance (to pay money), most debt first
    debtors = sorted(
        [p for p, b in balances.items() if b < 0],
        key=lambda p: balances[p],
    )
    # greedy algorithm: always match the largest debtor with the largest creditor
    transfers = []
    i = 0
    j = 0
    while i < len(creditors) and j < len(debtors):
        c, d = creditors[i], debtors[j]
        # each transfer takes the smaller of the two amounts, so at least one person is settled
        amount = min(balances[c], -balances[d])          
        transfers.append((d, c, round(amount, 2)))
        balances[c] -= amount                       
        balances[d] += amount
        # move to the next person once either is settled
        if abs(balances[c]) < 1e-9:   
            i += 1
        if abs(balances[d]) < 1e-9:
            j += 1
    return transfers
