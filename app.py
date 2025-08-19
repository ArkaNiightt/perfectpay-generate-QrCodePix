from generate.qrcode_pix import PerfectPayPixGenerator
from config.config import Config

config = Config()

if __name__ == "__main__":

    generator = PerfectPayPixGenerator(
        base_url=config.get_perfectpay_checkout_url(),
        headless=True,
        user_agent=config.get_user_agent()
    )

    try:
        # Dados do cliente (Esses dados são obrigatórios)
        # Dados de teste fictícios
        # Foram gerados no https://www.4devs.com.br/gerador_de_pessoas
        qr_code = generator.generate_pix(
            email="iago.heitor.souza@inglesasset.com.br",
            name="Iago Heitor Souza",
            phone="95997984584",
            cpf="25252856974"
        )

        if qr_code:
            print(f"QR Code gerado: {qr_code}")
        else:
            print("Falha ao gerar QR Code")

    except Exception as e:
        print(f"Erro: {str(e)}")
    finally:
        generator.close()
