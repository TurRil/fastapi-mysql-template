
import csv
import json

from pathlib import Path
from urllib.request import Request, urlopen
from lib import check_cfg, get_cfg

from app.api.categorization import Categorization

TRANSACTION_URL = "http://localhost:8090/transactions"


def post_transaction(row: dict[str, str]) -> str:

    print("Posting transaction:", row)
    payload = {
        "transaction_id": row.get('Transaction ID'),
        "amount": row.get('Amount'),
        "transaction_date": row.get('Timestamp'),
        "description": row.get('Description'),
        "transaction_type": row.get('Transaction Type'),
        "account_number": row.get('Account Number')
    }

    print(json.dumps(payload).encode("utf-8"))
    # request = Request(
    #     TRANSACTION_URL,
    #     data=json.dumps(payload).encode("utf-8"),
    #     headers={"Content-Type": "application/json"},
    #     method="POST",
    # )
    # with urlopen(request, timeout=10) as response:
    #     return response.read().decode("utf-8")


def main(settings):
    # print("Settings loaded successfully.")
    # print(settings)

    with open(Path("data/transaction_history.csv"), "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        i = 0
        for row in reader:
            print(post_transaction(row))
            i += 1

            break
            # if i > 10:
                # break

    # TXN00001	-87.18	2024-05-16 07:22:18.808433	Municipal Tax Payment	debit	NLINGB1944573686

    # categorization_test = Categorization(settings.openai_api_key.get_secret_value())
    # test_transaction = {
    #     "amount": -87.18,
    #     "description": "Municipal Tax Payment",
    #     "transaction_type": "debit"
    # }
    # classification = categorization_test.categorize(
    #     amount=test_transaction["amount"],
    #     description=test_transaction["description"],
    #     transaction_type=test_transaction["transaction_type"]
    # )
    # print(f"Classification result: {classification}")

if __name__ == '__main__':
    if check_cfg():
        main( get_cfg() )
    else:
        print("ERR: Missing config file.")
