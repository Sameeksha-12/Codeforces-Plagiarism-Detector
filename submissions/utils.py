# submissions/utils.py
import requests
import time
from .models import Contest, User, Submission
from bs4 import BeautifulSoup
import random
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import jaccard_score

def fetch_top_users(contest_id):
    url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=50"
    response = requests.get(url)
    time.sleep(2)  # To avoid hitting the rate limit
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            contest, created = Contest.objects.get_or_create(contest_id=contest_id, defaults={'name': data['result']['contest']['name']})

            for row in data['result']['rows']:
                handle = row['party']['members'][0]['handle']
                rank = row['rank']
                user, created = User.objects.update_or_create(
                    handle=handle,
                    contest=contest,
                    defaults={'rank': rank}
                )
                
                fetch_user_submissions(contest_id, user)
                
            contest.fetched = True
            contest.save()
        else:
            raise Exception(f"Error in API response: {data['comment']}")
    else:
        raise Exception(f"Failed to fetch contest data: {response.status_code}")

def fetch_user_submissions(contest_id, user):
    url = f"https://codeforces.com/api/contest.status?contestId={contest_id}&handle={user.handle}"
    response = requests.get(url)
    time.sleep(2)  # To avoid hitting the rate limit
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            for sub in data['result']:
                Submission.objects.update_or_create(
                    submission_id=sub['id'],
                    user=user,
                    contest=user.contest,
                    defaults={
                        'problem_index': sub['problem']['index'],
                        'problem_name': sub['problem']['name'],
                        'programming_language': sub['programmingLanguage'],
                        'verdict': sub['verdict'],
                    }
                )
        else:
            raise Exception(f"Error in API response: {data['comment']}")
    else:
        raise Exception(f"Failed to fetch submissions: {response.status_code}")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# def fetch_submission_code(submission):
#     if submission.fetched:
#         print(f"Code for submission {submission.submission_id} already fetched.")
#         return

#     options = Options()
#     options.headless = True  # Run in headless mode (without opening a browser window)
#     driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

   

#     try:
#         url = f"https://codeforces.com/contest/{submission.contest.contest_id}/submission/{submission.submission_id}"
#         driver.get(url)
#         time.sleep(2)  # Wait for the page to load completely

#         code_element = driver.find_element(By.ID, "program-source-text")
#         if code_element:
#             submission.code = code_element.text
#             submission.fetched = True  # Mark as fetched after successful fetch
#             submission.save()
#             print(f"Code for submission {submission.submission_id} fetched and saved.")
#         else:
#             print(f"Code element not found for submission {submission.submission_id}.")
#             time.sleep(4 * 60)  
#             return 
#     except NoSuchElementException:
#         print(f"Code element not found for submission {submission.submission_id}.")
#         time.sleep(4 * 60)  
#         return 
    
#     except WebDriverException as e:
#         print(f"An error occurred while fetching submission {submission.submission_id} with Selenium: {str(e)}")
#     except Exception as e:
#         print(f"An error occurred while fetching submission {submission.submission_id} with Selenium: {str(e)}")
#     finally:
#         driver.quit()
#         # Add a random sleep to further mitigate the risk of detection
#         time.sleep(random.uniform(3, 7))

def fetch_submission_code(submission):
    if submission.fetched:
        print(f"Code for submission {submission.submission_id} already fetched.")
        return
    session = requests.Session()
    url = f"https://codeforces.com/contest/{submission.contest.contest_id}/submission/{submission.submission_id}"
    headers = {
        'User-Agent': random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15'
        ]),
        'Referer': f"https://codeforces.com/contest/{submission.contest.contest_id}",
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            code_div = soup.find('pre', {'id': 'program-source-text'})
            if code_div:
                submission.code = code_div.text
                submission.fetched = True  # Mark as fetched after successful fetch
                submission.save()
                print(f"Code for submission {submission.submission_id} fetched and saved.")
        elif response.status_code == 403:
            print(f"Access denied for submission {submission.submission_id}. Waiting for 3 minutes before retrying...")
            print(f"Response Headers: {response.headers}")
            print(f"Response Content: {response.text[:50]}...")
            time.sleep(185)  # Wait for 3 minutes (180 seconds) before allowing further processing
            response = session.get(url, headers=headers)  
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                code_div = soup.find('pre', {'id': 'program-source-text'})
                if code_div:
                    submission.code = code_div.text
                    submission.fetched = True  
                    submission.save()
                    print(f"Code for submission {submission.submission_id} fetched and saved after retry.")
                else:
                    print(f"Code element still not found for submission {submission.submission_id} after retry.")
            elif response.status_code == 403:
                print(f"Access still denied for submission {submission.submission_id} after retry.")
                time.sleep(185)
            else:
                print(f"Failed to fetch submission code after retry: {response.status_code}")

        else:
            print(f"Failed to fetch submission code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while fetching submission {submission.submission_id}: {str(e)}")
    # Add a random sleep to further mitigate the risk of detection
    finally:
        session.close()
        time.sleep(random.uniform(3, 7))

def check_code_similarity(contest):
    submissions = Submission.objects.filter(contest=contest, verdict='OK', fetched=True)
    results = []

    grouped_submissions = {}
    for submission in submissions:
        key = (submission.problem_index, submission.programming_language)
        if key not in grouped_submissions:
            grouped_submissions[key] = []
        grouped_submissions[key].append(submission)
    
    for key,subs in grouped_submissions.items():
        problem_index,language = key
        for i in range(len(subs)):
            for j in range(i+1,len(subs)):
                if subs[i].user_id != subs[j].user_id:
                    # if subs[i].programming_language == subs[j].programming_language:
                    sim_score = jaccard_similarity(subs[i].code, subs[j].code)
                    if sim_score > 0.5:
                        results.append({
                            'submission1': subs[i],
                            'submission2': subs[j],
                            'similarity_score': sim_score,
                            'problem_index': problem_index
                        })
    results = sorted(results, key=lambda x: x['similarity_score'], reverse=True)
    return results

def jaccard_similarity(code1, code2):
    vectorizer = CountVectorizer(token_pattern=r'\w+', binary=True)
    X = vectorizer.fit_transform([code1, code2])
    X = X.toarray()
    return jaccard_score(X[0], X[1])

