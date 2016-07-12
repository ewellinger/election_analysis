<center><h1>Election Analysis</h1>

<h4>Data Science Capstone Project</h4></center>


## Note: I am currently updating the code and adding more detail to the README
### Should be up by 7/16/2016 so check back soon!
---
The purpose of this project is to scrape a variety of news sites for articles relating to the 2016 U.S. Election cycle as part of my Galvanize Data Science Immersive Capstone Project.  Natural Language Processing analysis will then be done on the text of the articles to see what latent topics are present in the media coverage across a variety of news outlets.  Once latent topics are identified, we can look at how certain topics are trending over time and whether certain outlets are reporting on them more prevalently than others.  While predicting a winner would be nice, the ultimate goal of this project is to identify how the media is reporting on the election and not to predict the outcome.

Analysis was primarily done using Non-Negative Matrix Factorization (NMF) for extracting latent topics from the corpus.  Currently data is present from The New York Times, Fox News, The Guardian, NPR, and The Wall Street Journal ranging from January 1st, 2015, to May 15th, 2016, with 21,160 articles in total.

Future steps could include performing a similar analysis on previous general election cycles (e.g. 2007 for the election cycle of Obama's first election) to identify topics which are perennially present in the coverage of a Presidential election regardless of the candidates or current events.  Twitter data could also be incorporated to compare how social media influences what stories the media reports on (i.e. does the reporting by news outlets drive the discourse on social media or vice-versa?)

Below is an example of one of the latent topics extracted with the [NMF][wiki-nmf] Algorithm.  This graph shows the number of articles attributed to this topic over the course of election cycle (up to May 15th), a breakdown of the normalized percentage of coverage by each news outlet, and a word cloud showing the most prominent words associated with this topic.  Following the explanation of the methodology behind the data collection, processing, and analysis, other topics will be explored.

[wiki-nmf]: https://en.wikipedia.org/wiki/Non-negative_matrix_factorization

![gun_control](./plots/Gun_Control.png "Sample Time Series Graph With WordCloud")

---

### Web-Scraping Methodology

Web Scraping scripts for each of the included news outlets were written employing the python packages `BeautifulSoup` and `selenium`.  Several of the web-scraping scripts also employ multi-threading techniques for performance boosts.  Currently the Dataframe has articles from the following news outlets:

* Fox News (5,739 Articles)
* The New York Times (API) (8,944 Articles)
* The Wall Street Journal (2,419 Articles)
* The Guardian (API) (2,863 Articles)
* NPR (API) (1,195 Articles)

Searches were then performed for each of the following keywords for each day in a particular time period across each news outlet:

```python
keywords = ['jeb bush', 'carson', 'christie', 'cruz', 'fiorina', 'jim gilmore',
            'lindsey graham', 'huckabee', 'kasich', 'george pataki',
            'rand paul', 'rubio', 'santorum', 'donald trump', 'rick perry',
            'scott walker', 'jindal', 'clinton', "o'malley", 'omalley',
            'sanders', 'jim webb', 'chafee', 'lessig', 'biden']
```

All articles that were returned were assumed to be at least cursorily related to the general election (further checks are done to ensure this during the [data cleaning](#data-cleaning) phase) 
Articles pertaining to the general election were then added to a Mongo Database with metadata and article text for further analysis.  In the case of the Fox News and Wall Street Journal scrapers, relevant url addresses were first saved to a text file prior to extracting metadata and article text.

---

### 2016 Candidates
#### Republican

Candidate      | Announcement Date | Suspension Date
---------------|:-----------------:|:--------------:
Ted Cruz       |    03/23/2015     |   05/03/2016
Rand Paul      |    04/07/2015     |   02/03/2016
Marco Rubio    |    04/13/2015     |   03/15/2016
Ben Carson     |    05/04/2015     |   03/02/2016
Carly Fiorina  |    05/04/2015     |   02/10/2016
Mike Huckabee  |    05/05/2015     |   02/01/2016
Rick Santorum  |    05/27/2015     |   02/03/2016
George Pataki  |    05/28/2015     |   12/29/2015
Lindsey Graham |    06/01/2015     |   12/21/2015
Rick Perry     |    06/04/2015     |   09/11/2015
Jeb Bush       |    06/15/2015     |   02/20/2016
Donald Trump   |    06/16/2015     |       N/A
Bobby Jindal   |    06/24/2015     |   11/17/2015
Chris Christie |    06/30/2015     |   02/10/2016
Scott Walker   |    07/13/2015     |   09/21/2015
John Kasich    |    07/21/2015     |   05/04/2016
Jim Gilmore    |    07/30/2015     |   02/12/2016


#### Democratic

Candidate       | Announcement Date | Suspension Date
----------------|:-----------------:|:--------------:
Hillary Clinton |    04/12/2015     |       N/A
Bernie Sanders  |    04/30/2015     |       N/A
Martin O'Malley |    05/30/2015     |   02/01/2016
Lincoln Chafee  |    06/03/2015     |   10/23/2015
Jim Webb        |    07/02/2015     |   10/20/2015
Lawrence Lessig |    09/06/2015     |   11/02/2015
Joe Biden       |        N/A        |   10/21/2015

Below we can see how the media coverage of topics associated with particular candidates compare over the course of the election season.  For brevity, only a select few candidates will be shown for each plot.

![republican_candidates](./candidate_plots/republican.png "Coverage of Top 5 Polling Republican Candidates As Of February 1st, 2016")


![democratic_candidates](./candidate_plots/democrat.png "Coverage of Remaining Democratic Candidates As Of February 1st, 2016")

We can then take a look at each candidate's topic in turn and overlay the dates in which they announced and, if applicable, withdrew their candidacy.  A word cloud indicating the most prominent words for that topic and a breakdown of how prevalently particular news sources were reporting on it are also provided.  For a breakdown of each candidate please refer to the [candidate_plots](./candidate_plots) folder.

**** Imbed some candidate plots here

**NOTE**: It may appear that Hillary Clinton has a relatively few number of articles associated with her topic, but that actually isn't the case.  Due to the media storm around certain aspects of Clinton's candidacy, the NMF algorithm factored the general "Hillary Clinton" topic into multiple topics associated with different aspects of her bid for the Presidency.  For example, topics exist related to her use of a private email server (Topics 3, 4, 198), the Clinton Foundation (Topic 51), and the committee to investigate the Benghazi attack (Topics 30, 98, 222).  We will see later what it means for a more general subject, such as the Benghazi attack, to be factored into multiple topics.

---

### Data Cleaning

Several data cleaning steps were taken in the `clean_data.py` script to read in the data from the Mongo Database and produce the final `pandas` dataframe which the analysis was conducted on.  The resulting dataframe was pickled for easy access in subsequent scripts.

Cleaning Steps Included:
* Convert `date_published` to the proper datetime format
* Remove numbers, email addresses, and punctuation from the article text
* Parse unicode characters from article text
* Filter out any articles whose article text doesn't contain at least one candidate name
* Text Processing / Lemmatization (See Below)
* Add sentiment data to dataframe using `pattern.en` [sentiment][pattern-sentiment] function

A article was then assumed to being pertained to the general election if the body of the article contained one or more of the candidate(s) full names (e.g. A search for `sanders` may yield an article about Deion Sanders rather than Bernie Sanders, which should not be included).

[pattern-sentiment]: http://www.clips.ua.ac.be/pages/pattern-en#sentiment

---

### Text Processing

#### Stop Words

#### Lemmatization

#### TFIDF Matrix
Quickly go over word count matrices and how they differ from a TFIDF matrix

---

### Non-Negative Matrix Factorization
Overview of NMF and how it works to decompose our our TFIDF matrix into latent topics.

#### How Does NMF Differ From K-Means Clustering?
* Doesn't impose a strict clustering
* K-means isn't deterministic and could potentially converge to non-optimal solutions
* For my project, I chose to assign a particular article to a topic if it was at least 10% attributable to a topic
    * What does it mean to have no articles assigned to a topic?

#### How many latent topics should we look for?
Rundown of the challenges associated with trying to determine the number of topics to factorize into.  Include nmf_similarity plot and give a rundown of the thinking behind it as well as the PCA scree plot that gives another approach to the same question.

---

### `NMFClustering` Class
Overview of how this class works and a rundown of each of the available methods

---

### Interpreting Topics
How do we get the label for a topic?  Give a print out of the summary for a particular topic and ask the reader to think about what they think that topic is about.
Print out another topic that is a "junk" topic which isn't really indicative of anything in particular.
After determining the number of topics to factorize into, a manual inspection of each of the resulting topics is performed to determine what that topic is about.
Include a table with each of the topic labels...
Maybe touch on the challenge of incorporating new data into the analysis.  Topics change, the number of topics that are covered in the political discourse changes, and the order of the resulting topics changes which necessitate performing the analysis over again.  :(

---

### `ElectionPlotting` Class
Overview of how this class works and a sampling of what kind of plots can be made.

---

### Topics, Topics, Topics!
Show some of the cooler plots here

---

### Thanks
Thank people and shit...
