import os


class Config:
    def __init__(self):
        self.perfectpay_checkout_url = os.getenv("PERFECTPAY_CHECKOUT_URL")
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"

    def get_perfectpay_checkout_url(self):
        return self.perfectpay_checkout_url

    def get_user_agent(self):
        return self.user_agent
