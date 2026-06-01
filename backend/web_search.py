from ddgs import DDGS
def web_search(query, max_results=3):
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({"title": r["title"], "body": r["body"], "href": r["href"]})
        return results
    except Exception as e:
        print(f"Web search error: {e}")
        return []
