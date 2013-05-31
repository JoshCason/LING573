#!/opt/python-2.7/bin/python2.7
# -*- coding: utf-8 -*-
# LING 573 - Spring 2013 - QA Project
#
# Class to apply filters/weighting to web search results
#
# @author Anthony Gentile <agentile@uw.edu>
import sys, os, re
from operator import itemgetter

class qa_filters:
    # all results start with a weight of 1.0
    def __init__(self, results, set_initial = 1):
        if set_initial:
            for r in results:
                r['weight'] = 1.0
        self.results = results
        
    # weigh the results based on their rank returned from search engine
    # from a 1.0 - 0.1 scale, so that the top ranked get 1.0 and the bottom gets 0.1
    def weigh_index_position(self):
        size = len(self.results)
        
        if size == 0:
            return self
            
        step = 0.9 / size
        position = 1
        for r in self.results:
            r['weight'] = r['weight'] - (step * (position - 1))
            r['rank'] = position
            position += 1
            
        return self
        
    # weight based on location regex matching
    def weigh_location_context(self):
        patterns = [
            '(mississippi|wyoming|minnesota|illinois|indiana|louisiana|texas|kansas|connecticut|montana|west virginia|alaska|missouri|south dakota|new jersey|washington|maryland|arizona|iowa|michigan|oregon|massachusetts|florida|ohio|rhode island|north carolina|maine|oklahoma|delaware|arkansas|new mexico|california|georgia|north dakota|pennsylvania|colorado|new york|nevada|idaho|utah|virginia|district of columbia|new hampshire|south carolina|vermont|hawaii|kentucky|nebraska|wisconsin|alabama|tennessee)',
            '(africa|north america|south america|antarctica|europe|asia|australia)',
            '(AFGHANISTAN|ALBANIA|ALGERIA|AMERICAN SAMOA|ANDORRA|ANGOLA|ANGUILLA|ANTARCTICA|ANTIGUA AND BARBUDA|ARGENTINA|ARMENIA|ARUBA|AUSTRALIA|AUSTRIA|AZERBAIJAN|BAHAMAS|BAHRAIN|BANGLADESH|BARBADOS|BELARUS|BELGIUM|BELIZE|BENIN|BERMUDA|BHUTAN|BOLIVIA|BONAIRE|BOSNIA|BOTSWANA|BOUVET ISLAND|BRAZIL|BULGARIA|BURUNDI|CAMBODIA|CAMEROON|CANADA|CAPE VERDE|CAYMAN ISLANDS|CENTRAL AFRICAN REPUBLIC|CHAD|CHILE|CHINA|CHRISTMAS ISLAND|COLOMBIA|COMOROS|CONGO|COOK ISLANDS|COSTA RICA|CROATIA|CUBA|CYPRUS|CZECH REPUBLIC|DENMARK|DJIBOUTI|DOMINICA|DOMINICAN REPUBLIC|ECUADOR|EGYPT|EL SALVADOR|EQUATORIAL GUINEA|ERITREA|ESTONIA|ETHIOPIA|FALKLAND ISLANDS|FAROE ISLANDS|FIJI|FINLAND|FRANCE|FRENCH GUIANA|FRENCH POLYNESIA|FRENCH SOUTHERN TERRITORIES|GABON|GAMBIA|GEORGIA|GERMANY|GHANA|GIBRALTAR|GREECE|GREENLAND|GRENADA|GUADELOUPE|GUAM|GUATEMALA|GUERNSEY|GUINEA|GUINEA-BISSAU|GUYANA|HAITI|HONDURAS|HONG KONG|HUNGARY|ICELAND|INDIA|INDONESIA|IRAN|IRAQ|IRELAND|ISRAEL|ITALY|JAMAICA|JAPAN|JERSEY|JORDAN|KAZAKHSTAN|KENYA|KIRIBATI|KOREA|KUWAIT|KYRGYZSTAN|LATVIA|LEBANON|LESOTHO|LIBERIA|LIBYA|LIECHTENSTEIN|LITHUANIA|LUXEMBOURG|MACAO|MACEDONIA|MADAGASCAR|MALAWI|MALAYSIA|MALDIVES|MALI|MALTA|MARSHALL ISLANDS|MARTINIQUE|MAURITANIA|MAURITIUS|MAYOTTE|MEXICO|MICRONESIA|MOLDOVA|MONACO|MONGOLIA|MONTENEGRO|MONTSERRAT|MOROCCO|MOZAMBIQUE|MYANMAR|NAMIBIA|NAURU|NEPAL|NETHERLANDS|NEW CALEDONIA|NEW ZEALAND|NICARAGUA|NIGER|NIGERIA|NIUE|NORFOLK ISLAND|NORTHERN MARIANA ISLANDS|NORWAY|OMAN|PAKISTAN|PALAU|PALESTINE|PANAMA|NEW GUINEA|PARAGUAY|PERU|PHILIPPINES|PITCAIRN|POLAND|PORTUGAL|PUERTO RICO|QATAR|ROMANIA|RUSSIA|RWANDA|SAINT LUCIA|SAMOA|SAN MARINO|SAO TOME AND PRINCIPE|SAUDI ARABIA|SENEGAL|SERBIA|SEYCHELLES|SIERRA LEONE|SINGAPORE|SLOVAKIA|SLOVENIA|SOLOMON ISLANDS|SOMALIA|SOUTH AFRICA|SPAIN|SRI LANKA|SUDAN|SURINAME|SWAZILAND|SWEDEN|SWITZERLAND|TAIWAN|TAJIKISTAN|TANZANIA|THAILAND|TIMOR-LESTE|TOGO|TOKELAU|TONGA|TRINIDAD AND TOBAGO|TUNISIA|TURKEY|TURKMENISTAN|TURKS AND CAICOS|TUVALU|UGANDA|UKRAINE|UNITED ARAB EMIRATES|UNITED KINGDOM|UNITED STATES|URUGUAY|UZBEKISTAN|VANUATU|VENEZUELA|VIETNAM|VIRGIN ISLANDS|WALLIS AND FUTUNA|SAHARA|YEMEN|ZAMBIA|ZIMBABWE)'
        ]
        boost_multiplier = 1.2
        
        return self.weigh_context_by_pattern(patterns, boost_multiplier)
        
    # weight based on numerical (cardinal as well) regex matching
    def weigh_numerical_context(self):
        patterns = [
            '\b[0-9]{1,3}(,?[0-9]{3})*(\.[0-9]+)?\b|\.[0-9]+\b',
            '(one|two|three|four|five|six|seven|eight|nine|ten|zero|hundred|thousand|million|billion|trillion|eleven|twelve|thirteen|fifteen|twenty|thirty|fifty)'
        ]
        boost_multiplier = 1.2
        
        return self.weigh_context_by_pattern(patterns, boost_multiplier)
        
    # while there are more robust packages for this like
    # https://github.com/cnorthwood/ternip
    # we probably just want to deal with a handful of regular expressions 
    def weigh_temporal_context(self):
        patterns = ['(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', '(Spring|Summer|Winter|Fall|Autumn)', '(Christmas|Thanksgiving|Easter|Halloween)', '(January|February|March|April|May|June|July|August|September|October|November|December)', '(14\d{2}|15\d{2}|16\d{2}|17\d{2}|18\d{2}|19\d{2}|20\d{2})']
        boost_multiplier = 1.2
        
        return self.weigh_context_by_pattern(patterns, boost_multiplier)
        
    def weigh_context_by_pattern(self, patterns, boost_multiplier):
        already_boosted = []
        
        for r in self.results:
            pattern_matched = False
            for pattern in patterns:
                if r['title'] not in already_boosted and (re.search(pattern, r['title'], re.IGNORECASE) or re.search(pattern, r['description'], re.IGNORECASE)):
                    r['weight'] = r['weight'] * boost_multiplier
                    already_boosted.append(r['title'])
                    pattern_matched = True
             
            # if we remove results that don't match our pattern
            # it seems that we get a increase in the strict score
            # but a decrease in the lenient score. 
            # TODO: play with this concept more
            
            #if pattern_matched == False:
            #    self.results.remove(r)
                    
        return self
        
    def sort_by_weight(self):
        self.results = sorted(self.results, key=itemgetter('weight'), reverse=True)
        return self
        
    def top(self, limit):
        return self.sort_by_weight().results[:limit]
        
    def addFeatures(pattern_values):
        boost_multiplier = 1.2
        for r in self.results:
            for k in pattern_values:
                for pattern in pattern_values[k]:
                    if (re.search(pattern, r['title'], re.IGNORECASE) or re.search(pattern, r['description'], re.IGNORECASE)):
                        # to increase the weight or not, not sure if it is appropriate, I guess once classifier is in place, we can test
                        # with or without to see if there is a score increase and let that be the judge.
                        # r['weight'] = r['weight'] * boost_multiplier
                        r[k] = 1
                        
        return self.results
                        
    def addFeaturesByType(self, answer_type):
        # ['LOC', 'HUM', 'NUM', 'ABBR', 'ENTY', 'DESC']
        if (answer_type == 'LOC'):
            return self.addFeaturesLocation()
        elif (answer_type == 'HUM'):
            return self.addFeaturesHuman()
        elif (answer_type == 'NUM'):
            return self.addFeaturesNumeric()
        elif (answer_type == 'ABBR'):
            return self.addFeaturesAbbreviation()
        elif (answer_type == 'ENTY'):
            return self.addFeaturesEntity()
        elif (answer_type == 'DESC'):
            return self.addFeaturesDescription()
        else:
            return self.results
            
    def addFeaturesLocation():
        pattern_values = {}
        #city 	cities
        # perhaps just some most populated ones
        pattern_values['city'] = [
            '(new york|shanghai|london|hong kong|buenos aires|bangkok|seoul|mexico city|mumbai|beijing|moscow|istanbul|karachi|jakarta|tokyo|los angeles|seattle|chicago|austin|portland|sacremento|atlanta|boston|miami|rio de janeiro|lima)'
        ]
        
        #country 	countries
        pattern_values['country'] = [
            '(AFGHANISTAN|ALBANIA|ALGERIA|AMERICAN SAMOA|ANDORRA|ANGOLA|ANGUILLA|ANTARCTICA|ANTIGUA AND BARBUDA|ARGENTINA|ARMENIA|ARUBA|AUSTRALIA|AUSTRIA|AZERBAIJAN|BAHAMAS|BAHRAIN|BANGLADESH|BARBADOS|BELARUS|BELGIUM|BELIZE|BENIN|BERMUDA|BHUTAN|BOLIVIA|BONAIRE|BOSNIA|BOTSWANA|BOUVET ISLAND|BRAZIL|BULGARIA|BURUNDI|CAMBODIA|CAMEROON|CANADA|CAPE VERDE|CAYMAN ISLANDS|CENTRAL AFRICAN REPUBLIC|CHAD|CHILE|CHINA|CHRISTMAS ISLAND|COLOMBIA|COMOROS|CONGO|COOK ISLANDS|COSTA RICA|CROATIA|CUBA|CYPRUS|CZECH REPUBLIC|DENMARK|DJIBOUTI|DOMINICA|DOMINICAN REPUBLIC|ECUADOR|EGYPT|EL SALVADOR|EQUATORIAL GUINEA|ERITREA|ESTONIA|ETHIOPIA|FALKLAND ISLANDS|FAROE ISLANDS|FIJI|FINLAND|FRANCE|FRENCH GUIANA|FRENCH POLYNESIA|FRENCH SOUTHERN TERRITORIES|GABON|GAMBIA|GEORGIA|GERMANY|GHANA|GIBRALTAR|GREECE|GREENLAND|GRENADA|GUADELOUPE|GUAM|GUATEMALA|GUERNSEY|GUINEA|GUINEA-BISSAU|GUYANA|HAITI|HONDURAS|HONG KONG|HUNGARY|ICELAND|INDIA|INDONESIA|IRAN|IRAQ|IRELAND|ISRAEL|ITALY|JAMAICA|JAPAN|JERSEY|JORDAN|KAZAKHSTAN|KENYA|KIRIBATI|KOREA|KUWAIT|KYRGYZSTAN|LATVIA|LEBANON|LESOTHO|LIBERIA|LIBYA|LIECHTENSTEIN|LITHUANIA|LUXEMBOURG|MACAO|MACEDONIA|MADAGASCAR|MALAWI|MALAYSIA|MALDIVES|MALI|MALTA|MARSHALL ISLANDS|MARTINIQUE|MAURITANIA|MAURITIUS|MAYOTTE|MEXICO|MICRONESIA|MOLDOVA|MONACO|MONGOLIA|MONTENEGRO|MONTSERRAT|MOROCCO|MOZAMBIQUE|MYANMAR|NAMIBIA|NAURU|NEPAL|NETHERLANDS|NEW CALEDONIA|NEW ZEALAND|NICARAGUA|NIGER|NIGERIA|NIUE|NORFOLK ISLAND|NORTHERN MARIANA ISLANDS|NORWAY|OMAN|PAKISTAN|PALAU|PALESTINE|PANAMA|NEW GUINEA|PARAGUAY|PERU|PHILIPPINES|PITCAIRN|POLAND|PORTUGAL|PUERTO RICO|QATAR|ROMANIA|RUSSIA|RWANDA|SAINT LUCIA|SAMOA|SAN MARINO|SAO TOME AND PRINCIPE|SAUDI ARABIA|SENEGAL|SERBIA|SEYCHELLES|SIERRA LEONE|SINGAPORE|SLOVAKIA|SLOVENIA|SOLOMON ISLANDS|SOMALIA|SOUTH AFRICA|SPAIN|SRI LANKA|SUDAN|SURINAME|SWAZILAND|SWEDEN|SWITZERLAND|TAIWAN|TAJIKISTAN|TANZANIA|THAILAND|TIMOR-LESTE|TOGO|TOKELAU|TONGA|TRINIDAD AND TOBAGO|TUNISIA|TURKEY|TURKMENISTAN|TURKS AND CAICOS|TUVALU|UGANDA|UKRAINE|UNITED ARAB EMIRATES|UNITED KINGDOM|UNITED STATES|URUGUAY|UZBEKISTAN|VANUATU|VENEZUELA|VIETNAM|VIRGIN ISLANDS|WALLIS AND FUTUNA|SAHARA|YEMEN|ZAMBIA|ZIMBABWE)'
        ]
        
        #mountain 	mountains
        pattern_values['mountain'] = [
            '(highest|hill|ledge|mesa|mountain|peak|plateau|point|range|ridge|slope|tallest|volcan|mt\.)'
        ]

        #other 	other locations
        pattern_values['other_location'] = [
            '(africa|north america|south america|antarctica|europe|asia|australia)'
        ]
        
        #state 	states
        pattern_values['state'] = [
            '(mississippi|wyoming|minnesota|illinois|indiana|louisiana|texas|kansas|connecticut|montana|west virginia|alaska|missouri|south dakota|new jersey|washington|maryland|arizona|iowa|michigan|oregon|massachusetts|florida|ohio|rhode island|north carolina|maine|oklahoma|delaware|arkansas|new mexico|california|georgia|north dakota|pennsylvania|colorado|new york|nevada|idaho|utah|virginia|district of columbia|new hampshire|south carolina|vermont|hawaii|kentucky|nebraska|wisconsin|alabama|tennessee)'
        ]
        
        return self.addFeatures(pattern_values)
        
    def addFeaturesHuman():
        pattern_values = {}
        #group 	a group or organization of persons
        pattern_values['group'] = [
            '(cult|army|coalition|committee|consortium|crew|fraternity|gang|jury|possee|team)'
        ]
        #ind 	an individual
        #title 	title of a person
        #description 	description of a person
        return self.addFeatures(pattern_values)
        
    def addFeaturesNumeric():
        pattern_values = {}
        #code 	postcodes or other codes
        #count 	number of sth.
        #date 	dates
        pattern_values['date'] =  [
            '(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', 
            '(Spring|Summer|Winter|Fall|Autumn)', 
            '(Christmas|Thanksgiving|Easter|Halloween)', 
            '(January|February|March|April|May|June|July|August|September|October|November|December)', 
            '(14\d{2}|15\d{2}|16\d{2}|17\d{2}|18\d{2}|19\d{2}|20\d{2})'
        ]
        #distance 	linear measures
        pattern_values['distance'] = [
            '(mile|meter|inch|foot)'
        ]
        #money 	prices
        #order 	ranks
        pattern_values['order'] = [
            '(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh)'
        ]
        #other 	other numbers
        #period 	the lasting time of sth.
        #percent 	fractions
        pattern_values['percent'] = [
            '(\%)'
        ]
        #speed 	speed
        pattern_values['speed'] = [
            '(mph|kph)'
        ]
        #temp 	temperature
        pattern_values['temperature'] = [
            '(farhenheit|celcius)'
        ]
        #size 	size, area and volume
        #weight 	weight
        pattern_values['weight'] = [
            '(lbs|kg)'
        ]
        return self.addFeatures(pattern_values)
        
    def addFeaturesAbbreviation():
        pattern_values = {}
        #abb 	abbreviation
        pattern_values['abb'] = [
            '(M\.D\.|M\.A\.|M\.S\.|A\.D\.|B\.C\.|B\.S\.|Ph\.D|D\.C\.|NAACP|AARP|NASA|NATO|UNICEF|U\.S\.|USMC|USAF|USSR|YMCA)'
        ]
        #exp 	expression abbreviated
        return self.addFeatures(pattern_values)
        
    def addFeaturesEntity():
        pattern_values = {}
        #animal 	animals
        pattern_values['letter'] = [
            '(peacock|penguin|squirrel|camel|bear|koala|deer|kangaroo|giraffe|fox|wolf|dog|cat|bird|fish|gorilla|monkey|elephant|puma|lion|tiger|leopard|cougar|panther|beaver|bison|moose|antelope|aardvark|dolphin|whale|shark|clam|squid|octopus|crab|falcon|eagle|parrot|turtle|panda|slug|snail|iguana|flamingo|hippo|heron|hyena|hummingbird|jellyfish|lizard|butterfly|meerkat|mollusk|owl|ocelot|orca|ostrich|pelican|pig|rabbit|rhino|skunk)'
        ]
        #body 	organs of body
        pattern_values['body_organ'] = [
            '(Adrenal gland|Bladder|Brain|Ear|Esophagus|Eye|Gall bladder|Heart|Kidney|intestine|Liver|Lung|Mouth|Muscle|Nose|Pancreas|Skin|Spleen|Stomach|Thymus|Thyroid|Trachea|Uterus|Penis|Vagina|Ovaries|Rectum)'
        ]
        #color 	colors
        pattern_values['color'] = [
            '(White|Silver|Gray|Grey|Black|Red|Maroon|Yellow|Green|Aqua|Teal|Blue|Fuchsia|Purple|Pink|Violet|Crimson|Lavender|Magenta|Indigo|Cyan|Brown)'
        ]
        #creative 	inventions, books and other creative pieces
        #currency 	currency names .. maybe we should leave Euro/Frank/Pound out.
        pattern_values['currency'] = [
            '(Baht|Dollar|Bitcoin|Dime|Quarter|Penny|Nickel|Dinar|Dinero|Denier|Euro|Franc|Frank|Rupee|Krona|Krone|Lira|Peso|Pound|Schilling|Shekel|Shilling|Tenga|Thaler|Yen)'
        ]
        #dis.med. 	diseases and medicine
        pattern_values['disease_medicine'] = [
            '(Cancer|Viagra|Acne|Allergy|Alzheimer|Arthritis|Asperger|Asthma|Autism|back pain|bipolar|aids|HIV|diarrhea|depression|thrombosis|crohn|dyslexia|infection|epilepsy|fibromyalgia|flu|herpes|gnorrhoea|heart attack|myocardial infarction|hemmorhoid|hepatitis|polio|influenza|leukemia|malaria|lipitor|obesity|ulcer|parkinson|pneumonia|psoriasis|rosacea|schizo|STD|smallpox|syphilis|tuberculosis|fever|vertigo|tylenol|asprin|advil|acetominophen)'
        ]
        #event 	events
        #food 	food
        pattern_values['food'] = [
            '(alcoholic|apple|apples|ate|beer|berry|berries|breakfast|brew|butter|Butter|candy|cereal|cereals|champagne|chef|chefs|chew|chews|chocoloate|cocktail|condiment|condiments|consume|consumed|consumes|cook|cooked|cookie|cookies|cooking|cooks|corn|corns|cream|creams|crop|crops|crunchy|delicacy|delicacies|delicious|dine|dinner|dip|dips|dipped|dish|dishes|drink|drinks|eat|eats|fat|feed|feeded|feeds|fish|flavor|flavors|food|foods|fry|fries|fruit|fruits|gin|imbibe|imbibed|imbibes|intake|intakes|intaked|juice|lunch|mayonnaise|meal|meals|meat|milk|nutrient|nutrients|nuts|onion|pea|peanut|peanuts|Peanut|peas|pickle|pickled|pickles|pineapple|pineapples|pizza|pizzas|potato|potatoes|protein|powdered|rum|rums|salty|sauce|savoury|sip|sips|snack|snacks|soda|sour|spice|spices|Spice|stomach|supper|swallow|swallows|sweet|sweeter|taste|tastes|tasting|tasty|tequila|treat|treats|vegetable|vegetables|vermouth|vitamin|whisky|wine|wines)'
        ]
        #instrument 	musical instrument
        pattern_values['instrument'] = [
            '(piano|drum|guitar|bango|xylophone|conga|accordian|horn|harmonica|bassoon|tuba|trumpet|clarinet|flute|bugle|piccolo|pipe|organ|sax|trombone|harp|violin|cello|bass|fiddle|sitar|ukulele)'
        ]
        #lang 	languages
        pattern_values['language'] = [
            '(Afrikaans|Albanian|Arabic|Armenian|Azeri|Basque|Bengali|Bosnian|Brazilian Portuguese|Breton|Bulgarian|Byelorussian|Catalan|Cebuano|Cornish|Croatian|Czech|Danish|Dutch|English|Esperanto|Estonian|Faroese|Fijian|Finnish|French|Frisian|Galician|Georgian|German|Greek|Guarani|Gujarati|Haitian Creole|Hawaiian|Hebrew|Hiligaynon|Hindi|Hmong|Hungarian|Chinese|Icelandic|Indonesian|Interlingua|Inuit|Inuktitut|Irish|Italian|Japanese|Japanese Romaji|Kabyle|Kazakh|Kinyarwanda|Kiribati|Korean|Kurdish|Latin|Latvian|Lithuanian|Macedonian|Malagasy|Malay|Malayalam|Maltese|Manx|Maori|Mapudungun|Marathi|Masai|Mongolian|Nepali|Norwegian Bokmal|Norwegian Nynorsk|Pali|Papiamento|Persian|Polish|Portuguese|Punjabi|Quechua|Rapanui|Romanian|Russian|Sanskrit|Scottish Gaelic|Serbian|Sesotho|Setswana|Sinhala|Slovak|Slovenian|Somali|Spanish|Sranan|Swahili|Swedish|Tagalog|Tamil|Tatar|Telugu|Thai|Tok Pisin|Tongan|Turkish|Turkmen|Urdu|Valencian|Vietnamese|Walloon|Welsh|Xhosa|Zulu)'
        ]
        
        #letter 	letters like a-z 
        pattern_values['letter'] = [
            '\s[a-zAZ]\s'
        ]
        #other 	other entities
        #plant 	plants
        pattern_values['plant'] = [
            '(Rose|Weed|Tulip|Daisy|Flower|Orchid|Bonzai|Dogwood)'
        ]
        #product 	products
        #religion 	religions
        patter_values['religion'] = [
            '(Christian|Islam|Agnostic|Atheist|Hinduism|Buddhism|Sikhism|Juche|Spiritism|Judaism|Baha\'i|Jainism|Shinto|Cao Dai|Zoroastrian|Tenrikyo|Neo-Pagan|Unitarian-Universal|Rastafarian|Scientology|Zen|Jehovah\'s Witness|Mormon|Voodoo|Quaker|Islam)'
        ]
        #sport 	sports
        pattern_values['sport'] = [
            '(Aquatics|Archery|Automobile Racing|Badminton|Base Jumping|Baseball|Basketball|Beach Volleyball|Biathlon|Bobsleigh|Bocce Ball|Body Building|Boomerang|Bowling|Boxing|Bull Fighting|Camping|Canoeing|Caving|Cheerleading|Chess|Classical Dance|Cricket|Cross Country Running|Cross Country Skiing|Curling|Cycling|Darts|Decathlon|Diving|Dog Sledding|Dog Training|Down Hill Skiing|Equestrianism|Falconry|Fencing|Figure Skating|Fishing|Flag Football|Foosball|Football|Fox Hunting|Golf|Gymnastics|Hand Ball|Hang Gliding|High Jump|Hiking|Hockey|Horseshoes|Hot Air Ballooning|Hunting|Ice Skating|Inline Skating|Jai Alai|Judo|Karate|Kayaking|Knee Boarding|Lacrosse|Land Sailing|Log Rolling|Long Jump|Luge|Modern Dance|Modern Pentathlon|Motorcycle Racing|Mountain Biking|Mountaineering|Netball|Paint Ball|Para Gliding|Parachuting|Petanque|Pool Playing|Power Walking|Quad Biking|Racquetball|Remote Control Boating|River Rafting|Rock Climbing|Rodeo Riding|Roller Skating|Rowing|Rugby|Sailing|Scuba Diving|Shooting|Shot Put|Shuffleboard|Skateboarding|Skeet Shooting|Snooker|Snow Biking|Snow Boarding|Snow Shoeing|Snow Sledding|Soccer|Sombo|Speed Skating|Sport Fishing|Sport Guide|Sprint Running|Squash|Stunt Plane Flying|Sumo Wrestling|Surfing|Swimming|Synchronized Swimming|Table Tennis|Taekwondo|Tchoukball|Tennis|Track and Field|Trampolining|Triathlon|Tug of War|Volleyball|Water Polo|Water Skiing|Weight Lifting|Wheelchair Basketball|White Water Rafting|Wind Surfing|Wrestling|Wushu|Yachting|Yoga)'
        ]
        #substance 	elements and substances
        #symbol 	symbols and signs
        #technique 	techniques and methods
        #term 	equivalent terms
        #vehicle 	vehicles
        pattern_values['vehicle'] = [
            '(Peugeot|Renault|Citroen|Volkswagon|VW|Acura|Maza|Mitsubishi|Aston Martin|mini cooper|rolls royce|lincoln|Nissan|Scion|Fiat|Maserati|Bugatti|Ford|Chevy|Chevrolet|Dodge|Mercedes|BMW|Audi|Toyota|Suzuki|Yamaha|Honda|Kia|Jeep|Buick|GMC|Land Rover|Range Rover|Tank|ATV|Cadillac|Oldsmobile|Ferrari|lamborghini|chrysler)'
        ]
        #word 	words with a special property
        return self.addFeatures(pattern_values)
        
    def addFeaturesDescription():
        pattern_values = {}
        #definition 	definition of sth.
        #description 	description of sth.
        #manner 	manner of an action
        #reason 	reasons
        return self.addFeatures(pattern_values)
        
