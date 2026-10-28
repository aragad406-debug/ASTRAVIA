"""Canonical starting content for ASTRAVIA (seed_astravia). This is the initial narrative foundation,
not final production writing. Everything here becomes editable database content after seeding.

Provisional names (not fixed by the canon brief, change freely in the Studio):
  - Rayyan  — Kaizen's younger brother
  - Lyssa   — Noxar's sister (deliberately NOT Eilen, who is Zerath's daughter)
"""

SITE = {
    "hero_intro_en": "Six worlds once shared a single heartbeat. Five of them are ruled by sovereigns who saved their people "
    "and lost themselves doing it. The sixth was erased from every map.",
    "hero_intro_ar": "تقاسمت ستةُ عوالم يومًا نبضًا واحدًا. يحكم خمسةً منها حكّامٌ أنقذوا شعوبهم وأضاعوا أنفسهم في سبيل ذلك. "
    "أما السادس فقد مُحي من كل الخرائط.",
    "universe_intro_en": "Everfrost, the Verdant Realm, Solaris, Nyxara and Astrion are bound by an ancient force known as the "
    "Heart of Eternity. Every great miracle in their history drew on it, and every miracle took something in return. "
    "Ordinary civilizations know of five worlds. The oldest records hint at a sixth.",
    "universe_intro_ar": "ترتبط إيفرفروست والمملكة الخضراء وسولاريس ونيكسارا وأستريون بقوةٍ قديمة تُعرف بقلب الأبدية. "
    "كل معجزةٍ عظيمة في تاريخها استمدّت منه، وكل معجزةٍ أخذت شيئًا في المقابل. لا تعرف الحضارات العادية سوى خمسة عوالم، "
    "غير أن أقدم السجلات تلمّح إلى عالمٍ سادس.",
    "narrative_intro_en": "ASTRAVIA is a story about promises made in desperate hours: a father who froze time to save his "
    "daughter, a queen who traded her memories for a cure, an emperor who forgot the brother who taught him mercy. "
    "You will uncover what each of them lost, and decide what can still be recovered.",
    "narrative_intro_ar": "أسترافيا حكايةُ وعودٍ قُطعت في ساعات اليأس: أبٌ جمّد الزمن لينقذ ابنته، وملكةٌ قايضت ذكرياتها بالشفاء، "
    "وإمبراطورٌ نسي الأخ الذي علّمه الرحمة. ستكشف ما فقده كلٌّ منهم، وتقرّر ما الذي ما زال ممكنًا استعادته.",
    "gameplay_intro_en": "The design centres on exploration you can read, battles that mean something, and choices whose "
    "consequences you can see in the world.",
    "gameplay_intro_ar": "يرتكز التصميم على استكشافٍ يُقرأ، ومعارك ذات معنى، وخياراتٍ ترى عواقبها في العالم.",
}

WORLDS = [
    {
        "slug": "everfrost", "order": 1, "theme": "frost", "colors": ("#9FE4FF", "#16284F", "#E6F4FF"),
        "name_en": "Everfrost", "name_ar": "إيفرفروست",
        "tagline_en": "A kingdom frozen in the moment its emperor could not bear to lose.",
        "tagline_ar": "مملكةٌ تجمّدت عند اللحظة التي لم يحتمل إمبراطورها خسارتها.",
        "capital_en": "Crystalheim", "capital_ar": "كريستالهايم",
        "short_description_en": "Ice palaces, frozen gardens and streets where snow hangs motionless in the air.",
        "short_description_ar": "قصورٌ من جليد، وحدائق متجمدة، وشوارع يتعلّق فيها الثلج بلا حراك.",
        "description_en": "Everfrost was once a northern kingdom of festivals and glasswork. Now its mountains wear "
        "palaces of transparent ice and its forests stand frozen mid-sway. In Crystalheim, celebrations stopped "
        "halfway through: lanterns still hang over the squares, letters lie unfinished on desks, and the snow itself "
        "has forgotten how to fall.",
        "description_ar": "كانت إيفرفروست مملكةً شمالية تعجّ بالمهرجانات وصناعة الزجاج. أمّا اليوم فتكسو جبالَها قصورٌ من جليدٍ شفاف، "
        "وتقف غاباتها متجمدةً في منتصف تمايلها. في كريستالهايم توقفت الاحتفالات في منتصفها: ما زالت الفوانيس معلّقة فوق الساحات، "
        "والرسائل مطروحة على المكاتب دون أن تكتمل، والثلج نفسه نسي كيف يهطل.",
        "lore_teaser_en": "Somewhere beneath the palace, a light still flickers inside the ice.",
        "lore_teaser_ar": "في مكانٍ ما تحت القصر، ما زال ضوءٌ يرتعش داخل الجليد.",
        "environment_en": "Frozen mountains, massive ice palaces, snow-covered streets, transparent magical crystals, "
        "blue and silver light, ancient frozen gardens and suspended snow — beautiful and oppressive at once.",
        "environment_ar": "جبالٌ متجمدة، وقصورٌ جليدية شاهقة، وشوارع يكسوها الثلج، وبلّورات سحرية شفافة، وضوءٌ أزرق وفضي، "
        "وحدائق قديمة متجمدة، وثلجٌ معلّق في الهواء؛ جمالٌ وخناقٌ في آنٍ واحد.",
        "ruler": "zerath",
        "regions": [
            ("crystalheim", "Crystalheim", "كريستالهايم", "city", "The capital, preserved at the moment the winter came.", "العاصمة، محفوظةٌ عند اللحظة التي حلّ فيها الشتاء."),
            ("frozen-gardens", "The Frozen Gardens", "الحدائق المتجمدة", "sanctum", "Royal gardens where every flower became glass.", "حدائق ملكية تحوّلت فيها كل زهرةٍ إلى زجاج."),
            ("crystal-throne", "The Crystal Throne", "العرش البلّوري", "arena", "The emperor's throne hall, and the crystal beneath it.", "قاعة عرش الإمبراطور، والبلّورة القابعة تحتها."),
        ],
    },
    {
        "slug": "verdant-realm", "order": 2, "theme": "verdant", "colors": ("#7BE495", "#0F2A1E", "#E8C878"),
        "name_en": "The Verdant Realm", "name_ar": "المملكة الخضراء",
        "tagline_en": "A forest that protects itself from everyone, including its own people.",
        "tagline_ar": "غابةٌ تحمي نفسها من الجميع، حتى من أهلها.",
        "capital_en": "Eilorin", "capital_ar": "إيلورين",
        "short_description_en": "Living trees, luminous roots and shrines swallowed by a forest that has grown hostile.",
        "short_description_ar": "أشجارٌ حيّة، وجذورٌ مضيئة، ومزاراتٌ ابتلعتها غابةٌ صارت عدائية.",
        "description_en": "Beneath the Verdant Realm lies the Mother of Roots, an ancient living intelligence. Its light "
        "once fed every tree in Eilorin. Today the roots glow with an infected brilliance, guardians attack travellers, "
        "and whole settlements have been reclaimed by vines that seem to remember a grudge.",
        "description_ar": "تحت المملكة الخضراء ترقد أمّ الجذور، وهي وعيٌ حيٌّ قديم كان نوره يغذّي كل شجرةٍ في إيلورين. "
        "أمّا اليوم فتتوهّج الجذور ببريقٍ عليل، ويهاجم الحرّاسُ المسافرين، واستعادت الكرومُ قرىً بأكملها كأنها تحمل ضغينة.",
        "lore_teaser_en": "The queen saved her people from a plague. Nobody remembers what she paid.",
        "lore_teaser_ar": "أنقذت الملكة شعبها من الوباء، ولا أحد يذكر الثمن الذي دفعته.",
        "environment_en": "Ancient forests, giant luminous roots, living trees, bioluminescent flowers, floating pollen, "
        "emerald and gold light, ruined shrines, forest creatures — a beautiful place hiding corruption.",
        "environment_ar": "غاباتٌ عتيقة، وجذورٌ عملاقة مضيئة، وأشجارٌ حيّة، وأزهارٌ متلألئة، وغبار طلعٍ عائم، وضوءٌ زمرّدي وذهبي، "
        "ومزاراتٌ متهدّمة، وكائناتٌ برّية؛ مكانٌ جميل يخفي فسادًا.",
        "ruler": "vespera",
        "regions": [
            ("eilorin", "Eilorin", "إيلورين", "city", "A city grown, not built, now half-swallowed by roots.", "مدينةٌ نمت ولم تُبنَ، ابتلعت الجذور نصفها."),
            ("sacred-grove", "The Sacred Grove", "البستان المقدّس", "sanctum", "Where the queen first spoke to the Mother of Roots.", "حيث خاطبت الملكة أمَّ الجذور أول مرة."),
        ],
    },
    {
        "slug": "solaris", "order": 3, "theme": "solar", "colors": ("#F2B45A", "#2A1606", "#E8C878"),
        "name_en": "Solaris", "name_ar": "سولاريس",
        "tagline_en": "An empire built on a promise that no child would starve.",
        "tagline_ar": "إمبراطوريةٌ قامت على وعدٍ ألّا يجوع طفل.",
        "capital_en": "Azharan", "capital_ar": "أزهران",
        "short_description_en": "Golden deserts, monumental sandstone cities and the black storms that bury them.",
        "short_description_ar": "صحارٍ ذهبية، ومدنٌ من الحجر الرملي الشاهق، وعواصف سوداء تدفنها.",
        "description_en": "Azharan's sandstone towers glow like embers at dusk, and its royal storehouses are the largest "
        "in any world. Yet beyond the capital, villages wait for grain that rarely comes. Out in the dunes, the black "
        "sandstorms still circle the ruins of cities that the emperor could not save.",
        "description_ar": "تتوهّج أبراج أزهران الرملية كالجمر عند الغسق، ومخازنها الملكية هي الأكبر في العوالم كلها. "
        "لكن خارج العاصمة تنتظر القرى حبوبًا قلّما تصل. وفي الكثبان البعيدة ما زالت العواصف السوداء تدور حول أطلال مدنٍ "
        "لم يستطع الإمبراطور إنقاذها.",
        "lore_teaser_en": "A child's toy lies buried in a shelter that appears on no royal map.",
        "lore_teaser_ar": "لعبةُ طفلٍ مدفونة في ملجأٍ لا يظهر على أي خريطةٍ ملكية.",
        "environment_en": "Vast golden deserts, ancient desert cities, monumental sandstone architecture, black "
        "sandstorms, solar energy, ruined temples, buried civilizations and burning horizons in gold, amber and obsidian.",
        "environment_ar": "صحارٍ ذهبية شاسعة، ومدنٌ صحراوية قديمة، وعمارةٌ رملية ضخمة، وعواصف رملية سوداء، وطاقةٌ شمسية، "
        "ومعابد متهدّمة، وحضاراتٌ مدفونة، وآفاقٌ مشتعلة بألوان الذهب والكهرمان والسَّبَج.",
        "ruler": "kaizen",
        "regions": [
            ("azharan", "Azharan", "أزهران", "city", "The capital and its overflowing royal storehouses.", "العاصمة ومخازنها الملكية الطافحة."),
            ("forgotten-shelter", "The Forgotten Shelter", "الملجأ المنسي", "ruins", "A storm shelter half-buried in black sand.", "ملجأٌ من العواصف نصفه مدفون في الرمل الأسود."),
        ],
    },
    {
        "slug": "nyxara", "order": 4, "theme": "cyber", "colors": ("#63E6FF", "#120B2E", "#9C6BFF"),
        "name_en": "Nyxara", "name_ar": "نيكسارا",
        "tagline_en": "A city where nothing bad can happen, because nothing goes unseen.",
        "tagline_ar": "مدينةٌ لا يحدث فيها سوء، لأن لا شيء فيها يغيب عن الأنظار.",
        "capital_en": "Nova City", "capital_ar": "مدينة نوفا",
        "short_description_en": "Neon megastructures, holographic streets and surveillance towers that never sleep.",
        "short_description_ar": "منشآتٌ عملاقة بأضواء النيون، وشوارع هولوغرافية، وأبراج مراقبة لا تنام.",
        "description_en": "Nova City is the most advanced civilization in the five worlds. Its towers think, its streets "
        "anticipate, and its citizens are safe in ways no other people have ever been. They are also watched in every "
        "room, every message and every dream that the neural core can reach.",
        "description_ar": "مدينة نوفا أكثر حضارات العوالم الخمسة تقدّمًا؛ أبراجها تفكّر، وشوارعها تتوقّع، ومواطنوها آمنون "
        "كما لم يأمن شعبٌ من قبل. لكنهم مراقَبون في كل غرفة، وكل رسالة، وكل حلمٍ تبلغه النواة العصبية.",
        "lore_teaser_en": "One citizen's records have been deleted from every archive. The emperor ordered it himself.",
        "lore_teaser_ar": "حُذفت سجلات مواطنةٍ واحدة من كل أرشيف، وقد أمر الإمبراطور بذلك بنفسه.",
        "environment_en": "Futuristic megastructures, neon-blue architecture, dark reflective surfaces, holographic "
        "interfaces, cybernetic infrastructure, artificial intelligence, surveillance towers and mechanical districts "
        "under violet and cyan light.",
        "environment_ar": "منشآتٌ مستقبلية عملاقة، وعمارةٌ بزرقة النيون، وأسطحٌ داكنة عاكسة، وواجهاتٌ هولوغرافية، وبنيةٌ "
        "سيبرانية، وذكاءٌ اصطناعي، وأبراج مراقبة، وأحياءٌ ميكانيكية تحت ضوءٍ بنفسجي وسماوي.",
        "ruler": "noxar",
        "regions": [
            ("nova-city", "Nova City", "مدينة نوفا", "city", "The capital: perfect, luminous, and monitored.", "العاصمة: مثالية، مضيئة، ومراقَبة."),
            ("restricted-archive", "The Restricted Archive", "الأرشيف المحظور", "dungeon", "Where deleted lives are kept.", "حيث تُحفظ الحيوات المحذوفة."),
        ],
    },
    {
        "slug": "astrion", "order": 5, "theme": "celestial", "colors": ("#E8C878", "#1A1238", "#9C6BFF"),
        "name_en": "Astrion", "name_ar": "أستريون",
        "tagline_en": "An empire that stopped the future to keep it from ending.",
        "tagline_ar": "إمبراطوريةٌ أوقفت المستقبل كي لا ينتهي.",
        "capital_en": "Celestara", "capital_ar": "سيليستارا",
        "short_description_en": "Floating observatories, star bridges and libraries where time runs in circles.",
        "short_description_ar": "مراصدُ عائمة، وجسورٌ من نجوم، ومكتباتٌ يدور فيها الزمن في حلقات.",
        "description_en": "Celestara floats among its own constellations, linked by bridges of starlight. Its astronomers "
        "once mapped every possible future. Now their instruments point at a single one, the empress keeps it fixed in "
        "place, and the people of Astrion repeat the same safe year without knowing it.",
        "description_ar": "تطفو سيليستارا بين كوكباتها الخاصة، تصلها جسورٌ من ضوء النجوم. رسم فلكيّوها يومًا كل مستقبلٍ ممكن، "
        "أمّا اليوم فتشير أجهزتهم إلى مستقبلٍ واحد تُبقيه الإمبراطورة ثابتًا، ويكرّر أهل أستريون العام الآمن نفسه دون أن يعلموا.",
        "lore_teaser_en": "The prophecy the empress fears may not mean what she believes.",
        "lore_teaser_ar": "النبوءة التي تخشاها الإمبراطورة قد لا تعني ما تظنّه.",
        "environment_en": "Floating celestial structures, vast observatories, star bridges, cosmic temples, celestial "
        "libraries, golden and violet light, massive astronomical instruments and time-distorted architecture.",
        "environment_ar": "منشآتٌ سماوية عائمة، ومراصدُ شاسعة، وجسورٌ نجمية، ومعابد كونية، ومكتباتٌ سماوية، وضوءٌ ذهبي وبنفسجي، "
        "وأدواتٌ فلكية ضخمة، وعمارةٌ يلتوي فيها الزمن.",
        "ruler": "asteria",
        "regions": [
            ("celestara", "Celestara", "سيليستارا", "city", "The floating capital among the constellations.", "العاصمة العائمة بين الكوكبات."),
            ("observatory-of-futures", "The Observatory of Futures", "مرصد المستقبلات", "sanctum", "Where every possible future was once recorded.", "حيث سُجّل يومًا كل مستقبلٍ ممكن."),
        ],
    },
    {
        "slug": "umbra", "order": 6, "theme": "umbra", "colors": ("#C9D1E8", "#06060C", "#8E2439"),
        "visibility": "hidden",
        "name_en": "Umbra", "name_ar": "أمبرا",
        "tagline_en": "The world that remembers for all the others.",
        "tagline_ar": "العالم الذي يتذكّر نيابةً عن العوالم الأخرى.",
        "capital_en": "The Empty Palace", "capital_ar": "القصر الخالي",
        "short_description_en": "A hidden realm of broken celestial structures and archives of forgotten voices.",
        "short_description_ar": "عالمٌ خفيّ من منشآتٍ سماوية محطّمة وأرشيفاتٍ لأصواتٍ منسية.",
        "description_en": "Umbra lies beyond ordinary space. Its palaces are empty, its archives hold memories surrendered "
        "by every world, and its architecture rearranges itself around whatever the visitor has recovered.",
        "description_ar": "تقع أمبرا وراء الفضاء المعروف. قصورها خالية، وأرشيفاتها تحفظ ذكرياتٍ تخلّت عنها العوالم كلها، "
        "وعمارتها تعيد تشكيل نفسها حول ما استعاده الزائر.",
        "lore_teaser_en": "Someone is still waiting at the palace gate.",
        "lore_teaser_ar": "ما زال أحدٌ ينتظر عند بوابة القصر.",
        "environment_en": "Broken celestial structures, empty palaces, vast memory archives, black and silver architecture, "
        "faint suspended stars, fractured timelines, echoes of forgotten voices.",
        "environment_ar": "منشآتٌ سماوية محطّمة، وقصورٌ خالية، وأرشيفات ذاكرةٍ شاسعة، وعمارةٌ سوداء وفضية، ونجومٌ باهتة معلّقة، "
        "وخطوطٌ زمنية متصدّعة، وأصداءُ أصواتٍ منسية.",
        "ruler": "hollow-king",
        "regions": [
            ("palace-gate", "The Palace Gate", "بوابة القصر", "hidden", "Where someone has waited for ten thousand years.", "حيث ينتظر أحدٌ منذ عشرة آلاف عام."),
        ],
    },
]

CHARACTERS = [
    {
        "slug": "zerath", "category": "sovereign", "world": "everfrost", "order": 1, "color": "#9FE4FF",
        "age": 1247, "transformation_age": 30,
        "name_en": "Zerath", "name_ar": "زيراث", "title_en": "The Ice Emperor", "title_ar": "إمبراطور الجليد",
        "teaser_en": "He froze an entire kingdom to save one child, then forgot which child it was.",
        "teaser_ar": "جمّد مملكةً بأكملها لينقذ طفلةً واحدة، ثم نسي من تكون.",
        "biography_en": "Zerath was a loving father before he was an emperor anyone feared. When an exceptionally deadly "
        "winter threatened the life of his nine-year-old daughter, Eilen, he placed a cursed crown on his head and froze "
        "time to preserve her. Eilen was sealed inside a transparent crystal of magical ice.\n\nThe crown kept her safe, "
        "and it fed on him. Year by year it consumed his memories and sharpened his grief, until he no longer remembered "
        "why he had worn it. His wish to protect one girl became an obsession with controlling everything, and the "
        "emperor who wanted to save a single child became a tyrant who would not let his world move forward.",
        "biography_ar": "كان زيراث أبًا محبًّا قبل أن يصبح إمبراطورًا يخشاه الجميع. وحين هدّد شتاءٌ قاتلٌ على نحوٍ استثنائي حياةَ ابنته "
        "إيلين ذات الأعوام التسعة، وضع على رأسه تاجًا ملعونًا وجمّد الزمن ليحفظها، فحُبست إيلين داخل بلّورةٍ شفافة من الجليد السحري.\n\n"
        "حفظها التاج، لكنه تغذّى عليه. عامًا بعد عام التهم ذكرياته وأذكى حزنه، حتى لم يعد يذكر لماذا وضعه. فتحوّلت رغبته في حماية "
        "فتاةٍ واحدة إلى هوسٍ بالسيطرة على كل شيء، وصار الإمبراطور الذي أراد إنقاذ طفلة طاغيةً يمنع عالمه من المضيّ قُدمًا.",
        "appearance_en": "Tall and gaunt beneath layered silver robes, frost creeping along his skin from the crown's points.",
        "appearance_ar": "طويلٌ نحيل تحت أرديةٍ فضية متراكبة، يزحف الصقيع على جلده من أطراف التاج.",
        "personality_en": "Controlled, courteous, and terrifyingly certain. Flashes of tenderness surface without explanation.",
        "personality_ar": "منضبط، دمث، ويقينه مخيف. تلوح منه ومضاتُ حنانٍ لا يجد لها تفسيرًا.",
        "motivation_en": "To keep anything else from being lost, even if nothing is ever allowed to change.",
        "motivation_ar": "ألّا يضيع شيءٌ آخر، حتى لو مُنع كل شيءٍ من التغيّر.",
        "fears_en": "Thaw. The moment after the last moment.", "fears_ar": "الذوبان. اللحظة التي تلي اللحظة الأخيرة.",
        "secrets_en": "The Hollow King gave him the crown.", "secrets_ar": "الملك الأجوف هو من أعطاه التاج.",
    },
    {
        "slug": "eilen", "category": "supporting", "world": "everfrost", "order": 2, "color": "#CFEFFF",
        "age": 9, "transformation_age": None,
        "name_en": "Eilen", "name_ar": "إيلين", "title_en": "The Girl in the Crystal", "title_ar": "الفتاة في البلّورة",
        "teaser_en": "Zerath's daughter. She has been nine years old for twelve centuries.",
        "teaser_ar": "ابنة زيراث. ظلّت في التاسعة من عمرها اثني عشر قرنًا.",
        "biography_en": "Eilen was nine when the winter came. Inside the crystal she does not age, but she is not entirely "
        "asleep: her father's grief reaches her, and in the decisive battle her presence is what disrupts the crown's grip.",
        "biography_ar": "كانت إيلين في التاسعة حين حلّ الشتاء. لا تكبر داخل البلّورة، لكنها ليست نائمةً تمامًا؛ يبلغها حزن أبيها، "
        "وفي المعركة الحاسمة يكون حضورها هو ما يزعزع قبضة التاج.",
        "personality_en": "Curious, stubborn, kind. She left drawings for her father in places only he would look.",
        "personality_ar": "فضولية، عنيدة، طيّبة. تركت رسوماتٍ لأبيها في أماكن لا يبحث فيها سواه.",
    },
    {
        "slug": "vespera", "category": "sovereign", "world": "verdant-realm", "order": 3, "color": "#7BE495",
        "age": 986, "transformation_age": 19,
        "name_en": "Vespera", "name_ar": "فيسبيرا", "title_en": "The Forest Queen", "title_ar": "ملكة الغابة",
        "teaser_en": "She bonded with the forest to cure her people. The forest kept her memories as payment.",
        "teaser_ar": "ارتبطت بالغابة لتشفي شعبها، فاحتفظت الغابة بذكرياتها ثمنًا.",
        "biography_en": "When a mysterious disease spread through Eilorin, nineteen-year-old Vespera bonded herself to the "
        "Mother of Roots, the ancient intelligence beneath the forest. The plague stopped. The bond demanded her memories "
        "in return, and one by one she lost the faces, names and songs that tied her to her people.\n\nAs the ancient force "
        "grew corrupted, so did her methods. She now protects the forest by any means, and the forest's hostility is "
        "partly the wound in her bond with the Mother.",
        "biography_ar": "حين انتشر مرضٌ غامض في إيلورين، ربطت فيسبيرا ذات التسعة عشر عامًا نفسها بأمّ الجذور، الوعي القديم القابع تحت "
        "الغابة. توقّف الوباء، لكن الرابطة طلبت ذكرياتها في المقابل، ففقدت واحدةً تلو الأخرى الوجوهَ والأسماءَ والأغاني التي ربطتها "
        "بشعبها.\n\nومع فساد تلك القوة القديمة فسدت أساليبها أيضًا. صارت تحمي الغابة بأي وسيلة، وعداءُ الغابة جرحٌ في رابطتها بالأم.",
        "motivation_en": "Preserve the forest at any cost.", "motivation_ar": "أن تحفظ الغابة مهما كلّف الأمر.",
        "fears_en": "Discovering that she no longer knows who she is protecting.", "fears_ar": "أن تكتشف أنها لم تعد تعرف من تحمي.",
    },
    {
        "slug": "mother-of-roots", "category": "historical", "world": "verdant-realm", "order": 4, "color": "#4FAF78",
        "age": None, "age_unknown": True, "visibility": "teaser",
        "name_en": "The Mother of Roots", "name_ar": "أمّ الجذور", "title_en": "The Living Intelligence", "title_ar": "الوعي الحيّ",
        "teaser_en": "An ancient consciousness beneath the forest. Its voice has not been heard in centuries.",
        "teaser_ar": "وعيٌ قديم تحت الغابة، لم يُسمع صوته منذ قرون.",
        "secrets_en": "Its consciousness still survives within the roots.", "secrets_ar": "ما زال وعيها حيًّا داخل الجذور.",
    },
    {
        "slug": "kaizen", "category": "sovereign", "world": "solaris", "order": 5, "color": "#F2B45A",
        "age": 2063, "transformation_age": 42,
        "name_en": "Kaizen", "name_ar": "كايزن", "title_en": "The Desert Emperor", "title_ar": "إمبراطور الصحراء",
        "teaser_en": "He swore no child would starve. He forgot the brother who made him swear it.",
        "teaser_ar": "أقسم ألّا يجوع طفل، ونسي الأخ الذي جعله يُقسم.",
        "biography_en": "Kaizen grew up poor with his younger brother, Rayyan, and promised himself that no child in his "
        "kingdom would ever go hungry. During a catastrophic black sandstorm he used an ancient shard to stop the "
        "disaster. Many lived; the shard took important memories in return.\n\nOver time he forgot Rayyan entirely. The "
        "tragedy is not only that he forgot someone. The brother whose sacrifice shaped his whole philosophy became the "
        "one person he could not remember.",
        "biography_ar": "نشأ كايزن فقيرًا مع أخيه الأصغر ريّان، وعاهد نفسه ألّا يجوع طفلٌ في مملكته أبدًا. وأثناء عاصفةٍ رملية سوداء مدمّرة "
        "استخدم شظيةً قديمة ليوقف الكارثة، فنجا كثيرون، وأخذت الشظية ذكرياتٍ مهمة في المقابل.\n\nومع الزمن نسي ريّان تمامًا. وليست "
        "المأساة أنه نسي أحدًا فحسب، بل أن الأخ الذي صاغت تضحيتُه فلسفتَه كلها صار الشخص الوحيد الذي لا يستطيع تذكّره.",
        "motivation_en": "Feed his people. Prove the promise was kept.", "motivation_ar": "أن يُطعم شعبه، ويثبت أن الوعد لم يُخلَف.",
        "fears_en": "That the storehouses are full and the villages are still hungry.", "fears_ar": "أن تكون المخازن ممتلئة والقرى ما زالت جائعة.",
    },
    {
        "slug": "rayyan", "category": "historical", "world": "solaris", "order": 6, "color": "#E8C878",
        "age": None, "age_unknown": True, "visibility": "teaser",
        "name_en": "Rayyan", "name_ar": "ريّان", "title_en": "The Brother in the Storm", "title_ar": "الأخ في العاصفة",
        "teaser_en": "No royal record mentions him. A child's toy suggests otherwise.",
        "teaser_ar": "لا يذكره أي سجلٍّ ملكي، لكن لعبة طفلٍ توحي بغير ذلك.",
        "biography_en": "Kaizen's younger brother. He died during the black storm while leading children to a shelter.",
        "biography_ar": "الأخ الأصغر لكايزن. مات أثناء العاصفة السوداء وهو يقود الأطفال إلى ملجأ.",
    },
    {
        "slug": "noxar", "category": "sovereign", "world": "nyxara", "order": 7, "color": "#63E6FF",
        "age": 614, "transformation_age": 31,
        "name_en": "Noxar", "name_ar": "نوكسار", "title_en": "The Cybernetic Emperor", "title_ar": "الإمبراطور السيبراني",
        "teaser_en": "He watches every citizen so that no one will ever be lost again.",
        "teaser_ar": "يراقب كل مواطن كي لا يضيع أحدٌ مرةً أخرى.",
        "biography_en": "Noxar used the neural city core to save his sister, Lyssa. The intervention averted the immediate "
        "catastrophe but damaged his memory, and in time he forgot the sister he had tried to save.\n\nDriven by a fear he "
        "can no longer explain, he built a society where nearly every action is monitored. He believed total surveillance "
        "would prevent suffering. His citizens lost their privacy, their autonomy and their freedom.",
        "biography_ar": "استخدم نوكسار النواة العصبية للمدينة لينقذ أخته ليسا. حال تدخّله دون الكارثة الوشيكة، لكنه أصاب ذاكرته، "
        "ومع الزمن نسي الأخت التي حاول إنقاذها.\n\nوبدافعٍ من خوفٍ لم يعد يستطيع تفسيره، بنى مجتمعًا يُراقَب فيه كل فعلٍ تقريبًا، "
        "معتقدًا أن المراقبة الشاملة ستمنع المعاناة. ففقد مواطنوه خصوصيتهم واستقلالهم وحريتهم.",
        "motivation_en": "Prevent loss through total knowledge.", "motivation_ar": "أن يمنع الفقد بالمعرفة الشاملة.",
        "fears_en": "An empty room he cannot see into.", "fears_ar": "غرفةٌ خالية لا يستطيع رؤية ما بداخلها.",
    },
    {
        "slug": "lyssa", "category": "secret", "world": "nyxara", "order": 8, "color": "#B79CFF",
        "age": None, "age_unknown": True, "visibility": "teaser",
        "name_en": "Lyssa", "name_ar": "ليسا", "title_en": "The Deleted Citizen", "title_ar": "المواطنة المحذوفة",
        "teaser_en": "Her records were erased from every archive in Nova City.",
        "teaser_ar": "مُحيت سجلاتها من كل أرشيفٍ في مدينة نوفا.",
        "biography_en": "Noxar's sister. Her fate after the neural core intervention is one of Nyxara's central mysteries.",
        "biography_ar": "أخت نوكسار. مصيرها بعد تدخّل النواة العصبية أحد أكبر ألغاز نيكسارا.",
    },
    {
        "slug": "asteria", "category": "sovereign", "world": "astrion", "order": 9, "color": "#E8C878",
        "age": 3412, "transformation_age": 80,
        "name_en": "Asteria", "name_ar": "أستيريا", "title_en": "The Celestial Empress", "title_ar": "الإمبراطورة السماوية",
        "teaser_en": "She saw how the world ends, and decided it would never get the chance.",
        "teaser_ar": "رأت كيف ينتهي العالم، فقرّرت ألّا تمنحه الفرصة أبدًا.",
        "biography_en": "At eighty, Asteria witnessed visions of catastrophes that seemed certain. Convinced the future "
        "would destroy civilization, she used the Eclipse Crown to prevent change itself, freezing societies and limiting "
        "their power to shape what comes next.\n\nShe acts from fear, not cruelty. Her conflict asks whether a safe future "
        "is worth sacrificing the freedom to create a different one.",
        "biography_ar": "في الثمانين من عمرها رأت أستيريا رؤى كوارث بدت محتومة. وإذ أيقنت أن المستقبل سيدمّر الحضارة، استخدمت تاج "
        "الكسوف لتمنع التغيّر ذاته، فجمّدت المجتمعات وقيّدت قدرتها على صنع ما سيأتي.\n\nتتصرّف بدافع الخوف لا القسوة. وصراعها "
        "يطرح سؤالًا: هل يستحق المستقبلُ الآمن أن نضحّي من أجله بحرية صنع مستقبلٍ مختلف؟",
        "motivation_en": "Protect civilization from a future she has already seen.", "motivation_ar": "أن تحمي الحضارة من مستقبلٍ رأته بالفعل.",
        "fears_en": "Uncertainty.", "fears_ar": "الغموض واللايقين.",
    },
    {
        "slug": "hollow-king", "category": "secret", "world": "umbra", "order": 10, "color": "#C9D1E8",
        "age": 10000, "transformation_age": None, "visibility": "hidden",
        "name_en": "The Hollow King", "name_ar": "الملك الأجوف", "title_en": "Guardian of Umbra", "title_ar": "حارس أمبرا",
        "teaser_en": "His true name is unknown, even to him.", "teaser_ar": "اسمه الحقيقي مجهول، حتى بالنسبة إليه.",
        "biography_en": "Once the guardian of a realm associated with memory. As Umbra collapsed, he sacrificed his own "
        "memories to delay its destruction. Over ten thousand years he forgot his identity, the people he swore to "
        "protect, and someone who kept waiting for him at the palace gate.\n\nTerrified of losing everything, he began "
        "manipulating the five sovereigns, helping create the crises that shaped their worlds. He believes that "
        "controlling memory, destiny and time may prevent another catastrophe. His greatest fear is not death, but "
        "discovering that everything he sacrificed was meaningless.",
        "biography_ar": "كان يومًا حارسًا لعالمٍ مرتبطٍ بالذاكرة. وحين أخذت أمبرا تنهار، ضحّى بذكرياته ليؤخّر دمارها. وعلى مدى عشرة "
        "آلاف عام نسي هويته، والشعب الذي أقسم على حمايته، ومن ظلّ ينتظره عند بوابة القصر.\n\nوخوفًا من فقدان كل شيء، أخذ يتلاعب "
        "بالحكّام الخمسة، فأسهم في صنع الأزمات التي شكّلت عوالمهم. يعتقد أن السيطرة على الذاكرة والقدر والزمن قد تمنع كارثةً أخرى. "
        "وأعظم ما يخشاه ليس الموت، بل أن يكتشف أن كل ما ضحّى به كان بلا معنى.",
        "age_note": True,
    },
    {
        "slug": "celestial-guide", "category": "guide", "world": None, "order": 0, "color": "#63E6FF",
        "age": None, "age_unknown": True,
        "name_en": "Celestial Guide", "name_ar": "مرشدة الكواكب", "title_en": "Guide of the Five Worlds", "title_ar": "دليلة العوالم الخمسة",
        "teaser_en": "She has walked every world and remembers what their rulers have forgotten.",
        "teaser_ar": "سارت في كل العوالم، وتتذكّر ما نسيه حكّامها.",
        "biography_en": "The Celestial Guide accompanies travellers through ASTRAVIA. She introduces each world, explains "
        "discovered lore and offers hints, though she is careful never to say more than a traveller is ready to hear. "
        "Why she alone remembers so much is a question she answers with a smile.",
        "biography_ar": "ترافق مرشدةُ الكواكب المسافرين عبر أسترافيا؛ تعرّفهم بكل عالم، وتشرح ما يكتشفونه من سجلات، وتقدّم التلميحات، "
        "مع حرصها ألّا تقول أكثر مما يحتمل المسافر سماعه. أمّا لماذا تتذكّر وحدها كل هذا، فسؤالٌ تجيب عنه بابتسامة.",
        "appearance_en": "A slender figure in layered midnight blue, constellations drifting slowly across her cloak.",
        "appearance_ar": "قامةٌ رشيقة في ثيابٍ متراكبة بلون منتصف الليل، تنساب الكوكبات ببطءٍ على عباءتها.",
        "personality_en": "Warm, precise, gently teasing. Speaks of tragedy without flinching.",
        "personality_ar": "دافئة، دقيقة، تمازح برفق. تتحدّث عن المآسي دون أن ترتجف.",
    },
]

RELATIONSHIPS = [
    ("zerath", "eilen", "parent_of", "Zerath froze time to keep Eilen alive.", "جمّد زيراث الزمن ليُبقي إيلين على قيد الحياة.", False),
    ("kaizen", "rayyan", "sibling", "Brothers who grew up poor in Solaris.", "أخوان نشآ فقيرين في سولاريس.", False),
    ("noxar", "lyssa", "sibling", "Noxar tried to save his sister with the neural core.", "حاول نوكسار إنقاذ أخته بالنواة العصبية.", False),
    ("vespera", "mother-of-roots", "ally", "Bonded to cure a plague; the bond is now damaged.", "رابطةٌ عُقدت لعلاج الوباء، وهي اليوم متضرّرة.", False),
    ("hollow-king", "zerath", "manipulates", "", "", True),
    ("hollow-king", "vespera", "manipulates", "", "", True),
    ("hollow-king", "kaizen", "manipulates", "", "", True),
    ("hollow-king", "noxar", "manipulates", "", "", True),
    ("hollow-king", "asteria", "manipulates", "", "", True),
]

ARTIFACTS = [
    ("cursed-crown", "The Cursed Crown", "التاج الملعون", "everfrost", "mythic", True, "A crown that freezes time and feeds on the memories of its wearer.", "تاجٌ يجمّد الزمن ويتغذّى على ذكريات من يرتديه."),
    ("blue-winter-flower", "Blue Winter Flower", "زهرة الشتاء الزرقاء", "everfrost", "legendary", False, "The first flower to bloom when Everfrost thaws.", "أول زهرةٍ تتفتّح حين تذوب إيفرفروست."),
    ("rayyans-toy", "Rayyan's Toy", "لعبة ريّان", "solaris", "rare", True, "A small carved camel, worn smooth by a child's hands.", "جملٌ صغير منحوت، صقلته يدا طفل."),
    ("shard-of-the-black-storm", "Shard of the Black Storm", "شظية العاصفة السوداء", "solaris", "mythic", True, "The ancient shard Kaizen used to stop the storm.", "الشظية القديمة التي أوقف بها كايزن العاصفة."),
    ("neural-city-core", "Neural City Core", "النواة العصبية للمدينة", "nyxara", "mythic", True, "The mind at the centre of Nova City.", "العقل القابع في قلب مدينة نوفا."),
    ("eclipse-crown", "The Eclipse Crown", "تاج الكسوف", "astrion", "mythic", True, "Holds a civilization in a single safe moment.", "يُمسك حضارةً في لحظةٍ آمنةٍ واحدة."),
]

LORE = [
    {
        "slug": "heart-of-eternity", "type": "record", "importance": 4, "timeline": -10000,
        "worlds": ["everfrost", "verdant-realm", "solaris", "nyxara", "astrion"],
        "title_en": "On the Heart of Eternity", "title_ar": "في قلب الأبدية",
        "timeline_label_en": "Before recorded history", "timeline_label_ar": "قبل التاريخ المدوَّن",
        "summary_en": "The oldest surviving description of the force that binds the five worlds.",
        "summary_ar": "أقدم وصفٍ باقٍ للقوة التي تربط العوالم الخمسة.",
        "content_en": "The scribes of every world describe the same thing in different words: a pulse beneath reality "
        "that answers desperate need. The crown in Everfrost, the roots of the Verdant Realm, the shard of Solaris, the "
        "core of Nyxara and the crown of Astrion all drew from it.\n\nNone of the records agree on what it is. All of "
        "them agree that it never gives without taking.",
        "content_ar": "يصف كتبةُ كل عالمٍ الشيءَ نفسه بكلماتٍ مختلفة: نبضٌ تحت الواقع يستجيب للحاجة اليائسة. التاج في إيفرفروست، "
        "وجذور المملكة الخضراء، وشظية سولاريس، ونواة نيكسارا، وتاج أستريون، كلها استمدّت منه.\n\nلا يتّفق سجلٌّ واحد على ماهيته، "
        "لكنها جميعًا تتّفق على أنه لا يعطي دون أن يأخذ.",
        "related": ["the-long-winter", "eclipse-prophecy"],
    },
    {
        "slug": "the-long-winter", "type": "event", "importance": 3, "timeline": -1217,
        "worlds": ["everfrost"], "characters": ["zerath", "eilen"],
        "title_en": "The Long Winter", "title_ar": "الشتاء الطويل",
        "timeline_label_en": "1,217 years ago", "timeline_label_ar": "قبل 1217 عامًا",
        "summary_en": "The winter that should have ended Everfrost, and the night time stopped.",
        "summary_ar": "الشتاء الذي كان سينهي إيفرفروست، والليلة التي توقّف فيها الزمن.",
        "content_en": "Court records end mid-sentence on the night of the first great frost. Physicians had been summoned "
        "to the princess's chamber. The next entry, in a different hand, is dated twelve centuries later.",
        "content_ar": "تنتهي سجلات البلاط في منتصف جملةٍ ليلةَ الصقيع العظيم الأول. كان الأطباء قد استُدعوا إلى جناح الأميرة. "
        "أمّا القيد التالي، وبخطٍّ مختلف، فمؤرَّخٌ بعد اثني عشر قرنًا.",
        "related": ["eilens-last-letter"],
    },
    {
        "slug": "eilens-last-letter", "type": "letter", "importance": 3, "timeline": -1217,
        "worlds": ["everfrost"], "characters": ["eilen", "zerath"],
        "title_en": "Eilen's Last Letter", "title_ar": "رسالة إيلين الأخيرة",
        "timeline_label_en": "The night of the frost", "timeline_label_ar": "ليلة الصقيع",
        "summary_en": "A child's letter, hidden where only her father would look.",
        "summary_ar": "رسالةُ طفلة، خُبّئت حيث لا يبحث سوى أبيها.",
        "content_en": "Father — the doctors whisper when they think I'm asleep. If I have to go somewhere far, don't be "
        "angry at the winter. Plant the blue flowers in the garden for me, and when they bloom, that's me saying I'm fine.",
        "content_ar": "أبي، يتهامس الأطباء حين يظنّون أني نائمة. إن كان عليّ أن أذهب إلى مكانٍ بعيد، فلا تغضب من الشتاء. ازرع الأزهار "
        "الزرقاء في الحديقة من أجلي، وحين تتفتّح فاعلم أنني أقول لك إنني بخير.",
        "discovery": {"quest": "letters-to-a-daughter", "state": "active"},
    },
    {
        "slug": "mother-of-roots", "type": "forbidden", "importance": 3, "timeline": -986,
        "worlds": ["verdant-realm"], "characters": ["vespera", "mother-of-roots"],
        "title_en": "The Bond Beneath Eilorin", "title_ar": "الرابطة تحت إيلورين",
        "timeline_label_en": "The plague years", "timeline_label_ar": "سنوات الوباء",
        "summary_en": "What the queen agreed to, recorded by the last shrine-keeper.",
        "summary_ar": "ما ارتضته الملكة، كما دوّنه آخر سدنة المزار.",
        "content_en": "The Mother asked for nothing she could hold. She asked for what the queen carried: every song her "
        "mother sang, every name she knew. The queen agreed before the keeper finished explaining.",
        "content_ar": "لم تطلب الأم شيئًا يُمسَك باليد، بل طلبت ما تحمله الملكة: كل أغنيةٍ غنّتها لها أمها، وكل اسمٍ عرفته. "
        "ووافقت الملكة قبل أن يُتمّ السادن شرحه.",
    },
    {
        "slug": "azharan-shelter-ledger", "type": "document", "importance": 3, "timeline": -2021,
        "worlds": ["solaris"], "characters": ["rayyan", "kaizen"],
        "title_en": "Shelter Ledger, Southern Quarter", "title_ar": "سجلّ الملجأ، الحيّ الجنوبي",
        "timeline_label_en": "The year of the black storm", "timeline_label_ar": "عام العاصفة السوداء",
        "summary_en": "A list of children brought to safety, and the name of the young man who brought them.",
        "summary_ar": "قائمةٌ بأطفالٍ أُوصلوا إلى برّ الأمان، واسمُ الشاب الذي أوصلهم.",
        "content_en": "Forty-one children counted in. The forty-second entry is not a child. It reads only: “Rayyan "
        "went back for the last ones.” No further entries.",
        "content_ar": "أُحصي واحدٌ وأربعون طفلًا عند الدخول. أمّا القيد الثاني والأربعون فليس لطفل، ونصّه فقط: «عاد ريّان من أجل "
        "آخرهم». ولا قيود بعد ذلك.",
    },
    {
        "slug": "archived-message-001", "type": "message", "importance": 2, "timeline": -614,
        "worlds": ["nyxara"], "characters": ["noxar", "lyssa"],
        "title_en": "Archived Message 0-0-1", "title_ar": "رسالةٌ مؤرشفة 0-0-1",
        "timeline_label_en": "Before the core", "timeline_label_ar": "قبل النواة",
        "summary_en": "The only message in Nova City that the surveillance network refuses to open.",
        "summary_ar": "الرسالة الوحيدة في مدينة نوفا التي ترفض شبكة المراقبة فتحها.",
        "content_en": "Sender field: blank. Recipient: the emperor. Access: denied by order of the emperor. The message "
        "has been flagged for deletion 1,204 times and restored 1,204 times.",
        "content_ar": "حقل المرسِل: فارغ. المستلِم: الإمبراطور. الوصول: مرفوض بأمر الإمبراطور. وُسمت الرسالة للحذف 1204 مرات، "
        "واستُعيدت 1204 مرات.",
    },
    {
        "slug": "eclipse-prophecy", "type": "prophecy", "importance": 3, "timeline": -3332,
        "worlds": ["astrion"], "characters": ["asteria"],
        "title_en": "The Eclipse Prophecy", "title_ar": "نبوءة الكسوف",
        "timeline_label_en": "The empress's eightieth year", "timeline_label_ar": "العام الثمانون للإمبراطورة",
        "summary_en": "The vision that convinced Asteria to stop time's forward motion.",
        "summary_ar": "الرؤيا التي أقنعت أستيريا بإيقاف مضيّ الزمن.",
        "content_en": "“When the six hearts beat apart, the stars go dark.” The empress read it as an ending. The "
        "observatory's oldest copy uses a word that can also mean “again”.",
        "content_ar": "«حين تنبض القلوب الستة متفرّقة، تنطفئ النجوم.» قرأتها الإمبراطورة نهايةً. غير أن أقدم نسخةٍ في المرصد "
        "تستعمل كلمةً قد تعني أيضًا «من جديد».",
    },
    {
        "slug": "the-gatekeepers-vigil", "type": "memory", "importance": 4, "timeline": -10000, "visibility": "hidden",
        "worlds": ["umbra"], "characters": ["hollow-king"],
        "title_en": "The Vigil at the Gate", "title_ar": "السهر عند البوابة",
        "timeline_label_en": "Unknown", "timeline_label_ar": "مجهول",
        "summary_en": "A memory fragment found in Umbra. It belongs to no one who is still alive.",
        "summary_ar": "شظية ذاكرةٍ عُثر عليها في أمبرا، لا تخصّ أحدًا ما زال حيًّا.",
        "content_en": "Someone stands at the palace gate, holding a lantern for a king who will not remember them.",
        "content_ar": "ثمّة من يقف عند بوابة القصر، يحمل فانوسًا لملكٍ لن يتذكّره.",
    },
]

ARCS = [
    {
        "slug": "heart-of-eternity", "arc_type": "main", "order": 0, "world": None,
        "title_en": "The Heart of Eternity", "title_ar": "قلب الأبدية",
        "summary_en": "The thread that connects every sovereign's story. Its full shape is not yet visible.",
        "summary_ar": "الخيط الذي يربط حكايات الحكّام جميعًا. لم يتّضح شكله الكامل بعد.",
        "characters": ["celestial-guide"],
        "chapters": [
            {"slug": "prologue", "order": 1, "type": "prologue",
             "title_en": "Every World Has a Memory", "title_ar": "لكل عالمٍ ذاكرة",
             "summary_en": "The Celestial Guide meets a traveller at the edge of the five worlds.",
             "summary_ar": "تلتقي مرشدة الكواكب بمسافرٍ عند حافة العوالم الخمسة.",
             "body_en": "The stars here do not twinkle. They wait.\n\n“You came,” says the woman in midnight blue, as though "
             "she has been expecting you for a very long time. “Five worlds are waiting too. Each one was saved once, by "
             "someone who paid more than they understood. Shall we go and see what they paid?”",
             "body_ar": "النجوم هنا لا تتلألأ، بل تنتظر.\n\n«لقد أتيت»، تقول المرأة ذات الثوب الأزرق كمنتصف الليل، كأنها تنتظرك منذ "
             "زمنٍ بعيد. «خمسة عوالم تنتظر هي الأخرى. أُنقذ كلٌّ منها مرة، على يد من دفع أكثر مما أدرك. أنمضي لنرى ما الذي دفعوه؟»"},
        ],
    },
    {
        "slug": "the-frozen-promise", "arc_type": "world", "order": 1, "world": "everfrost",
        "title_en": "The Frozen Promise", "title_ar": "الوعد المتجمّد",
        "summary_en": "In Crystalheim, a father's love became an endless winter.",
        "summary_ar": "في كريستالهايم، تحوّل حبّ أبٍ إلى شتاءٍ لا ينتهي.",
        "characters": ["zerath", "eilen"],
        "chapters": [
            {"slug": "the-city-that-stopped", "order": 1, "type": "chapter",
             "title_en": "The City That Stopped", "title_ar": "المدينة التي توقّفت",
             "summary_en": "The traveller enters Crystalheim and finds a celebration frozen mid-step.",
             "summary_ar": "يدخل المسافر كريستالهايم فيجد احتفالًا تجمّد في منتصف خطوته.",
             "body_en": "Lanterns hang over the square, still lit. A musician's bow rests against a string that will never "
             "finish its note. In a bakery window, bread has been waiting twelve hundred years to cool.\n\nThe people are "
             "gone. Their things are not. Toys lie where children dropped them; a letter on a desk stops at the word “tomorrow”.",
             "body_ar": "تتدلّى الفوانيس فوق الساحة وما زالت مضاءة. يستقرّ قوسُ موسيقيٍّ على وترٍ لن يُتمّ نغمته أبدًا. وفي واجهة مخبزٍ "
             "ينتظر الخبز منذ ألفٍ ومئتي عام أن يبرد.\n\nرحل الناس، أمّا أشياؤهم فباقية. الألعاب حيث أسقطها الأطفال، ورسالةٌ على مكتبٍ "
             "تتوقّف عند كلمة «غدًا»."},
            {"slug": "letters-under-ice", "order": 2, "type": "memory",
             "title_en": "Letters Under Ice", "title_ar": "رسائل تحت الجليد",
             "summary_en": "Hidden letters and drawings reveal that the emperor once had a daughter.",
             "summary_ar": "رسائل ورسومات مخبّأة تكشف أن الإمبراطور كانت له ابنةٌ يومًا.",
             "body_en": "The drawings are everywhere once you know to look: a crown drawn too large, a tall figure holding a "
             "small hand, a garden full of blue flowers. Each is signed in a careful child's script: E.",
             "body_ar": "الرسومات في كل مكان حين تعرف أين تنظر: تاجٌ رُسم أكبر من حجمه، وقامةٌ طويلة تمسك يدًا صغيرة، وحديقةٌ مليئة "
             "بالأزهار الزرقاء. وكلها موقّعة بخطّ طفلةٍ متأنٍّ: إ."},
            {"slug": "the-girl-in-the-crystal", "order": 3, "type": "boss_intro", "spoiler": True,
             "title_en": "The Girl in the Crystal", "title_ar": "الفتاة في البلّورة",
             "summary_en": "Beneath the throne, the traveller finds what the emperor has been protecting.",
             "summary_ar": "تحت العرش، يجد المسافر ما كان الإمبراطور يحميه.",
             "body_en": "She is nine years old. Her eyes are closed, her hand half-raised as if reaching for someone. Above "
             "her, the throne room trembles, and the emperor's voice fills the hall: “Step away from her.”",
             "body_ar": "إنها في التاسعة. عيناها مغمضتان، ويدها مرفوعةٌ إلى منتصفها كأنها تمتدّ إلى أحد. وفوقها ترتجف قاعة العرش، "
             "ويملأ صوتُ الإمبراطور القاعة: «ابتعد عنها.»"},
            {"slug": "the-crowns-grip", "order": 4, "type": "chapter", "spoiler": True, "graph": "everfrost_battle",
             "title_en": "The Crown's Grip", "title_ar": "قبضة التاج",
             "summary_en": "The battle with Zerath can only be won by breaking the crown's hold on him.",
             "summary_ar": "لا يمكن كسب المعركة مع زيراث إلا بكسر قبضة التاج عليه.",
             "body_en": "Every blow lands on ice that regrows. The emperor is not fighting to win. He is fighting so that "
             "nothing will ever change.",
             "body_ar": "كل ضربةٍ تقع على جليدٍ ينمو من جديد. لا يقاتل الإمبراطور لينتصر، بل يقاتل كي لا يتغيّر شيءٌ أبدًا."},
            {"slug": "spring-in-the-garden", "order": 5, "type": "post_boss", "spoiler": True, "ending": "canonical",
             "graph": "everfrost_garden",
             "title_en": "Spring in the Garden", "title_ar": "الربيع في الحديقة",
             "summary_en": "Everfrost thaws. A father and daughter say goodbye.",
             "summary_ar": "تذوب إيفرفروست، ويودّع أبٌ ابنته.",
             "body_en": "Water runs in the gutters of Crystalheim for the first time in twelve centuries. In the royal "
             "garden, a single blue flower opens.\n\nZerath kneels in the grass. He is fading; the crown took too much for "
             "him to stay. Eilen runs to him, and he holds her the way he meant to hold her on the night of the frost. "
             "Then both of them become light, and the light rises, and the garden is quiet.",
             "body_ar": "يجري الماء في قنوات كريستالهايم لأول مرةٍ منذ اثني عشر قرنًا. وفي الحديقة الملكية تتفتّح زهرةٌ زرقاء وحيدة.\n\n"
             "يجثو زيراث على العشب وهو يتلاشى؛ فقد أخذ التاج منه أكثر مما يسمح له بالبقاء. تركض إيلين إليه، فيضمّها كما أراد أن يضمّها "
             "ليلة الصقيع. ثم يصيران كلاهما نورًا، ويرتفع النور، وتسكن الحديقة.",
             "closing_line_en": "Some promises are not fulfilled in this life... but they find their way to the stars.",
             "closing_line_ar": "بعض الوعود لا تتحقق في هذه الحياة... لكنها تجد طريقها إلى النجوم."},
        ],
    },
    {
        "slug": "roots-that-remember", "arc_type": "world", "order": 2, "world": "verdant-realm",
        "title_en": "Roots That Remember", "title_ar": "جذورٌ تتذكّر",
        "summary_en": "The forest is not cruel. It is wounded, and so is its queen.",
        "summary_ar": "الغابة ليست قاسية، بل جريحة، وكذلك ملكتها.",
        "characters": ["vespera", "mother-of-roots"],
        "chapters": [
            {"slug": "the-hostile-forest", "order": 1, "type": "chapter",
             "title_en": "The Hostile Forest", "title_ar": "الغابة العدائية",
             "summary_en": "Infected roots and corrupted guardians bar the way to Eilorin.",
             "summary_ar": "جذورٌ عليلة وحرّاسٌ فاسدون يسدّون الطريق إلى إيلورين.",
             "body_en": "The flowers glow brighter the closer you come to the city, and the brightness is wrong, like a fever.",
             "body_ar": "تتوهّج الأزهار أكثر كلما اقتربت من المدينة، وهو توهّجٌ غير سويّ، كالحمّى."},
            {"slug": "the-queens-repair", "order": 2, "type": "epilogue", "spoiler": True,
             "title_en": "What the Queen Must Repair", "title_ar": "ما على الملكة إصلاحه",
             "summary_en": "Vespera begins the slow work of undoing the damage she caused. Deep below, something stirs.",
             "summary_ar": "تبدأ فيسبيرا العمل البطيء لإصلاح ما أفسدته. وفي الأعماق، يتحرّك شيء.",
             "body_en": "Nothing is restored in a single moment. The queen walks the ruined settlements herself, learning the "
             "names of the people she no longer remembers. Beneath her feet, a root pulses once, gently, as if in answer.",
             "body_ar": "لا يعود شيءٌ إلى سابق عهده في لحظةٍ واحدة. تجول الملكة بنفسها في القرى المهدّمة، تتعلّم أسماء أناسٍ لم تعد "
             "تذكرهم. وتحت قدميها ينبض جذرٌ مرةً واحدة، برفق، كأنه يجيب."},
        ],
    },
    {
        "slug": "the-brothers-storm", "arc_type": "world", "order": 3, "world": "solaris",
        "title_en": "The Brother's Storm", "title_ar": "عاصفة الأخ",
        "summary_en": "An emperor's mercy was taught to him by someone he can no longer remember.",
        "summary_ar": "رحمةُ الإمبراطور علّمه إياها شخصٌ لم يعد يتذكّره.",
        "characters": ["kaizen", "rayyan"],
        "chapters": [
            {"slug": "full-storehouses", "order": 1, "type": "chapter",
             "title_en": "Full Storehouses, Empty Villages", "title_ar": "مخازن ممتلئة، وقرى خاوية",
             "summary_en": "The emperor's reputation and the villages' hunger do not match.",
             "summary_ar": "سمعة الإمبراطور لا تتّفق مع جوع القرى.",
             "body_en": "In Azharan, they sing about the emperor who ended famine. Three days' walk south, nobody sings.",
             "body_ar": "في أزهران يتغنّون بالإمبراطور الذي أنهى المجاعة. وعلى مسيرة ثلاثة أيامٍ جنوبًا، لا يغنّي أحد."},
            {"slug": "the-toy-in-the-sand", "order": 2, "type": "memory", "spoiler": True,
             "title_en": "The Toy in the Sand", "title_ar": "اللعبة في الرمل",
             "summary_en": "A buried shelter, a ledger, and a name the emperor has forgotten.",
             "summary_ar": "ملجأٌ مدفون، وسجلّ، واسمٌ نسيه الإمبراطور.",
             "body_en": "Kaizen turns the little carved camel over and over. He does not know why his hands are shaking.",
             "body_ar": "يقلّب كايزن الجمل الصغير المنحوت مرةً بعد مرة، ولا يدري لماذا ترتجف يداه."},
        ],
    },
    {
        "slug": "the-unlisted", "arc_type": "world", "order": 4, "world": "nyxara",
        "title_en": "The Unlisted", "title_ar": "غير المُدرَجين",
        "summary_en": "In a city that sees everything, one person has been made invisible.",
        "summary_ar": "في مدينةٍ ترى كل شيء، جُعل شخصٌ واحد غير مرئي.",
        "characters": ["noxar", "lyssa"],
        "chapters": [
            {"slug": "perfect-safety", "order": 1, "type": "chapter",
             "title_en": "Perfect Safety", "title_ar": "الأمان التام",
             "summary_en": "Nova City's wonders, and the price its citizens pay without noticing.",
             "summary_ar": "عجائب مدينة نوفا، والثمن الذي يدفعه مواطنوها دون أن ينتبهوا.",
             "body_en": "Crime is zero. Accidents are zero. Unscheduled conversations are, according to the city's statistics, "
             "also nearly zero.",
             "body_ar": "الجريمة صفر. الحوادث صفر. والمحادثات غير المجدولة، بحسب إحصاءات المدينة، تكاد هي الأخرى تكون صفرًا."},
        ],
    },
    {
        "slug": "futures-in-glass", "arc_type": "world", "order": 5, "world": "astrion",
        "title_en": "Futures in Glass", "title_ar": "مستقبلاتٌ في الزجاج",
        "summary_en": "To free Astrion, the traveller must decide whether an uncertain future is worth the risk.",
        "summary_ar": "لتحرير أستريون، على المسافر أن يقرّر هل يستحق المستقبلُ المجهول المخاطرة.",
        "characters": ["asteria"],
        "chapters": [
            {"slug": "the-repeating-year", "order": 1, "type": "chapter",
             "title_en": "The Repeating Year", "title_ar": "العام المتكرّر",
             "summary_en": "Celestara lives the same safe year again and again.",
             "summary_ar": "تعيش سيليستارا العام الآمن نفسه مرةً بعد مرة.",
             "body_en": "The astronomers have catalogued the same comet four thousand times. Each time, they call it a discovery.",
             "body_ar": "فهرس الفلكيون المذنّب نفسه أربعة آلاف مرة، وفي كل مرةٍ يسمّونه اكتشافًا."},
        ],
    },
    {
        "slug": "the-hollow-crown", "arc_type": "secret", "order": 6, "world": "umbra", "visibility": "hidden",
        "title_en": "The Hollow Crown", "title_ar": "التاج الأجوف",
        "summary_en": "The secret path toward an ending in which all six worlds survive.",
        "summary_ar": "الطريق السرّي نحو نهايةٍ تنجو فيها العوالم الستة جميعًا.",
        "characters": ["hollow-king"],
        "chapters": [
            {"slug": "the-gate-that-waits", "order": 1, "type": "alt_ending", "ending": "hidden", "spoiler": True,
             "title_en": "The Gate That Waits", "title_ar": "البوابة التي تنتظر",
             "summary_en": "A hidden ending, reachable only after every world's truth is recovered.",
             "summary_ar": "نهايةٌ خفية، لا تُبلَغ إلا بعد استعادة حقيقة كل عالم.",
             "body_en": "Rather than sacrificing one world to save the others, the traveller returns a single memory to the "
             "Hollow King: the face of the one who waited.",
             "body_ar": "بدل التضحية بعالمٍ لإنقاذ البقية، يعيد المسافر إلى الملك الأجوف ذكرى واحدة: وجه من انتظر."},
        ],
    },
]

# Story graphs (structured nodes + branches) for chapters that declare "graph".
GRAPHS = {
    "everfrost_battle": {
        "nodes": [
            ("approach", "narration", True, "", "The frozen court", "البلاط المتجمّد",
             "Zerath rises from the throne. Frost spreads from the crown across the floor toward the crystal.",
             "ينهض زيراث عن العرش. يمتدّ الصقيع من التاج عبر الأرض نحو البلّورة.", None),
            ("decision", "choice", False, "", "What do you strike?", "ماذا تضرب؟",
             "The emperor stands between you and the crystal. The crown pulses with cold light.",
             "يقف الإمبراطور بينك وبين البلّورة، والتاج ينبض بضوءٍ بارد.", None),
            ("blade-to-blade", "narration", False, "", "Blade to blade", "نصلٌ لنصل",
             "Every wound you open freezes shut. The crown is feeding on the fight.",
             "كل جرحٍ تفتحه يتجمّد ويلتئم. التاج يتغذّى على القتال.", None),
            ("endless-winter", "ending", False, "failure", "Endless winter", "شتاءٌ بلا نهاية",
             "You fall. Above you, the snow stops falling again.", "تسقط. وفوقك يتوقّف الثلج عن الهطول من جديد.", None),
            ("eilens-voice", "dialogue", False, "", "A voice in the ice", "صوتٌ في الجليد",
             "You press the letter against the crystal. Inside, a small hand moves.",
             "تضع الرسالة على البلّورة. وفي داخلها تتحرّك يدٌ صغيرة.", "eilen"),
            ("he-remembers", "ending", False, "canonical", "He remembers", "إنه يتذكّر",
             "The crown cracks. Zerath stops, and for the first time in twelve centuries he says her name.",
             "يتصدّع التاج. يتوقّف زيراث، ولأول مرةٍ منذ اثني عشر قرنًا ينطق اسمها.", "zerath"),
        ],
        "branches": [
            ("approach", "decision", "", "", {}, []),
            ("decision", "blade-to-blade", "Fight the emperor", "قاتل الإمبراطور", {}, [{"choice": "zerath_battle", "value": "fight"}]),
            ("decision", "eilens-voice", "Reach for the crystal", "امدد يدك إلى البلّورة",
             {"lore": "eilens-last-letter"}, [{"choice": "zerath_battle", "value": "crystal"}]),
            ("blade-to-blade", "endless-winter", "", "", {}, []),
            ("eilens-voice", "he-remembers", "", "", {}, [{"flag": "crown_broken", "value": True}]),
        ],
    },
    "everfrost_garden": {
        "nodes": [
            ("thaw", "narration", True, "", "The thaw", "الذوبان",
             "Water runs through Crystalheim. In the garden, a blue flower opens.",
             "يجري الماء في كريستالهايم. وفي الحديقة تتفتّح زهرةٌ زرقاء.", None),
            ("farewell", "dialogue", False, "", "Farewell", "الوداع",
             "“I remember now. I remember all of it.”", "«أتذكّر الآن. أتذكّر كل شيء.»", "zerath"),
            ("to-the-stars", "ending", False, "canonical", "To the stars", "إلى النجوم",
             "Father and daughter become light and rise together.", "يصير الأب وابنته نورًا ويرتفعان معًا.", None),
        ],
        "branches": [
            ("thaw", "farewell", "", "", {}, []),
            ("farewell", "to-the-stars", "", "", {}, []),
        ],
    },
}

QUESTS = [
    {"slug": "the-silent-festival", "type": "exploration", "world": "everfrost", "order": 1, "giver": "celestial-guide",
     "title_en": "The Silent Festival", "title_ar": "المهرجان الصامت",
     "summary_en": "Walk the frozen streets of Crystalheim and learn what happened on the last night of the festival.",
     "summary_ar": "تجوّل في شوارع كريستالهايم المتجمدة واعرف ما جرى في الليلة الأخيرة من المهرجان.",
     "objectives": [("reach-square", "reach", "Reach the festival square", "بلوغ ساحة المهرجان", 1, False),
                    ("frozen-toys", "collect", "Find the abandoned toys", "العثور على الألعاب المهجورة", 5, True),
                    ("unfinished-letter", "discover", "Read the unfinished letter", "قراءة الرسالة غير المكتملة", 1, False)],
     "rewards": [("lore", None, "the-long-winter", "Unlocks the record of the Long Winter.", "يكشف سجلّ الشتاء الطويل.")]},
    {"slug": "letters-to-a-daughter", "type": "memory", "world": "everfrost", "order": 2, "giver": None,
     "requires": ["the-silent-festival"],
     "title_en": "Letters to a Daughter", "title_ar": "رسائل إلى ابنة",
     "summary_en": "Collect the drawings and letters hidden throughout the palace.",
     "summary_ar": "اجمع الرسومات والرسائل المخبّأة في أرجاء القصر.",
     "objectives": [("drawings", "collect", "Collect Eilen's drawings", "جمع رسومات إيلين", 7, False),
                    ("last-letter", "discover", "Find the last letter", "العثور على الرسالة الأخيرة", 1, False)],
     "rewards": [("lore", None, "eilens-last-letter", "Eilen's last letter.", "رسالة إيلين الأخيرة.")]},
    {"slug": "shatter-the-crown", "type": "boss", "world": "everfrost", "order": 3, "giver": None,
     "requires": ["letters-to-a-daughter"],
     "title_en": "Shatter the Crown", "title_ar": "حطّم التاج",
     "summary_en": "Confront the Ice Emperor beneath the throne.",
     "summary_ar": "واجه إمبراطور الجليد تحت العرش.",
     "completion": {"flag": "crown_broken", "equals": True},
     "objectives": [("confront-zerath", "defeat", "Break the crown's hold on Zerath", "كسر قبضة التاج على زيراث", 1, False)],
     "rewards": [("item", "blue-winter-flower", None, "The Blue Winter Flower.", "زهرة الشتاء الزرقاء.")]},
    {"slug": "spring-returns", "type": "restoration", "world": "everfrost", "order": 4, "giver": "eilen",
     "requires": ["shatter-the-crown"],
     "title_en": "Spring Returns", "title_ar": "عودة الربيع",
     "summary_en": "Help the people of Everfrost return to a kingdom that has finally thawed.",
     "summary_ar": "ساعد أهل إيفرفروست على العودة إلى مملكةٍ ذابت أخيرًا.",
     "objectives": [("plant-flowers", "custom", "Plant blue flowers in the royal garden", "زراعة الأزهار الزرقاء في الحديقة الملكية", 3, False)],
     "rewards": [("title", None, None, "Title: Herald of Spring.", "لقب: بشير الربيع.")]},
    {"slug": "the-infected-roots", "type": "investigation", "world": "verdant-realm", "order": 1, "giver": "celestial-guide",
     "title_en": "The Infected Roots", "title_ar": "الجذور العليلة",
     "summary_en": "Trace the corruption spreading through the roots back to its source.",
     "summary_ar": "تتبّع الفساد المنتشر في الجذور حتى منبعه.",
     "objectives": [("samples", "collect", "Gather glowing root samples", "جمع عيّنات من الجذور المتوهّجة", 4, False),
                    ("keeper-record", "discover", "Find the shrine-keeper's record", "العثور على سجلّ سادن المزار", 1, False)],
     "rewards": [("lore", None, "mother-of-roots", "The record of the bond.", "سجلّ الرابطة.")]},
    {"slug": "the-shelter-in-the-dunes", "type": "character", "world": "solaris", "order": 1, "giver": None,
     "title_en": "The Shelter in the Dunes", "title_ar": "الملجأ في الكثبان",
     "summary_en": "Search the storm regions for a shelter missing from every royal map.",
     "summary_ar": "ابحث في مناطق العواصف عن ملجأٍ غائبٍ عن كل الخرائط الملكية.",
     "objectives": [("find-shelter", "reach", "Find the forgotten shelter", "العثور على الملجأ المنسي", 1, False),
                    ("the-toy", "collect", "Recover the carved toy", "استعادة اللعبة المنحوتة", 1, False)],
     "rewards": [("item", "rayyans-toy", None, "Rayyan's toy.", "لعبة ريّان."),
                 ("lore", None, "azharan-shelter-ledger", "The shelter ledger.", "سجلّ الملجأ.")]},
    {"slug": "unlisted-citizens", "type": "investigation", "world": "nyxara", "order": 1, "giver": None,
     "title_en": "Unlisted Citizens", "title_ar": "مواطنون غير مُدرَجين",
     "summary_en": "Find out why one message in Nova City can never be deleted.",
     "summary_ar": "اكتشف لماذا لا يمكن حذف رسالةٍ واحدة في مدينة نوفا.",
     "objectives": [("archive-access", "reach", "Enter the restricted archive", "دخول الأرشيف المحظور", 1, False),
                    ("choose-disclosure", "choose", "Decide who may read the message", "تقرير من يحقّ له قراءة الرسالة", 1, False)],
     "rewards": [("lore", None, "archived-message-001", "Archived message 0-0-1.", "الرسالة المؤرشفة 0-0-1.")]},
    {"slug": "futures-in-glass", "type": "investigation", "world": "astrion", "order": 1, "giver": None,
     "title_en": "Futures in Glass", "title_ar": "مستقبلاتٌ في الزجاج",
     "summary_en": "Compare the observatory's records of the prophecy and find the word the empress misread.",
     "summary_ar": "قارن سجلات المرصد للنبوءة وجد الكلمة التي أساءت الإمبراطورة قراءتها.",
     "objectives": [("prophecy-copies", "collect", "Collect copies of the prophecy", "جمع نسخ النبوءة", 3, False)],
     "rewards": [("lore", None, "eclipse-prophecy", "The Eclipse Prophecy.", "نبوءة الكسوف.")]},
    {"slug": "the-gate-that-waits", "type": "hidden", "world": "umbra", "order": 1, "giver": None, "visibility": "hidden",
     "requires": ["spring-returns"],
     "title_en": "The Gate That Waits", "title_ar": "البوابة التي تنتظر",
     "summary_en": "Hidden questline toward the ending in which all six worlds survive.",
     "summary_ar": "سلسلة مهامٍ خفية نحو النهاية التي تنجو فيها العوالم الستة.",
     "start": {"all": [{"quest": "spring-returns", "state": "completed"}, {"lore": "the-gatekeepers-vigil"}]},
     "objectives": [("recover-memory", "custom", "Recover the memory of the one who waited", "استعادة ذكرى من انتظر", 1, False)],
     "rewards": []},
]

DIALOGUE = [
    # Celestial Guide (website lines, rule-based)
    {"key": "guide-home-greeting", "guide": True, "category": "greeting", "page": "home", "priority": 10, "emotion": "warm",
     "en": "Welcome, traveller. Five worlds are waiting for you, and each of them is hiding something from you.",
     "ar": "مرحبًا بك أيها المسافر. خمسة عوالم في انتظارك، وكلٌّ منها يخفي عنك شيئًا."},
    {"key": "guide-home-heart", "guide": True, "category": "hint", "page": "home", "priority": 5, "emotion": "mysterious",
     "en": "Every miracle in these worlds drew on the Heart of Eternity. Ask yourself what each one cost.",
     "ar": "كل معجزةٍ في هذه العوالم استمدّت من قلب الأبدية. اسأل نفسك: ما الذي كلّفته كلٌّ منها؟"},
    {"key": "guide-home-sixth", "guide": True, "category": "secret", "page": "home", "priority": 1, "emotion": "mysterious",
     "en": "Five worlds, they say. Count the stars again sometime.",
     "ar": "خمسة عوالم، هكذا يقولون. أعد عدّ النجوم يومًا ما."},
    {"key": "guide-worlds-intro", "guide": True, "category": "exploration", "page": "worlds", "priority": 5,
     "en": "Choose any world. They are all connected, and you will understand each one better after seeing the others.",
     "ar": "اختر أي عالم. كلها مترابطة، وستفهم كلًّا منها أفضل بعد أن ترى البقية."},
    {"key": "guide-world-everfrost", "guide": True, "category": "world_intro", "page": "world", "world": "everfrost", "priority": 8, "emotion": "sorrowful",
     "en": "Everfrost. Listen: no wind, no footsteps. Even the snow is holding its breath. Look for the drawings.",
     "ar": "إيفرفروست. أنصت: لا ريح ولا وقع أقدام. حتى الثلج يحبس أنفاسه. ابحث عن الرسومات."},
    {"key": "guide-world-verdant", "guide": True, "category": "world_intro", "page": "world", "world": "verdant-realm", "priority": 8,
     "en": "The forest is beautiful and it is in pain. Try not to confuse the two.",
     "ar": "الغابة جميلة، وهي تتألّم. حاول ألّا تخلط بين الأمرين."},
    {"key": "guide-world-solaris", "guide": True, "category": "world_intro", "page": "world", "world": "solaris", "priority": 8,
     "en": "In Azharan they will tell you famine ended. Walk south before you believe them.",
     "ar": "سيخبرونك في أزهران أن المجاعة انتهت. سِر جنوبًا قبل أن تصدّقهم."},
    {"key": "guide-world-nyxara", "guide": True, "category": "world_intro", "page": "world", "world": "nyxara", "priority": 8, "emotion": "cold",
     "en": "Nova City sees you already. Notice what it chooses not to look at.",
     "ar": "مدينة نوفا تراك بالفعل. انتبه إلى ما تختار ألّا تنظر إليه."},
    {"key": "guide-world-astrion", "guide": True, "category": "world_intro", "page": "world", "world": "astrion", "priority": 8,
     "en": "Celestara has seen this year before. So, perhaps, have you.",
     "ar": "رأت سيليستارا هذا العام من قبل. وربما رأيته أنت أيضًا."},
    {"key": "guide-characters", "guide": True, "category": "hint", "page": "characters", "priority": 5,
     "en": "Don't judge the sovereigns by what they rule. Judge them by what they lost.",
     "ar": "لا تحكم على الحكّام بما يحكمونه، بل بما فقدوه."},
    {"key": "guide-character", "guide": True, "category": "hint", "page": "character", "priority": 3,
     "en": "Every bond on this page was once a promise. Some of them were broken by forgetting.",
     "ar": "كل رابطةٍ في هذه الصفحة كانت يومًا وعدًا، وبعضها انكسر بالنسيان."},
    {"key": "guide-story", "guide": True, "category": "hint", "page": "story", "priority": 5,
     "en": "Read slowly. The turning points are marked, and I won't spoil them for you.",
     "ar": "اقرأ على مهل. نقاط التحوّل معلَّمة، ولن أفسدها عليك."},
    {"key": "guide-lore", "guide": True, "category": "hint", "page": "lore", "priority": 5, "emotion": "mysterious",
     "en": "Some of these records contradict each other. That is not a mistake.",
     "ar": "بعض هذه السجلات يناقض بعضًا، وليس ذلك خطأً."},
    {"key": "guide-news", "guide": True, "category": "greeting", "page": "news", "priority": 5,
     "en": "News from the people building these worlds. I read every update.",
     "ar": "أخبارٌ من صانعي هذه العوالم. أقرأ كل تحديث."},
    # Character dialogue (game content)
    {"key": "zerath-boss-intro", "speaker": "zerath", "category": "boss_intro", "world": "everfrost", "quest": "shatter-the-crown",
     "emotion": "cold", "trigger": "boss_start:zerath",
     "en": "You have walked through my city and touched nothing. Do the same here, and you may leave.",
     "ar": "عبرتَ مدينتي ولم تمسّ شيئًا. افعل الشيء نفسه هنا، ولك أن ترحل.",
     "choices": [("I came for her.", "جئتُ من أجلها.", "zerath-why"), ("Who is she?", "من تكون؟", "zerath-why")]},
    {"key": "zerath-why", "speaker": "zerath", "category": "revelation", "world": "everfrost", "emotion": "desperate",
     "en": "She is... she is the reason. I do not remember the reason. Step away from her.",
     "ar": "إنها... إنها السبب. لا أذكر السبب. ابتعد عنها."},
    {"key": "zerath-phase-two", "speaker": "zerath", "category": "combat_phase", "world": "everfrost", "emotion": "angry",
     "trigger": "boss_phase:zerath:2",
     "en": "Nothing else will be taken from me. Nothing!", "ar": "لن يُؤخذ مني شيءٌ آخر. لا شيء!"},
    {"key": "eilen-voice", "speaker": "eilen", "category": "memory", "world": "everfrost", "emotion": "warm",
     "trigger": "boss_phase:zerath:3",
     "en": "Father, the flowers. You promised you'd plant the blue flowers.",
     "ar": "أبي، الأزهار. وعدتني أن تزرع الأزهار الزرقاء."},
    {"key": "zerath-remembers", "speaker": "zerath", "category": "ending", "world": "everfrost", "emotion": "sorrowful",
     "en": "Eilen. I remember now. I remember all of it.", "ar": "إيلين. أتذكّر الآن. أتذكّر كل شيء."},
    {"key": "vespera-warning", "speaker": "vespera", "category": "warning", "world": "verdant-realm", "emotion": "cold",
     "en": "Turn back. The forest does not forgive trespass, and neither do I.",
     "ar": "عُد أدراجك. الغابة لا تغفر التعدّي، ولا أنا."},
    {"key": "kaizen-greeting", "speaker": "kaizen", "category": "greeting", "world": "solaris", "emotion": "warm",
     "en": "No one in my empire goes hungry. Ask anyone in Azharan.",
     "ar": "لا يجوع أحدٌ في إمبراطوريتي. اسأل أيّ أحدٍ في أزهران."},
    {"key": "noxar-greeting", "speaker": "noxar", "category": "greeting", "world": "nyxara", "emotion": "neutral",
     "en": "You entered the city four minutes ago. Your heart rate is elevated. Relax. You are safe here.",
     "ar": "دخلتَ المدينة منذ أربع دقائق. نبضك مرتفع. استرخِ، فأنت آمنٌ هنا."},
    {"key": "asteria-warning", "speaker": "asteria", "category": "warning", "world": "astrion", "emotion": "fearful",
     "en": "I have watched this world end eleven thousand ways. Do not ask me to let it try a twelve-thousandth.",
     "ar": "شاهدتُ هذا العالم ينتهي بأحد عشر ألف طريقة. لا تطلب مني أن أدعه يجرّب الطريقة الثانية عشرة ألفًا."},
    {"key": "hollow-king-whisper", "speaker": "hollow-king", "category": "secret", "world": "umbra", "emotion": "mysterious",
     "status": "draft",
     "en": "Did they send you? No... no one sends anyone here anymore.",
     "ar": "هل أرسلوك؟ لا... لم يعد أحدٌ يُرسل أحدًا إلى هنا."},
]

BOSS = {
    "slug": "zerath-the-ice-emperor", "boss": "zerath", "world": "everfrost", "arena": "crystal-throne",
    "quest": "shatter-the-crown",
    "title_en": "Zerath, the Ice Emperor", "title_ar": "زيراث، إمبراطور الجليد",
    "narrative_purpose_en": "The player cannot win by force alone: the battle is about breaking the crown's influence "
    "so that Zerath can remember his daughter.",
    "narrative_purpose_ar": "لا يمكن للاعب أن ينتصر بالقوة وحدها؛ فالمعركة تدور حول كسر تأثير التاج كي يتذكّر زيراث ابنته.",
    "health_bar_label_en": "Zerath, the Ice Emperor", "health_bar_label_ar": "زيراث، إمبراطور الجليد",
    "segments": 3, "color": "#9FE4FF",
    "environmental_changes": "Throne hall freezes progressively; in the final phase cracks of warm light appear in the ice.",
    "victory_en": "Disrupt the crown three times using Eilen's crystal while surviving the emperor's attacks.",
    "victory_ar": "زعزِع التاج ثلاث مرات مستعينًا ببلّورة إيلين، مع النجاة من هجمات الإمبراطور.",
    "defeat_en": "The player falls, or the frost reaches the crystal.",
    "defeat_ar": "يسقط اللاعب، أو يبلغ الصقيع البلّورة.",
    "phases": [
        (1, "The Frozen Court", "البلاط المتجمّد", 100, "Zerath fights with precise, courtly attacks.", "يقاتل زيراث بضرباتٍ دقيقة مهيبة.", "zerath-boss-intro"),
        (2, "Crown Ascendant", "صعود التاج", 60, "The crown takes control; frost spreads toward the crystal.", "يتولّى التاج السيطرة، ويمتدّ الصقيع نحو البلّورة.", "zerath-phase-two"),
        (3, "The Memory Breaks", "انكسار الذاكرة", 25, "Eilen's voice disrupts the crown. Strike the crown, not the man.", "يزعزع صوت إيلين التاج. اضرب التاج لا الرجل.", "eilen-voice"),
    ],
}

CINEMATICS = [
    {"slug": "the-girl-in-the-crystal", "chapter": "the-girl-in-the-crystal", "characters": ["zerath", "eilen"],
     "title_en": "The Girl in the Crystal", "title_ar": "الفتاة في البلّورة", "duration": 95,
     "unreal": "/Game/Cinematics/Everfrost/LS_GirlInTheCrystal",
     "summary_en": "Boss introduction beneath the throne.", "summary_ar": "تمهيدٌ للمواجهة تحت العرش.",
     "scenes": [
         (1, "Descent", "النزول", "Slow descent through the ice beneath the throne; a faint light grows.", "نزولٌ بطيء عبر الجليد تحت العرش، وضوءٌ خافت يتّسع.", "Long crane down, shallow depth of field.", None),
         (2, "The crystal", "البلّورة", "Eilen inside the crystal, her hand half-raised.", "إيلين داخل البلّورة ويدها مرفوعةٌ إلى منتصفها.", "Slow push-in, cold rim light.", None),
         (3, "The emperor", "الإمبراطور", "Zerath descends. Frost spreads beneath his feet.", "ينزل زيراث، ويمتدّ الصقيع تحت قدميه.", "Low angle, crown silhouetted.", "zerath-boss-intro"),
     ]},
    {"slug": "the-final-garden", "chapter": "spring-in-the-garden", "characters": ["zerath", "eilen"],
     "title_en": "The Final Garden", "title_ar": "الحديقة الأخيرة", "duration": 140,
     "unreal": "/Game/Cinematics/Everfrost/LS_FinalGarden",
     "summary_en": "Spring returns; father and daughter depart as light.", "summary_ar": "يعود الربيع، ويرحل الأب وابنته نورًا.",
     "scenes": [
         (1, "The flower", "الزهرة", "A blue flower opens in melting snow.", "زهرةٌ زرقاء تتفتّح في الثلج الذائب.", "Macro shot, warm light entering frame.", None),
         (2, "The embrace", "العناق", "Zerath kneels; Eilen runs to him.", "يجثو زيراث وتركض إيلين إليه.", "Handheld, intimate framing.", "zerath-remembers"),
         (3, "To the stars", "إلى النجوم", "Both become light and rise. Final phrase appears.", "يصيران نورًا ويرتفعان، وتظهر العبارة الأخيرة.", "Tilt up into the sky; hold on stars.", None),
     ]},
]

GLOSSARY = [
    ("ASTRAVIA", "أسترافيا", "place"), ("Everfrost", "إيفرفروست", "place"), ("Verdant Realm", "المملكة الخضراء", "place"),
    ("Solaris", "سولاريس", "place"), ("Nyxara", "نيكسارا", "place"), ("Astrion", "أستريون", "place"), ("Umbra", "أمبرا", "place"),
    ("Crystalheim", "كريستالهايم", "place"), ("Eilorin", "إيلورين", "place"), ("Azharan", "أزهران", "place"),
    ("Nova City", "مدينة نوفا", "place"), ("Celestara", "سيليستارا", "place"),
    ("Zerath", "زيراث", "person"), ("Eilen", "إيلين", "person"), ("Vespera", "فيسبيرا", "person"), ("Kaizen", "كايزن", "person"),
    ("Noxar", "نوكسار", "person"), ("Asteria", "أستيريا", "person"), ("The Hollow King", "الملك الأجوف", "person"),
    ("Celestial Guide", "مرشدة الكواكب", "person"), ("Rayyan", "ريّان", "person"), ("Lyssa", "ليسا", "person"),
    ("Heart of Eternity", "قلب الأبدية", "concept"), ("Mother of Roots", "أمّ الجذور", "concept"),
    ("Eclipse Crown", "تاج الكسوف", "concept"), ("Sovereign", "حاكم", "title"),
]

ANNOUNCEMENTS = [
    {"slug": "astravia-enters-pre-production", "category": "news", "pinned": True,
     "title_en": "ASTRAVIA enters pre-production", "title_ar": "أسترافيا تدخل مرحلة ما قبل الإنتاج",
     "summary_en": "The universe, its six worlds and their rulers now exist as a living content foundation.",
     "summary_ar": "الكون وعوالمه الستة وحكّامها صارت الآن أساسًا حيًّا للمحتوى.",
     "body_en": "ASTRAVIA is a cosmic fantasy action RPG in pre-production. This website is its first public piece: the "
     "worlds, sovereigns and stories you see here are managed in the same content platform that will later feed the "
     "game itself.\n\nThere is no playable build yet, and no online services. We'll say so clearly when that changes.",
     "body_ar": "أسترافيا لعبة تقمّص أدوار حركية من عالم الفانتازيا الكونية، وهي في مرحلة ما قبل الإنتاج. هذا الموقع أول ما يُعرض منها "
     "للجمهور؛ فالعوالم والحكّام والحكايات التي تراها هنا تُدار في منصة المحتوى نفسها التي ستغذّي اللعبة لاحقًا.\n\nلا توجد نسخةٌ قابلة "
     "للعب بعد، ولا خدماتٌ عبر الإنترنت. وسنعلن ذلك بوضوح حين يتغيّر."},
    {"slug": "creator-studio-online", "category": "devlog", "pinned": False,
     "title_en": "Development update: the Creator Studio", "title_ar": "تحديث التطوير: استوديو الإنشاء",
     "summary_en": "Worlds, characters, quests and dialogue are now authored in a dedicated studio.",
     "summary_ar": "صارت العوالم والشخصيات والمهام والحوارات تُكتب في استوديو مخصّص.",
     "body_en": "Every world, sovereign, quest and line of dialogue on this site is a database record written in both "
     "English and Arabic. The studio tracks revisions, missing translations and publication state, and exposes approved "
     "content through a versioned API designed for the future Unreal Engine 5 client.",
     "body_ar": "كل عالمٍ وحاكمٍ ومهمةٍ وسطر حوارٍ في هذا الموقع سجلٌّ في قاعدة البيانات مكتوبٌ بالإنجليزية والعربية. يتتبّع الاستوديو "
     "المراجعات والترجمات الناقصة وحالة النشر، ويتيح المحتوى المعتمد عبر واجهةٍ برمجية ذات إصدارات صُمّمت لعميل Unreal Engine 5 المستقبلي."},
]

PAGES = [
    {"slug": "privacy", "order": 1, "title_en": "Privacy policy", "title_ar": "سياسة الخصوصية",
     "body_en": "This website can be used without an account.\n\nWhat we store if you create an account: your email "
     "address, a securely hashed password (never the password itself), your display name, language preference and "
     "privacy settings. If you subscribe to updates, we store your email and language.\n\nCookies: a session cookie keeps "
     "you signed in, a CSRF cookie protects forms, and a language cookie remembers your language. We do not use "
     "advertising or third-party tracking cookies.\n\nYou can request deletion of your account at any time from your "
     "account page. Questions: use the contact address in the footer.\n\nThe studio should review this policy with "
     "qualified counsel before public launch.",
     "body_ar": "يمكن استخدام هذا الموقع دون حساب.\n\nما نحفظه إن أنشأت حسابًا: بريدك الإلكتروني، وكلمة مرورٍ مُعمّاة بأمان (لا كلمة "
     "المرور نفسها)، واسمك الظاهر، وتفضيل اللغة، وإعدادات الخصوصية. وإن اشتركت في التحديثات نحفظ بريدك ولغتك.\n\nملفات تعريف "
     "الارتباط: ملف الجلسة يُبقيك مسجّلًا، وملف CSRF يحمي النماذج، وملف اللغة يتذكّر لغتك. لا نستخدم ملفات إعلانية أو ملفات تتبّع "
     "من جهاتٍ خارجية.\n\nيمكنك طلب حذف حسابك في أي وقت من صفحة حسابك. وللاستفسار استخدم عنوان التواصل في التذييل.\n\nينبغي "
     "للاستوديو مراجعة هذه السياسة مع مختصٍّ قانوني قبل الإطلاق العام."},
    {"slug": "terms", "order": 2, "title_en": "Terms of use", "title_ar": "شروط الاستخدام",
     "body_en": "ASTRAVIA, its worlds, characters, stories and artwork are the property of their creators. You may share "
     "links and short excerpts with attribution. Do not use the site to attack, overload or probe its systems, and do not "
     "attempt to access the Creator Studio without permission.\n\nASTRAVIA is in pre-production: features described on "
     "this site are planned and may change.",
     "body_ar": "أسترافيا وعوالمها وشخصياتها وحكاياتها وأعمالها الفنية ملكٌ لصانعيها. يجوز لك مشاركة الروابط ومقتطفاتٍ قصيرة مع ذكر "
     "المصدر. لا تستخدم الموقع لمهاجمة أنظمته أو إثقالها أو فحصها، ولا تحاول الدخول إلى استوديو الإنشاء دون إذن.\n\nأسترافيا في "
     "مرحلة ما قبل الإنتاج، والميزات الموصوفة في هذا الموقع مخطّط لها وقد تتغيّر."},
    {"slug": "cookies", "order": 3, "title_en": "Cookies", "title_ar": "ملفات تعريف الارتباط",
     "body_en": "We only set cookies the site needs to work: session (keeps you signed in), csrftoken (protects forms) and "
     "astravia_lang (remembers your language). Because none of them are used for tracking or advertising, there is "
     "nothing to opt out of. Clearing your browser cookies removes them.",
     "body_ar": "لا نضع إلا الملفات التي يحتاجها الموقع ليعمل: ملف الجلسة (يُبقيك مسجّلًا)، وcsrftoken (يحمي النماذج)، "
     "وastravia_lang (يتذكّر لغتك). ولأن أيًّا منها لا يُستخدم للتتبّع أو الإعلان، فلا شيء لإلغاء الاشتراك فيه. ويزيلها مسح "
     "ملفات تعريف الارتباط من متصفّحك."},
]
