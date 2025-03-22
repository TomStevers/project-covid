# Project Covid
This project contains Python code for analyzing, modeling, and visualizing data related to the Covid-19 virus. The project has the data stored in the files CSV files (cleaned_complete.csv) and SQLite databases (covid_database.db), whose data has been used to gain insight into Covid-19 trends worldwide and in the United States in more detail.

## How to use:

As the code in the repository is written in the language Python, any editor that is applicable for Python should work. However, the creators of the repository have used Visual Studio Code; therefore, the use of Visual Studio Code is recommended.

In the file streamlit.py, the dashboard is generated by calling all functions and plots in the other files. One can get a local copy of the dashboard by entering in their terminal the code: streamlit run streamlit.py.

In the files covid_sird_model.py, covid_statistics_usa.py, and covid_statistics.py, the plots and figures are generated that get called upon in the file streamlit.py. These files use the data from the cleaned_complete.csv as well as from the covid_database.db.

The file complete.csv contains the raw data that was provided to the creators. This file contained many missing values that have been filled in to the best of our abilities. How this was done can be seen in data_wrangling.py. However, some gaps in the data were too large to fill in, as for example, The Netherlands did not provide any amount of recovered cases to the complete.csv. It was decided that significant gaps like that one would just be kept at the value of 0 to prevent any further errors from arising.

## Visualizations on the Dashboard

Most visualizations on the dashboard are self-explanatory. However, when looking at the graphs on the SIRD-model tab, it is recommended to have the cleaned_complete.csv open next to it as this file will provide the explanation of why a certain graph might look incomplete for that particular country. Such would be the case again for The Netherlands, as the recovered line in the SIRD model graph is a straight line at 0. This is, of course, due to the fact that no recovered cases were reported.