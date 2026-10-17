import asyncio
import httpx
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

# ВСТАВЬТЕ СЮДА ВАШ ТОКЕН ИЗ BOTFATHER
TOKEN = "8367627402:AAFHVWLoM5BpD2pJpR2LZzSHTwVAXuDHY68"

dp = Dispatcher()

# --- ПОИСК ПО ДОМЕНУ ---
async def whois_lookup(domain: str) -> str:
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(f"https://rdap.org/domain/{domain}")
            if r.status_code != 200:
                return "Нет данных по этому домену."
            d = r.json()
            name = d.get("ldhName", domain)
            status = ", ".join(d.get("status", [])) or "—"
            return f"🌐 Домен: {name}\nСтатус: {status}"
        except Exception as e:
            return f"Ошибка при проверке домена: {e}"

# --- ПОИСК ПО IP ---
async def ip_lookup(ip: str) -> str:
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(f"https://ipinfo.io/{ip}/json")
            if r.status_code != 200:
                return "Нет данных по этому IP."
            d = r.json()
            return (
                f"🖥 IP: {ip}\n"
                f"Страна: {d.get('country', '—')}\n"
                f"Город: {d.get('city', '—')}\n"
                f"Организация: {d.get('org', '—')}"
            )
        except Exception as e:
            return f"Ошибка при проверке IP: {e}"

# --- ПОИСК ПО EMAIL ---
async def email_lookup(email: str) -> str:
    # Проверка утечек через публичный API (без ключа работает только проверка, но мы имитируем запрос)
    # Показываем открытые данные о домене почты
    domain = email.split('@')[-1] if '@' in email else ''
    if not domain:
        return "❌ Некорректный email."
    
    res = f"📧 Email: {email}\n"
    res += f"Домен почты: {domain}\n"
    
    # Проверка домена почты (существует ли он)
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"https://rdap.org/domain/{domain}")
            if r.status_code == 200:
                res += "✅ Домен почты существует.\n"
            else:
                res += "⚠️ Домен почты не найден или скрыт.\n"
    except:
        pass
        
    res += "\n💡 Для проверки утечек паролей используйте сайт: haveibeenpwned.com"
    return res

# --- ПОИСК ПО НОМЕРУ ---
async def phone_lookup(phone: str) -> str:
    # Очищаем номер от лишних символов
    clean_phone = ''.join(filter(str.isdigit, phone))
    
    if not clean_phone:
        return "❌ Некорректный номер телефона."
    
    res = f"📱 Номер: {clean_phone}\n"
    
    # Простейший определитель оператора для РФ (по первым цифрам)
    if clean_phone.startswith('7') or clean_phone.startswith('8'):
        code = clean_phone[1:4] if clean_phone.startswith('7') else clean_phone[1:4]
        operators = {
            '900': 'МегаФон', '901': 'МТС', '902': 'МТС', '903': 'МТС', '904': 'МТС', '905': 'МТС', '906': 'МТС', '908': 'МТС', '909': 'МТС',
            '910': 'МТС', '911': 'МТС', '912': 'МТС', '913': 'МТС', '914': 'МТС', '915': 'МТС', '916': 'МТС', '917': 'МТС', '918': 'МТС', '919': 'МТС',
            '920': 'МегаФон', '921': 'МегаФон', '922': 'МегаФон', '923': 'МегаФон', '924': 'МегаФон', '925': 'МегаФон', '926': 'МегаФон', '927': 'МегаФон', '928': 'МегаФон',
            '930': 'МегаФон', '931': 'МегаФон', '932': 'МегаФон', '933': 'МегаФон', '934': 'МегаФон', '936': 'МегаФон', '937': 'МегаФон', '938': 'МегаФон', '939': 'МегаФон',
            '950': 'Билайн', '951': 'Билайн', '952': 'Билайн', '953': 'Билайн', '954': 'Билайн', '955': 'Билайн', '956': 'Билайн', '957': 'Билайн', '958': 'Билайн', '959': 'Билайн',
            '960': 'Билайн', '961': 'Билайн', '962': 'Билайн', '963': 'Билайн', '964': 'Билайн', '965': 'Билайн', '966': 'Билайн', '967': 'Билайн', '968': 'Билайн', '969': 'Билайн',
        }
        operator = operators.get(code, 'Неизвестный оператор (РФ)')
        res += f"Оператор: {operator}\n"
        res += f"Регион: РФ\n"
    else:
        res += "🌍 Иностранный номер (определение оператора недоступно бесплатно).\n"
        
    res += f"\n🔗 Проверить в WhatsApp: https://wa.me/{clean_phone}\n"
    res += f"🔗 Проверить в Telegram: https://t.me/+{clean_phone}"
    return res

# --- КОМАНДЫ БОТА ---

@dp.message(Command("start"))
async def start(m: Message):
    await m.answer(
        "👋 Привет! Я OSINT-бот.\n"
        "Доступные команды:\n"
        "/whois example.com — информация о домене\n"
        "/ip 8.8.8.8 — информация об IP\n"
        "/email test@example.com — проверка email\n"
        "/phone 89991234567 — проверка номера"
    )

@dp.message(Command("whois"))
async def cmd_whois(m: Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        return await m.answer("Формат: /whois example.com")
    await m.answer("⏳ Смотрю домен...")
    await m.answer(await whois_lookup(parts[1].strip()))

@dp.message(Command("ip"))
async def cmd_ip(m: Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        return await m.answer("Формат: /ip 8.8.8.8")
    await m.answer("⏳ Смотрю IP...")
    await m.answer(await ip_lookup(parts[1].strip()))

@dp.message(Command("email"))
async def cmd_email(m: Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        return await m.answer("Формат: /email test@example.com")
    await m.answer("⏳ Проверяю email...")
    await m.answer(await email_lookup(parts[1].strip()))

@dp.message(Command("phone"))
async def cmd_phone(m: Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        return await m.answer("Формат: /phone 89991234567")
    await m.answer("⏳ Проверяю номер...")
    await m.answer(await phone_lookup(parts[1].strip()))

# --- ЗАПУСК ---
async def main():
    bot = Bot(TOKEN)
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())