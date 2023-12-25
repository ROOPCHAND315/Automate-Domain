from selenium import webdriver
import time
from rich import print
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import mysql.connector
class Auto_Domain_Source():
    def __init__(self):
        self.LOCAL_USERNAME='roop'
        self.LOCAL_PASSWORD='roop@12345'
        self.LIVE_USERNAME=''
        self.LIVE_PASSWORD=''
        self.type='local'
        self.options=webdriver.ChromeOptions()
        self.driver=webdriver.Chrome(options=self.options)
    def mql_connection(self):
        try:
            db = mysql.connector.connect(
                host='10.5.50.221',
                port=3306,
                user='newsusr',
                password='q-jXhjB-mA18USpD',
                database='newsdashdb',
                autocommit=True
            )
            return (db, db.cursor())
        except Exception as e:
            logging.error(str(e), exc_info=True)
            return None, None    
    def read_domain_from_exel(self,domain_name=None,data_type=None):
        # print(f"inside read sheet   {domain_name}   {data_type}")
        try:
            sheet_path='/home/roopchand/projects/newsdatafeeds/feeds_crawler/spiders_data/Spiders_Data.xlsx'

            if data_type=='doamin_name':
                df=pd.read_excel(sheet_path,sheet_name='Domains')
                domain_lists=df['Name'].to_list()
                return domain_lists
            
            elif data_type == 'domain_data':
                df2 = pd.read_excel(sheet_path, sheet_name='Domains')
                entry = df2[df2['Name'] == domain_name]
                if not entry.empty:
                    domain_data_dict = entry.to_dict(orient='records')[0]
                    return domain_data_dict
                
            elif data_type == 'xpath_data':
                df3=pd.read_excel(sheet_path,sheet_name='Xpath')
                filtered_rows = df3[(df3['Name'] == domain_name)]
                # print(f"fff {filtered_rows}")
                return filtered_rows
            elif data_type == 'source_data':
                df4=pd.read_excel(sheet_path,sheet_name='Sources')
                filtered_rows=df4
                return filtered_rows


        except Exception as err:
            print(f"Error reading Excel file: {err}")
            # return []        
    def open_dashboard(self):
        if self.type=='local':
            try:
                Domain_names=self.read_domain_from_exel(domain_name=None,data_type='doamin_name')
                time.sleep(1)
                self.driver.get(f'http://dashboard.newsdata.remote/newsdata_feeds/domain/')
                Username = self.driver.find_element('xpath', '//*[@id="id_username"]')
                Username.send_keys(self.LOCAL_USERNAME)
                Password = self.driver.find_element("xpath", '//*[@id="id_password"]') 
                Password.send_keys(self.LOCAL_PASSWORD)
                Log_In = self.driver.find_element("xpath", '//*[@id="login-form"]/div[3]/input')
                Log_In.click()
                for Domain_name in Domain_names:
                    db, cursor = self.mql_connection()
                    Domain_name = str(Domain_name)
                    query = "SELECT name FROM domain WHERE domain.name = %s"
                    cursor.execute(query, (Domain_name,))
                    result = cursor.fetchall()
                    
                    if result:
                        print(f"Already Added this Domain!")
                        continue
                    else:
                        print(f"dddddddddd {Domain_name}")
                    db.close()


                    add_doamin=self.driver.find_element("xpath",'//div[@id="content-main"]/ul/li/a').click()
                    
                    self.add_domain(Domain_name)  
                
            except Exception as err:
                print(f"Authentication Failed !! {err}")      
        else:
            # live url
            pass

    def add_domain(self,Domain_name):
        try:
            domain_name=Domain_name
            Domains_data=self.read_domain_from_exel(domain_name=domain_name,data_type='domain_data')
            names =Domains_data['Name']
            domains = Domains_data['Domain']
            display_names =Domains_data['Display_Name']
            prioritys = Domains_data['Priority']
            descriptions = Domains_data['Description']
            print(f"{names} {domains} {display_names}  {prioritys} {descriptions}")

            name_field = self.driver.find_element('xpath', '//div[@class="form-row field-name"]//input[@id="id_name"]')
            name_field.send_keys(names)
            time.sleep(2)
            # int(input("Inter any number!"))
            domain_field = self.driver.find_element("xpath", '//div[@class="form-row field-domain"]//input[@id="id_domain"]')
            domain_field.send_keys(domains)
            # int(input("Inter any number!")) 
            display_name_field = self.driver.find_element("xpath", '//*[@id="id_display_name"]')
            display_name_field.send_keys(display_names)
            time.sleep(2)
            # int(input("Inter any number!")) 

            connection = self.driver.find_element("xpath", "//span[@role='combobox']").click()
            time.sleep(1)
            connection = self.driver.find_element("xpath", "//span[@class='select2-results']/ul/li[2]").click()

            time.sleep(2)
      
    

            priority_field = self.driver.find_element('xpath', "//input[@id='id_priority']")
            priority_field.send_keys(int(prioritys))
            # int(input("Inter any number!")) 
            # if entry['UserAgent'] == 'UserAgent':
            #     user_agent_field = self.driver.find_element(
            #         "xpath", "//textarea[@id='id_user_agent']")
            #     user_agent_field.send_keys(
            #         'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36')
            # # time.sleep(4)

            desciption_field = self.driver.find_element('xpath', "//textarea[@id='id_description']")
            desciption_field.send_keys(descriptions)

            Is_Full_Description_field = self.driver.find_element('xpath', "//select[@id='id_is_full_description']/option[@value='1']").click()
            time.sleep(2)
            self.add_xpath(domain_name)
        except:
            pass    
        # Add_xpath = self.driver.find_element("xpath", "//div[@class='submit-row']/input[3]").click()
        time.sleep(3)

        # int(input("Inter any number last!"))

    def add_xpath(self,Domain_name):
        try:
            domain_name=Domain_name
            xpath_dframe=self.read_domain_from_exel(domain_name=domain_name,data_type='xpath_data')
            # print(f"Inside addxpath {xpath_dframe}")
            fd_xpaths=xpath_dframe['Fd_Xpath'].tolist()
            fd_priority=xpath_dframe['Fd_priority'].tolist()
            image_xpaths=xpath_dframe['Image_Xpath'].tolist()
            img_priority=xpath_dframe['Img_priority'].tolist()
            print(f"{fd_xpaths} {fd_priority} ->   {image_xpaths}  {img_priority}")
            if fd_xpaths:
                for xpath,fd_pri in zip(fd_xpaths,fd_priority):
                    # int(input("add xpath !"))
                    time.sleep(3)
                    add_xpath=self.driver.find_element("xpath","(//tbody)[3]/tr[last()]//a").click()
                    time.sleep(2)
                    # int(input("inster to next ! "))
                    send_xpath=self.driver.find_element("xpath","(//tbody)[3]/tr[last()-2]/td[2]/textarea")
                    send_xpath.send_keys(xpath)

                    fd_priority=self.driver.find_element("xpath","(//tbody)[3]/tr[last()-2]/td[6]/input[@type='number']")
                    fd_priority.clear()
                    fd_priority.send_keys(fd_pri)
                    # int(input("xpath input!!! "))
            if image_xpaths:
                for xpath,img_pri in zip(image_xpaths,img_priority):
                    time.sleep(2)
                    add_xpath=self.driver.find_element("xpath","(//tbody)[3]/tr[last()]//a").click()
                    time.sleep(2)
                    # int(input("inster to next ! "))
                    send_xpath=self.driver.find_element("xpath","(//tbody)[3]/tr[last()-2]/td[2]/textarea")
                    send_xpath.send_keys(xpath)

                    is_img=self.driver.find_element("xpath","(//tbody)[3]/tr[last()-2]/td[5]/input[@type='checkbox']").click()
                    # int(input("xpath input!!! "))                    
                    img_priority=self.driver.find_element("xpath","(//tbody)[3]/tr[last()-2]/td[6]/input[@type='number']")
                    img_priority.clear()
                    img_priority.send_keys(img_pri)
                    time.sleep(2)
            Save_and_another=self.driver.find_element("xpath","//div[@class='submit-row']/input[@value='Save']").click()
            # self.add_source(domain_name)
            # int(input("Inter any number last!"))

        except:
            pass
    
    def add_source(self):
        try:
            # domain_name=Domain_Name
            source_dataframe=self.read_domain_from_exel(domain_name=None,data_type='source_data')
            Add_source=self.driver.get(f"http://dashboard.newsdata.remote/newsdata_feeds/source/add/")
            Username = self.driver.find_element('xpath', '//*[@id="id_username"]')
            Username.send_keys(self.LOCAL_USERNAME)
            Password = self.driver.find_element("xpath", '//*[@id="id_password"]') 
            Password.send_keys(self.LOCAL_PASSWORD)
            Log_In = self.driver.find_element("xpath", '//*[@id="login-form"]/div[3]/input')
            Log_In.click()
            for index, row in source_dataframe.iterrows():
                # print(f"Row {index}:\n{row}\n")
                # domain=row['Name']
                # source_link=row['Source_Link']
                # language=row['Language']
                # country=row['Country']
                # category=row['Category']
                # print(f"{domain} --> {source_link} --> {language} --> {country} --> {category}")
                
                try:
                    # pass
                    # int(input("Inter any number last!"))
                    domain=self.driver.find_element("xpath","(//span[@role='combobox'])[1]").click()
                    domain_search=self.driver.find_element("xpath","/html/body/span/span/span[1]/input")
                    time.sleep(2)
                    domain_search.send_keys(row['Name'])
                    time.sleep(2)
                    domain_search=self.driver.find_element("xpath","//span[@class='select2-results']/ul/li[1]").click()
                    time.sleep(2)
                    
                    source_url_field = self.driver.find_element("xpath", "//input[@id='id_url']")
                    source_url_field.send_keys(row['Source_Link'])
                    time.sleep(2)

                    Status_field = self.driver.find_element('xpath', '//*[@id="id_feed_status"]/option[1]').click()
                    
                    try:
                        language_field = self.driver.find_element("xpath", "(//span[@role='combobox'])[2]").click()
                        time.sleep(2)
                        language_field=self.driver.find_element("xpath","(//input[@role='searchbox'])[3]")
                        language_field.send_keys(row['Language'])
                        time.sleep(2)
                        language_field=self.driver.find_element("xpath","//span[@class='select2-results']/ul/li[1]").click()
                        time.sleep(2)
                    except Exception as er:
                        print(f"language load error {er}")
                    try:
                        # Country Field
                        country_combobox_xpath = '//*[@id="source_form"]/div/fieldset/div[5]/div/div[1]/div/div/span/span[1]/span/ul'
                        country_combobox = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, country_combobox_xpath)))
                        country_combobox.click()
                        country_search_box_xpath = '//*[@id="source_form"]/div/fieldset/div[5]/div/div[1]/div/div/span/span[1]/span/ul/li/input'
                        country_search_box = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, country_search_box_xpath)))
                        country_search_box.send_keys(row['Country'])
                        time.sleep(2)
                        country_suggestion_xpath = "//span[@class='select2-results']/ul/li[1]"
                        country_suggestion = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, country_suggestion_xpath)))
                        country_suggestion.click()
                        time.sleep(2)
                    except Exception as er:
                        print(f"country load error {er}")
                    try:    
                        # Category Field
                        category_combobox_xpath = '//*[@id="source_form"]/div/fieldset/div[6]/div/div[1]/div/div/span/span[1]/span/ul'
                        category_combobox = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, category_combobox_xpath)))
                        category_combobox.click()
                        category_search_box_xpath = '//*[@id="source_form"]/div/fieldset/div[6]/div/div[1]/div/div/span/span[1]/span/ul/li/input'
                        category_search_box = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, category_search_box_xpath)))
                        category_search_box.send_keys(str(row['Category']))
                        time.sleep(2)
                        category_suggestion_xpath = "//span[@class='select2-results']/ul/li[1]"
                        category_suggestion = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, category_suggestion_xpath)))
                        category_suggestion.click()
                        time.sleep(2)

                    except Exception as error:
                        print(f"category load error : {error}")
                    # if 'crypto' == 'crypto':
                    #     custom_collection_field = self.driver.find_element('xpath', '//*[@id="id_custom_api_ids"]')
                    #     custom_collection_field.send_keys('13')
                    Add_More_source = self.driver.find_element("xpath", '//*[@id="source_form"]/div/div/input[2]').click()
                    # int(input("Inter any number last!"))
                except Exception as erro:
                    print(f"eeeeeeeeeee {erro}")
                    
        
        except:
            pass           


obj=Auto_Domain_Source()
# obj.add_source()  
obj.open_dashboard()