import httpx

class CurrencyServiceError(Exception):
    pass

class CurrencyService:
    def __init__(self):
        self.base_url = "https://api.exchangerate-api.com/v4/latest"

    def convert(self, amount: float, from_currency: str, to_currency: str) -> str:
        try:
            response = httpx.get(
                f"{self.base_url}/{from_currency.upper()}",
                timeout=5
            )
            response.raise_for_status()
            data = response.json()

            rates = data.get("rates", {})
            to_rate = rates.get(to_currency.upper())

            if not to_rate:
                return f"Currency '{to_currency}' not found."

            converted = round(amount * to_rate, 2)
            return (
                f"{amount} {from_currency.upper()} = "
                f"{converted} {to_currency.upper()}"
            )

        except httpx.HTTPStatusError as e:
            raise CurrencyServiceError(f"HTTP error: {str(e)}")

        except Exception as e:
            raise CurrencyServiceError(f"Currency conversion failed: {str(e)}")
