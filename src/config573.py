

config = {
    "search_libraries": ["pattern", "requests", "xgoogle"],
    "search_library_active": "pattern",
    "search_engines": ["bing", "google"],
    "search_engine_active": "google",
    "google_per_page": 10,
    "bing_per_page": 50,
    "josh_google_key": "AIzaSyDwqZl_4hPZCBk7ePFUKxizus52tnLgTWE",
    "anthony_google_key": "AIzaSyBXfu02iYBd4FvIa6fSYGUIv8WXIkNC8ZY",
    "marie_google_key":"AIzaSyCMJUqmyyzwZMBBxdhKt5Fi4yRaeounW6o",
    "use_whose_key": "josh",
    "use_lucene_wildcard": True,
    "answer_char_length" : 100,
    # you can limit the number of questions in a run
    # for experimentation
    # 2006 has 403, 2004 has 230, 2005 has 362
    # 0 means do all questions
    "questions_to_answer":0,
    "aquant_index_dir": "aquaint_index", # aquaint_index2 for 2007
    "web_cache_dir": "web_cache",
    "reset_web_cache": 0,
    "web_results_limit": 50,
    "answer_candidates_limit": 20,
    "include_exact_query_matches": 0,
    "deliverable": "D4",
    "trec_file": "/dropbox/12-13/573/Data/Questions/devtest/TREC-2006.xml",
    "model_dir": "./models/"
}
