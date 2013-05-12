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
        patterns = ['(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', '(January|February|March|April|May|June|July|August|September|October|November|December)', '(14\d{2}|15\d{2}|16\d{2}|17\d{2}|18\d{2}|19\d{2}|20\d{2})']
        boost_multiplier = 1.2
        
        return self.weigh_context_by_pattern(patterns, boost_multiplier)
        
    def weigh_context_by_pattern(self, patterns, boost_multiplier):
        already_boosted = []
        
        for r in self.results:
            for pattern in patterns:
                if r['title'] not in already_boosted and (re.search(pattern, r['title'], re.IGNORECASE) or re.search(pattern, r['description'], re.IGNORECASE)):
                    r['weight'] = r['weight'] * boost_multiplier
                    already_boosted.append(r['title'])
                    
        return self
        
    def sort_by_weight(self):
        self.results = sorted(self.results, key=itemgetter('weight'), reverse=True)
        return self
        
    def top(self, limit):
        return self.sort_by_weight().results[:limit]
        
