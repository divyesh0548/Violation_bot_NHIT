import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import psycopg2
from psycopg2 import extras
from typing import Tuple

URL = "https://parivahan.gov.in/"
WAIT_TIME = 30
ELEMENT_WAIT = 15
DB_HOST = "db-1.c2n44a20y9k5.us-east-1.rds.amazonaws.com"
DB_PORT = 5432
DB_NAME = "nhit"
DB_USER = "postgres"
DB_PASSWORD = "postgres1234"

def get_db_connection():
    """Create and return a PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("[DB] Connection established")
        return conn
    except psycopg2.Error as e:
        print(f"[DB-ERROR] Error connecting to database: {e}")
        return None

def check_and_restore_db_connection(conn):
    """
    Check if connection is still open. If closed, reconnect.
    
    Args:
        conn: PostgreSQL connection object
        
    Returns:
        conn: Open PostgreSQL connection (new if old one was closed)
    """
    if conn is None:
        print("[DB] Connection is None, creating new connection...")
        return get_db_connection()
    
    try:
        # Try to execute a simple query to check if connection is alive
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("[DB] Connection is healthy")
        return conn
    except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
        print(f"[DB-WARNING] Connection closed ({e}), reconnecting...")
        try:
            conn.close()
        except:
            pass
        
        # Try to reconnect
        new_conn = get_db_connection()
        if new_conn:
            print("[DB] Successfully reconnected to database")
            return new_conn
        else:
            print("[DB-ERROR] Could not reconnect to database")
            return None
    except Exception as e:
        print(f"[DB-ERROR] Error checking connection: {e}")
        return conn

# [All other functions remain the same - insert them here]
# (setup_driver, wait_for_page_load, close_mobile_popup, select_state_tamilnadu, etc.)
# Include all functions from the original file until insert_vehicle_to_checkpost

def setup_driver():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-images')
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument('--disable-gpu')
        options.page_load_strategy = 'normal'
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        print("Browser launched")
        return driver
    except WebDriverException as e:
        print(f"Browser setup failed: {e}")
        return None

def wait_for_page_load(driver, wait, timeout=30):
    """Wait for page to completely load."""
    try:
        print("Waiting for page to load completely...")
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        print("Page loaded completely")
        return True
    except Exception as e:
        print(f"Page load timeout: {e}")
        return False

def close_mobile_popup(driver, wait):
    """Close the mobile number update popup if it appears."""
    try:
        popup_text_xpath = "//span[contains(@class, 'english') and contains(text(), 'Update Your Mobile Number')]"
        popup_text = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, popup_text_xpath)))
        if popup_text:
            close_button_xpath = "//button[contains(@class, 'btn-close') and contains(@class, 'position-absolute')]"
            close_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, close_button_xpath)))
            close_button.click()
            print("Mobile number popup closed")
            time.sleep(2)
            return True
    except TimeoutException:
        return False
    except Exception as e:
        print(f"Error handling mobile popup: {e}")
        return False

def select_state_tamilnadu(driver, wait):
    """Select Tamil Nadu from the state selection interface."""
    for attempt in range(3):
        try:
            print(f"Selecting Tamil Nadu state (attempt {attempt+1})")
            state_selectors = [
                "//div[contains(text(), 'Select State Name')]",
                "//span[contains(text(), 'Select State Name')]",
                "//a[contains(text(), 'Select State Name')]",
                "//button[contains(text(), 'Select State Name')]",
                "//*[contains(text(), 'Select State Name') and contains(@class, 'select')]",
                "//*[contains(text(), 'Select State Name')]"
            ]
            state_element = None
            for selector in state_selectors:
                try:
                    state_element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"Found state selection element with: {selector}")
                    break
                except:
                    continue

            if not state_element:
                print("Could not find state selection element")
                return False

            driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", state_element)
            time.sleep(1)
            print("Clicking state selection element...")
            state_element.click()
            time.sleep(2)

            tamilnadu_selectors = [
                "//div[contains(text(), 'TAMIL NADU')]",
                "//span[contains(text(), 'TAMIL NADU')]",
                "//a[contains(text(), 'TAMIL NADU')]",
                "//li[contains(text(), 'TAMIL NADU')]",
                "//option[contains(text(), 'TAMIL NADU')]",
                "//*[contains(text(), 'TAMIL NADU') and contains(@class, 'option')]",
                "//*[contains(text(), 'TAMIL NADU')]"
            ]
            tamilnadu_element = None
            for selector in tamilnadu_selectors:
                try:
                    tamilnadu_element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"Found Tamil Nadu option with: {selector}")
                    break
                except:
                    continue

            if not tamilnadu_element:
                print("Could not find Tamil Nadu option")
                return False

            driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", tamilnadu_element)
            time.sleep(1)
            print("Clicking Tamil Nadu...")
            tamilnadu_element.click()
            time.sleep(3)

            service_heading_xpath = "//h3[@class='top-space' and contains(text(), 'Service Name')]"
            try:
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, service_heading_xpath)))
                print("State selection successful - Service Name section found")
                return True
            except:
                print("Service Name section not found yet")
                print("Retrying state selection...")
                time.sleep(2)
        except Exception as e:
            print(f"Error selecting state on attempt {attempt+1}: {e}")
            time.sleep(2)

    print("Failed to select Tamil Nadu after all attempts")
    return False

def select_service(driver, wait):
    """Select service on the service selection page."""
    for attempt in range(3):
        try:
            print(f"\nSelecting service (attempt {attempt+1})")
            print("Waiting for service dropdown...")
            service_dropdown_xpath = "//span[contains(@class,'ui-selectonemenu-label') and contains(text(),'---Select Service Name---')]"
            service_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, service_dropdown_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", service_dropdown)
            time.sleep(1)
            print("Clicking service dropdown...")
            service_dropdown.click()
            time.sleep(2)

            print("Waiting for VEHICLE TAX COLLECTION option...")
            service_option_xpath = "//li[contains(@data-label, 'VEHICLE TAX COLLECTION') and contains(@data-label, 'OTHER STATE')]"
            service_option = wait.until(EC.element_to_be_clickable((By.XPATH, service_option_xpath)))
            print("Selecting VEHICLE TAX COLLECTION (OTHER STATE)...")
            service_option.click()
            time.sleep(2)

            print("Selected service: VEHICLE TAX COLLECTION (OTHER STATE)")
            print("Waiting for Go button...")
            go_button_xpath = "//button[.//span[contains(text(), 'Go')]]"
            go_button = wait.until(EC.element_to_be_clickable((By.XPATH, go_button_xpath)))
            print("Clicking Go button...")
            go_button.click()

            print("Waiting for vehicle entry page...")
            time.sleep(5)

            vehicle_input_xpath = "//input[@type='text' and @maxlength='10']"
            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, vehicle_input_xpath)))
                print("Successfully loaded vehicle entry page")
                return True
            except:
                print("Vehicle entry page not loaded, retrying...")
                driver.execute_script("location.reload()")
                time.sleep(3)
        except Exception as e:
            print(f"Error selecting service: {e}")
            driver.execute_script("location.reload()")
            time.sleep(3)

    print("Failed to select service after multiple attempts")
    return False

def navigate_to_tax_page(driver, wait):
    """Navigate from parivahan.gov.in to the tax collection page."""
    try:
        print("Opening parivahan.gov.in...")
        driver.get(URL)

        if not wait_for_page_load(driver, wait):
            return False

        popup_closed = close_mobile_popup(driver, wait)
        if popup_closed:
            print("Mobile number popup closed")
        else:
            print("No mobile number popup found")

        print("Hovering over Online Services...")
        online_services_xpath = "//a[@id='Online' and contains(@class, 'parent-link-with-submenu')]"
        online_services = wait.until(EC.element_to_be_clickable((By.XPATH, online_services_xpath)))
        ActionChains(driver).move_to_element(online_services).pause(2).perform()
        time.sleep(3)

        print("Clicking Checkpost Tax...")
        checkpost_tax_xpath = "//a[@href='/en/node/579' and contains(@class, 'second-child-menu')]"
        checkpost_tax = wait.until(EC.element_to_be_clickable((By.XPATH, checkpost_tax_xpath)))
        checkpost_tax.click()

        print("Waiting for Checkpost Tax page to load...")
        checkpost_title_xpath = "//span[@class='field field--name-title field--type-string field--label-hidden' and contains(text(), 'Checkpost Tax')]"
        wait.until(EC.visibility_of_element_located((By.XPATH, checkpost_title_xpath)))
        print("Checkpost Tax page loaded successfully")

        if not select_state_tamilnadu(driver, wait):
            print("Failed to select Tamil Nadu state")
            return False

        print("Waiting for Service Name section...")
        service_heading_xpath = "//h3[@class='top-space' and contains(text(), 'Service Name')]"
        wait.until(EC.visibility_of_element_located((By.XPATH, service_heading_xpath)))
        print("Service Name section is visible")

        if not select_service(driver, wait):
            print("Failed to select service")
            return False

        print("Successfully navigated to vehicle entry page")
        return True

    except Exception as e:
        print(f"Error navigating to tax page: {e}")
        return False

def safe_click(driver, wait, xpath, description="element", timeout=15):
    """Safely click element with proper waits."""
    try:
        print(f"Waiting for {description} to be clickable...")
        elem = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        print(f"Clicking {description}...")
        elem.click()
        time.sleep(1)
        print(f"Successfully clicked {description}")
        return True
    except TimeoutException:
        print(f"Timeout: could not find or click {description}")
        return False
    except Exception as e:
        print(f"Error clicking {description}: {e}")
        return False

def get_vehicle_weight(driver):
    """Extract vehicle weight with special handling for BUS, OMNI BUS, MAXI CAB, MOTOR CAB."""
    weight = "0"
    try:
        vehicle_type = ""
        try:
            vehicle_type_selectors = [
                "//span[contains(@class,'ui-selectonemenu-label') and contains(text(),'BUS')]",
                "//span[contains(@class,'ui-selectonemenu-label') and contains(text(),'OMNI BUS')]",
                "//span[contains(@class,'ui-selectonemenu-label') and contains(text(),'MAXI CAB')]",
                "//span[contains(@class,'ui-selectonemenu-label') and contains(text(),'MOTOR CAB')]",
                "//input[contains(@id, 'vehicle_type') and contains(@class, 'ui-state-filled')]"
            ]
            for selector in vehicle_type_selectors:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    if element.tag_name == 'span':
                        vehicle_type = element.text.strip()
                    else:
                        vehicle_type = element.get_attribute('value') or ''
                    if vehicle_type:
                        break
                except:
                    continue
        except:
            pass

        print(f"Vehicle Type detected: {vehicle_type}")

        special_vehicles = ["BUS", "OMNI BUS", "MAXI CAB", "MOTOR CAB"]
        is_special_vehicle = any(vehicle in vehicle_type.upper() for vehicle in special_vehicles)

        if is_special_vehicle:
            print(f"Special vehicle type detected: {vehicle_type}. Getting seat capacity sum.")
            seat_capacity = "0"
            sleeper_capacity = "0"
            try:
                seat_cap_element = driver.find_element(By.ID, "txt_seat_cap")
                seat_capacity = seat_cap_element.get_attribute('value') or "0"
                print(f"Seat Capacity: {seat_capacity}")
            except Exception as e:
                print(f"Could not find seat capacity: {e}")
            try:
                sleeper_cap_element = driver.find_element(By.ID, "txt_sleeper_cap")
                sleeper_capacity = sleeper_cap_element.get_attribute('value') or "0"
                print(f"Sleeper Capacity: {sleeper_capacity}")
            except Exception as e:
                print(f"Could not find sleeper capacity: {e}")
            try:
                total_capacity = int(seat_capacity) + int(sleeper_capacity)
                weight = str(total_capacity)
                print(f"Total Capacity (Weight): {weight}")
            except:
                weight = "0"
                print("Error calculating total capacity")
        else:
            print("Regular vehicle type. Getting laden weight.")
            try:
                weight_element = driver.find_element(By.ID, "txt_laden_wt")
                weight = weight_element.get_attribute('value') or "0"
                print(f"Laden Weight: {weight}")
            except Exception as e:
                print(f"Could not find laden weight by ID: {e}")
                weight_selectors = [
                    "//input[contains(@id, 'laden') and contains(@class, 'ui-state-filled')]",
                    "//input[contains(@name, 'laden') and contains(@class, 'ui-state-filled')]",
                    "//input[contains(@id, 'weight') and contains(@class, 'ui-state-filled')]",
                    "//input[contains(@name, 'weight') and contains(@class, 'ui-state-filled')]"
                ]
                for selector in weight_selectors:
                    try:
                        weight_element = driver.find_element(By.XPATH, selector)
                        weight = weight_element.get_attribute('value') or "0"
                        if weight != "0":
                            print(f"Found weight via fallback: {weight}")
                            break
                    except:
                        continue

            if weight == "0" or not weight:
                print("Weight is 0 or empty, checking for any weight input...")
                try:
                    all_inputs = driver.find_elements(By.XPATH, "//input[contains(@class, 'ui-state-filled')]")
                    for inp in all_inputs:
                        value = inp.get_attribute('value') or ''
                        if value and value.isdigit() and int(value) > 0:
                            try:
                                parent_text = inp.find_element(By.XPATH, "./ancestor::tr[1] | ./ancestor::div[1]").text.lower()
                                if 'weight' in parent_text or 'laden' in parent_text or 'capacity' in parent_text:
                                    weight = value
                                    print(f"Found weight via text analysis: {weight}")
                                    break
                            except:
                                continue
                except Exception as e:
                    print(f"Error in final weight search: {e}")

    except Exception as e:
        print(f"Error in get_vehicle_weight: {e}")

    return weight

def restart_browser_and_continue(driver):
    """Restart browser and continue."""
    print(f"\n[RESTART] RESTARTING BROWSER...")
    try:
        driver.quit()
        print("Closed current browser session")
    except:
        print("Could not properly close browser")

    time.sleep(3)

    new_driver = setup_driver()
    if not new_driver:
        print("Could not restart browser — aborting")
        return None, None

    new_wait = WebDriverWait(new_driver, WAIT_TIME)

    print("Re-navigating to tax page...")
    if not navigate_to_tax_page(new_driver, new_wait):
        print("Could not navigate to tax page after restart — aborting")
        new_driver.quit()
        return None, None

    print("[OK] Browser restarted successfully")
    return new_driver, new_wait

def insert_vehicle_to_checkpost(cursor, veh_reg_no, weight):
    """Insert a single vehicle record into checkpostmaster table.
    
    Returns: (success: bool, message: str)
    """
    try:
        # Convert weight to float and validate
        try:
            weight_value = float(weight)
        except (TypeError, ValueError):
            return False, f"Invalid weight: {weight}"

        # Skip records with weight <= 100
        if weight_value <= 100:
            return False, f"Weight <= 100: {weight_value}"

        # Check if vehicle already exists
        check_query = """
        SELECT COUNT(*) as count
        FROM checkpostmaster
        WHERE "Unique Vehicle Number" = %s
        """
        cursor.execute(check_query, (veh_reg_no,))
        result = cursor.fetchone()

        if result[0] > 0:
            return False, "Already exists in database"

        # Insert new vehicle
        insert_query = """
        INSERT INTO checkpostmaster
        ("Unique Vehicle Number", "weight")
        VALUES (%s, %s)
        """
        cursor.execute(insert_query, (veh_reg_no, weight_value))
        return True, f"Added successfully"

    except psycopg2.Error as e:
        return False, f"Database error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def process_single_vehicle(driver, wait, vehicle_no, idx, df):
    """Process a single vehicle - extract weight only."""
    max_retries = 5
    retry_count = 0

    while retry_count <= max_retries:
        try:
            print(f"\n{'='*50}")
            print(f"Processing {idx+1}/{len(df)} — Vehicle: {vehicle_no} (Attempt {retry_count + 1})")
            print(f"{'='*50}")

            print("Quick refreshing page...")
            driver.execute_script("location.reload()")
            time.sleep(2)

            vehicle_input_xpath = "//input[@type='text' and @maxlength='10']"

            print("Waiting for Vehicle Number input to be interactable...")
            try:
                input_element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, vehicle_input_xpath)))
                print("[OK] Vehicle Number input found and ready")
            except TimeoutException:
                print("[ERROR] Timeout: could not find Vehicle Number input")
                if retry_count < max_retries:
                    retry_count += 1
                    print(f"[RETRY] Attempting browser restart ({retry_count}/{max_retries})...")
                    new_driver, new_wait = restart_browser_and_continue(driver)
                    if new_driver:
                        driver = new_driver
                        wait = new_wait
                        continue
                    else:
                        break
                else:
                    print("[ERROR] Max retries reached")
                    df.at[idx, "Weight"] = "Error - Input Not Found"
                    return driver, wait, False

            try:
                popup_xpath = "//div[contains(@class,'ui-dialog') and contains(@style,'display: block')]"
                popup = WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.XPATH, popup_xpath)))
                if popup:
                    ok_button_xpath = "//div[contains(@class,'ui-dialog')]//button[.//span[contains(text(),'OK') or contains(text(),'Ok')]]"
                    safe_click(driver, wait, ok_button_xpath, "OK button on popup")
            except TimeoutException:
                pass

            try:
                input_element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, vehicle_input_xpath)))
                driver.execute_script("arguments[0].value = arguments[1];", input_element, vehicle_no)
                print("[OK] Vehicle number entered via JavaScript")
            except:
                input_element.clear()
                input_element.send_keys(vehicle_no)
                print("[OK] Vehicle number entered")

            get_details_xpath = "//button[.//span[contains(text(), 'Get Details')]]"
            try:
                get_details_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, get_details_xpath)))
                driver.execute_script("arguments[0].click();", get_details_btn)
                print("[OK] Get Details clicked")
            except:
                safe_click(driver, wait, get_details_xpath, "Get Details button")

            print("Waiting for vehicle details...")
            time.sleep(3)

            popup_appeared = False
            data_appeared = False

            for attempt in range(3):
                try:
                    popup_xpath = "//div[contains(@class,'ui-dialog') and contains(@style,'display: block')]"
                    try:
                        popup = WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.XPATH, popup_xpath)))
                        popup_appeared = True
                        print("Popup detected - no data available")
                        break
                    except TimeoutException:
                        pass

                    try:
                        filled_fields = driver.find_elements(By.XPATH, "//input[@class='ui-state-filled'] | //span[contains(@class,'ui-selectonemenu-label') and not(contains(text(),'---Select'))]")
                        if filled_fields:
                            data_appeared = True
                            print("[OK] Vehicle details loaded")
                            break
                    except:
                        pass

                except Exception:
                    pass

                if not popup_appeared and not data_appeared:
                    time.sleep(1)

            if popup_appeared:
                ok_button_xpath = "//div[contains(@class,'ui-dialog')]//button[.//span[contains(text(),'OK') or contains(text(),'Ok')]]"
                safe_click(driver, wait, ok_button_xpath, "OK button on popup")
                df.at[idx, "Weight"] = "N/A"
                print("[OK] Marked as N/A (no data available)")
                return driver, wait, True

            elif data_appeared:
                weight = get_vehicle_weight(driver)
                df.at[idx, "Weight"] = weight
                print(f"[OK] Weight extracted: {weight}")
                return driver, wait, True

            else:
                # No data loaded after 2 attempts - restart browser and retry
                print("[WARNING] No data loaded after attempts - restarting browser...")
                new_driver, new_wait = restart_browser_and_continue(driver)
                if new_driver:
                    # Browser restarted successfully - retry this vehicle
                    print(f"[RETRY] Re-processing vehicle {vehicle_no} after browser restart...")
                    driver = new_driver
                    wait = new_wait
                    return process_single_vehicle(driver, wait, vehicle_no, idx, df)
                else:
                    # Browser restart failed - mark as error
                    print(f"[ERROR] Could not restart browser for {vehicle_no}")
                    df.at[idx, "Weight"] = "Error - Browser Restart Failed"
                    return driver, wait, False

        except Exception as e:
            print(f"Error processing {vehicle_no}: {e}")
            if retry_count < max_retries:
                retry_count += 1
                print(f"[RETRY] Attempting browser restart ({retry_count}/{max_retries})...")
                new_driver, new_wait = restart_browser_and_continue(driver)
                if new_driver:
                    driver = new_driver
                    wait = new_wait
                    continue
                else:
                    break
            else:
                print("[ERROR] Max retries reached")
                df.at[idx, "Weight"] = "Error"
                return driver, wait, False

    df.at[idx, "Weight"] = "Error - Max Retries"
    return driver, wait, False

def scrape_vehicle_weights(df_not_found):
    """
    Scrape vehicle weights and update checkpostmaster table AFTER EACH VEHICLE is processed.
    
    Returns the dataframe with Weight column populated (same as before - no breaking changes).
    
    FIXED: Handles database connection failures with automatic reconnection
    """
    print("=" * 80)
    print("STARTING WEB SCRAPING FOR VEHICLE WEIGHTS")
    print("=" * 80)

    # Make a copy to avoid modifying the original
    df = df_not_found.copy()

    # Add Weight column if not present
    if "Weight" not in df.columns:
        df["Weight"] = ""
        print("Added 'Weight' column")

    print(f"Total vehicles to process: {len(df)}")

    if len(df) == 0:
        print("No vehicles to process. Skipping web scraping step.")
        return df

    # Start browser
    driver = setup_driver()
    if not driver:
        print("Could not start browser — aborting")
        return df

    wait = WebDriverWait(driver, WAIT_TIME)

    # Navigate to tax page with retry logic
    print("Starting navigation to tax page...")
    max_nav_attempts = 5
    nav_attempt = 0
    nav_success = False

    while nav_attempt < max_nav_attempts and not nav_success:
        nav_attempt += 1
        attempt_msg = f"[Attempt {nav_attempt}/{max_nav_attempts}] Navigating to tax page..."
        print(attempt_msg)

        if navigate_to_tax_page(driver, wait):
            nav_success = True
            print("[OK] Navigation to tax page successful")
            break

        print(f"[WARNING] Navigation attempt {nav_attempt} failed")

        if nav_attempt < max_nav_attempts:
            print("Restarting browser and retrying navigation...")
            try:
                driver.quit()
            except Exception:
                pass

            time.sleep(5)

            driver = setup_driver()
            if not driver:
                print("Could not restart browser — aborting")
                return df

            wait = WebDriverWait(driver, WAIT_TIME)
        else:
            print("[ERROR] Max navigation attempts reached — aborting")
            driver.quit()
            return df

    # ============================================================================
    # MODIFIED: Create database connection ONCE before processing loop
    # ============================================================================
    conn = get_db_connection()
    if not conn:
        print("[ERROR] Could not connect to database — aborting")
        driver.quit()
        return df

    start_time = time.perf_counter()
    processed_count = 0
    db_added_count = 0
    db_skipped_count = 0

    # ============================================================================
    # MODIFIED: Process each vehicle and INSERT INTO DATABASE IMMEDIATELY
    # WITH CONNECTION HEALTH CHECKS
    # ============================================================================
    for idx, row in df.iterrows():
        vehicle_no = str(row["Veh Reg No."]).strip()

        # Process single vehicle with retry logic
        driver, wait, success = process_single_vehicle(driver, wait, vehicle_no, idx, df)

        if success:
            processed_count += 1

            # ====================================================================
            # FIXED: Check connection health before database operations
            # ====================================================================
            weight = df.at[idx, "Weight"]
            
            # Only attempt database insert if weight was successfully extracted
            if weight and weight not in ["N/A", "Error", "Error - Input Not Found", "Error - Browser Restart Failed", "Error - Max Retries"]:
                
                # Check and restore connection if needed
                conn = check_and_restore_db_connection(conn)
                
                if conn is None:
                    db_skipped_count += 1
                    print(f"[DB-SKIP] {vehicle_no}: Database connection unavailable")
                    continue
                
                try:
                    with conn.cursor() as cursor:
                        success_insert, message = insert_vehicle_to_checkpost(cursor, vehicle_no, weight)
                        conn.commit()
                        
                        if success_insert:
                            db_added_count += 1
                            print(f"[DB-OK] {vehicle_no}: {message}")
                        else:
                            db_skipped_count += 1
                            print(f"[DB-SKIP] {vehicle_no}: {message}")
                
                except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
                    # Connection error - try to reconnect
                    print(f"[DB-WARNING] Connection error for {vehicle_no}: {e}")
                    db_skipped_count += 1
                    
                    try:
                        conn.rollback()
                    except:
                        pass
                    
                    # Attempt to reconnect for next vehicle
                    conn = check_and_restore_db_connection(conn)
                
                except psycopg2.Error as e:
                    conn.rollback()
                    db_skipped_count += 1
                    print(f"[DB-ERROR] {vehicle_no}: Database error: {e}")
                    
            else:
                db_skipped_count += 1
                print(f"[DB-SKIP] {vehicle_no}: Invalid weight - {weight}")

            print(f"Progress: {processed_count}/{len(df)} scraped | {db_added_count} added to DB")

        # Short wait before next vehicle
        time.sleep(1)

    # ============================================================================
    # MODIFIED: Close database connection after loop completes
    # ============================================================================
    if conn:
        try:
            conn.close()
            print("[DB] Database connection closed")
        except:
            pass

    # Summary
    print(f"\n{'='*50}")
    print(f"WEB SCRAPING AND DATABASE UPDATE COMPLETE")
    print(f"{'='*50}")
    print(f"Total vehicles to process: {len(df)}")
    print(f"Vehicles scraped: {processed_count}")
    print(f"Records added to checkpostmaster: {db_added_count}")
    print(f"Records skipped: {db_skipped_count}")
    print(f"{'='*50}")

    # Calculate execution time
    elapsed = time.perf_counter() - start_time
    hrs = int(elapsed // 3600)
    mins = int((elapsed % 3600) // 60)
    secs = int(elapsed % 60)

    print(f"Total execution time: {hrs:02d}:{mins:02d}:{secs:02d} (HH:MM:SS)")

    driver.quit()

    df.to_excel('vehicle_check_results_with_weights.xlsx', sheet_name='Not Found', index=False)

    # ============================================================================
    # IMPORTANT: Return the SAME dataframe as before - no breaking changes!
    # ============================================================================
    return df

# Example usage when running standalone
if __name__ == "__main__":
    # Load from Excel
    EXCEL_PATH = "vehicle_check_results.xlsx"
    SHEET_NAME = "Not Found"

    df_not_found = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME, dtype=str)

    print(f"Loaded {len(df_not_found)} vehicles from Excel")

    # Scrape weights and update database immediately
    df_updated = scrape_vehicle_weights(df_not_found)

    # Save back to Excel
    with pd.ExcelFile(EXCEL_PATH) as xls:
        sheets_dict = {sheet: pd.read_excel(xls, sheet_name=sheet) for sheet in xls.sheet_names}

    sheets_dict[SHEET_NAME] = df_updated

    with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl') as writer:
        for sheet, data in sheets_dict.items():
            data.to_excel(writer, sheet_name=sheet, index=False)

    print(f"[OK] Results saved back to '{EXCEL_PATH}'")
