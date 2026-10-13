import json
import random

from click import prompt
# from openai import OpenAI, OpenAIError

from app.settings import settings


class MissingOpenAIKey(RuntimeError):
    pass


class CategorizationError(RuntimeError):
    pass

# TODO: read this from Database table
class Categorization:
    classifications = {
        1: "other or unclear",
        2: "groceries",
        3: "dining out",
        4: "utilities",
        5: "transportation",
        6: "entertainment",
        7: "healthcare",
        8: "shopping",
        9: "housing",
        10: "education",
        11: "miscellaneous",
        12: "income"
    }

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini") -> None:
        self.api_key = api_key or settings.openai_api_key.get_secret_value()
        self.model = model

    def categorize(
        self, *, amount: float, description: str, transaction_type: str
    ) -> int:
        if not self.api_key:
            raise MissingOpenAIKey("OPENAI_API_KEY is not configured")

        prompt = (
            "Classify this financial transaction. Return a JSON object with one integer "
            f'field, "classification", using one of these IDs: '
            f"{json.dumps(self.classifications)}. Transaction: "
            f"amount={amount}, type={transaction_type}, description={description!r}."
        )

        # print(prompt)
        return random.choice(list(self.classifications.keys()))

        # try:
        #     response = OpenAI(api_key=self.api_key).chat.completions.create(
        #         model=self.model,
        #         temperature=0,
        #         response_format={"type": "json_object"},
        #         messages=[
        #             {"role": "system", "content": "Return only the requested JSON object."},
        #             {"role": "user", "content": prompt},
        #         ],
        #     )
        # except OpenAIError as error:
        #     raise CategorizationError("Transaction categorization failed") from error

        # content = response.choices[0].message.content
        # try:
        #     classification = json.loads(content or "{}")["classification"]
        # except (KeyError, TypeError, json.JSONDecodeError) as error:
        #     raise CategorizationError("Categorizer returned an invalid response") from error

        # if type(classification) is not int or classification not in self.classifications:
        #     raise CategorizationError("Categorizer returned an unknown classification")
        # return classification
