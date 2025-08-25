# Overview
This repository features Leveraging Large Language Models, Sentiment Analytics (Tagging reviews, Grouping reviews based on topics, extracting relevant phrases) & app development.

## About:
This is a deployable Web application that aids with the analysis on Voice of the customer from Google Maps Reviews.

#### This app provides insights on the following:
> Market Buzz: What is that people are talking about? <br>

> Customer Experience: What are the Delight Factors & Pain Points?<br>

> Product Offering: What do people say on the Product Offerings?<br>

> Brand Reputation: How the brand fairs from the lens of a customer?<br>

> Competitive Advantage: Where do we stand amidst competition?<br>

### Architecture:
![Alt text](process.jpg)

- Web Scraping <br>
- Leveraging LLM for extracting information <br>
- Structuring the LLM response <br>
- App development for Visualization <br>

### Dataset: <br>
The dataset is derived from Google Maps reviews that is available open source on maps.google.com.<br>
I have considered certain top jewellery brands from USA & GCC market for my analysis. 
The data is web scraped using Google Maps Reviews Scraper created by Compass and maintained by Apify.
**This data is opensource and publicly available**

### Pre requisites
- The following should be installed in your local environment:
> git <br>

> pip <br>

> python3 <br>
- An active OpenAI API key <br>
- A suitable IDE for making any changes to the code.

### How to use this repository?
- Fork the repository <br>
- Clone your forked repo to your local <br>
`git clone https://github.com/sundarram1608/Google-Review-Analytics.git`
- Open terminal and follow the below CLI prompts one by one<br>
`cd “path to directory“` <br>
`python3 -m venv myenv` <br>
`source myenv/bin/activate` <br>
`pip install -r requirements.txt` <br>
`streamlit run GMB_Sentiment_Analytics.py` <br>

The App is up and running.



