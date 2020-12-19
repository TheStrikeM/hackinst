from time import sleep
from random import randint
from msedge.selenium_tools import Edge, EdgeOptions
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

class InstUtil():

    def __init__(self):
        self.options = EdgeOptions()
        self.options.use_chromium = True
        self.browser = Edge(options=self.options)

    def t( self, n1, n2):
        sleep(randint(n1, n2))

    def quit(self):
        browser = self.browser

        browser.close()
        browser.quit()

    def existcheck(self, url):
        browser = self.browser
        try:
            browser.find_element_by_xpath(url)
            result = True
        except NoSuchElementException:
            result = False
        return result

    def login(self, username, password):
        browser = self.browser

        browser.get('https://instagram.com/')

        self.t(2, 5)
        un = browser.find_element_by_xpath('/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[1]/div/label/input')
        un.clear()
        un.click()
        un.send_keys(username)

        self.t(2, 5)

        up = browser.find_element_by_xpath('/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[2]/div/label/input')
        up.clear()
        up.click()
        up.send_keys(password)
        up.send_keys(Keys.ENTER)
        self.t(2, 5)

    def get_recomendations( self):
        browser = self.browser
        try:
            browser.get('https://www.instagram.com/explore/people/suggested/')
            self.t(2, 5)

            recomends = browser.find_elements_by_class_name("FPmhX")
            recomends = [ item.get_attribute( 'href' ) for item in recomends if "/" in item.get_attribute( 'href' ) ]
            return recomends

        except Exception as e:
            return print(f"Ошибка {e}")

    def subscribe( self, list ):
        browser = self.browser
        try:
            for i in list:
                browser.get(i)
                self.t(4, 5)

                sbtn = "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button"
                zbtn = "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/button"

                if self.existcheck(sbtn):
                    browser.find_element_by_xpath(sbtn).click()
                else:
                    browser.find_element_by_xpath(zbtn).click()

                print(f'Успешная подписка')

        except Exception as e:
            print(f"Ошибка {e}")

    def smart_unsubscribe( self, username ):

        browser = self.browser
        browser.get( f"https://www.instagram.com/{username}/" )
        self.t(6, 7)

        followers_button = browser.find_element_by_xpath(
            "/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span" )
        followers_count = followers_button.get_attribute( "title" )

        following_button = browser.find_element_by_xpath(
            "/html/body/div[1]/section/main/div/header/section/ul/li[3]/a" )
        following_count = following_button.find_element_by_tag_name( "span" ).text

        self.t(6, 7)

        # если количество подписчиков больше 999, убираем из числа запятые
        if ',' in followers_count or following_count:
            followers_count, following_count = int( ''.join( followers_count.split( ',' ) ) ), int(
                ''.join( following_count.split( ',' ) ) )
        else:
            followers_count, following_count = int( followers_count ), int( following_count )

        print( f"Количество подписчиков: {followers_count}" )
        followers_loops_count = int( followers_count / 12 ) + 1
        print( f"Число итераций для сбора подписчиков: {followers_loops_count}" )

        print( f"Количество подписок: {following_count}" )
        following_loops_count = int( following_count / 12 ) + 1
        print( f"Число итераций для сбора подписок: {following_loops_count}" )

        # собираем список подписчиков
        followers_button.click( )
        self.t(6, 7)

        followers_ul = browser.find_element_by_xpath( "/html/body/div[5]/div/div/div[2]" )

        try:
            followers_urls = [ ]
            print( "Запускаем сбор подписчиков..." )
            for i in range( 1, followers_loops_count + 1 ):
                browser.execute_script( "arguments[0].scrollTop = arguments[0].scrollHeight", followers_ul )
                self.t(6, 7)
                print( f"Итерация #{i}" )

            all_urls_div = followers_ul.find_elements_by_tag_name( "li" )

            for url in all_urls_div:
                url = url.find_element_by_tag_name( "a" ).get_attribute( "href" )
                followers_urls.append( url )

            # сохраняем всех подписчиков пользователя в файл
            with open( f"{username}_followers_list.txt", "a" ) as followers_file:
                for link in followers_urls:
                    followers_file.write( link + "\n" )
        except Exception as ex:
            print( ex )
            self.quit()

        self.t(6, 7)
        browser.get( f"https://www.instagram.com/{username}/" )
        self.t(6, 7)

        # собираем список подписок
        following_button = browser.find_element_by_xpath(
            "/html/body/div[1]/section/main/div/header/section/ul/li[3]/a" )
        following_button.click( )
        self.t(6, 7)

        following_ul = browser.find_element_by_xpath( "/html/body/div[5]/div/div/div[2]" )

        try:
            following_urls = [ ]
            print( "Запускаем сбор подписок" )

            for i in range( 1, following_loops_count + 1 ):
                browser.execute_script( "arguments[0].scrollTop = arguments[0].scrollHeight", following_ul )
                self.t(6, 7)
                print( f"Итерация #{i}" )

            all_urls_div = following_ul.find_elements_by_tag_name( "li" )

            for url in all_urls_div:
                url = url.find_element_by_tag_name( "a" ).get_attribute( "href" )
                following_urls.append( url )

            # сохраняем всех подписок пользователя в файл
            with open( f"{username}_following_list.txt", "a" ) as following_file:
                for link in following_urls:
                    following_file.write( link + "\n" )

            """Сравниваем два списка, если пользователь есть в подписках, но его нет в подписчиках,
            заносим его в отдельный список"""

            count = 0
            unfollow_list = [ ]
            for user in following_urls:
                if user not in followers_urls:
                    count += 1
                    unfollow_list.append( user )
            print( f"Нужно отписаться от {count} пользователей" )

            # сохраняем всех от кого нужно отписаться в файл
            with open( f"{username}_unfollow_list.txt", "a" ) as unfollow_file:
                for user in unfollow_list:
                    unfollow_file.write( user + "\n" )

            print( "Запускаем отписку..." )
            self.t(6, 7)

            # заходим к каждому пользователю на страницу и отписываемся
            with open( f"{username}_unfollow_list.txt" ) as unfollow_file:
                unfollow_users_list = unfollow_file.readlines( )
                unfollow_users_list = [ row.strip( ) for row in unfollow_users_list ]

            try:
                count = len( unfollow_users_list )
                for user_url in unfollow_users_list:
                    browser.get( user_url )
                    self.t(6, 7)

                    # кнопка отписки
                    unfollow_button = browser.find_element_by_xpath(
                        "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div[2]/div/span/span[1]/button" )
                    unfollow_button.click( )

                    self.t(6, 7)

                    # подтверждение отписки
                    unfollow_button_confirm = browser.find_element_by_xpath(
                        "/html/body/div[4]/div/div/div/div[3]/button[1]" )
                    unfollow_button_confirm.click( )

                    print( f"Отписались от {user_url}" )
                    count -= 1
                    print( f"Осталось отписаться от: {count} пользователей" )

                    # time.sleep(random.randrange(120, 130))
                    self.t(6, 7)

            except Exception as ex:
                print( ex )
                self.quit()

        except Exception as ex:
            print( ex )
            self.quit()

blacklist = []
inst = InstUtil( )

while True:
    inst.login(yourlogin, yourpassword)
    inst.smart_unsubscribe("strikecodestudio")
    inst.quit()
