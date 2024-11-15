from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def click_show_more_button(driver):
    """
    Attempts to click the 'Show More' button if it exists.
    """
    try:
        # Locate the button by text and scroll it into view
        show_more_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Show more')]")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_more_button)
        time.sleep(1)  # Give time for scrolling
        
        # Click the button using JavaScript to avoid interception issues
        driver.execute_script("arguments[0].click();", show_more_button)
        print("Successfully clicked 'Show More' button.")
    except Exception as e:
        print(f"No 'Show More' button found or could not click: {e}")

def scrape_multiplayer_games(max_games):
    print(f"Scraping up to {max_games} multiplayer games from Steam...")
    games = []

    # Set up Selenium WebDriver
    driver = webdriver.Chrome()  # Replace with webdriver.Firefox() if needed
    driver.get("https://store.steampowered.com/category/multiplayer/?flavor=contenthub_all&facets13268=6%3A4")
    time.sleep(10)  # Allow the page to load

    try:
        while len(games) < max_games:
            # Wait for games to load
            time.sleep(3)

            # Find game titles on the current page
            game_elements = driver.find_elements(By.CLASS_NAME, "_2ekpT6PjwtcFaT4jLQehUK.StoreSaleWidgetTitle")
            for game in game_elements:
                game_title = game.text.strip()
                if game_title not in games:
                    games.append(game_title)  # Avoid duplicates
                    print(f"Scraped: {game_title}")

                # Stop if we reach the desired number of games
                if len(games) >= max_games:
                    break

            print(f"Scraped {len(game_elements)} games on this page. Total so far: {len(games)}")

            # Try to click the "Show More" button
            click_show_more_button(driver)

    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        driver.quit()

    # Return the list of games
    return games

if __name__ == "__main__":
    # Specify how many games you want to scrape
    max_games = int(input("Enter the number of games you want to scrape: "))
    games = scrape_multiplayer_games(max_games)

    # Print the scraped games
    print("\nScraped Multiplayer Games:")
    for idx, game in enumerate(games, start=1):
        print(f"{idx}: {game}")

    # Save the games to a file
    with open("multiplayer_games_limited.txt", "w", encoding="utf-8") as file:
        for game in games:
            file.write(game + "\n")
    print(f"\nGame titles saved to 'multiplayer_games_limited.txt'.")
