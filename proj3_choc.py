import sqlite3
import pandas as pd
import re
import plotly.graph_objs as go

# Part 1: Read data from a database called choc.db
DBNAME = 'choc.sqlite'

# Part 1: Implement logic to process user commands
def fetch_db(query):
    connection = sqlite3.connect(DBNAME)
    cursor = connection.cursor()
    result = cursor.execute(query).fetchall()
    connection.close()
    return result

def bar_plot(xvalue,yvalue):
    graph=go.Bar(x=xvalue,y=yvalue)
    fig=go.Figure(data=graph)
    return fig.show()

def process_command(command):
    '''Take a command string and returns a list of tuples representing records that match the query. 
       If 'barplot' is provided, display a barplot which nicely visualizes the results.
    
    Parameters
    ----------
    command: string
        The command string represents a query that the user want to run
    
    Returns
    -------
    list
        a list of tuples that represent the query result
    '''
    identifier = command.split(' ')[0]
    if identifier == 'bars':
        results = Command().bars(command)
        if 'barplot' in command:
            xval = [result[0] for result in results]
            if 'cocoa' in command:
                yval=[result[4] for result in results]
                bar_plot(xval,yval)
            else:
                yval=[result[3] for result in results]
                bar_plot(xval,yval)

    elif identifier == 'countries':
        results = Command().countries(command)
        if 'barplot' in command:
            xval = [result[0] for result in results]
            yval = [result[2] for result in results]
            bar_plot(xval,yval)

    elif identifier == 'companies':
        results = Command().companies(command)
        if 'barplot' in command:
            xval = [result[0] for result in results]
            yval = [result[2] for result in results]
            bar_plot(xval,yval)

    else:
        results = Command().regions(command)
        if 'barplot' in command:
            xval = [result[0] for result in results]
            yval = [result[1] for result in results]
            bar_plot(xval,yval)        
    return results

def print_query_result(command):
    ''' Pretty prints raw query result 
    
    Parameters
    ----------
    command: string
        The command string represents a query that the user want to run
    
    Returns
    -------
    None
    '''
    results_list = process_command(command)
    identifier = command.split(' ')[0]
    format_list=[]
    if identifier == 'bars':
        for results in results_list:
            results=list(results)
            results[4]='{:.0%}'.format(results[4])
            results=tuple(results)
            format_list.append(results)
        results_list=format_list
    else:
        if 'cocoa' in command:
            for results in results_list:
                results=list(results)
                if len(results) == 3:
                    results[2]='{:.0%}'.format(results[2])
                    results=tuple(results)
                    format_list.append(results)
                else:
                    results[1]='{:.0%}'.format(results[1])
                    results=tuple(results)
                    format_list.append(results)
            results_list=format_list
        
    pd.set_option('max_colwidth',16)
    df= pd.DataFrame(results_list)
    return df.to_string(index=False,header=False,max_colwidth=16)

class Command:
    '''A command.

    Instance Attributes
    -------------------
    None
    '''
    def __init__(self):
        self.areas = 'none'
        self.sources = 'sell'
        self.filters = 'b.Rating'
        self.orders = 'desc'
        self.integer = 10

    def bars(self,command):
        ''' Constructs and executes SQL query to retrieve data 
        based on the high level command bars, and its valid options
        
        Parameters
        ----------
        command: string
            The command string represents a query that the user want to run

        Returns
        -------
        list
            a list of tuples that represent the query result
        '''
        select = f"select b.SpecificBeanBarName,b.Company,c.EnglishName,b.Rating,b.CocoaPercent,o.EnglishName from Bars b \
                   left join Countries c on b.CompanyLocationId = c.Id left join Countries o on b.BroadBeanOriginId=o.Id"
        parameter_num = command.split(' ')
        area_index = [key for key,val in enumerate(parameter_num) if 'country' in val or 'region' in val]
        filter_index =[key for key,val in enumerate(parameter_num) if 'cocoa' in val or 'ratings' in val]
        order_index = [key for key,val in enumerate(parameter_num) if 'top' in val or 'bottom' in val]
        integer_index =[key for key,val in enumerate(parameter_num) if val.isnumeric() == True]

        if area_index:
            area = parameter_num[area_index[0]].split('=')[1]
            if parameter_num[area_index[0]].split('=')[0] == 'country':
                if 'source' in command:
                    self.areas = f'o.Alpha2=\'{area.upper()}\''
                else:
                    self.areas= f'c.Alpha2=\'{area.upper()}\''
            else:
                if 'source' in command:
                    self.areas = f'o.Region=\'{area.capitalize()}\''
                else:
                    self.areas = f'c.Region=\'{area.capitalize()}\''

        if filter_index:
            if parameter_num[filter_index[0]] == 'cocoa':
                self.filters = 'b.CocoaPercent'

        if order_index:
            if parameter_num[order_index[0]] == 'bottom':
                self.orders = 'asc'
        
        if integer_index:
            self.integer = parameter_num[integer_index[0]]
        
        if 'country' in command or 'region' in command:
            return fetch_db(select+f' where {self.areas} order by {self.filters} {self.orders} limit {self.integer}')
        else:
            return fetch_db(select+f' order by {self.filters} {self.orders} limit {self.integer}')

    def companies(self,command):
        ''' Constructs and executes SQL query to retrieve data 
        based on the high level command countries, and its valid options
        
        Parameters
        ----------
        command: string
            The command string represents a query that the user want to run

        Returns
        -------
        list
            a list of tuples that represent the query result
        '''
        parameter_num = command.split(' ')
        area_index = [key for key,val in enumerate(parameter_num) if 'country' in val or 'region' in val]
        filter_index =[key for key,val in enumerate(parameter_num) if 'cocoa' in val or 'ratings' in val or 'number_of_bars' in val]
        order_index = [key for key,val in enumerate(parameter_num) if 'top' in val or 'bottom' in val]
        integer_index =[key for key,val in enumerate(parameter_num) if val.isnumeric() == True]

        if area_index:
            area = parameter_num[area_index[0]].split('=')[1]
            if parameter_num[area_index[0]].split('=')[0] == 'country':
                self.areas = f'c.Alpha2=\'{area.upper()}\''
            else:
                self.areas = f'c.Region=\'{area.capitalize()}\''

        if filter_index:
            if parameter_num[filter_index[0]] == 'cocoa':
                self.filters = 'b.CocoaPercent'
            elif parameter_num[filter_index[0]] == 'number_of_bars':
                self.filters = 'b.Id'

        if order_index:
            if parameter_num[order_index[0]] == 'bottom':
                self.orders = 'asc'
        
        if integer_index:
            self.integer = parameter_num[integer_index[0]]

        if self.filters == 'b.CocoaPercent':
            if 'country' in command or 'region' in command:
                return fetch_db(f'select b.Company,c.EnglishName,round(avg({self.filters}),2) as AvgCocoaPercent \
                                  from Bars b left join Countries c on b.CompanyLocationId=c.Id \
                                  where {self.areas} group by b.Company having count(b.Id)>4 \
                                  order by avg({self.filters}) {self.orders} limit {self.integer}')
            else:
                return fetch_db(f'select b.Company,c.EnglishName,round(avg({self.filters}),2) as AvgCocoaPercent \
                                  from Bars b left join Countries c on b.CompanyLocationId=c.Id \
                                  group by b.Company having count(b.Id)>4 \
                                  order by avg({self.filters}) {self.orders} limit {self.integer}')
        elif self.filters == 'b.Id':
            if 'country' in command or 'region' in command:
                return fetch_db(f'select b.Company,c.EnglishName,count({self.filters}) as NumberOfBars \
                                  from Bars b left join Countries c on b.CompanyLocationId=c.Id \
                                  where {self.areas} group by b.Company having NumberOfBars>4 \
                                  order by NumberOfBars {self.orders} limit {self.integer}')
            else:
                return fetch_db(f'select b.Company,c.EnglishName,count({self.filters}) as NumberOfBars \
                                  from Bars b left join Countries c on b.CompanyLocationId=c.Id \
                                  group by b.Company having NumberOfBars>4 \
                                  order by NumberOfBars {self.orders} limit {self.integer}')
 
        else:
            if 'country' in command or 'region' in command:
                return fetch_db(f'select b.Company,c.EnglishName,round(avg({self.filters}),1) as AverageRating \
                           from Bars b left join Countries c on b.CompanyLocationId=c.Id \
                           where {self.areas} group by b.Company having count(b.Id)>4 \
                           order by avg({self.filters}) {self.orders} limit {self.integer}')
            else:
                return fetch_db(f'select b.Company,c.EnglishName,round(avg({self.filters}),1) as AverageRating \
                           from Bars b left join Countries c on b.CompanyLocationId=c.Id \
                           group by b.Company having count(b.Id)>4 \
                           order by avg({self.filters}) {self.orders} limit {self.integer}')

    def countries(self,command):
        ''' Constructs and executes SQL query to retrieve data 
        based on the high level command countries, and its valid options
        
        Parameters
        ----------
        command: string
            The command string represents a query that the user want to run

        Returns
        -------
        list
            a list of tuples that represent the query result
        '''
        parameter_num = command.split(' ')
        area_index = [key for key,val in enumerate(parameter_num) if 'region' in val]
        filter_index =[key for key,val in enumerate(parameter_num) if 'cocoa' in val or 'ratings' in val or 'number_of_bars' in val]
        order_index = [key for key,val in enumerate(parameter_num) if 'top' in val or 'bottom' in val]
        integer_index =[key for key,val in enumerate(parameter_num) if val.isnumeric() == True]

        if area_index:
            area = parameter_num[area_index[0]].split('=')[1]
            if parameter_num[area_index[0]].split('=')[0] == 'region':
                self.areas = f'c.Region=\'{area.capitalize()}\''

        if filter_index:
            if parameter_num[filter_index[0]] == 'cocoa':
                self.filters = 'b.CocoaPercent'
            elif parameter_num[filter_index[0]] == 'number_of_bars':
                self.filters = 'b.Id'

        if order_index:
            if parameter_num[order_index[0]] == 'bottom':
                self.orders = 'asc'
        
        if integer_index:
            self.integer = parameter_num[integer_index[0]]
        
        if self.filters == 'b.CocoaPercent':
            if 'region' in command:
                if 'source' in command:
                    return fetch_db(f'select c.EnglishName,c.Region,round(avg({self.filters}),2) as AvgCocoaPercent \
                                  from Bars b left join Countries c on b.BroadBeanOriginId=c.Id \
                                  where {self.areas} group by c.Id having count(b.Id)>4 \
                                  order by avg({self.filters}) {self.orders} limit {self.integer}')
                else:
                    return fetch_db(f'select c.EnglishName,c.Region,round(avg({self.filters}),2) as AvgCocoaPercent \
                                  from Bars b left join Countries c on b.CompanyLocationId=c.Id \
                                  where {self.areas} group by c.Id having count(b.Id)>4 \
                                  order by avg({self.filters}) {self.orders} limit {self.integer}')
            else:
                if 'source' in command:
                    return fetch_db(f'select c.EnglishName,c.Region,round(avg({self.filters}),2) as AvgCocoaPercent \
                                  from Bars b left join Countries c on b.BroadBeanOriginId=c.Id \
                                  group by c.Id having count(b.Id)>4 \
                                  order by avg({self.filters}) {self.orders} limit {self.integer}')
                else: 
                    return fetch_db(f'select c.EnglishName,c.Region,round(avg({self.filters}),2) as AvgCocoaPercent \
                                  from Bars b left join Countries c on b.CompanyLocationId=c.Id \
                                  group by c.Id having count(b.Id)>4 \
                                  order by avg({self.filters}) {self.orders} limit {self.integer}')


        elif self.filters == 'b.Id':
            if 'region' in command:
                if 'source' in command:
                    return fetch_db(f'select c.EnglishName,c.Region,count({self.filters}) as NumberOfBars \
                                  from Bars b left join Countries c on b.BroadBeanOriginId=c.Id \
                                  where {self.areas} group by c.Id having NumberofBars>4 \
                                  order by NumberOfBars {self.orders} limit {self.integer}')
                else:
                    return fetch_db(f'select c.EnglishName,c.Region,count({self.filters}) as NumberOfBars \
                                  from Bars b left join Countries c on b.CompanyLocationId=c.Id \
                                  where {self.areas} group by c.Id having NumberofBars>4 \
                                  order by NumberOfBars {self.orders} limit {self.integer}')
            else:
                if 'source' in command:
                    return fetch_db(f'select c.EnglishName,c.Region,count({self.filters}) as NumberOfBars \
                                  from Bars b left join Countries c on b.BroadBeanOriginId=c.Id \
                                  group by c.Id having NumberOfBars>4 \
                                  order by NumberOfBars {self.orders} limit {self.integer}')
                else:
                    return fetch_db(f'select c.EnglishName,c.Region,count({self.filters}) as NumberOfBars \
                                  from Bars b left join Countries c on b.CompanyLocationId=c.Id \
                                  group by c.Id having NumberOfBars>4 \
                                  order by NumberOfBars {self.orders} limit {self.integer}')
        
        else:
            if 'region' in command:
                if 'source' in command:
                    return fetch_db(f'select c.EnglishName,c.Region,round(avg({self.filters}),1) as AverageRating \
                                  from Bars b left join Countries c on b.BroadBeanOriginId=c.Id \
                                  where {self.areas} group by c.Id having count(b.Id)>4 \
                                  order by avg({self.filters}) {self.orders} limit {self.integer}')
                else:
                    return fetch_db(f'select c.EnglishName,c.Region,round(avg({self.filters}),1) as AverageRating \
                                  from Bars b left join Countries c on b.CompanyLocationId=c.Id \
                                  where {self.areas} group by c.Id having count(b.Id)>4 \
                                  order by avg({self.filters}) {self.orders} limit {self.integer}')
            else:
                if 'source' in command:
                    return fetch_db(f'select c.EnglishName,c.Region,round(avg({self.filters}),1) as AverageRating \
                                  from Bars b left join Countries c on b.BroadBeanOriginId=c.Id \
                                  group by c.Id having count(b.Id)>4 \
                                  order by avg({self.filters}) {self.orders} limit {self.integer}') 
                else:
                    return fetch_db(f'select c.EnglishName,c.Region,round(avg({self.filters}),1) as AverageRating \
                                  from Bars b left join Countries c on b.CompanyLocationId=c.Id \
                                  group by c.Id having count(b.Id)>4 \
                                  order by avg({self.filters}) {self.orders} limit {self.integer}') 

    def regions(self, command):
        ''' Constructs and executes SQL query to retrieve data 
        based on the high level command regions, and its valid options
        
        Parameters
        ----------
        command: string
            The command string represents a query that the user want to run

        Returns
        -------
        list
            a list of tuples that represent the query result
        '''
        parameter_num = command.split(' ')
        filter_index =[key for key,val in enumerate(parameter_num) if 'cocoa' in val or 'ratings' in val or 'number_of_bars' in val]
        order_index = [key for key,val in enumerate(parameter_num) if 'top' in val or 'bottom' in val]
        integer_index =[key for key,val in enumerate(parameter_num) if val.isnumeric() == True]

        if filter_index:
            if parameter_num[filter_index[0]] == 'cocoa':
                self.filters = 'b.CocoaPercent'
            elif parameter_num[filter_index[0]] == 'number_of_bars':
                self.filters = 'b.Id'

        if order_index:
            if parameter_num[order_index[0]] == 'bottom':
                self.orders = 'asc'
        
        if integer_index:
            self.integer = parameter_num[integer_index[0]]
       
        if self.filters == 'b.CocoaPercent':
            if 'source' in command:
                return fetch_db(f'select c.Region,round(avg({self.filters}),2) as AvgCocoaPercent \
                                  from Bars b left join Countries c on b.BroadBeanOriginId=c.Id \
                                  group by c.Region having count(b.Id)>4 \
                                  order by avg({self.filters}) {self.orders} limit {self.integer}')
            else:
                return fetch_db(f'select c.Region,round(avg({self.filters}),2) as AvgCocoaPercent \
                                  from Bars b left join Countries c on b.CompanyLocationId=c.Id \
                                  group by c.Region having count(b.Id)>4 \
                                  order by avg({self.filters}) {self.orders} limit {self.integer}')

        elif self.filters == 'b.Id':
            if 'source' in command:
                return fetch_db(f'select c.Region,count({self.filters}) as NumberOfBars \
                                  from Bars b left join Countries c on b.BroadBeanOriginId=c.Id \
                                  group by c.Region having count(b.Id)>4 \
                                  order by NumberOfBars {self.orders} limit {self.integer}')
            else:
                return fetch_db(f'select c.Region,count({self.filters}) as NumberOfBars \
                                  from Bars b left join Countries c on b.CompanyLocationId=c.Id \
                                  group by c.Region having count(b.Id)>4 \
                                  order by NumberOfBars {self.orders} limit {self.integer}')
        else:
            if 'source' in command:
                return fetch_db(f'select c.Region,round(avg({self.filters}),1) as AverageRating \
                                  from Bars b left join Countries c on b.BroadBeanOriginId=c.Id \
                                  group by c.Region having count(b.Id)>4 \
                                  order by avg({self.filters}) {self.orders} limit {self.integer}')
            else:
                return fetch_db(f'select c.Region,round(avg({self.filters}),1) as AverageRating \
                                  from Bars b left join Countries c on b.CompanyLocationId=c.Id \
                                  group by c.Region having count(b.Id)>4 \
                                  order by avg({self.filters}) {self.orders} limit {self.integer}')
def load_help_text():
    with open('Proj3Help.txt') as f:
        return f.read()

# Part 2 & 3: Implement interactive prompt and plotting. We've started for you!
def interactive_prompt():
    help_text = load_help_text()
    response = ''
    commands_list =['bars','countries','companies','regions','']
    bars_list = ['none','sell','source','ratings','cocoa','top','bottom','barplot']
    companies_list = ['none','number_of_bars','ratings','cocoa','top','bottom','barplot']
    countries_list = ['none','sell','source','number_of_bars','ratings','cocoa','top','bottom','barplot']
    regions_list= ['sell','source','number_of_bars','ratings','cocoa','top','bottom','barplot']

    while response != 'exit':
        response = input('Enter a command: ').lower()
        words = response.split(' ')
        if response == 'help':
            print(help_text)
            continue
        elif response == 'exit':
            print('Bye')
            exit()
        else:
            if words[0] not in commands_list[:5] or (words[0] == commands_list[4] and len(words)!=1):
                print('Command not recognized. You can enter \'help\' to view valid options.')
                continue
            elif words[0] == commands_list[4] and len(words)==1:
                print((print_query_result('bars')))
            else:      
                if words[0] !='regions':
                    if 'country' in response or 'region' in response:
                        areas_index = [key for key,val in enumerate(words) if 'region' in val or 'country' in val]
                        words.remove(words[areas_index[0]])

                bars_validity = False
                companies_validity= False
                countries_validity= False
                regions_validity = False

                if words[0] == 'bars':
                    bars_validity = all(word in bars_list for word in words[1:] if word.isnumeric()==False)
                elif words[0] =='companies':
                    companies_validity = all(word in companies_list for word in words[1:] if word.isnumeric()==False) 
                elif words[0] =='regions':
                    regions_validity = all(word in regions_list for word in words[1:] if word.isnumeric()==False) 
                else:
                    countries_validity = all(word in countries_list for word in words[1:] if word.isnumeric()==False) 
                
                if words[0] !='regions':
                    if 'country' in response or 'region' in response:
                        result = response.split(' ')
                        areas_index = [key for key,val in enumerate(result) if 'region' in val or 'country' in val]
                        areas_validity = re.match('country=[a-z][a-z]|region=[a-z]+',result[areas_index[0]])

                        if areas_validity:
                            if bars_validity is True or companies_validity is True or countries_validity is True or regions_validity is True:
                                print(print_query_result(response))
                                continue
                            else:
                                print('Command not recognized. You can enter \'help\' to view valid options.')
                                continue
                        else:
                            print('Command not recognized. You can enter \'help\' to view valid options.')
                            continue
                    else:
                        if bars_validity is True or companies_validity is True or countries_validity is True or regions_validity is True:
                            print(print_query_result(response))
                            continue
                        else:
                            print('Command not recognized. You can enter \'help\' to view valid options.')
                            continue
                else:
                    if bars_validity is True or companies_validity is True or countries_validity is True or regions_validity is True:
                        print(print_query_result(response))
                        continue  
                    else:
                        print('Command not recognized. You can enter \'help\' to view valid options.')
                        continue
    else:
        print('Bye')
        exit()

# Make sure nothing runs or prints out when this file is run as a module/library
if __name__=="__main__":
    interactive_prompt()

