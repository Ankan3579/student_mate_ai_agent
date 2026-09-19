from langchain.tools import tool
from dotenv import load_dotenv
import os
from tavily import TavilyClient
import requests
from bs4 import BeautifulSoup
load_dotenv()
api_key = os.getenv("TAVILY_API_KEY")
tavily_client=TavilyClient(api_key=api_key)
@tool
def web_search(query_type:str , college_name:str)->str:
    """you are a web search tool that can serach information about colleges or universities in country , any state or any city in the world. user will give query_type: fees , academic , admission, placement , ranking , scholarship , hostel , sports , faculty , research , events , news , contct details , location , courses , departments , alumni , reviews , infrastructure , transportation , safety , culture , diversity , student life , career services , financial aid , international students , student organizations , campus facilities , student support services, and i will provide  college_name: name of  the college or university.  
    
    you will return the topic : title , urls , content.

    """

    query = f"{query_type} information for {college_name}"

    try:
        response= tavily_client.search(api_key=api_key, query=query , max_results=5) 
        results = response.get("results",[])
        if not results:
            return "no result found "

        output =[]
        for result in results:
            title=result.get("title",'N/A')
            url = result.get("url",'N/A')
            content = result.get("content",'N/A')
            output.append(f"Title: {title}\nURL: {url}\nContent: {content}\n")
    except Exception as e:
        return f"An error occurred: {e}"

    return "\n".join(output)

@tool
def scrape_tool(url:str)->str:
    """
    you are a web scrping tool , you can go any website url and scrape from their important information. 
    """
    try:
        response = requests.get(url , timeout=8, headers={"User-Agent":"Mozilla/5.0"})

        soup=BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script','style','nav','footer']):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]   
    except Exception as e:
        return f"An error ocurred while scaping from the website url :{str(e)}"



# if __name__=="__main__":
#     final = web_search.invoke({
#         "query_type": "admission",
#         "college_name": "Stanford University"
#     })
#     print(final)
