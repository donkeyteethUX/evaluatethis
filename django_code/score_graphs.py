import courses
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import graphs

def df_maker(args_from_ui, sentiment_or_score, graph_type):
    '''
    Uses the query functions in courses to get a dataframe corresponding to the user's search, 
    then returns a dataframe reduced by get_small_df that includes the columns required by the
    different possible types of graphs (specified by sentiment_or_score, where the two options
    are "sentiment" or "score"). 
    Depending on the user's input, graph_type can be either "prof" or "course."
    '''
    if graph_type == "prof":
        prof_df, dept_df, dept = courses.find_courses(args_from_ui)
        small_df, year = get_small_df(prof_df, graph_type)
    if graph_type == "course":
        course_df, dept_df = courses.find_courses(args_from_ui)
        dept = args_from_ui['dept']
        small_df, year = get_small_df(course_df, graph_type)

    columns_not_to_graph = ['num_recommend', 
                            'num_dont_recommend', 
                            'good_inst', 
                            'bad_inst']

    small_df.dropna(axis = (1), how = "all", inplace = True)
    if sentiment_or_score == "sentiment":
        columns_not_to_graph += ['course_id', 
                                'low_time', 
                                'avg_time', 
                                'high_time', 
                                'fn', 
                                'ln', 
                                'year', 
                                'num_responses', 
                                'prof_score', 
                                'ass_score', 
                                'test_score',
                                'over_score',
                                'read_score']
    if sentiment_or_score == "score":
        columns_not_to_graph += ['course_id', 
                                'low_time', 
                                'avg_time', 
                                'high_time', 
                                'fn', 
                                'ln', 
                                'year', 
                                'num_responses', 
                                'inst_sentiment', 
                                'course_sentiment']
    columns = list(small_df.columns)
    graph_columns = list(set(columns).difference(columns_not_to_graph))
    small_df = small_df[graph_columns]
    if graph_type == "prof":
        continuous_df = small_df.groupby(['course']).mean()
    if graph_type == "course":
        continuous_df = small_df.groupby(['fn', 'ln']).mean()
    compare_to_dept_columns = list(continuous_df.columns)
    dept_df = dept_df[compare_to_dept_columns].mean()
    dept_df.rename(index = dept, inplace = True)
    continuous_df = continuous_df.append(dept_df)
    
    return continuous_df

def get_small_df(dataframe, prof_or_course):
    '''
    Drops results from successive years from the dataframe so that the resulting graph
    will not have more than 10 groups of columns. 
    This happens in slightly different ways corresponding to the data visualization 
    requirements for "prof" or "course" type graphs. 
    '''
    current_year = 2018
    timespan = 15
    if prof_or_course == "prof":
        while dataframe.course.unique().shape[0] > 10:
            timespan -= 1
            dataframe = dataframe[dataframe.year >= current_year - timespan]
        dataframe = dataframe.groupby(['course']).mean()

    if prof_or_course == "course":
        while dataframe.groupby(['fn', 'ln']).mean().shape[0] > 10:
            timespan -= 1
            dataframe = dataframe[dataframe.year >= current_year - timespan]
        dataframe = dataframe.groupby(['fn', 'ln']).mean()


    return dataframe, current_year - timespan

def graph_from_df(continuous_df):
    '''
    Given a dataframe of continuous non-time data, creates a grouped bar graph displaying scores 
    and sentiment scores for that data. 
    Different versions of matplotlib require you to switch out "left" for "x" sometimes in 
    the line that starts with "bar = "
    The error that will let you know that this is happening is: "bar() missing 1 required positional argument"
    '''
    n = continuous_df.shape[0]
    ind = np.arange(n)
    width = 0.1  
    offset = 0
    plt.figure(figsize = (20, 7))
    bars = []
    for column in continuous_df:
        bar = plt.bar(left = ind - (offset * width), width=width, height=continuous_df[column])
        offset += 1
        bars.append(bar)
    xnames = list(continuous_df.axes[0])
    plt.xticks(ind, xnames, rotation = 10, fontsize = 10, ha = 'right')
    plt.legend(bars, continuous_df.axes[1])
    return plt


def prof_score_graph(args_from_ui):
    '''
    Creates a graph for a professor's scores compared to the department average. 
    '''
    continuous_df = df_maker(args_from_ui, "score", "prof")
    plt = graph_from_df(continuous_df)
    prof = args_from_ui['prof_fn'] + " " + args_from_ui['prof_ln']
    title = prof + "'s aggregated scores compared to dept avg."
    plt.title(title)
    plt.ylabel("Aggregated scores from reviews")
    plt.savefig('./static/images/profscore.png')

def prof_sentiment_graph(args_from_ui):
    '''
    Creates a graph for a professor's sentiment scores compared to the department average. 
    '''
    continuous_df = df_maker(args_from_ui, "sentiment", "prof")
    plt = graph_from_df(continuous_df)
    prof = args_from_ui['prof_fn'] + " " + args_from_ui['prof_ln']
    title = prof + "'s sentiment scores compared to dept avg."
    plt.title(title)
    plt.ylabel("Sentiment scores from reviews")
    plt.savefig('./static/images/profsent.png')

def course_sentiment_graph(args_from_ui):
    '''
    Creates a graph for the sentiment scores for all professors that have taught a
    class compared to the department average. 
    '''
    continuous_df = df_maker(args_from_ui, "sentiment", "course")
    plt = graph_from_df(continuous_df)
    course = args_from_ui['dept'] + " " + args_from_ui['course_num']
    title = "Sentiment scores for " + course + "compared to dept avg."
    plt.title(title)
    plt.ylabel("Sentiment scores from reviews")
    plt.savefig('./static/images/coursesent.png')

def course_score_graph(args_from_ui):
    '''
    Creates a graph for the scores for all professors that have taught a class compared to
    the department average. 
    '''
    continuous_df = df_maker(args_from_ui, "score", "course")
    plt = graph_from_df(continuous_df)
    course = args_from_ui['dept'] + " " + args_from_ui['course_num']
    title = "Aggregated scores for " + course + "compared to dept avg."
    plt.title(title)
    plt.ylabel("Aggregated scores from reviews")
    plt.savefig('./static/images/coursescore.png')

def non_time_graphs(args_from_ui):
    if 'dept' in args_from_ui and 'course_num' in args_from_ui and len(args_from_ui) == 2:
        course_score_graph(args_from_ui)
        course_sentiment_graph(args_from_ui)

    if 'prof_fn' in args_from_ui and 'prof_ln' in args_from_ui and len(args_from_ui) == 2:
        prof_score_graph(args_from_ui)
        prof_sentiment_graph(args_from_ui)

    elif len(args) == 4:
        course_and_prof_score_graph(args_from_ui)
        course_and_prof_sentiment_graph(args_from_ui)