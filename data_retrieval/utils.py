import requests
from time import sleep

import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver


class NikeProductCard:
    
    def __init__(self, card_tag):
        self.card_tag = card_tag
        self.url = self.get_url() # href to the product page
        self.soup = self.get_page() # soup of individual product page
        
    def get_url(self):
        return self.card_tag.select_one('figure a').get('href')

    def get_page(self):
        return BeautifulSoup(requests.get(self.url, 'html.parser').content)
    
    def get_label(self): 
        # e.g. "Best Seller", "Coming Soon", "Just In", "Sold our", "Member Access",
        # "Sustainable Materials", "Launching in SNKRS", "Available in SNKRS", 
        # "Customize", etc.
        label_tag = self.card_tag.select_one('figure .product-card__info .product-card__messaging')
        # if label_tag is None:
        #     return ""
        return np.nan if label_tag is None else label_tag.text

    def get_title(self):
        return self.card_tag.select_one("figure .product-card__title").text

    def get_subtitle(self):
        # e.g. "Shoes", "Men's Shoes", "Women's Shoes", 
        # "Big Kids' Shoes", "Basketball Shoes", etc.
        return self.card_tag.select_one("figure .product-card__subtitle").text

    def get_count(self):
        # Number of colors
        # e.g. "2 Colors"
        return self.card_tag.select_one("figure .product-card__product-count").text

    def get_reduced_price(self):
        reduced_pricetag = self.card_tag.find(attrs = {'data-test': 'product-price-reduced'})
        # if reduced_pricetag is None:
        #     return "" # full price (see get_price())
        return np.nan if reduced_pricetag is None else reduced_pricetag.text

    def get_price(self):
        pricetag = self.card_tag.find(attrs = {'data-test': 'product-price'})
        # if pricetag is None: # will result in N/A in dataframe 
        #     return None
        return np.nan if pricetag is None else pricetag.text

    def get_description(self):
        description = self.soup.select_one('.description-preview p')
        # if description is None:
        #     return None
        return np.nan if description is None else description.text

    def get_colors(self):
        all_colors = self.soup.select('.colorway-images img')
        # if all_colors is None:
        #     return None
        return np.nan if all_colors is None else '; '.join([c.get('alt') for c in all_colors])

    def get_review_info(self):
        review_section = self.soup.find(attrs = {'data-test': 'reviewsAccordionClick'})
        if review_section is None:
            return np.nan, np.nan
        review_title = review_section.select_one('h3').text
        n_reviews = review_title[review_title.index('(') + 1 : review_title.index(')')]
        avg_stars = review_section.select_one('div').get('aria-label')
        return n_reviews, avg_stars
    
    
class AdidasProductCard:
    
    def __init__(self, card_tag):
        self.card_tag = card_tag
        self.url = self.get_url() # href to the product page
        self.soup = self.get_page()
        
    def get_url(self):
        # url = tag.select_one(".glass-product-card__assets a").get('href')
        return self.card_tag.select_one(".glass-product-card__assets a").get('href')

    def get_page(self):
        driver = webdriver.Chrome()
        driver.get(self.url)
        sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.close()
        return soup
        
    def get_title(self):
        title = self.card_tag.select_one(".glass-product-card__title")
        # if title is None:
        #     return None
        return np.nan if title is None else title.text

    def get_subtitle(self):
        # e.g. "Women's Originals", "Sportswear", "Men's Essentials", "Running" etc.
        subtitle = self.card_tag.select_one(".glass-product-card__category")
        # if subtitle is None:
        #     return None
        return np.nan if subtitle is None else subtitle.text

    def get_num_colors(self):
        # Number of colors
        # e.g. "2 Colors"
        num_colors = self.card_tag.select_one(".glass-product-card__label span")
        # if num_colors is None:
        #     return None
        return np.nan if num_colors is None num_colors.text

    def get_price(self):
        pricetag = self.card_tag.select(".gl-price-item")
        return [p.text for p in pricetag] # [original, sale]

    def get_description(self):
        # some shoes don't have description
        description = self.soup.select_one("#navigation-target-description .gl-accordion__content p")
        # if description is None:
        #     return None
        return np.nan if description is None else description.text

    def get_details(self):
        details = self.soup.select_one("#navigation-target-specifications .gl-accordion__content")
        if details is None:
            return np.nan
        bullets = [x.select(".gl-vspace-bpall-small") for x in details.select(".gl-list")]
        bullet_text = [x_sub.text for x in bullets for x_sub in x]
        return "; ".join(bullet_text)

    def get_review_info(self):
        review_section = self.soup.select_one("#navigation-target-reviews")
        if review_section is None:
            return np.nan, np.nan
        
        review_title = review_section.select_one('.gl-accordion__header .gl-accordion__title')
        if review_title:
            review_title = review_title.text
            n_reviews = review_title[review_title.index('(') + 1 : review_title.index(')')]
            avg_stars = review_section.find(attrs = {'data-auto-id': 
                                        'ratings-reviews'})
            if avg_stars:
                avg_stars = avg_stars.select_one('.out-of-5___i5A3q')
            
            return n_reviews, np.nan if avg_stars else n_reviews, avg_stars.text
            
        return np.nan, np.nan
                                        
    def get_colors(self):
        all_colors = self.soup.find(attrs = {"aria-labelledby": 
                                "available-colors-label"})
        if all_colors is None: 
            # products with one color 
            # -> none here but can get the color from product details
            return np.nan
        
        all_colors = all_colors.find(attrs = {"data-testid": "color-variation"})
        if all_colors is None:
            return np.nan
        
        color_list = [c.get('alt') for c in all_colors] 
        # e.g. "Product color: Core Black / Core Black / Cloud White" is one color
        # => remove "Product color:" in the front
        color_list = [c[c.index(":") + 1: ]  for c in color_list]
        return '; '.join(color_list) # each color is separated by a "; "
