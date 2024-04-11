def Upload():
    logging.info("Upload() is called...")

    ''' Read Config File    '''
    Config_Dict = read_config('config.txt')
    logging.debug("Config_Dict: {}".format(Config_Dict))

    DocumentsOfRecord_folder = Config_Dict['DocumentsOfRecord_folder']
    logging.debug("DocumentsOfRecord_folder : {0}".format(DocumentsOfRecord_folder))
    DownloadFolder = Config_Dict['Downloads_folder']
    logging.debug("Downloads_folder : {0}".format(DownloadFolder))

    '''  Read the Mappting File '''
    df = read_mapping(Config_Dict['EIDMapping'])
    logging.debug("")


    # check if DocumentsOfRecord folder exist on local machine
    if not os.path.exists(DocumentsOfRecord_folder):
        logging.debug("DocumentsOfRecord folder not found hence creating")
        os.makedirs(os.path.join(os.getcwd(), "DocumentsOfRecord"))
        os.makedirs(os.path.join(os.getcwd(), "DocumentsOfRecord", "BlobFiles"))
        logging.debug("Created folder: {}".format(os.path.join(os.getcwd(), "DocumentsOfRecord")))
    else:
        logging.debug("{0} Folder Already Exist so stopping Execution "
              "Please check manually {0} if failed in UI".format(DocumentsOfRecord_folder))
        sys.exit()

    # Initiate Paths
    PAYREGISTER_folder = Config_Dict['PAYREGISTER_folder']
    logging.debug("PAYREGISTER_folder: {0}".format(str(PAYREGISTER_folder)))
    Blobfiles_Path = os.path.join(DocumentsOfRecord_folder, "BlobFiles")
    logging.debug("Blobfiles_Path: {0}".format(Blobfiles_Path))

    no_of_files = len(os.listdir(PAYREGISTER_folder))
    logging.debug("{} Files Found in PAYREGISTER_folder".format(str(no_of_files)))
    logging.debug("Files are getting Moved....")



    # Till the folder exceeds size above 250 Mb or the folder becomes Empty
    # Excecute file movement and DAT file creation
    while checksize(DocumentsOfRecord_folder) == True:
        result = movefiles(PAYREGISTER_folder, Blobfiles_Path)
        logging.debug(result)

        if checksize(DocumentsOfRecord_folder) == False:
            logging.debug("Files moved till 230 mb and now moving to DAT Creation")
            break
        elif len(os.listdir(PAYREGISTER_folder)) == 0:
            logging.debug("{0} Folder is Now Empty hence Processing for DAT Creation".format(PAYREGISTER_folder))
            break


    logging.debug("Files are Moved")
    no_of_blob_files = len(os.listdir(Blobfiles_Path))
    logging.debug("{0} Files in Blofiles folder".format(str(no_of_blob_files)))



    # Create DAT file
    Today = datetime.today().strftime('%Y-%m-%d')
    logging.debug("Writing to DAT File")
    file = open(os.path.join(DocumentsOfRecord_folder, "DocumentsOfRecord.dat"), "a+")
    file.write("COMMENT HDL Template for Salary Slips Context in Documents of "
               "Record V1 Created on:{}\n".format(Today))
    file.write("METADATA|DocumentsOfRecord|PersonNumber|DocumentType|DocumentCode|DocumentName|DateFrom|DateTo\n")


    BlobFiles = os.listdir(Blobfiles_Path)
    logging.debug("Blobfiles Path: {}".format(folder_name+"\BlobFiles"))



    for filename in BlobFiles:
        """    get EMPLID for Excel from filename  """
        # logging.debug(type(filename))
        logging.debug(filename)
        EMP = str(filename.split('_')[0])
        # logging.debug(EMP)

        Month = filename.split('_')[1]
        if len(Month)<2:
            Month = "0"+Month

        Year = filename.split('_')[2].split(".")[0][:4]


        Emp_df = df.loc[df.EMPLID == EMP]
        Emp_Id = Emp_df.set_index('EMPLID').to_dict('dict').get('HX_PERSON_ORA').get(EMP)

        file.write("{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}\n".format(
            "MERGE",
            "DocumentsOfRecord",
            Emp_Id,
            "Salary Slips",
            "GLB_THIRD_PARTY_PAYSLIP_{}".format(filename[:-4]),
            filename[:-4],
            "{0}/{1}/{2}".format(Year, Month, "01"),
            ""))

    file.write("\nMETADATA|DocumentAttachment|PersonNumber|DocumentType|Country|DocumentCode|DataTypeCode|Title|URLorTextorFileName|File\n")

    for filename in BlobFiles:
        EMP = str(filename.split('_')[0])
        Emp_df = df.loc[df.EMPLID == EMP]
        Emp_Id = Emp_df.set_index('EMPLID').to_dict('dict').get('HX_PERSON_ORA').get(EMP)
        Title = filename[:-4]

        file.write("{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}|{9}\n".format(
            "MERGE",
            "DocumentAttachment",
            Emp_Id,
            "Salary Slips",
            "",
            "GLB_THIRD_PARTY_PAYSLIP_{}".format(Title),
            "FILE",
            Title,
            filename,
            filename)
        )
    file.write("\n")
    file.close()
    logging.debug("DAT File Created!")
    time.sleep(5)


    # zip the DocumentsOfRecord folder
    timenow = datetime.now().strftime("%Y_%m_%d__%H_%M")
    logging.debug("Time Now = {0}".format(timenow))
    try:
        logging.debug("The Folder Documents of records is getting zipped...")
        archived = shutil.make_archive('DocumentsOfRecord '+timenow, 'zip', './DocumentsOfRecord')
        logging.debug("{0} file Created Hence Uploading to Oracle portal\n".format(str(archived)))
    except Exception as e:
        raise Exception("Unable to create Zip file\n\tError: {0}".format(e))
    time.sleep(5)


    # Upload zipfile folder
    Downloads = os.path.join(os.getcwd(), 'Downloads')
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    prefs = {"download.default_directory": Downloads}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(chrome_options=options)
    driver.maximize_window()
    driver.get(
        'https://fa-etqo-dev1-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/faces/FuseWelcome?fnd=%3B%3B%3B%3Bfalse%3B256'
        '%3B%3B%3B&_afrLoop=3088899899617097&_afrWindowMode=0&_afrWindowId=l5r41t21c&_adf.ctrl-state=17ykk5lieu_217&_'
        'afrFS=16&_afrMT=screen&_afrMFW=1350&_afrMFH=608&_afrMFDW=1366&_afrMFDH=768&_afrMFC=8&_afrMFCI=0&_afrMFM=0&_'
        'afrMFR=96&_afrMFG=0&_afrMFS=0&_afrMFO=0'
    )
    wait = WebDriverWait(driver, 1000)

    logging.info("Chrome opened with URL: {}".format('https://fa-etqo-dev1-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/'
                                                     'faces/FuseWelcome?fnd=%3B%3B%3B%3Bfalse%3B256%3B%3B%3B&_afrLoop'
                                                     '=3088899899617097&_afrWindowMode=0&_afrWindowId=l5r41t21c&_adf.'
                                                     'ctrl-state=17ykk5lieu_217&_afrFS=16&_afrMT=screen&_afrMFW=1350&_'
                                                     'afrMFH=608&_afrMFDW=1366&_afrMFDH=768&_afrMFC=8&_afrMFCI=0&_'
                                                     'afrMFM=0&_afrMFR=96&_afrMFG=0&_afrMFS=0&_afrMFO=0'
                                                     )
                 )

    try:
        # Upload The Zipfile DocumentsOfRecord to Oracle
        usernameStr = 'bhagyar@hexaware.com'
        logging.debug("Login Username: {}".format(usernameStr))
        passwordStr = 'Vishnu@11'

        logging.info("Username: {0} & Password Initiallised".format(usernameStr))

        username = driver.find_element(By.ID, 'userid')
        username.send_keys(usernameStr)
        time.sleep(3)

        p = driver.find_element(By.ID, 'password')
        p.send_keys(passwordStr)
        time.sleep(3)

        logging.info("Username: '{0}' & Password Entered".format(usernameStr))

        btn_click = driver.find_element(By.ID, 'btnActive')
        btn_click.click()
        driver.implicitly_wait(1000)
        time.sleep(5)

        logging.info("User is Logged in...")

        clint_grp = driver.find_element("xpath", '//*[@id="groupNode_workforce_management"]')
        clint_grp.click()
        driver.implicitly_wait(1000)
        time.sleep(5)
        logging.info("Clicked On 'My Client Group'")

        show_m = driver.find_element(By.ID, 'itemNode_workforce_management_data_exchange')
        show_m.click()
        driver.implicitly_wait(1000)
        time.sleep(5)
        logging.info("Clicked On 'Data Exchange'")

        import_data = driver.find_element(By.ID,
                                          'pt1:_FOr1:1:_FONSr2:0:_FOTsr1:0:ll01Upl:UPsp1:ll01Pce:ll01Itr:0:ll02Pce:ll01Lv:2:ll01Pse:ll01Cl')
        import_data.click()
        driver.implicitly_wait(1000)
        time.sleep(7)
        logging.info("Clicked On 'Import and Load Data'")


        import_file = driver.find_element("xpath", '//*[@id="pt1:_FOr1:1:_FONSr2:0:MAnt2:1:ilsrSp:ctb3"]/a/span')
        import_file.click()
        driver.implicitly_wait(10)
        logging.info("Clicked On 'Import File' Button")

        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)

        file_upload = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pt1:_FOr1:1:_FONSr2:0:MAnt2:1:ilsrSp:if1::content")))
        # Select which file to upload
        # logging.info("folder_name: {}".format(folder_name))
        Zipfile = archived
        logging.info("Zipfile: {}".format(archived))
        file_upload.send_keys(Zipfile)
        logging.info("Uploaded Zip")
        time.sleep(25)


        try:
            submitnow = driver.find_element(By.XPATH, '//*[@id="pt1:_FOr1:1:_FONSr2:0:MAnt2:1:ilsrSp:cb2"]')
            submitnow.click()
            driver.implicitly_wait(100000)
            logging.debug("Submitted")
            logging.debug("Uploading....{}".format(Zipfile))
        except:
            logging.debug("Submit Button Was Not Clicked")
            raise Exception("Submit Button Was Not Clicked")
        time.sleep(10)

        actions = ActionChains(driver)
        actions.send_keys(Keys.ENTER)
        actions.perform()
        driver.implicitly_wait(1000)
        time.sleep(5) # Time before Refresh post submit
        logging.debug("Enter pressed for 'OK' Button")


        import_flag = bool
        load_flag = bool
        Success_Flag = bool

        # Get The Failed filenames
        try:
            while True:
			
	            Refresh = element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
					    (By.XPATH, '//*[@id="pt1:_FOr1:1:_FONSr2:0:MAnt2:1:ilsrSp:ls1:AT1:_ATp:ctb2"]/a/span')))


                refresh(driver, Refresh, 20)
                Imp_Status = driver.find_element(By.XPATH,
                 								 '//*[@id="pt1:_FOr1:1:_FONSr2:0:MAnt2:1:ilsrSp:ls1:AT1:_ATp:ATt4:0:i1"]').get_attribute("title")
                # logging.debug("Imp_Status: ", Imp_Status)
                if Imp_Status != 'Success' and Imp_Status != 'Error':
                    import_flag = False
                    Success_Flag = False
                    logging.debug("Imp_Status: {0}".format(Imp_Status))
                    continue
                elif Imp_Status == 'Error':
                    import_flag = False
                    Success_Flag = False
                    logging.debug("Imp_Status: {0}".format(Imp_Status))
                    break
                elif Imp_Status == 'Success':
                    import_flag = True
                    Success_Flag = True
                    logging.debug("Imp_Status: {0}".format(Imp_Status))
                    break
            time.sleep(20)

            while True:
                Refresh = WebDriverWait(driver, 1000).until(EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="pt1:_FOr1:1:_FONSr2:0:MAnt2:1:ilsrSp:ls1:AT1:_ATp:ctb2"]/a/span')))
                refresh(driver, Refresh, 20)
                time.sleep(30)

                Load_Status = driver.find_element(By.XPATH, '//*[@id="pt1:_FOr1:1:_FONSr2:0:MAnt2:1:ilsrSp:ls1:AT1:_ATp:ATt4:7:i2"]').get_attribute("title")
                logging.debug("Load_Status: {0}".format(Load_Status))
                if Load_Status != 'Success' and Load_Status != 'Error':
                    load_flag = False
                    Success_Flag = False
                    logging.warning("Load_Status: {0}".format(Load_Status))
                    continue
                elif Load_Status == 'Error':
                    load_flag = False
                    Success_Flag = False
                    logging.warning("Load_Status: {0}".format(Load_Status))
                    break
                elif Load_Status == 'Success':
                    load_flag = True
                    Success_Flag = True
                    logging.info("Load_Status: {0}".format(Load_Status))
                    break

        except Exception as e:
            logging.debug("Unable to get Import and Load Status: {}".format(e))
            raise Exception("Unable to get Import and Load Status: \n{}".format(e))

        logging.debug("import_flag: {0}".format(import_flag))
        logging.debug("load_flag: {0}".format(load_flag))
        logging.debug("Success_Flag: {0}".format(Success_Flag))


        if not Success_Flag:
            Files = GetFailedFilenames()
            logging.debug("Failed files from exported file: {}".format(Files))

            # Logic for Move these Files to Exception Directory
            for File in Files:
                # Specify the paths of the source and destination files
                # src_path = (Config_Dict['DocumentsOfRecord_folder']+"\BlobFiles\\"+str(File))
                # src_path = os.path.join(os.getcwd(), "DocumentsOfRecord", "BlobFiles", str(File))
                src_path = os.path.join(os.getcwd(), "DocumentsOfRecord", "BlobFiles")
                logging.debug("src_path: {}".format(src_path))
                dst_path = os.path.join(os.getcwd(), "Exception")
                logging.debug("dst_path: {}".format(dst_path))
                try:
                    logging.debug("trying to move files from {0} to {1}")
                    shutil.copy(src_path, dst_path)
                    logging.debug("The file {0} has been moved from {1} to the folder {2}"
                                  .format(File, DocumentsOfRecord_folder+"\BobFiles", os.path.join(os.getcwd(), 'Exception')))
                except Exception as E:
                    logging.warning("Unable to move the Failed files from {0} to {1} due to Exception: {2}".format(src_path, dst_path, E))

            ErrorZipFiles = os.path.join(os.getcwd(), "ErrorZipFiles")
            try:
                logging.debug("Trying to move zip file from {0} to {1}".format(archived, ErrorZipFiles))
                shutil.move(archived,
                            os.path.join(os.getcwd(), 'ErrorZipFiles', 'DocumentsOfRecord' + timenow + ".zip"))
                logging.debug("The file DocumentsOfRecord{0}.zip has been moved to the folder {1}"
                              .format(timenow, str(os.path.join(os.getcwd(), 'ErrorZipFiles')))
                              )
                # Get directory name
                mydir = os.path.join(os.getcwd(), "DocumentsOfRecord")
                try:
                    shutil.rmtree(mydir)
                    logging.debug("The Folder {} is Deleted".format(mydir))
                except OSError as e:
                    logging.debug("Error: {0} - {1}}.".format(e.filename, e.strerror))

            except Exception as E:
                logging.debug("Unable to move the Zip file due to Exception: {}".format(E))

            return Success_Flag


        elif Success_Flag:
            logging.info("Import and Load is Successful!")

            try:
                shutil.move(archived,
                            os.path.join(os.getcwd(), 'UploadedZipFiles', 'DocumentsOfRecord' + timenow + ".zip"))
                logging.debug("The file DocumentsOfRecord{}.zip has been moved to the folder {}"
                              .format(timenow, str(os.path.join(os.getcwd(), 'UploadedZipFiles')))
                              )
                # Get directory name
                mydir = os.path.join(os.getcwd(), "DocumentsOfRecord")
                try:
                    shutil.rmtree(mydir)
                    logging.debug("The Folder {} is Deleted".format(mydir))
                except OSError as e:
                    logging.debug("Error: {0} - {1}}.".format(e.filename, e.strerror))

            except Exception as E:
                logging.debug("Unable to move the Zip file due to Exception: {}".format(E))

            return Success_Flag


    except (StaleElementReferenceException) as Stale:
        logging.critical("Exception", Stale)