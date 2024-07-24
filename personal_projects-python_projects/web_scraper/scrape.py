from collections import deque
import pandas as pd
import os
import time
import requests
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By


class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []
        self.todoque = deque([])

    def visit_and_get_children(self, node):
        """ Record the node value in self.order, and return its children
        param: node
        return: children of the given node
        """
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        self.visited.clear()
        self.order = []
        self.dfs_visit(node)

    def dfs_visit(self, node):
        if node in self.visited:
            return
        else:
            self.visited.add(node)
        children = self.visit_and_get_children(node)
        for child in children:
            self.dfs_visit(child)
            
    def bfs_search(self, node):
        self.order = []
        self.added = {node}
        self.todoque.append(node)
    
        while len(self.todoque) > 0:
            curr_node = self.todoque.popleft()
            for child in self.visit_and_get_children(curr_node):
                if not (child in self.added):
                    self.todoque.append(child)
                    self.added.add(child)

                    
class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__()
        self.df = df

    def visit_and_get_children(self, node):
        self.order.append(node)
        return [child for child, has_edge in self.df.loc[node].items() if has_edge == 1]



class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()

    def visit_and_get_children(self, node):
        children = []
        value = None
        with open(os.path.join("file_nodes", f'{node}'), 'r') as file: 
            lines = file.read().splitlines()
            if lines:
                value = lines[0]
                for x in lines:
                    if ',' in x:
                        children = x.split(',')
        if value is not None:
            self.order.append(value)
        return children

    def concat_order(self):
        return ''.join(self.order)



class WebSearcher(GraphSearcher):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.rows = []
        
    def visit_and_get_children(self, url):
        childs = []
        self.driver.get(url)
        source = self.driver.page_source
        data = pd.read_html(source)[0]
        self.rows.append(data)
        for element in self.driver.find_elements("tag name", "a"):
            child = element.get_attribute("href")
            childs.append(child)
        self.order.append(url)
        return childs

    def table(self):
        self.table = pd.concat(self.rows, ignore_index = True)
        return self.table
    
# exapmle of how to use these searching algo's
def reveal_secrets(driver, url, travellog):
    clues_values = travellog['clue']
    to_string = clues_values.astype(str)
    password = ''.join(to_string)
    driver.get(url)
    driver.find_element(by = By.XPATH, value = '//*[@id="password-textbox"]').send_keys(password)
    driver.find_element(by = By.XPATH, value = '//*[@id="submit-button"]').click()
    time.sleep(0.5)
    driver.find_element(by = By.XPATH, value = '//*[@id="location-button"]').click()
    time.sleep(1)
    location = driver.find_element(by = By.XPATH, value = '//*[@id="location"]').text
    img_url = driver.find_element(by = By.XPATH, value = '//*[@id="image"]').get_attribute('src')
    response = requests.get(img_url, stream=True)
    response.raise_for_status()
    with open('Current_Location.jpg', 'wb') as out_file:
        out_file.write(response.content)
    return location 
