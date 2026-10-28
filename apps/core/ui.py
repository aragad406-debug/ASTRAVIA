"""Interface strings (English, Arabic). Studio editors can override any of these from
Creator Studio → Localization → Interface text, without code changes.

Narrative content does NOT live here: worlds, characters, stories and dialogue are database records.
Arabic follows formal Modern Standard Arabic.
"""
from django.core.cache import cache
from django.utils.functional import lazy

from .text import current_language

STRINGS = {
    # Navigation and chrome
    "site.name": ("ASTRAVIA", "أسترافيا"),
    "nav.home": ("Home", "الرئيسية"),
    "nav.universe": ("Universe", "الكون"),
    "nav.worlds": ("Worlds", "العوالم"),
    "nav.characters": ("Sovereigns & characters", "الحكّام والشخصيات"),
    "nav.characters_short": ("Characters", "الشخصيات"),
    "nav.story": ("Story", "القصة"),
    "nav.lore": ("Memory archive", "أرشيف الذاكرة"),
    "nav.news": ("News", "الأخبار"),
    "nav.search": ("Search", "بحث"),
    "nav.account": ("Account", "الحساب"),
    "nav.sign_in": ("Sign in", "تسجيل الدخول"),
    "nav.sign_out": ("Sign out", "تسجيل الخروج"),
    "nav.register": ("Create account", "إنشاء حساب"),
    "nav.studio": ("Creator Studio", "استوديو الإنشاء"),
    "nav.menu": ("Menu", "القائمة"),
    "nav.close": ("Close", "إغلاق"),
    "nav.skip": ("Skip to content", "انتقل إلى المحتوى"),
    "nav.main_label": ("Main navigation", "التنقل الرئيسي"),
    "lang.label": ("Language", "اللغة"),
    "lang.switch_to": ("العربية", "English"),
    "lang.switch_code": ("ar", "en"),
    # Home
    "home.cta.explore": ("Explore the universe", "استكشف الكون"),
    "home.cta.story": ("Discover the story", "اكتشف القصة"),
    "home.cta.sovereigns": ("Meet the sovereigns", "تعرّف على الحكّام"),
    "home.trailer": ("Watch the trailer", "شاهد العرض التشويقي"),
    "home.universe.title": ("Five worlds. One heart. A sixth that was never meant to be found.", "خمسة عوالم. قلبٌ واحد. وعالمٌ سادس لم يكن مقدّرًا له أن يُكتشف."),
    "home.worlds.title": ("The worlds", "العوالم"),
    "home.worlds.lead": ("Each world is held together by a ruler who once made a sacrifice to save it.", "يحكم كلَّ عالمٍ حاكمٌ قدّم يومًا تضحيةً لينقذه."),
    "home.world.ruler": ("Ruled by", "يحكمه"),
    "home.world.capital": ("Capital", "العاصمة"),
    "home.world.enter": ("Enter", "ادخل"),
    "home.sovereigns.title": ("The sovereigns", "الحكّام"),
    "home.sovereigns.lead": ("They were not born tyrants. Each of them paid with a memory.", "لم يولدوا طغاة. دفع كلٌّ منهم ثمنًا من ذاكرته."),
    "home.narrative.title": ("A story told through what was lost", "قصةٌ تُروى عبر ما ضاع"),
    "theme.promises": ("Ancient promises", "وعودٌ قديمة"),
    "theme.memories": ("Forgotten memories", "ذكرياتٌ منسية"),
    "theme.politics": ("Political conflicts", "صراعاتٌ سياسية"),
    "theme.sacrifice": ("Personal sacrifices", "تضحياتٌ شخصية"),
    "theme.histories": ("Hidden histories", "تواريخ مخفية"),
    "theme.choices": ("Difficult choices", "خياراتٌ صعبة"),
    "theme.endings": ("More than one ending", "أكثر من نهاية"),
    "home.gameplay.title": ("How ASTRAVIA is meant to play", "كيف صُمّمت أسترافيا لتُلعب"),
    "home.gameplay.note": ("ASTRAVIA is in pre-production. Everything below describes planned design, not a released game.", "أسترافيا في مرحلة ما قبل الإنتاج. كل ما يلي يصف تصميمًا مخططًا له، لا لعبةً صدرت."),
    "home.guide.title": ("The Celestial Guide", "مرشدة الكواكب"),
    "home.guide.talk": ("Talk to her", "تحدّث إليها"),
    "home.lore.title": ("The Heart of Eternity", "قلب الأبدية"),
    "home.lore.more": ("Open the memory archive", "افتح أرشيف الذاكرة"),
    "home.news.title": ("From the studio", "من الاستوديو"),
    "home.news.all": ("All updates", "كل التحديثات"),
    "home.hidden_world": ("A sixth world", "عالمٌ سادس"),
    "home.hidden_world.text": ("Beyond the five, something remembers. Its name has not been recovered.", "ما وراء العوالم الخمسة، ثمّة شيءٌ يتذكّر. لم يُستعَد اسمه بعد."),
    "gameplay.exploration": ("Exploration", "الاستكشاف"),
    "gameplay.exploration.text": ("Frozen capitals, living forests and buried cities, each built to be read as much as crossed.", "عواصم متجمدة وغابات حيّة ومدن مدفونة، صُمّمت لتُقرأ كما تُعبَر."),
    "gameplay.combat": ("Combat", "القتال"),
    "gameplay.combat.text": ("Action combat designed around reading an enemy and choosing when to strike.", "قتالٌ حركي مبني على قراءة الخصم واختيار لحظة الضربة."),
    "gameplay.bosses": ("Boss encounters", "مواجهات الزعماء"),
    "gameplay.bosses.text": ("Every sovereign is fought for a reason. Some battles are won by breaking a curse, not a body.", "لكل مواجهةٍ مع حاكمٍ سبب. بعض المعارك تُكسب بكسر لعنة لا بكسر جسد."),
    "gameplay.progression": ("Progression", "التطوّر"),
    "gameplay.progression.text": ("Characters grow through what they learn and restore, not only through what they defeat.", "تنمو الشخصيات بما تتعلّمه وتستعيده، لا بما تهزمه فحسب."),
    "gameplay.choices": ("Narrative choices", "الخيارات السردية"),
    "gameplay.choices.text": ("Decisions carry forward. Endings reflect the journey that produced them.", "القرارات تمتد آثارها، والنهايات تعكس الرحلة التي صنعتها."),
    "gameplay.secrets": ("Secrets", "الأسرار"),
    "gameplay.secrets.text": ("Letters, memory fragments and hidden rooms reveal what the rulers chose to forget.", "رسائل وشظايا ذاكرة وغرف مخفية تكشف ما اختار الحكّام نسيانه."),
    "gameplay.restoration": ("World restoration", "استعادة العوالم"),
    "gameplay.restoration.text": ("Freeing a world changes it: snow melts, roots heal, cities choose their future.", "تحرير العالم يغيّره: يذوب الثلج، وتُشفى الجذور، وتختار المدن مستقبلها."),
    "gameplay.multiplayer": ("Multiplayer (future ambition)", "اللعب الجماعي (طموح مستقبلي)"),
    "gameplay.multiplayer.text": ("Shared worlds are a long-term goal. No online services exist yet.", "العوالم المشتركة هدفٌ بعيد المدى. لا توجد خدمات عبر الإنترنت حتى الآن."),
    "status.planned": ("Planned", "مخطط له"),
    "status.future": ("Future", "مستقبلي"),
    # Worlds / characters / story / lore
    "worlds.title": ("The worlds of ASTRAVIA", "عوالم أسترافيا"),
    "worlds.lead": ("Five worlds bound to the Heart of Eternity.", "خمسة عوالم مرتبطة بقلب الأبدية."),
    "world.environment": ("The land", "الأرض"),
    "world.regions": ("Places to explore", "أماكن للاستكشاف"),
    "world.characters": ("Who you will meet", "من ستلتقي"),
    "world.lore": ("Recovered records", "سجلات مستعادة"),
    "world.quests": ("Quests", "المهام"),
    "world.story": ("Story arcs", "الأقواس القصصية"),
    "world.other": ("Other worlds", "عوالم أخرى"),
    "characters.title": ("Sovereigns and characters", "الحكّام والشخصيات"),
    "characters.lead": ("Rulers, guardians and the people their choices left behind.", "حكّام وحرّاس، وأناسٌ تركتهم خياراتهم خلفها."),
    "characters.filter.all": ("Everyone", "الجميع"),
    "character.age": ("Age", "العمر"),
    "character.age_years": ("about {n} years", "قرابة {n} عامًا"),
    "character.age_unknown": ("Unknown", "مجهول"),
    "character.transformed_at": ("Transformed at {n}", "تحوّل في سن {n}"),
    "character.world": ("World", "العالم"),
    "character.biography": ("Story", "الحكاية"),
    "character.appearance": ("Appearance", "المظهر"),
    "character.personality": ("Personality", "الشخصية"),
    "character.motivation": ("What drives them", "ما يدفعه"),
    "character.fears": ("What they fear", "ما يخشاه"),
    "character.relationships": ("Bonds", "الروابط"),
    "story.title": ("The story", "القصة"),
    "story.lead": ("Every world remembers differently.", "كل عالمٍ يتذكّر على طريقته."),
    "story.chapters": ("Chapters", "الفصول"),
    "story.previous": ("Previous chapter", "الفصل السابق"),
    "story.next": ("Next chapter", "الفصل التالي"),
    "story.spoiler": ("This chapter reveals a turning point. Only its summary is shown here.", "يكشف هذا الفصل نقطة تحوّل، لذا يُعرض ملخّصه فقط."),
    "story.back_to_arc": ("Back to the arc", "العودة إلى القوس القصصي"),
    "lore.title": ("Memory archive", "أرشيف الذاكرة"),
    "lore.lead": ("Fragments recovered from five worlds. Some contradict each other.", "شظايا مستعادة من خمسة عوالم. بعضها يناقض بعضًا."),
    "lore.related": ("Cross-references", "إحالات مرتبطة"),
    "lore.timeline": ("When", "متى"),
    "quests.title": ("Quests", "المهام"),
    "quest.objectives": ("Objectives", "الأهداف"),
    "quest.optional": ("Optional", "اختياري"),
    "news.title": ("News and development updates", "الأخبار وتحديثات التطوير"),
    "news.empty": ("No updates have been published yet.", "لم تُنشر أي تحديثات بعد."),
    "news.back": ("All updates", "كل التحديثات"),
    "search.title": ("Search the universe", "ابحث في الكون"),
    "search.placeholder": ("Search worlds, characters, lore…", "ابحث في العوالم والشخصيات والسجلات…"),
    "search.button": ("Search", "بحث"),
    "search.results": ("{n} results for “{q}”", "{n} نتيجة لـ «{q}»"),
    "search.none": ("Nothing matches “{q}”. Try a world or character name.", "لا شيء يطابق «{q}». جرّب اسم عالمٍ أو شخصية."),
    "search.filter.type": ("Type", "النوع"),
    "search.filter.world": ("World", "العالم"),
    "search.filter.any": ("Any", "الكل"),
    "type.world": ("World", "عالم"),
    "type.character": ("Character", "شخصية"),
    "type.chapter": ("Story", "قصة"),
    "type.quest": ("Quest", "مهمة"),
    "type.lore": ("Lore", "سجل"),
    "type.news": ("News", "خبر"),
    "pagination.previous": ("Previous", "السابق"),
    "pagination.next": ("Next", "التالي"),
    "pagination.page": ("Page {n} of {total}", "الصفحة {n} من {total}"),
    "empty.worlds": ("No worlds have been published yet.", "لم يُنشر أي عالم بعد."),
    "empty.characters": ("No characters have been published yet.", "لم تُنشر أي شخصية بعد."),
    "empty.story": ("No story arcs have been published yet.", "لم يُنشر أي قوس قصصي بعد."),
    "empty.lore": ("No lore entries have been published yet.", "لم تُنشر أي سجلات بعد."),
    # Guide widget
    "guide.open": ("Ask the guide", "اسأل المرشدة"),
    "guide.next": ("Continue", "متابعة"),
    "guide.close": ("Close the guide", "إغلاق المرشدة"),
    "guide.unavailable": ("The guide has nothing to say here yet.", "ليس لدى المرشدة ما تقوله هنا بعد."),
    "sound.on": ("Sound on", "تشغيل الصوت"),
    "sound.off": ("Sound off", "إيقاف الصوت"),
    # Footer
    "footer.status": ("Project status", "حالة المشروع"),
    "footer.newsletter": ("Get development updates", "تابع تحديثات التطوير"),
    "footer.newsletter.email": ("Email address", "البريد الإلكتروني"),
    "footer.newsletter.button": ("Subscribe", "اشترك"),
    "footer.newsletter.thanks": ("You're subscribed. Updates will arrive when there is something worth sending.", "تم اشتراكك. ستصلك التحديثات حين يكون هناك ما يستحق."),
    "footer.newsletter.invalid": ("Enter a valid email address to subscribe.", "أدخل بريدًا إلكترونيًا صحيحًا للاشتراك."),
    "footer.contact": ("Contact", "تواصل"),
    "footer.follow": ("Follow", "تابِع"),
    "footer.rights": ("All rights reserved.", "جميع الحقوق محفوظة."),
    "footer.explore": ("Explore", "استكشف"),
    "footer.legal": ("Legal", "قانوني"),
    # Accounts
    "account.email": ("Email", "البريد الإلكتروني"),
    "account.password": ("Password", "كلمة المرور"),
    "account.password_confirm": ("Confirm password", "تأكيد كلمة المرور"),
    "account.display_name": ("Display name", "الاسم الظاهر"),
    "account.sign_in.title": ("Sign in", "تسجيل الدخول"),
    "account.sign_in.button": ("Sign in", "دخول"),
    "account.register.title": ("Create your account", "أنشئ حسابك"),
    "account.register.button": ("Create account", "إنشاء الحساب"),
    "account.register.lead": ("An account is optional. It will hold your preferences now and game progress later.", "الحساب اختياري. يحفظ تفضيلاتك الآن وتقدّمك في اللعبة لاحقًا."),
    "account.forgot": ("Forgot your password?", "نسيت كلمة المرور؟"),
    "account.no_account": ("New here? Create an account", "جديد هنا؟ أنشئ حسابًا"),
    "account.have_account": ("Already have an account? Sign in", "لديك حساب؟ سجّل الدخول"),
    "account.rate_limited": ("Too many sign-in attempts. Wait 15 minutes and try again.", "محاولات دخول كثيرة. انتظر 15 دقيقة ثم حاول مجددًا."),
    "account.invalid": ("That email and password don't match an account.", "البريد الإلكتروني وكلمة المرور لا يطابقان أي حساب."),
    "account.profile.title": ("Your account", "حسابك"),
    "account.profile.save": ("Save changes", "حفظ التغييرات"),
    "account.profile.saved": ("Changes saved.", "تم حفظ التغييرات."),
    "account.verify.pending": ("Your email address is not verified yet.", "لم يتم التحقق من بريدك الإلكتروني بعد."),
    "account.verify.resend": ("Send verification email", "إرسال رسالة التحقق"),
    "account.verify.sent": ("If email delivery is configured, a verification link is on its way.", "إن كان إرسال البريد مُفعّلًا، فرابط التحقق في طريقه إليك."),
    "account.verify.done": ("Email address verified.", "تم التحقق من البريد الإلكتروني."),
    "account.verify.invalid": ("This verification link is invalid or has expired. Request a new one from your account.", "رابط التحقق غير صالح أو منتهي الصلاحية. اطلب رابطًا جديدًا من حسابك."),
    "account.verified": ("Verified", "مُتحقَّق منه"),
    "account.security": ("Security", "الأمان"),
    "account.change_password": ("Change password", "تغيير كلمة المرور"),
    "account.privacy": ("Privacy", "الخصوصية"),
    "account.delete.title": ("Delete your account", "حذف حسابك"),
    "account.delete.lead": ("Your request is reviewed and completed by the studio. Confirm with your password.", "يراجع الاستوديو طلبك ويُنفّذه. أكّد بكلمة المرور."),
    "account.delete.button": ("Request account deletion", "طلب حذف الحساب"),
    "account.delete.requested": ("Your deletion request was received.", "تم استلام طلب الحذف."),
    "account.delete.pending": ("A deletion request is pending for this account.", "يوجد طلب حذف قيد المعالجة لهذا الحساب."),
    "account.reset.title": ("Reset your password", "إعادة تعيين كلمة المرور"),
    "account.reset.button": ("Send reset link", "إرسال رابط إعادة التعيين"),
    "account.reset.done": ("If an account exists for that address, a reset link has been sent.", "إن وُجد حساب لهذا العنوان فقد أُرسل رابط إعادة التعيين."),
    "account.reset.new": ("Choose a new password", "اختر كلمة مرور جديدة"),
    "account.reset.invalid": ("This reset link is invalid or has expired.", "رابط إعادة التعيين غير صالح أو منتهي الصلاحية."),
    "account.reset.complete": ("Your password has been changed. You can sign in now.", "تم تغيير كلمة المرور. يمكنك تسجيل الدخول الآن."),
    "form.errors": ("Fix the highlighted fields and try again.", "صحّح الحقول المحددة ثم حاول مجددًا."),
    # Errors
    "error.404.title": ("This place is not on any star chart", "هذا المكان ليس على أي خريطة نجمية"),
    "error.404.text": ("The page may have moved, or it was never recovered.", "ربما نُقلت الصفحة، أو لم تُستعَد قط."),
    "error.403.title": ("This archive is sealed", "هذا الأرشيف مختوم"),
    "error.403.text": ("You don't have permission to open this page.", "ليست لديك صلاحية لفتح هذه الصفحة."),
    "error.500.title": ("Something broke on our side", "حدث عطل من جهتنا"),
    "error.500.text": ("The error has been logged. Try again in a moment.", "تم تسجيل الخطأ. حاول مجددًا بعد لحظات."),
    "error.home": ("Return home", "العودة إلى الرئيسية"),
    # Studio chrome
    "studio.name": ("ASTRAVIA Creator Studio", "استوديو إنشاء أسترافيا"),
    "studio.dashboard": ("Dashboard", "لوحة التحكم"),
    "studio.view_site": ("View site", "عرض الموقع"),
    "studio.new": ("New", "جديد"),
    "studio.save": ("Save", "حفظ"),
    "studio.cancel": ("Cancel", "إلغاء"),
    "studio.edit": ("Edit", "تعديل"),
    "studio.search": ("Search", "بحث"),
    "studio.preview": ("Preview", "معاينة"),
    "studio.publish": ("Publish", "نشر"),
    "studio.unpublish": ("Unpublish", "إلغاء النشر"),
    "studio.schedule": ("Schedule", "جدولة"),
    "studio.submit_review": ("Submit for review", "إرسال للمراجعة"),
    "studio.approve": ("Approve", "اعتماد"),
    "studio.return_draft": ("Return to draft", "إعادة إلى المسودة"),
    "studio.archive": ("Archive", "أرشفة"),
    "studio.delete": ("Delete", "حذف"),
    "studio.revisions": ("Revisions", "المراجعات"),
    "studio.restore": ("Restore this revision", "استعادة هذه المراجعة"),
    "studio.saved": ("Saved.", "تم الحفظ."),
    "studio.no_items": ("Nothing here yet.", "لا يوجد شيء هنا بعد."),
    "studio.sign_in": ("Sign in to the studio", "الدخول إلى الاستوديو"),
}


def _overrides():
    data = cache.get("astravia_ui_overrides")
    if data is None:
        from .models import UIString

        try:
            data = {row.key: (row.text_en, row.text_ar) for row in UIString.objects.all()}
        except Exception:  # table missing during the first migrate
            data = {}
        cache.set("astravia_ui_overrides", data, 300)
    return data


def clear_cache():
    cache.delete("astravia_ui_overrides")


def ui(key, lang=None, **fmt):
    lang = lang or current_language()
    idx = 1 if lang == "ar" else 0
    default = STRINGS.get(key)
    override = _overrides().get(key)
    text = ""
    if override and override[idx]:
        text = override[idx]
    elif default:
        text = default[idx] or default[0]
    else:
        text = key
    if fmt:
        try:
            text = text.format(**fmt)
        except (KeyError, IndexError, ValueError):
            pass
    return text


t = lazy(ui, str)  # lazy version for form labels and module-level constants
