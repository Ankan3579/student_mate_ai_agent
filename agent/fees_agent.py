from  config import LLM
from dotenv import load_dotenv
import os
from state.state import State
from tools.web_tool import web_search, scrape_tool
load_dotenv()

def fees_agent(state:State)->str:
  

    try:


        web_response = web_search.invoke({
            "query_type": state['user_query_type'],
            "user_query": state['user_query'],
            "college_name": state['college_name'],
            "semister": state['semister']
        })
        if "An error occurred" in web_response:
            return web_response
        # -----------------------------------------
        # STEP 2: Extract URLs from search results
        # -----------------------------------------

        urls = []

        for line in web_response.splitlines():

            if line.startswith("URL:"):
                url = line.replace("URL:", "").strip()

                if url.startswith("http"):
                    urls.append(url)

        # Remove duplicates
        urls = list(dict.fromkeys(urls))

        if not urls:
            return "No relevant webpages were found."

        # -----------------------------------------
        # STEP 3: Scrape relevant webpages
        # -----------------------------------------

        scraped_content = []

        for url in urls[:3]:

            content = scrape_tool.invoke({
                "url": url
            })

            if content and "Scraping error" not in content:
                scraped_content.append(
                    f"""
                    SOURCE URL: {url}

                    CONTENT:
                    {content}
                    """
                )

        if not scraped_content:
            return "Could not extract information from the available webpages."

        prompt = f"""
        You are a fees agent that can provide information about college or university fees  
        User has provided the following details:
        - user_query: {state['user_query']}
        - user_query_type: {state['user_query_type']}
        - College Name: {state['college_name']}
        - Semester: {state['semister']}

        Here are the search results from the web search tool:
            {web_response}

        Please provide a concise and informative response based on the above information.
        """
        
        response = LLM.invoke(prompt)
        return {
            "fees_result":response.content
        }
    except Exception as e:
        return f"An error occurred while processing your request: {e}"



# if __name__=="__main__":
#     final = fees_agent({
#         "user_query_type": "fees",
#         "college_name": "jis college of engineering",
#         "semister": "2nd Semester"
#     })
#     print(final)
