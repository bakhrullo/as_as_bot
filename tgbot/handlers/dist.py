from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice, ContentTypes

from tgbot.db.db_api import get_industries, add_product, add_agent, get_my_products, get_one_product, get_count, \
    get_user, status_update
from tgbot.filters.back import BackFilter
# from tgbot.keyboards.inline import *
from tgbot.keyboards.reply import *
from tgbot.misc.i18n import i18ns
from tgbot.misc.states import *

_ = i18ns.gettext


async def main_dist_start(m: Message, state: FSMContext, config, user_lang):
    if m.text == _("Mening maxsulotlarim", locale=user_lang):
        products = await get_my_products(config, str(m.from_user.id))
        await m.answer(_("Mening maxsulotlarim", locale=user_lang), reply_markup=products_kb(products, user_lang))
        await UserDistMainState.get_my_products.set()
    elif m.text == _("Maxsulot qo'shish", locale=user_lang):
        industries = await get_industries(config, user_lang)
        await m.answer(_("Siz qaysi sohada distirbyutersiz? 👇"), reply_markup=industry_kb(industries, user_lang))
        await UserDistState.get_industry.set()
    else:
        await m.answer(_("Qaysi viloyatdagi magazinlar sizga qiziq?", locale=user_lang), reply_markup=city_btn)
        await UserSearchMagazinPaymentState.get_region.set()


# Mahsulot
# 1 - step industry
async def get_dist_industry(m: Message, state: FSMContext, config, user_lang):
    await state.update_data(parent_category=m.text)
    industries = await get_industries(config, user_lang, m.text)
    await m.answer(_("Yo'nalishni tanlang 👇"), reply_markup=industry_kb(industries, user_lang))
    await UserDistState.next()


# 1.1 Select sub_category
async def get_dist_sub_industry(m: Message, state: FSMContext, config, user_lang):
    await state.update_data(parent_category=m.text)
    industries = await get_industries(config, user_lang, m.text)
    await m.answer(_("Tovarni tanlang 👇"), reply_markup=industry_kb(industries, user_lang, 1))
    await UserDistState.next()


# 1.2 Select product type
async def get_dist_prod_industry(m: Message, state: FSMContext, config):
    await state.update_data(category=m.text)
    await m.answer(_("Tovar nomini kiriting"), reply_markup=ReplyKeyboardRemove())
    await UserDistState.next()


# 2 Get product name
async def get_product_name(m: Message, state: FSMContext, config, user_lang):
    await state.update_data(name=m.text)
    await m.answer(_("Mahsulot rasmini jo'nating"), reply_markup=None)
    await UserDistState.next()


# Get product photo
async def get_product_photo(m: Message, state: FSMContext, config, user_lang):
    await state.update_data(photo=m.photo[-1]['file_id'])
    await m.answer(_("Mahsulot tavsifini yozing"), reply_markup=None)
    await UserDistState.next()


# Get product description
async def get_product_description(m: Message, state: FSMContext, config, user_lang):
    await state.update_data(description=m.text)
    await m.answer(_("Agent xududini tanlang"), reply_markup=region_btn)
    await UserDistState.next()


# Get product agent region
async def get_product_agent_region(m: Message, state: FSMContext, config, user_lang):
    await state.update_data(agent_region=m.text)
    await m.answer(_("Agent shaxrini tanlang"), reply_markup=city_btn)
    await UserDistState.next()


async def get_product_agent_city(m: Message, state: FSMContext, config, user_lang):
    await state.update_data(agent_city=m.text)
    await m.answer(_("Agent tumanini tanlang"), reply_markup=distreet_btn)
    await UserDistState.next()


async def get_product_agent_distreet(m: Message, state: FSMContext, config, user_lang):
    await state.update_data(agent_distreet=m.text)
    await m.answer(_("Agent telefon raqamini yozing"), reply_markup=ReplyKeyboardRemove())
    await UserDistState.next()


# Get product agent phone
async def get_product_agent_phone(m: Message, state: FSMContext, config, user_lang):
    await state.update_data(agent_phone=m.text)
    await m.answer(_("Supervayzer tel raqamini yozing"), reply_markup=None)
    await UserDistState.next()


# Get product agent phone
async def get_product_supervisor_phone(m: Message, state: FSMContext, config, user_lang):
    await state.update_data(supervisor_phone=m.text)
    await m.answer(_("Korxona nomini yozing"), reply_markup=None)
    await UserDistState.next()


# Get organization name
async def get_organization_name(m: Message, state: FSMContext, config, user_lang):
    await state.update_data(org_name=m.text)
    await m.answer(_("Korxona tel raqamini yozing"), reply_markup=None)
    await UserDistState.next()


# Get organization name and send to API
async def get_organization_phone(m: Message, state: FSMContext, config, user_lang):
    data = await state.get_data()
    product_data = {
        "tg_id": m.from_user.id,
        "industry": data.get("category"),
        "name": data.get("name"),
        "description": data.get("description"),
        "photo_uri": data.get("photo")
    }

    product = await add_product(config, product_data)
    if product:
        agent_data = {
            "agent_region": data.get("agent_region"),
            "agent_city": data.get("agent_city"),
            "agent_distreet": data.get("agent_distreet"),
            "agent_phone": data.get("agent_phone"),
            "supervisor_phone": data.get("supervisor_phone"),
            "corp_name": data.get("org_name"),
            "corp_phone": m.text,
            "product_name": product["name"]
        }
        await add_agent(config, agent_data)
        await m.answer(_("Malumotlaringiz saqlandi"), reply_markup=distributer_start_btn(user_lang))
        await m.answer(_("Bo'limni tanlang"), reply_markup=distributer_start_btn(user_lang))
        await state.finish()
        await UserDistMainState.get_main.set()
    else:
        await m.answer(_("Server bilan bog'lanish yo'q. Qayta urunib ko'ring"))
        await main_dist_start(m, state, config, user_lang)


async def search_magazines_get_region(m: Message, state: FSMContext, config, user_lang):
    await state.update_data(region=m.text)
    await m.answer(_("Shaharni tanlang"), reply_markup=region_btn)
    await UserSearchMagazinPaymentState.next()


async def search_magazines_get_city(m: Message, state: FSMContext, config, user_lang):
    # await m.answer(_("Shuncha magazin bor"), reply_markup=ReplyKeyboardRemove())
    data = await state.get_data()
    user = await get_user(m.from_user.id, config)
    results = await get_count(config, "check-magazines", data.get("region"), m.text)
    if user["is_subscribed"] is False:
        await m.answer(_("{count} ta magazin. Bular haqida ma'lumot olish uchun PRO versiyani xarid"
                         " qiling").format(count=results["count"]), reply_markup=buy_kb)
        return await UserSearchMagazinPaymentState.get_pay.set()
    else:
        # TODO: Need write paginated kbs for the magazines results
        industries = await get_industries(config, user_lang)
        await m.answer(_("Magazinlarni tanlang 👇"), reply_markup=industry_kb(industries, user_lang))
        await UserSearchMagazinPaymentState.get_magazines.set()


async def get_buy_dist_sell(m: Message, state: FSMContext, config):
    price = LabeledPrice(label="Pro podpiska uchun to'lov", amount=100 * 100)
    photo = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTgWGCXrpS2g54YYm0eTzAHHFzY7Kj3ZXEcbg&usqp=CAU" if \
        m.text == "click" else "https://synthesis.uz/wp-content/uploads/2022/01/payme-1920x1080-1.jpg"
    token = config.misc.click if m.text == "click" else config.misc.payme
    await state.update_data(pay_type=m.text)
    msg = await m.bot.send_invoice(chat_id=m.from_user.id, photo_url=photo, currency="rub", title="PRO",
                                   description="Pro uchun tolov",
                                   payload="test-invoice-payload",
                                   provider_token=token,
                                   prices=[price])
    await state.update_data()
    await UserSearchMagazinPaymentState.next()


async def pre_checkout_query(query: PreCheckoutQuery, state: FSMContext):
    stat = await state.get_state()
    print("@@@", stat)
    await query.bot.answer_pre_checkout_query(query.id, ok=True)
    await UserSearchMagazinPaymentState.next()


async def success_payment(m: Message, state: FSMContext, config, user_lang):
    await status_update(config, m.from_user.id)
    await m.delete()
    await m.answer(_("Siz oylik patpiskaga a'zo bo'ldingiz!"))
    industries = await get_industries(config, user_lang, m.text)
    # TODO: need to response paginated kbs view
    await m.answer(_("Magazinlarni tanlang 👇"), reply_markup=industry_kb(industries, user_lang))
    await UserSearchMagazinPaymentState.get_magazines.set()


async def echo_magazine(m: Message, state: FSMContext, config, user_lang):
    data = await state.get_data()
    print(data, "DATA")
    await m.answer(m.text)


async def get_my_product_handler(m: Message, state: FSMContext, config, user_lang):
    product_name = m.text
    data = await get_one_product(config=config, product_name=product_name)
    description = (
        f"Maxsulot nomi: {data['name']}\n"
        f"Tavsif: {data['description']}\n"
        f"Soha: {data[f'category_{user_lang}']}\n"
    )

    await m.answer_photo(caption=description, photo=data["photo_uri"])
    for i in data["agents"]:
        agent_info = (
            f"Supervisor tel: {i['supervisor_phone']}\n"
            f"Agent region: {i['agent_region']}\n"
            f"Agent tel: {i['agent_phone']}\n"
            f"Korxona nomi: {i['corp_name']}\n"
            f"Korxona tel: {i['corp_phone']}\n"
        )
        await m.answer(agent_info)


# async def get_sub_cat(m: Message, state: FSMContext):
#     await state.update_data(sub_cat=m.text)
#     data = await state.get_data()
#     await m.answer(_("Sohani tanlang 👇", locale=data["lang"]), reply_markup=prod_cat_kb(m.text, data["cat"]))
#     if data["type"] == "Ishlab chiqaruvchi 🤵‍♂️":
#         return await UserBuisState.get_buis_prod.set()
#     return await UserDistState.get_prod.set()


# async def get_prod_buis(m: Message, state: FSMContext):
#     data = await state.get_data()
#     await create_user(m.from_user.id, data["lang"], data["name"], data["number"], data["type"], data["region"], m.text)
#     await m.answer(_("Qaysi viloyatdan distribyuter qidiryapsiz?"), reply_markup=citys_btn)
#     await UserBuisState.next()


# data = await state.get_data()
# json_data = {
#     "tg_id": m.from_user.id,
#     "industry": data["category"],
#     "tg_name": m.from_user.full_name,
#     "product_name": m.text
# }

def register_dist(dp: Dispatcher):
    dp.register_message_handler(main_dist_start, BackFilter(), state=UserDistMainState.get_main)
    dp.register_message_handler(get_my_product_handler, BackFilter(), state=UserDistMainState.get_my_products)
    dp.register_message_handler(get_dist_industry, BackFilter(), state=UserDistState.get_industry)
    dp.register_message_handler(get_dist_sub_industry, BackFilter(), state=UserDistState.get_sub_industry)
    dp.register_message_handler(get_dist_prod_industry, BackFilter(), state=UserDistState.get_prod_industry)
    dp.register_message_handler(get_product_name, BackFilter(), state=UserDistState.get_prod_name)
    dp.register_message_handler(get_product_photo, BackFilter(), content_types='photo',
                                state=UserDistState.get_prod_photo)
    dp.register_message_handler(get_product_description, BackFilter(), state=UserDistState.get_prod_description)
    dp.register_message_handler(get_product_agent_region, BackFilter(), state=UserDistState.get_agent_region)
    dp.register_message_handler(get_product_agent_city, BackFilter(), state=UserDistState.get_agent_city)
    dp.register_message_handler(get_product_agent_distreet, BackFilter(), state=UserDistState.get_agent_distreet)
    dp.register_message_handler(get_product_agent_phone, BackFilter(), state=UserDistState.get_agent_phone)
    dp.register_message_handler(get_product_supervisor_phone, BackFilter(), state=UserDistState.get_supervisor)
    dp.register_message_handler(get_organization_name, BackFilter(), state=UserDistState.company_name)
    dp.register_message_handler(get_organization_phone, BackFilter(), state=UserDistState.company_phone)
    dp.register_message_handler(search_magazines_get_region, BackFilter(), state=UserSearchMagazinPaymentState.get_region)
    dp.register_message_handler(search_magazines_get_city, BackFilter(),
                                state=UserSearchMagazinPaymentState.get_city)
    dp.register_message_handler(get_buy_dist_sell, BackFilter(), state=UserSearchMagazinPaymentState.get_pay)
    dp.register_pre_checkout_query_handler(pre_checkout_query, state=UserSearchMagazinPaymentState.get_pay_conf)
    dp.register_message_handler(success_payment, BackFilter(), content_types=ContentTypes.SUCCESSFUL_PAYMENT,
                                state=UserSearchMagazinPaymentState.get_success)
    dp.register_message_handler(echo_magazine, BackFilter(), state=UserSearchMagazinPaymentState.get_magazines)
    # dp.register_message_handler(get_buis_sub_cat, BackFilter(), state=UserBuisState.get_sub_cat)
    # dp.register_message_handler(get_buis_prod, BackFilter(), state=UserBuisState.get_prod)
