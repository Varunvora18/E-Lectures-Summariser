
from summa import summarizer
import pandas as pd
from time import sleep
from selenium import webdriver # for interacting with website
from youtube_transcript_api import YouTubeTranscriptApi
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




def open_url_in_chrome(url, mode='headed'):
    #print(f'Opening {url}')
    if mode == 'headed':
        options = webdriver.ChromeOptions()
        #options.add_argument("start-maximized")
            
    elif mode == 'headless':   
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        
    options.add_argument("--auto-open-devtools-for-tabs")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome('./chromedriver.exe', options=options)
    
    driver.get(url)
    return driver

def accept_T_and_C(driver):
    
    # Click I agree
    driver.find_element_by_xpath("//*[@id='yDmH0d']/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button/div[2]").click()
    sleep(2)
    try:
        # click 'no thanks' if it pops up
        driver.find_element_by_xpath("//*[@id='dismiss-button']").click()
    except:
        sleep(2)
    
def get_transcript(driver, mode):

    count = 0
    
    driver.implicitly_wait(10)
    
    if mode=='headed':
        print('Accepting Terms and Conditions')
        accept_T_and_C(driver)
        
        # Click 'More actions' (full xpath)
        #driver.find_elements_by_xpath("//button[@aria-label='More actions']")[1].click()
        driver.find_element_by_xpath("/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[8]/div[2]/ytd-video-primary-info-renderer/div/div/div[3]/div/ytd-menu-renderer/yt-icon-button/button").click()
        
        # Click 'Open transcript'
        driver.find_element_by_xpath("//*[@id='items']/ytd-menu-service-item-renderer/tp-yt-paper-item").click()
        sleep(3)
    
    elif mode=='headless':
        # Click 'More actions'
        try:
            driver.find_element_by_xpath("/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[8]/div[2]/ytd-video-primary-info-renderer/div/div/div[3]/div/ytd-menu-renderer/yt-icon-button/button").click()

        except:
            sleep(3)
            count += 1
            if count < 5:
                driver.refresh()
                get_transcript(driver, mode)
            else:
                print("Error loading page.")
                return None
        
        # Click 'open transcript'
        try:
            #driver.find_element_by_xpath("//*[@id='items']/ytd-menu-service-item-renderer/paper-item").click()
            driver.find_element_by_xpath("//*[@id='items']/ytd-menu-service-item-renderer/tp-yt-paper-item").click()

        except:
            sleep(3)
            count += 1
            if count < 5:
                driver.refresh()
                get_transcript(driver, mode)
            else: 
                print("Error loading page.")
                return None
            
    
    # Get all transcript text
    print("Copying transcript ")
    transcript_element = driver.find_element_by_xpath("//*[@id='body']/ytd-transcript-body-renderer")
    transcript = transcript_element.text

    return transcript

def transcript2df(transcript):
    if transcript == None:
        return "None in transcript."
    transcript = transcript.split('\n')
    transcript_timestamps = transcript[::2]
    
    transcript_text = transcript[1::2]
    df = pd.DataFrame({'timestamp':transcript_timestamps, 
                   'text':transcript_text})
    
    return df


def summary(inp_text):
    summarized_text = summarizer.summarize(
    inp_text, ratio=0.4, language="english", split=True, scores=True)
    sl=0
    summary=''
    for sentence, score in summarized_text:
        summary = summary + " " + sentence
    return summary

def punctuator(sample):

    option = webdriver.ChromeOptions()
    option.add_argument('headless')

    driver = webdriver.Chrome(executable_path=r"chromedriver.exe", options=option)
    driver.get("http://bark.phon.ioc.ee/punctuator")

    search = driver.find_element_by_id("input-text")
    # sample="ever wondered about the differences between AI m LD L and D s well we're about to explore all of those today stay tuned so let's dive right into it so AI versus ml versus do versus dears a whole bunch of jargon but we're going to clarify all of that right up so let's kick things off and take a look at AI so AI is really to do with the ability of computers and machines to perform tasks without explicitly programming them otherwise known as the ability for computers and machines to think by themselves so we typically break out AI into two key categories these are general AI and neuro a on general AI typically refers to the ability for a computer or a machine to be able to handle a wide variety of tasks us as humans have the ability to do a whole heap of stuff we can see we can speak we can hear we can read we can drive we can do a whole range of things the ability for AI and machines to be able to do a broad range of tasks similar to humans is what we typically refer to as general AI now we're still a little bit of a while away from true general AI but that's not to say it's not to come now narrow AI on the other hand is the ability for a machine to handle a really simple or a really narrow range of tasks so that could possibly be the ability to translate speech to text or to classify images as having different categories or the ability to predict house prices for example all of these are examples of narrow AI so I'm going to be painting a bunch of visual imagery to help you remember some of these topics so the first one in terms of breaking out general and narrow AI or the ability to remember general and our AI is just picture a really narrow or really skinny journal in your mind so that way you know that there's two different types of AI general and narrow now on to the next topic machine learning so if taking a look at AI as being broken up into journal and narrow but how does machine learning fit into this well machine learning is the application of narrow AI to specific tasks now when we typically talk about machine learning we often compare it to traditional programming so in traditional programming we supply data plus rules or conditional logic and we get answers now in machine learning on the other hand we provide data plus historical answers to get rules we can then pass new data to get new answers so this is a bit of a change in the paradigm of how computer scientists and machine learning engineers are building programs these days so what are some typical machine learning tasks well we broadly break out machine learning into three key categories these are supervised learning unsupervised learning and semi-supervised learning so let's take a look at supervised learning first so supervised learning can be broadly broken out into two key categories these are classification and regression classification is all to do with grouping things into categories or labels so say you had a big data set on all the different types of pizzas you've liked and whether or not you've liked them yes or no you could take that data and pass it through to a classification algorithm to help but learn which types of pizzas you like so then when you pass through a new list of ingredients it would be able to predict yes you would like that Pizza or no you might not regression on the other hand is all to do with predicting continuous variables some great examples of regression are sales forecasting and predicting prices of houses so that encapsulates supervised learning now what about unsupervised learning well there's two key things to think about when you think of unsupervised learning these are really clustering so the ability to group people together so say you wanted to group together high performing and low performing and medium performing employees or high-value low value medium value customers or a whole bunch of other different types of data but really it's all to do with grouping things together now dimensionality reduction on the other hand is all to do with condensing the features that you've got within a machine learning model so a lot of the time you might start out with a huge data set with a lot of columns and you're not really sure which of those columns are important for your machine learning model dimensionality reduction helps you reduce the number of columns that you've got so that you can really focus on the important ones"
    # sample = """ are you one of the many who dreams of becoming a data scientist keep watching this video if you're passionate about data science because we will tell you how does it really work under the hood emma is a data scientist let's see how a day in her life goes while she's working on a data science project well it is very important to understand the business problem first in our meeting with the clients emma asks relevant questions understands and defines objectives for the problem that needs to be tackled she is a curious soul who asks a lot of eyes one of the many traits of a good data scientist now she gears up for data acquisition to gather and scrape data from multiple sources like web servers logs databases apis and online repositories oh it seems like finding the right data takes both time and effort after the data is gathered comes data preparation this step involves data cleaning and data transformation data cleaning is the most time consuming process as it involves handling many complex scenarios here emma deals with inconsistent data types misspelled attributes missing values duplicate values and what not then in data transformation she modifies the data based on defined mapping rules in a project etl tools like talent and informatica are used to perform complex transformations that helps the team to understand the data structure better then understanding what you actually can do with your data is very crucial for that emma does exploratory data analysis with the help of eda she defines and refines the selection of feature variables that will be used in the model development but what if emma skips this step she might end up choosing the wrong variables which will produce an inaccurate model thus exploratory data analysis becomes the most important step now she proceeds to the core activity of a data science project which is data modeling she repetitively applies diverse machine learning techniques like knn decision tree knife base to the data to identify the model that best fits the business requirement she trains the models on the training data set and test them to select the best performing model emma prefers python for modeling the data however it can also be done using r and sas well the trickiest part is not yet over visualization and communication emma meets the clients again to communicate the business findings in a simple and effective manner to convince the stakeholders she uses tools like tableau power bi and qlikview that can help her in creating powerful reports and dashboards and then finally she deploys and maintains the model she tests the selected model in a pre-production environment before deploying it in the production environment which is the best practice right after successfully deploying it she uses reports and dashboards to get real-time analytics further she also monitors and maintains the project's performance well that's how emma completes the data science project we have seen the daily routine of a data scientist is a whole lot of fun has a lot of interesting aspects and comes with its own share of challenges now let's see how data science is changing the world data science techniques along with genomic data provides a deeper understanding of genetic issues and reaction to particular drugs and diseases logistic companies like dhl fedex have discovered the best rules to ship the best suited time to deliver the best mode of transport to choose thus leading to cost efficiency with data science it is possible to not only predict employee attrition but to also understand the key variables that influence employee turnover also the airline companies can now easily predict flight delay and notify the passengers beforehand to enhance their travel experience well if you're wondering there are various roles offered to a data scientist like data analyst machine learning engineer deep learning engineer data engineer and of course data scientist the median base salaries of a data scientist can range from 95 000 to 165 000 so that was about the data science are you ready to be a data scientist if yes then start today the world of data needs you that's all from my side today thank you for watching comment below the next topic that you want to learn and subscribe to simply learn to get the latest updates on more such interesting videos thank you and keep learning"""
    search.send_keys(sample)
    driver.find_element_by_id('punctuate-btn').click()
    time.sleep(10)
    driver.implicitly_wait(10)
    element = driver.find_element_by_id("output-text")
    # print(element.text)
    # print("Text Printed")
    return element.text

def akaa_2(url):

    #url = "https://www.youtube.com/watch?v=HcqpanDadyQ"
    
    mode = 'headless'
    
    driver = open_url_in_chrome(url, mode)
    
    count = 0
    transcript = get_transcript(driver, mode)
    
    driver.close()
    	
    df = transcript2df(transcript)
    
    print('Saving transcript ')
    df.to_csv('output.csv', index=False) 
    with open("output.txt", "w") as text_file:
        print(" ".join(" ".join(df.text.values).split()), file=text_file)
    print('Done')
    #print(" ".join(" ".join(df.text.values).split()))

    final_t = " ".join(" ".join(df.text.values).split())
    print(final_t)
    print("Transcript printed")
    summ = summary(final_t)
    print(summ)
    print("Summary Printed")

    return summ



def generate_text_summary(link):
    unique_id = link.split("=")[-1]
    sub = YouTubeTranscriptApi.get_transcript(unique_id)
    # print(sub)
    subtitle = " ".join([x['text'] for x in sub])
    subtitle_p = punctuator(subtitle)
    print(subtitle_p)
    #print("Transcript Printed")
    summ = summary(subtitle_p)
    # print(summ)
    print("Summary Printed")

    return summ


#akaa("https://www.youtube.com/watch?v=HcqpanDadyQ")

# akaa("https://www.youtube.com/watch?v=iPUWwpocc1c")

#akaa("https://www.youtube.com/watch?v=ukzFI9rgwfU")