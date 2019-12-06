import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from auth import auth_dict
import time

def play_song(track_id, track_duration):
    song_url = "https://play.spotify.com/track/{track_id}".format(track_id = track_id)
    login_string = "https://accounts.spotify.com/en/login?continue={song_url}".format(song_url = song_url)
    
    driver = webdriver.Chrome('chromedriver')
    opts = Options()
    opts.add_argument("user-agent=[Mozilla/5.0 (Windows NT x.y; rv:10.0) Gecko/20100101 Firefox/10.0]")
    driver.get(login_string)
    username_form = driver.find_element_by_id("login-username")
    password_form = driver.find_element_by_id("login-password")
    
    username_form.send_keys(auth_dict["username"])
    password_form.send_keys(auth_dict["password"])
    
    login_button = driver.find_element_by_id("login-button")
    login_button.click()
    
    #play_button = driver.find_element_by_class_name("control-button spoticon-play-16 control-button--circled")
    #play_button.click()
    
    time.sleep(track_duration)
    driver.close()