from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, ContentType

from tgbot.db.db_api import *
from tgbot.filters.back import BackFilter
from tgbot.keyboards.reply import *
from tgbot.misc.i18n import i18ns
from tgbot.misc.states import *

_ = i18ns.gettext


# async def get_buis_industry(m: Message, state: FSMContext, config, user_lang):
# data = await state.get_data()
# print("DATA", data)
# current_level = data.get("current_level")
# if current_level is None:
#     industries = await get_industries(config, user_lang)
#     await state.update_data(current_level=0)
#     return await m.answer(_("Siz qaysi sohada ishlab chiqarasiz? 👇"),
#                    reply_markup=industry_kb(industries, user_lang))
# else:
#     if m.text in ["⬅️ Orqaga", "⬅️ Назад", "⬅️ Back"]:
#         industries = await get_industries(config, user_lang, data["industry"])
#         await state.update_data(current_level=current_level - 1)
#         return await m.answer(_("Siz qaysi yo'nalishda ishlab chiqarasiz? 👇") if current_level == 0 else
#                               _("Tovarni tanlang 👇"), reply_markup=industry_kb(industries, user_lang, current_level))
#     industries = await get_industries(config, user_lang, m.text)
#     if not industries:
#         return await m.answer(_("Mavjud bo'lmagan bo'lim tanladingiz!"))
#     await state.update_data(industry=m.text, current_level=current_level + 1)
#     print("CURRENT LEVEL", current_level)
#     await m.answer(text=_("Siz qaysi yo'nalishda ishlab chiqarasiz? 👇"), reply_markup=industry_kb(industries,
#                                                                                                   user_lang,
#                                                                                                   current_level))

async def main_menu_buis(m: Message, state: FSMContext, config, user_lang):
    print('HELLO', m.text)
    if m.text == _("Distributor qidirish️", locale=user_lang):
        await m.answer(_("Qaysi viloyatdan distirbyutor qidiryapsiz? 👇"), reply_markup=city_btn)
        return await UserBuisState.get_interested_region.set()
    elif m.text == _("Distributorga so'rov yuborish", locale=user_lang):
        await m.answer(_("O'zingiz haqingizda\n"
                         "ma'lumot qoldiring\n"
                         "distirbyutorlarga\n"
                         "ma'lumotlaringiz qiziq\n"
                         "bo'lsa aloqaga chiqishadi\n", locale=user_lang), reply_markup=remove_btn)
        await UserBuisProductRequest.get_description.set()
    else:
        await m.answer(_("Noto'g'ri bo'lim tanladingiz"))


async  def get_buis_industry(m: Message, state: FSMContext, config, user_lang):
    await state.update_data(category=m.text)
    industries = await get_industries(config, user_lang, m.text)
    await m.answer(_("Yo'nalishni tanlang 👇"), reply_markup=industry_kb(industries, user_lang))
    await UserBuisState.next()

async def get_buis_sub_industry(m: Message, state: FSMContext, config, user_lang):
    industries = await get_industries(config, user_lang, m.text)
    # data = await state.get_data()
    # print(data, "################")
    # user = await get_user(m.from_user.id, config)
    # results = await get_count(config, "check-magazines", user.get("region"), city=m.text)
    # print(results)
    await m.answer(_("Tovar turini tanlang"), reply_markup=industry_kb(industries, user_lang, 1))
    await UserBuisState.next()

async def get_buis_prod_industry(m: Message, state: FSMContext, config):
    data = await state.get_data()
    json_data = {
        "tg_id": m.from_user.id,
        "industry": data["category"],
        "tg_name": m.from_user.full_name,
        "product_name": m.text
    }

    res = await pre_register_user(config, user_type="business", data=json_data)
    await m.answer(_("Qaysi viloyatdan distribyuter qidiryapsiz?"), reply_markup=city_btn)
    await UserBuisState.next()

async def get_interested_region(m: Message, state: FSMContext, config, user_lang):
    if m.text != "Qashqadaryo":
        return await m.answer("Tez orada! 😃")
    await state.update_data(interested_region=m.text)
    industry = await get_industries(config, user_lang)
    await m.answer(_("Qaysi sohada?"), reply_markup=industry_kb(industry, user_lang))
    await UserBuisState.next()

async def get_interested_cat(m: Message, state: FSMContext):
    await state.update_data(interested_cat=m.text)
    await m.answer(_("Sohani tanlang 👇"), reply_markup=sub_cat_kb(m.text))
    await UserBuisState.next()

async def get_interested_sub_cat(m: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(interested_sub_cat=m.text)
    await m.answer(_("Sohani tanlang 👇"), reply_markup=prod_cat_kb(m.text, data["interested_cat"]))
    await UserBuisState.next()

async def get_interested_prod(m: Message, state: FSMContext, config, user, user_lang):
    data = await state.get_data()
    await state.update_data(interested_prod=m.text)
    if user["is_subscribed"] is False:
        res = await get_count(config, "check-distributes", data["interested_region"], city="Koson")
        await m.answer(_("{count} ta distributor. Bular haqida ma'lumot olish uchun PRO versiyani xarid"
                         " qiling").format(count=res["count"]), reply_markup=buy_kb)
        return await UserBuisState.next()
    params = {
        "agent_city": "",
        "agent_region": data["interested_region"]
        # TODO: need to filter after using category__name
    }
    agents = await get_agents(config, params=params)
    sended_agents = 0
    print(agents)
    for i in agents['results']:
        agent_info = (
            f"{sended_agents + 1}. Supervisor tel: {i['supervisor_phone']}\n"
            f"Agent region: {i['agent_region']}\n"
            f"Agent shaxar: <b>{i['agent_city']}</b>\n"
            f"Agent tuman: {i['agent_distreet']}\n"
            f"Agent tel: {i['agent_phone']}\n"
            f"Korxona nomi: {i['corp_name']}\n"
            f"Korxona tel: {i['corp_phone']}\n"
        )
        await m.answer(agent_info)
        sended_agents += 1

    if sended_agents == 0:
        await m.answer(_("Kechirasiz ushbu tanlovingiz bo'yicha sizni hududizda distributorlar mavjud emas"))
    await state.finish()
    await m.answer(_("Bo'limni tanlang"), reply_markup=main_menu_buis_btns(user_lang))
    await UserBuisMainState.get_main.set()

async def get_buy_buis(m: Message, state: FSMContext, config):
    price = LabeledPrice(label="Pro podpiska uchun to'lov", amount=100 * 100)
    photo = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTgWGCXrpS2g54YYm0eTzAHHFzY7Kj3ZXEcbg&usqp=CAU" if \
        m.text == "click" else "https://synthesis.uz/wp-content/uploads/2022/01/payme-1920x1080-1.jpg"
    token = config.misc.click if m.text == "click" else config.misc.payme
    await state.update_data(pay_type=m.text)
    await m.bot.send_invoice(chat_id=m.from_user.id, photo_url=photo, currency="rub", title="PRO",
                             description="Pro uchun tolov",
                             payload="test-invoice-payload", provider_token=token,
                             prices=[price])
    await UserBuisState.next()

async def pre_checkout_query(query: PreCheckoutQuery):
    await query.bot.answer_pre_checkout_query(query.id, ok=True)
    await UserBuisState.next()

async def success_payment(m: Message, state: FSMContext, config, user_lang):
    data = await state.get_data()
    await status_update(config, m.from_user.id)
    await m.answer(_("Siz oylik patpiskaga a'zo bo'ldingiz"))
    params = {
        "agent_city": data.get("city", "Koson"),
        "agent_region": data["interested_region"]
        # TODO: need to filter after using category__name
    }
    agents = await get_agents(config, params=params)
    sended_agents = 0
    for i in agents['results']:
        agent_info = (
            f"{sended_agents + 1}. Supervisor tel: {i['supervisor_phone']}\n"
            f"Agent region: {i['agent_region']}\n"
            f"Agent shaxar: <b>{i['agent_city']}</b>\n"
            f"Agent tuman: {i['agent_distreet']}\n"
            f"Agent tel: {i['agent_phone']}\n"
            f"Korxona nomi: {i['corp_name']}\n"
            f"Korxona tel: {i['corp_phone']}\n"
        )
        await m.answer(agent_info, reply_markup=remove_btn)
        sended_agents += 1
    if sended_agents == 0:
        await m.answer(_("Kechirasiz ushbu tanlovingiz bo'yicha sizni hududizda distributorlar mavjud emas"))
    await state.finish()
    await m.answer(_("Bo'limni tanlang"), reply_markup=main_menu_buis_btns(user_lang))
    await UserBuisMainState.get_main.set()


async def send_dist_request(m: Message, state: FSMContext, config, user_lang):
    print("HI")
    await m.answer(_("Sizning so'rovingiz distributorlarga jo'natildi ✅"))
    await m.send_copy(config.tg_bot.buis_ids)
    await state.finish()
    await m.answer(_("Bo'limni tanlang"), reply_markup=main_menu_buis_btns(user_lang))
    await UserBuisMainState.get_main.set()


async def get_dist(m: Message):
    res = await get_type(int(m.text.split(".")[0]))
    await m.answer(_("👤  Ismi: {name}\n📲 Raqam: {number}\n"
                     "📍 Manzil: {address}").format(name=res.name, number=res.number, address=res.region),
                   reply_markup=buis_get_info_kb)
    await UserBuisState.next()

async def get_buis_info(m: Message):
    await m.answer(
        _("O'zingiz haqingizda ma'lumot qoldiring distirbyutorlarga ma'lumotlaringiz qiziq bo'lsa aloqaga "
          "chiqishadi! 👨‍💻"), reply_markup=remove_btn)
    await UserBuisState.next()

async def send_buis(m: Message, user, config):
    await m.bot.send_message(chat_id=config.tg_bot.buis_ids, text=f"👤 Ismi: {user.name}\n📲 Raqam: {user.number}\n"
                                                                  f"📦 Tovar: {user.product}\n🌆 Shahar: {user.region}\n"
                                                                  f"💬 Ma'lumot: {m.text}")
    await m.answer(_("So'rovingiz distribyuterlarga yetkazildi!"), reply_markup=citys_btn)
    await UserBuisState.get_interested_region.set()

async def back(m: Message, state: FSMContext):
    data = await state.get_data()
    state = await state.get_state()
    if state == "UserBuisState:get_cat":
        await m.answer(_("Qaysi viloyatda faoliyat yuritasiz? 🏭"), reply_markup=city_btn)
        return await UserParamsState.get_region.set()
    elif state == "UserBuisState:get_sub_cat":
        await m.answer(_("Sohani tanlang 👇"), reply_markup=industry_kb(await get_industries()))
        return await UserBuisState.get_cat.set()
    elif state == "UserBuisState:get_prod":
        await m.answer(_("Sohani tanlang 👇"), reply_markup=sub_cat_kb(data['cat']))
        return await UserBuisState.get_sub_cat.set()
    elif state == "UserBuisState:get_interested_cat":
        await m.answer(_("Qaysi viloyatda faoliyat yuritasiz? 🏭"), reply_markup=citys_btn)
        return await UserBuisState.get_interested_region.set()
    elif state in ["UserBuisState:get_interested_sub_cat", "UserBuisState:get_buy"]:
        await m.answer(_("Sohani tanlang 👇"), reply_markup=cats_kb)
        return await UserBuisState.get_interested_cat.set()
    elif state == "UserBuisState:get_interested_prod":
        await m.answer(_("Sohani tanlang 👇"), reply_markup=sub_cat_kb(data['interested_cat']))
        return await UserBuisState.get_interested_sub_cat.set()
    elif state == "UserBuisState:get_info":
        res = await get_count(config, "check-distributes", data["interested_region"], city="Koson")
        await m.answer(
            _("{spec} sohasi bo'yicha {count} ta distribyuter").format(spec=data["interested_prod"],
                                                                       count=len(res)),
            reply_markup=buis_pro(res))
        return await UserBuisState.get_dist.set()
    elif state == "UserBuisState:get_dist":
        await m.answer(_("Sohani tanlang 👇"),
                       reply_markup=prod_cat_kb(data["interested_sub_cat"], data["interested_cat"]))
        return await UserBuisState.get_interested_prod.set()

def register_buis(dp: Dispatcher):
    dp.register_message_handler(main_menu_buis, state=UserBuisMainState.get_main)
    dp.register_message_handler(send_dist_request, BackFilter(), state=UserBuisProductRequest.get_description)
    dp.register_message_handler(get_buis_industry, state=UserBuisState.get_industry)
    dp.register_message_handler(get_buis_sub_industry, BackFilter(), state=UserBuisState.get_sub_industry)
    dp.register_message_handler(get_buis_prod_industry, BackFilter(), state=UserBuisState.get_prod_industry)
    dp.register_message_handler(get_interested_region, BackFilter(), state=UserBuisState.get_interested_region)
    dp.register_message_handler(get_interested_cat, BackFilter(), state=UserBuisState.get_interested_cat)
    dp.register_message_handler(get_interested_sub_cat, BackFilter(), state=UserBuisState.get_interested_sub_cat)
    dp.register_message_handler(get_interested_prod, BackFilter(), state=UserBuisState.get_interested_prod)
    dp.register_message_handler(get_buy_buis, BackFilter(), state=UserBuisState.get_buy)
    dp.register_pre_checkout_query_handler(pre_checkout_query, lambda query: True, state=UserBuisState.get_buy_conf)
    dp.register_message_handler(success_payment, content_types=ContentType.SUCCESSFUL_PAYMENT,
                                state=UserBuisState.get_success)
    dp.register_message_handler(get_dist, BackFilter(), state=UserBuisState.get_dist)
    dp.register_message_handler(get_buis_info, BackFilter(), state=UserBuisState.get_info)
    dp.register_message_handler(send_buis, BackFilter(), state=UserBuisState.get_text)
    dp.register_message_handler(back, state="*")

