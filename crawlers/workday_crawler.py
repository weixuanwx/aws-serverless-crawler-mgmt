import json
# import bs4
import os
import requests
from datetime import datetime
import time
import traceback
from random import randint


def crawl_workday(arg, s3_resource, s3_bucket_name, s3_folder_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    }
    company_name = arg['company_name']
    prefixlink = arg['prefixlink']
    linkWquery = arg['linkWquery']
    crawlLimit = arg['crawlLimit']
    
    print('STARTED Workday Crawling: {}'.format(company_name))

    try:
        results = ''
    
        dateFolder = datetime.now().strftime('%Y-%m-%d')
    
        session = requests.Session()
        response = session.get(linkWquery.format(0), headers=headers, timeout=15)
        time.sleep(randint(1,2))
        objs = json.loads(response.text)
        totaljobs = objs['body']['children'][0]['facetContainer']['paginationCount']['value']
        
        if totaljobs == 0:
            print('COMPANY {} HAS NO JOBS. URL: {}'.format(company_name,linkWquery))
        else:
            # if bucket don't exist, create bucket of company_name
            
            totalpages = int(totaljobs/100 + 2)

            counts = 1
            offset = 0

            for page in range(1,totalpages):
                pageLink = linkWquery.format(offset)
                # print pageLink
                res = session.get(url=pageLink, headers=headers, timeout=15)
                time.sleep(randint(2,4))
                json_obj = json.loads(res.text)
                jobs = json_obj['body']['children'][0]['children'][0]['listItems']
                for job in jobs:
                    joburl = prefixlink + job['title']['commandLink'].split('job')[-1] # get job link
                    rs = session.get(joburl, headers={'accept': 'application/json'})
                    time.sleep(randint(2,4))
                    
                    obj = json.loads(rs.text)
                    filename = company_name + "/" + dateFolder + "/" + str(counts) + "_page" + str(page) + ".json"
                
                    output_obj_path = os.path.join(s3_folder_path, filename)
                    s3_obj = s3_resource.Object(s3_bucket_name, output_obj_path)
                    s3_obj.put(Body=json.dumps(obj, separators=(',', ':')))
                    
                    counts +=1

                offset += 100

                if counts > crawlLimit:
                    break

        completion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("COMPLETED Workday Crawling {}".format(completion_time))
    except Exception as e:
        print(traceback.format_exc())


    return (totaljobs, results)


