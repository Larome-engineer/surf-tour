from datetime import date
from io import BytesIO
from bot.config import FONT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


async def generate_invoice_pdf_tour(
        user_name: str,
        name: str,
        destination: str,
        start_date: str,
        time: str,
        end_date: str,
        places: int,
        price: float,
) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdfmetrics.registerFont(
        TTFont("NotoSans", FONT)
    )

    c.setFont("NotoSans", 20)
    c.drawString(50, height - 50, "ИНФОРМАЦИЯ О ВАШЕМ ТУРЕ")

    c.setFont("NotoSans", 16)
    c.drawString(50, height - 70, f"Дата формирования: {date.today().strftime('%d.%m.%Y')}")

    c.drawString(50, height - 110, f"Покупатель: {user_name}")

    base_y = height - 150

    c.drawString(50, base_y, f"Тур: {name}")
    c.drawString(50, base_y - 20, f"Направление: {destination}")
    c.drawString(50, base_y - 40, f"Даты: {start_date} – {end_date} | {time}")
    c.drawString(50, base_y - 60, f"Количество мест: {places}")
    c.drawString(50, base_y - 80, f"Сумма оплаты: {price:,.0f} ₽".replace(",", " "))

    c.setFont("NotoSans", 14)
    c.drawString(50, base_y - 120, "Спасибо за покупку и приятного путешествия!")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

async def generate_invoice_pdf_lesson(
        user_name: str,
        lsn_type: str,
        destination: str,
        start_date: str,
        time: str,
        duration: str,
        places: int,
        price: float,
) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdfmetrics.registerFont(
        TTFont("NotoSans", FONT)
    )

    c.setFont("NotoSans", 20)
    c.drawString(50, height - 50, "ИНФОРМАЦИЯ О БРОНИРОВАНИИ НА УРОК")

    c.setFont("NotoSans", 16)
    c.drawString(50, height - 70, f"Дата формирования: {date.today().strftime('%d.%m.%Y')}")

    c.drawString(50, height - 110, f"Покупатель: {user_name}")

    base_y = height - 150

    c.drawString(50, base_y, f"{lsn_type}")
    c.drawString(50, base_y - 20, f"Направление: {destination}")
    c.drawString(50, base_y - 40, f"Дата: {start_date} | Начало: {time} | Продолжительность: {duration}")
    c.drawString(50, base_y - 60, f"Забронировано мест: {places}")
    c.drawString(50, base_y - 80, f"Сумма оплаты: {price:,.0f} ₽".replace(",", " "))

    c.setFont("NotoSans", 14)
    c.drawString(50, base_y - 120, "Спасибо за покупку!")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
