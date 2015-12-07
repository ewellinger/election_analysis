<center><h1>Election Analysis</h1>

<h4>Data Science Capstone Project</h4></center>

---
The purpose of this project is to scrape a variety of news sites for articles covering the 2016 U.S. Election cycle throughout 2015 as part of the Galvanize Data Science Immersive Capstone Project.  Natural Language Processing analysis will then be done on the text of the articles to see what sort of trends can be found in the coverage throughout the year.

Time permitting, similar analysis will be done on previous general election cycles (e.g. 2007 for the election cycle of Obama's first election).

Preliminary news outlets to scrape include:
* The New York Times
* The Washington Post
* Fox News
* MSNBC
* CNN
* ABC News
* NBC News
* The Wall Street Journal
* NPR
* BBC
* Al Jazeera

Articles pertaining to the general election will then be added to a Mongo Database with metadata and raw HTML for further analysis.  A article will be classified as pertaining to the general election if the headline of the article contains one or more of the following keywords:
```python
keywords = ['clinton', 'sanders', 'trump', 'perry', 'carson', "o'malley",
            'cristie', 'bush', '']
```
