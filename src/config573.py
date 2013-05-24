

config = {
    "search_libraries": ["pattern", "requests", "xgoogle"],
    "search_library_active": "pattern",
    "search_engines": ["bing", "google"],
    "search_engine_active": "google",
    "google_per_page": 10,
    "bing_per_page": 50,
    "josh_google_key": "AIzaSyDwqZl_4hPZCBk7ePFUKxizus52tnLgTWE",
    "anthony_google_key": "AIzaSyBXfu02iYBd4FvIa6fSYGUIv8WXIkNC8ZY",
    "use_whose_key": "anthony",
    "use_lucene_wildcard": True,
    # you can limit the number of questions in a run
    # for experimentation
    # 2006 has 403, 2004 has 230, 2005 has 362
    # 0 means do all questions
    "questions_to_answer":0,
    "aquant_index_dir": "aquaint_index",
    "web_cache_dir": "web_cache",
    "reset_web_cache": 0,
    "web_results_limit": 50,
    "answer_candidates_limit": 20,
    "include_exact_query_matches": 0,
    "deliverable": "D4",
    "trec_file": "/dropbox/12-13/573/Data/Questions/devtest/TREC-2006.xml",
    "main_model": "./models/main_model",
    "binarize_cmd": "/NLP_TOOLS/tool_sets/mallet/latest/bin/mallet import-svmlight --input train.vectors.txt --output train.vectors",
    "train_cmd": "/NLP_TOOLS/tool_sets/mallet/latest/bin/mallet train-classifier --input train.vectors --trainer MaxEnt --output-classifier ml.model",
    "test_cmd": "/NLP_TOOLS/tool_sets/mallet/latest/bin/mallet classify-svmlight --input test.vectors.txt --output classifier.result --classifier ml.model"
}