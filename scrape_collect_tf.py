from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import json

options = Options()
options.add_experimental_option("prefs", {
  "download.default_directory": r"C:/Users/saratahir/Desktop/vibrio_soa/soa/collectTF_DR_IR/",
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True
})

import os
import time

data = {}

def scrape():
    print("Begin Scraping")
    project_root = os.getcwd()
    path = os.path.join(project_root, 'chromedriver')
    driver = webdriver.Chrome(executable_path=path)

    # navigate to collecttf
    driver.get("http://www.collectf.org/browse/list_all_TFs/")
    
    data['all_motifs'] = []

    pages = driver.find_elements_by_class_name('paginate_button')
    # For each tab of results
    for i in range (1,7):
        time.sleep(2)
        num_rows = driver.find_elements_by_xpath("//table/tbody/tr")
        driver.find_elements_by_class_name('paginate_button')[i].click()
        # for each row in the table
        for j in range(1,len(num_rows)+1):
            driver.find_elements_by_class_name('paginate_button')[i].click()
            num_rows = driver.find_elements_by_xpath("//table/tbody/tr")
            # if 4th column link exists, click it
            try:
                rows = driver.find_elements_by_xpath("//table/tbody/tr["+str(j)+"]/td[4]/a")
                for k in range(0,len(rows)):
                    print(i, j, k)
                    tf_name = driver.find_element_by_xpath("//table/tbody/tr["+str(j)+"]/td[1]").text
                    print(tf_name)
                    
                    tf_family = driver.find_element_by_xpath("//table/tbody/tr["+str(j)+"]/td[2]").text
                    print(tf_family)

                    tf_instance_id = driver.find_elements_by_xpath("//table/tbody/tr["+str(j)+"]/td[4]/a")[k].text
                    print(tf_instance_id)
                    
                    driver.find_elements_by_xpath("//table/tbody/tr["+str(j)+"]/td[4]/a")[k].click()
                    exists = driver.find_element_by_xpath("//div/p").text
                    # if information exists, grab repeat type and sequence
                    if exists == "":
                        time.sleep(2)
                        repeat_type = driver.find_element_by_xpath("//table/tbody/tr[1]/td[1]").text
                        gc_content = driver.find_element_by_xpath("//table/tbody/tr[2]/td[1]").text

                        regulatory_mode_dict = {}
                        tf_conformation_dict = {}
                        binding_site_type_dict = {}

                        regulatory_mode_dict["activation"] = driver.find_element_by_xpath("//table/tbody/tr[4]/td[1]").text
                        regulatory_mode_dict["repression"] = driver.find_element_by_xpath("//table/tbody/tr[4]/td[2]").text
                        regulatory_mode_dict["dual"] = driver.find_element_by_xpath("//table/tbody/tr[4]/td[3]").text
                        regulatory_mode_dict["not_specified"] = driver.find_element_by_xpath("//table/tbody/tr[4]/td[4]").text

                        tf_conformation_dict["monomer"] = driver.find_element_by_xpath("//table/tbody/tr[6]/td[1]").text
                        tf_conformation_dict["dimer"] = driver.find_element_by_xpath("//table/tbody/tr[6]/td[2]").text
                        tf_conformation_dict["tetramer"] = driver.find_element_by_xpath("//table/tbody/tr[6]/td[3]").text
                        tf_conformation_dict["other"] = driver.find_element_by_xpath("//table/tbody/tr[6]/td[4]").text

                        binding_site_type_dict['motif_associated'] = driver.find_element_by_xpath("//table/tbody/tr[8]/td[1]").text
                        binding_site_type_dict['variable_motif_associated'] = driver.find_element_by_xpath("//table/tbody/tr[8]/td[2]").text
                        binding_site_type_dict['non_motif_associated'] = driver.find_element_by_xpath("//table/tbody/tr[8]/td[3]").text

                        binding_sites = []
                        # click Aligned binding sites tab
                        alignment_tab = driver.find_element_by_xpath("//ul/li/a[contains(text(), 'Aligned binding sites')]").click()
                        for sequence in driver.find_elements_by_xpath("//div[contains(@id, 'aligned_sites_box')]/span[@class = 'sequence']"):
                            if(len(sequence.text) > 0):
                                binding_sites.append(sequence.text)
                    
                        motif = {}
                        motif['tf_instance'] = tf_instance_id
                        motif['tf_name'] = tf_name
                        motif['tf_family'] = tf_family
                        motif['structure'] = repeat_type
                        motif['gc_content'] = gc_content
                        motif['regulatory_mode'] = regulatory_mode_dict
                        motif['tf_conformation'] = tf_conformation_dict
                        motif['binding_site_type'] = binding_site_type_dict
                        motif['aligned_binding_sites'] = binding_sites
                        data['all_motifs'].append(motif)

                        time.sleep(1)

                        # go back to the search page
                        driver.execute_script("window.history.go(-1)")
                        driver.find_elements_by_class_name('paginate_button')[i].click()
                    # if there is no information, go back to the search page
                    else:
                        driver.execute_script("window.history.go(-1)")
                        driver.find_elements_by_class_name('paginate_button')[i].click()
            # If no sequences found
            except NoSuchElementException:
                print("No Sequences available")
    driver.close()

scrape()
with open('collect_tf_motifs.json', 'w') as outfile:
    json.dump(data, outfile, indent=3)