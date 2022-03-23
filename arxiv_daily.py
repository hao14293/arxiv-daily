import datetime
import requests
import json
import arxiv
import os

base_url = base_url = "https://arxiv.paperswithcode.com/api/v0/papers/"

class getArxivPapers:

    def __init__(self, 
                json_fileName="arxiv-daily.json",
                md_fileName="README.md"):
        self.json_fileName = json_fileName
        self.md_fileName = md_fileName

    def get_authors(self, authors, first_author=False):
        output = str()
        if first_author == False:
            output = ', '.join(str(author) for author in authors)
        else:
            output = authors[0]
        return output

    def sort_papers(self, papers):
        output = dict()
        keys = list(papers.keys())
        keys.sort(reverse=True)
        for key in keys:
            output[key] = papers[key]
        return output

    def get_daily_papers(self, topic=None, query=None, max_results=10):

        content = dict()

        search_engine = arxiv.Search(
            query = query,
            max_results = max_results,
            sort_by = arxiv.SortCriterion.SubmittedDate
        )

        for result in search_engine.results():
            categories = result.categories
           
            paper_id = result.get_short_id()
            paper_title = result.title
            paper_url = result.entry_id
            code_url = base_url + paper_id

            paper_abstract = result.summary.replace('\n', ' ')
            paper_authors = self.get_authors(result.authors)
            paper_first_author = self.get_authors(result.authors, first_author=True)
            primary_category = result.primary_category

            publish_time = result.published.date()
            update_time = result.updated.date()

            print("update_time=", update_time, 
                  " title=", paper_title,
                  " author=", paper_first_author)

            ver_pos = paper_id.find('v')
            if ver_pos == -1:
                paper_key = paper_id
            else:
                paper_key = paper_id[0:ver_pos]
            
            # 是否有官方公开代码
            try:
                r = requests.get(code_url).json()
                if "official" in r and r["official"]:   
                    repo_url = r["official"]["url"]
                    content[paper_key] = f"|**{update_time}**|**{paper_title}**|{paper_first_author} et.al.|[{paper_id}]({paper_url})|**[link]({repo_url})**|\n"                   
                else:
                    content[paper_key] = f"|**{update_time}**|**{paper_title}**|{paper_first_author} et.al.|[{paper_id}]({paper_url})|null|\n"                    
            except Exception as e:
                print(f"exception: {e} with id: {paper_key}")
        
        data = {topic:content}
        return data
    
    def update_json_file(self, data_all):
        # 如果没有文件，用'w'创建
        if not os.path.exists(self.json_fileName):
            with open(self.json_fileName, "w") as f:
                pass
        with open(self.json_fileName, 'r') as f:
            content = f.read()
            if not content:
                m = {}
            else:
                m = json.loads(content)  
        json_data = m.copy()

        for data in data_all:
            for keyword in data.keys():
                papers = data[keyword]
                if keyword in json_data.keys():
                    json_data[keyword].update(papers)
                else:
                    json_data[keyword] = papers
        
        with open(self.json_fileName, "w") as f:
            json.dump(json_data, f)
    
    def json_to_md(self):
        '''
            将json文件转为Markdown
        '''
        DateNow = str(datetime.date.today()).replace('-', '.')

        with open(self.json_fileName, "r") as f:
            content = f.read()
            if not content:
                data = {}
            else:
                data = json.loads(content)
        # 确保文件存在
        
        with open(self.md_fileName, "w+") as f: 
            f.write("## Updated on " + DateNow + "\n\n")
            for keyword in data.keys():
                day_content = data[keyword]
                if not day_content:
                    continue
                f.write(f"## {keyword}\n\n")
                f.write("|Publish Date|Title|Authors|PDF|Code|\n" + "|---|---|---|---|---|\n")          
                # sort papers by date
                day_content = self.sort_papers(day_content)
                for _,v in day_content.items():
                    if v is not None:
                        f.write(v)       
                f.write(f"\n")

        print("ok!!!")

    def run(self, keywords, max_results=10):
        data_collector = []
        for topic, keyword in keywords.items():
            print("Keyword: " + topic)
            data = self.get_daily_papers(topic, keyword, max_results)
            data_collector.append(data)
        
        self.update_json_file(data_collector)
        self.json_to_md()

if __name__ == "__main__":

    keywords = dict()
    keywords["CVPR2022"] = 'cvpr2022'
    keywords["cs.CV"] = 'cat:cs.CV'
    
    getArxivPapers().run(keywords, 50)

        

        





