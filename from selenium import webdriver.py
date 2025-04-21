from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Remplacer par le chemin vers votre driver (Chrome, Firefox, etc.)
driver_path = '/path/to/chromedriver'

# Paramètres : identifiants, critères de recherche
EMAIL = "VOTRE_EMAIL"
PASSWORD = "VOTRE_MOT_DE_PASSE"
JOB_KEYWORDS = "Data Scientist"
LOCATION = "France"

# Initialisation du navigateur
driver = webdriver.Chrome(executable_path=driver_path)
wait = WebDriverWait(driver, 10)

def login_indeed():
    """Se connecte à Indeed avec les identifiants fournis."""
    driver.get("https://secure.indeed.com/account/login")
    time.sleep(3)
    # Localiser et remplir l'email
    email_input = wait.until(EC.presence_of_element_located((By.ID, "login-email-input")))
    email_input.clear()
    email_input.send_keys(EMAIL)
    # Localiser et remplir le mot de passe
    password_input = driver.find_element(By.ID, "login-password-input")
    password_input.clear()
    password_input.send_keys(PASSWORD)
    password_input.send_keys(Keys.RETURN)
    # Attendre la connexion
    time.sleep(5)

def search_jobs():
    """Navigue vers la page de recherche d'offres avec les critères spécifiés."""
    # Vous pouvez ajuster l'URL en fonction de votre recherche
    search_url = f"https://www.indeed.com/jobs?q={JOB_KEYWORDS}&l={LOCATION}"
    driver.get(search_url)
    time.sleep(5)

def apply_to_job(job_url):
    """Tente de postuler à une offre en se rendant sur l'URL de l'offre."""
    driver.get(job_url)
    time.sleep(3)
    try:
        # Exemple : tentative de cliquer sur le bouton 'Postuler'
        # Le sélecteur devra être adapté au design et langue du bouton
        apply_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Postuler')]")))
        apply_button.click()
        print(f"Candidature lancée pour : {job_url}")
        time.sleep(3)
        # Ici, il faudrait ajouter des étapes pour remplir les champs de candidature.
        # Par exemple :
        # nom_input = driver.find_element(By.ID, "nom")
        # nom_input.send_keys("Votre Nom")
        # Puis valider la candidature
    except Exception as e:
        print(f"Impossible de postuler sur ce poste ({job_url}) : {e}")

def main():
    login_indeed()
    search_jobs()
    # Récupérer les URLs des offres ; cela peut nécessiter une adaptation selon la structure HTML
    job_cards = driver.find_elements(By.CSS_SELECTOR, "a.tapItem")
    job_urls = []
    for card in job_cards:
        url = card.get_attribute("href")
        if url:
            job_urls.append(url)
    print(f"{len(job_urls)} offres trouvées.")
    
    # Parcourir les offres et tenter la candidature
    for url in job_urls:
        apply_to_job(url)
        # Pause entre les candidatures pour éviter d’être bloqué
        time.sleep(2)

    driver.quit()

if __name__ == "__main__":
    main()
