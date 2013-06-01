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
    
    STATES = set(['mississippi','wyoming','minnesota','illinois','indiana','louisiana','texas','kansas','connecticut','montana','west virginia','alaska','missouri','south dakota','new jersey','washington','maryland','arizona','iowa','michigan','oregon','massachusetts','florida','ohio','rhode island','north carolina','maine','oklahoma','delaware','arkansas','new mexico','california','georgia','north dakota','pennsylvania','colorado','new york','nevada','idaho','utah','virginia','district of columbia','new hampshire','south carolina','vermont','hawaii','kentucky','nebraska','wisconsin','alabama','tennessee'])
    CONTINENTS = set(['africa','north america','south america','antarctica','europe','asia','australia'])
    COUNTRIES = set(['afghanistan','albania','algeria','american samoa','andorra','angola','anguilla','antarctica','antigua and barbuda','argentina','armenia','aruba','australia','austria','azerbaijan','bahamas','bahrain','bangladesh','barbados','belarus','belgium','belize','benin','bermuda','bhutan','bolivia','bonaire','bosnia','botswana','bouvet island','brazil','bulgaria','burundi','cambodia','cameroon','canada','cape verde','cayman islands','central african republic','chad','chile','china','christmas island','colombia','comoros','congo','cook islands','costa rica','croatia','cuba','cyprus','czech republic','denmark','djibouti','dominica','dominican republic','ecuador','egypt','el salvador','equatorial guinea','eritrea','estonia','ethiopia','falkland islands','faroe islands','fiji','finland','france','french guiana','french polynesia','french southern territories','gabon','gambia','georgia','germany','ghana','gibraltar','greece','greenland','grenada','guadeloupe','guam','guatemala','guernsey','guinea','guinea-bissau','guyana','haiti','honduras','hong kong','hungary','iceland','india','indonesia','iran','iraq','ireland','israel','italy','jamaica','japan','jersey','jordan','kazakhstan','kenya','kiribati','korea','kuwait','kyrgyzstan','latvia','lebanon','lesotho','liberia','libya','liechtenstein','lithuania','luxembourg','macao','macedonia','madagascar','malawi','malaysia','maldives','mali','malta','marshall islands','martinique','mauritania','mauritius','mayotte','mexico','micronesia','moldova','monaco','mongolia','montenegro','montserrat','morocco','mozambique','myanmar','namibia','nauru','nepal','netherlands','new caledonia','new zealand','nicaragua','niger','nigeria','niue','norfolk island','northern mariana islands','norway','oman','pakistan','palau','palestine','panama','new guinea','paraguay','peru','philippines','pitcairn','poland','portugal','puerto rico','qatar','romania','russia','rwanda','saint lucia','samoa','san marino','sao tome and principe','saudi arabia','senegal','serbia','seychelles','sierra leone','singapore','slovakia','slovenia','solomon islands','somalia','south africa','spain','sri lanka','sudan','suriname','swaziland','sweden','switzerland','taiwan','tajikistan','tanzania','thailand','timor-leste','togo','tokelau','tonga','trinidad and tobago','tunisia','turkey','turkmenistan','turks and caicos','tuvalu','uganda','ukraine','united arab emirates','united kingdom','united states','uruguay','uzbekistan','vanuatu','venezuela','vietnam','virgin islands','wallis and futuna','sahara','yemen','zambia','zimbabwe'])
    CARDINAL_NUMBERS = set(['one','two','three','four','five','six','seven','eight','nine','ten','zero','hundred','thousand','million','billion','trillion','eleven','twelve','thirteen','fifteen','twenty','thirty','fifty'])
    DAYS_OF_WEEK = set(['monday','tuesday','wednesday','thursday','friday','saturday','sunday'])
    SEASONS = set(['spring','summer','winter','fall','autumn'])
    HOLIDAYS = set(['christmas','thanksgiving','easter','halloween'])
    MONTHS = set(['january','february','march','april','may','june','july','august','september','october','november','december'])
    CITIES = set(['new york','shanghai','london','hong kong','buenos aires','bangkok','seoul','mexico city','mumbai','beijing','moscow','istanbul','karachi','jakarta','tokyo','los angeles','seattle','chicago','austin','portland','sacremento','atlanta','boston','miami','rio de janeiro','lima'])
    GROUPS = set(['cult','army','coalition','committee','consortium','crew','fraternity','gang','jury','possee','team'])
    DISTANCE = set(['mile','meter','inch','foot'])
    ORDER = set(['first','second','third','fourth','fifth','sixth','seventh','eighth','ninth','tenth','eleventh'])
    SPEED = set(['mph','kph'])
    TEMPERATURE = set(['farhenheit','celcius'])
    WEIGHT = set(['lbs','kg'])
    ANIMALS = set(['peacock','penguin','squirrel','camel','bear','koala','deer','kangaroo','giraffe','fox','wolf','dog','cat','bird','fish','gorilla','monkey','elephant','puma','lion','tiger','leopard','cougar','panther','beaver','bison','moose','antelope','aardvark','dolphin','whale','shark','clam','squid','octopus','crab','falcon','eagle','parrot','turtle','panda','slug','snail','iguana','flamingo','hippo','heron','hyena','hummingbird','jellyfish','lizard','butterfly','meerkat','mollusk','owl','ocelot','orca','ostrich','pelican','pig','rabbit','rhino','skunk'])
    BODY_ORGANS = set(['adrenal gland','bladder','brain','ear','esophagus','eye','gall bladder','heart','kidney','intestine','liver','lung','mouth','muscle','nose','pancreas','skin','spleen','stomach','thymus','thyroid','trachea','uterus','penis','vagina','ovaries','rectum'])
    COLORS = set(['white','silver','gray','grey','black','red','maroon','yellow','green','aqua','teal','blue','fuchsia','purple','pink','violet','crimson','lavender','magenta','indigo','cyan','brown'])
    CURRENCY = set(['baht','dollar','bitcoin','dime','quarter','penny','nickel','dinar','dinero','denier','euro','franc','frank','rupee','krona','krone','lira','peso','pound','schilling','shekel','shilling','tenga','thaler','yen'])
    DISEASES_MEDICINE = set(['cancer','viagra','acne','allergy','alzheimer','arthritis','asperger','asthma','autism','back pain','bipolar','aids','hiv','diarrhea','depression','thrombosis','crohn','dyslexia','infection','epilepsy','fibromyalgia','flu','herpes','gnorrhoea','heart attack','myocardial infarction','hemmorhoid','hepatitis','polio','influenza','leukemia','malaria','lipitor','obesity','ulcer','parkinson','pneumonia','psoriasis','rosacea','schizo','std','smallpox','syphilis','tuberculosis','fever','vertigo','tylenol','asprin','advil','acetominophen'])
    FOODS = set(['alcoholic','apple','apples','ate','beer','berry','berries','breakfast','brew','butter','butter','candy','cereal','cereals','champagne','chef','chefs','chew','chews','chocoloate','cocktail','condiment','condiments','consume','consumed','consumes','cook','cooked','cookie','cookies','cooking','cooks','corn','corns','cream','creams','crop','crops','crunchy','delicacy','delicacies','delicious','dine','dinner','dip','dips','dipped','dish','dishes','drink','drinks','eat','eats','fat','feed','feeded','feeds','fish','flavor','flavors','food','foods','fry','fries','fruit','fruits','gin','imbibe','imbibed','imbibes','intake','intakes','intaked','juice','lunch','mayonnaise','meal','meals','meat','milk','nutrient','nutrients','nuts','onion','pea','peanut','peanuts','peanut','peas','pickle','pickled','pickles','pineapple','pineapples','pizza','pizzas','potato','potatoes','protein','powdered','rum','rums','salty','sauce','savoury','sip','sips','snack','snacks','soda','sour','spice','spices','spice','stomach','supper','swallow','swallows','sweet','sweeter','taste','tastes','tasting','tasty','tequila','treat','treats','vegetable','vegetables','vermouth','vitamin','whisky','wine','wines'])
    INSTRUMENTS = set(['piano','drum','guitar','bango','xylophone','conga','accordian','horn','harmonica','bassoon','tuba','trumpet','clarinet','flute','bugle','piccolo','pipe','organ','sax','trombone','harp','violin','cello','bass','fiddle','sitar','ukulele'])
    LANGUAGES = set(['afrikaans','albanian','arabic','armenian','azeri','basque','bengali','bosnian','brazilian portuguese','breton','bulgarian','byelorussian','catalan','cebuano','cornish','croatian','czech','danish','dutch','english','esperanto','estonian','faroese','fijian','finnish','french','frisian','galician','georgian','german','greek','guarani','gujarati','haitian creole','hawaiian','hebrew','hiligaynon','hindi','hmong','hungarian','chinese','icelandic','indonesian','interlingua','inuit','inuktitut','irish','italian','japanese','japanese romaji','kabyle','kazakh','kinyarwanda','kiribati','korean','kurdish','latin','latvian','lithuanian','macedonian','malagasy','malay','malayalam','maltese','manx','maori','mapudungun','marathi','masai','mongolian','nepali','norwegian bokmal','norwegian nynorsk','pali','papiamento','persian','polish','portuguese','punjabi','quechua','rapanui','romanian','russian','sanskrit','scottish gaelic','serbian','sesotho','setswana','sinhala','slovak','slovenian','somali','spanish','sranan','swahili','swedish','tagalog','tamil','tatar','telugu','thai','tok pisin','tongan','turkish','turkmen','urdu','valencian','vietnamese','walloon','welsh','xhosa','zulu'])
    PLANTS = set(['rose','weed','tulip','daisy','flower','orchid','bonzai','dogwood'])
    RELIGIONS = set(['christian','islam','agnostic','atheist','hinduism','buddhism','sikhism','juche','spiritism','judaism','baha\'i','jainism','shinto','cao dai','zoroastrian','tenrikyo','neo-pagan','unitarian-universal','rastafarian','scientology','zen','jehovah\'s witness','mormon','voodoo','quaker','islam'])
    SPORTS = set(['aquatics','archery','automobile racing','badminton','base jumping','baseball','basketball','beach volleyball','biathlon','bobsleigh','bocce ball','body building','boomerang','bowling','boxing','bull fighting','camping','canoeing','caving','cheerleading','chess','classical dance','cricket','cross country running','cross country skiing','curling','cycling','darts','decathlon','diving','dog sledding','dog training','down hill skiing','equestrianism','falconry','fencing','figure skating','fishing','flag football','foosball','football','fox hunting','golf','gymnastics','hand ball','hang gliding','high jump','hiking','hockey','horseshoes','hot air ballooning','hunting','ice skating','inline skating','jai alai','judo','karate','kayaking','knee boarding','lacrosse','land sailing','log rolling','long jump','luge','modern dance','modern pentathlon','motorcycle racing','mountain biking','mountaineering','netball','paint ball','para gliding','parachuting','petanque','pool playing','power walking','quad biking','racquetball','remote control boating','river rafting','rock climbing','rodeo riding','roller skating','rowing','rugby','sailing','scuba diving','shooting','shot put','shuffleboard','skateboarding','skeet shooting','snooker','snow biking','snow boarding','snow shoeing','snow sledding','soccer','sombo','speed skating','sport fishing','sport guide','sprint running','squash','stunt plane flying','sumo wrestling','surfing','swimming','synchronized swimming','table tennis','taekwondo','tchoukball','tennis','track and field','trampolining','triathlon','tug of war','volleyball','water polo','water skiing','weight lifting','wheelchair basketball','white water rafting','wind surfing','wrestling','wushu','yachting','yoga'])
    VEHICLES = set(['peugeot','renault','citroen','volkswagon','vw','acura','maza','mitsubishi','aston martin','mini cooper','rolls royce','lincoln','nissan','scion','fiat','maserati','bugatti','ford','chevy','chevrolet','dodge','mercedes','bmw','audi','toyota','suzuki','yamaha','honda','kia','jeep','buick','gmc','land rover','range rover','tank','atv','cadillac','oldsmobile','ferrari','lamborghini','chrysler'])
    
    # all results start with a weight of 1.0
    def __init__(self, results, set_initial = 1):
        if set_initial:
            for r in results:
                r['weight'] = 1.0
        self.results = results
        
    # check to see if token is in one of are plethora of sets
    def tokenFeatures(self, token):
        token = token.lower()
        feats = {}
        for local_var in self.__class__.__dict__:
            if type(self.__class__.__dict__[local_var]) != set:
                continue
            if token in self.__class__.__dict__[local_var]:
                feats[local_var] = 1
        
        return feats
        
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
            '(' + '|'.join(self.STATES) + ')',
            '(' + '|'.join(self.CONTINENTS) + ')',
            '(' + '|'.join(self.COUNTRIES) + ')'
        ]
        boost_multiplier = 1.2
        
        return self.weigh_context_by_pattern(patterns, boost_multiplier)
        
    # weight based on numerical (cardinal as well) regex matching
    def weigh_numerical_context(self):
        patterns = [
            '\b[0-9]{1,3}(,?[0-9]{3})*(\.[0-9]+)?\b|\.[0-9]+\b',
            '(' + '|'.join(self.CARDINAL_NUMBERS) + ')'
        ]
        boost_multiplier = 1.2
        
        return self.weigh_context_by_pattern(patterns, boost_multiplier)
        
    # while there are more robust packages for this like
    # https://github.com/cnorthwood/ternip
    # we probably just want to deal with a handful of regular expressions 
    def weigh_temporal_context(self):
        patterns = [
            '(' + '|'.join(self.DAYS_OF_WEEK) + ')',
            '(' + '|'.join(self.SEASONS) + ')',
            '(' + '|'.join(self.HOLIDAYS) + ')',
            '(' + '|'.join(self.MONTHS) + ')',
            '(14\d{2}|15\d{2}|16\d{2}|17\d{2}|18\d{2}|19\d{2}|20\d{2})'
        ]
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
        
    def addFeatures(self, pattern_values):
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
            
    def addFeaturesLocation(self):
        pattern_values = {}
        #city 	cities
        # perhaps just some most populated ones
        pattern_values['city'] = [
            '(' + '|'.join(self.CITIES) + ')'
        ]
        
        #country 	countries
        pattern_values['country'] = [
            '(' + '|'.join(self.COUNTRIES) + ')'
        ]
        
        #mountain 	mountains
        pattern_values['mountain'] = [
            '(highest|hill|ledge|mesa|mountain|peak|plateau|point|range|ridge|slope|tallest|volcan|mt\.)'
        ]

        #other 	other locations
        pattern_values['other_location'] = [
            '(' + '|'.join(self.CONTINENTS) + ')'
        ]
        
        #state 	states
        pattern_values['state'] = [
            '(' + '|'.join(self.STATES) + ')'
        ]
        
        return self.addFeatures(pattern_values)
        
    def addFeaturesHuman(self):
        pattern_values = {}
        #group 	a group or organization of persons
        pattern_values['group'] = [
            '(' + '|'.join(self.GROUPS) + ')'
        ]
        #ind 	an individual
        #title 	title of a person
        #description 	description of a person
        return self.addFeatures(pattern_values)
        
    def addFeaturesNumeric(self):
        pattern_values = {}
        #code 	postcodes or other codes
        #count 	number of sth.
        #date 	dates
        pattern_values['date'] =  [
            '(' + '|'.join(self.DAYS_OF_WEEK) + ')',
            '(' + '|'.join(self.SEASONS) + ')',
            '(' + '|'.join(self.HOLIDAYS) + ')',
            '(' + '|'.join(self.MONTHS) + ')',
            '(14\d{2}|15\d{2}|16\d{2}|17\d{2}|18\d{2}|19\d{2}|20\d{2})'
        ]
        #distance 	linear measures
        pattern_values['distance'] = [
            '(' + '|'.join(self.DISTANCE) + ')'
        ]
        #money 	prices
        #order 	ranks
        pattern_values['order'] = [
            '(' + '|'.join(self.ORDER) + ')'
        ]
        #other 	other numbers
        #period 	the lasting time of sth.
        #percent 	fractions
        pattern_values['percent'] = [
            '(\%)'
        ]
        #speed 	speed
        pattern_values['speed'] = [
            '(' + '|'.join(self.SPEED) + ')'
        ]
        #temp 	temperature
        pattern_values['temperature'] = [
            '(' + '|'.join(self.TEMPERATURE) + ')'
        ]
        #size 	size, area and volume
        #weight 	weight
        pattern_values['weight'] = [
            '(' + '|'.join(self.WEIGHT) + ')'
        ]
        return self.addFeatures(pattern_values)
        
    def addFeaturesAbbreviation(self):
        pattern_values = {}
        #abb 	abbreviation
        pattern_values['abb'] = [
            '(M\.D\.|M\.A\.|M\.S\.|A\.D\.|B\.C\.|B\.S\.|Ph\.D|D\.C\.|NAACP|AARP|NASA|NATO|UNICEF|U\.S\.|USMC|USAF|USSR|YMCA)'
        ]
        #exp 	expression abbreviated
        return self.addFeatures(pattern_values)
        
    def addFeaturesEntity(self):
        pattern_values = {}
        #animal 	animals
        pattern_values['animal'] = [
            '(' + '|'.join(self.ANIMALS) + ')'
        ]
        #body 	organs of body
        pattern_values['body_organ'] = [
            '(' + '|'.join(self.BODY_ORGANS) + ')'
        ]
        #color 	colors
        pattern_values['color'] = [
            '(' + '|'.join(self.COLORS) + ')'
        ]
        #creative 	inventions, books and other creative pieces
        #currency 	currency names .. maybe we should leave Euro/Frank/Pound out.
        pattern_values['currency'] = [
            '(' + '|'.join(self.CURRENCY) + ')'
        ]
        #dis.med. 	diseases and medicine
        pattern_values['disease_medicine'] = [
            '(' + '|'.join(self.DISEASES_MEDICINE) + ')'
        ]
        #event 	events
        #food 	food
        pattern_values['food'] = [
            '(' + '|'.join(self.FOODS) + ')'
        ]
        #instrument 	musical instrument
        pattern_values['instrument'] = [
            '(' + '|'.join(self.INSTRUMENTS) + ')'
        ]
        #lang 	languages
        pattern_values['language'] = [
            '(' + '|'.join(self.LANGUAGES) + ')'
        ]
        
        #letter 	letters like a-z 
        pattern_values['letter'] = [
            '\s[a-zAZ]\s'
        ]
        #other 	other entities
        #plant 	plants
        pattern_values['plant'] = [
            '(' + '|'.join(self.PLANTS) + ')'
        ]
        #product 	products
        #religion 	religions
        pattern_values['religion'] = [
            '(' + '|'.join(self.RELIGIONS) + ')'
        ]
        #sport 	sports
        pattern_values['sport'] = [
            '(' + '|'.join(self.SPORTS) + ')'
        ]
        #substance 	elements and substances
        #symbol 	symbols and signs
        #technique 	techniques and methods
        #term 	equivalent terms
        #vehicle 	vehicles
        pattern_values['vehicle'] = [
            '(' + '|'.join(self.VEHICLES) + ')'
        ]
        #word 	words with a special property
        return self.addFeatures(pattern_values)
        
    def addFeaturesDescription(self):
        pattern_values = {}
        #definition 	definition of sth.
        #description 	description of sth.
        #manner 	manner of an action
        #reason 	reasons
        return self.addFeatures(pattern_values)
        
