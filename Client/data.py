import pandas as pd

df = pd.read_csv('transaction_data.csv')

visited_accounts = set([])
operations_df = pd.DataFrame(data={"type": [], "account1":[], "account2":[], "balance":[]})  

for index, row in df.iterrows():
    acc1 = row["Sender Account ID"]
    acc2 = row["Receiver Account ID"]
    balance = row["Transaction Amount"]
    type_ = row["Transaction Type"]
    concats = [operations_df]
    if acc1 not in visited_accounts:
        concats.append(
            pd.DataFrame(
                {
                    "type": ["create_account"],
                    "account1": [acc1],
                    "account2": ["--"],
                    "balance": ["--"],
                }
            )
        )
        visited_accounts.add(acc1)

    if acc2 not in visited_accounts:
        concats.append(
            pd.DataFrame(
                {
                    "type": ["create_account"],
                    "account1": [acc2],
                    "account2": ["--"],
                    "balance": ["--"],
                }
            )
        )
        visited_accounts.add(acc2)
    concats.append(
        pd.DataFrame(
            {
                "type": [type_],
                "account1": [acc1],
                "account2": [acc2],
                "balance": [balance],
            }
        )
    )
    operations_df = pd.concat(concats, ignore_index=True)


operations_df